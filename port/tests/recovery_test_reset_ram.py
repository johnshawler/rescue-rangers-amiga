#!/usr/bin/env python3
"""Independent ROM-instruction vs assembled native recovery reset RAM slice.
No snapshots or generated fixtures. Original RAM write order is compared too.
Run with py65/machine68k on PYTHONPATH and VASM pointing to vasmm68k_mot.
"""
from pathlib import Path
import hashlib
import os
import random
import subprocess
import tempfile
import machine68k
from py65.devices.mpu6502 import MPU

PORT = Path(__file__).resolve().parents[1]
SHA = '051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
BASE, CTX, STOP, STACK = 0x10000, 0x12000, 0x800, 0x1f0000

class OriginalBus(list):
    def __init__(self, rom):
        super().__init__([0] * 65536)
        self[0xc000:] = rom[16 + 7 * 16384:16 + 8 * 16384]
        self.writes = []
    def __setitem__(self, key, value):
        if isinstance(key, int):
            assert 0 <= key < 2048, ('unexpected original write', hex(key))
            self.writes.append((key, value))
        super().__setitem__(key, value)

def main():
    rom = (PORT.parent / 'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest() == SHA
    assert int.from_bytes(rom[16+8*16384-4:16+8*16384-2], 'little') == 0xffe0
    with tempfile.TemporaryDirectory(prefix='recovery-reset-') as tmp:
        out = Path(tmp) / 'reset.bin'
        subprocess.run([os.environ['VASM'], '-quiet', '-m68020', '-Fbin',
                        '-o', str(out), str(PORT/'src/recovery_reset_ram.s')], check=True)
        code = out.read_bytes()
    m = machine68k.Machine(machine68k.CPUType.M68EC020, 2048)
    mem, cpu = m.mem, m.cpu
    mem.w_block(0x1000, code)
    mem.w16(STOP, 0x60fe)
    rng = random.Random(0xfe24)
    bus = OriginalBus(rom)
    ref = MPU(memory=bus)
    trace = []
    def memory_trace(mode, width, address, value):
        if mode == 'W' and BASE <= address < BASE+2048:
            assert width == 0, ('non-byte game RAM write', width)
            trace.append((address-BASE, value))
        elif mode == 'W':
            assert CTX <= address < CTX+8 or STACK-64 <= address < STACK, ('unexpected native write', address)
    mem.set_trace_func(memory_trace)
    guard = bytes(range(16))
    def native(state, context, expected_status):
        mem.set_trace_mode(False)
        mem.w_block(BASE-16, guard + state + guard)
        mem.w_block(CTX-16, guard + context + guard)
        regs = [rng.getrandbits(32) for _ in range(15)]
        regs[8:10] = [BASE, CTX]
        cpu.w_sr(0x2700)
        cpu.w_sp(STACK)
        mem.w32(STACK, STOP)
        for i, value in enumerate(regs):
            cpu.w_reg(i, value)
        cpu.w_pc(0x1000)
        trace.clear()
        mem.set_trace_mode(True)
        for _ in range(100):
            cpu.execute(1000)
            if cpu.r_pc() == STOP:
                break
        else:
            raise AssertionError('native execution timeout')
        mem.set_trace_mode(False)
        assert cpu.r_reg(0) == expected_status & 0xffffffff
        assert [cpu.r_reg(i) for i in range(1, 15)] == regs[1:]
        assert cpu.r_sp() == STACK+4
        for address in (BASE-16, BASE+2048, CTX-16, CTX+8):
            assert bytes(mem.r_block(address, 16)) == guard
        return bytes(mem.r_block(BASE, 2048)), bytes(mem.r_block(CTX, 8)), list(trace)
    count = 0
    # Every P bit pattern, four hostile RAM patterns, and 512 independent random states.
    cases = [(p, bytes([v])*2048) for p in range(256) for v in (0, 0xff, 0xa5, 0x5a)]
    cases += [(rng.randrange(256), rng.randbytes(2048)) for _ in range(512)]
    for flags, state in cases:
        a, x, sp, reserved = (rng.randrange(256) for _ in range(4))
        ctx = bytes((0xfe, 0x24, a, x, 0, flags, sp, reserved))
        bus[:2048] = state
        bus.writes.clear()
        ref.pc, ref.a, ref.x, ref.y, ref.p, ref.sp = 0xfe24, a, x, 0, flags, sp
        for _ in range(10000):
            if ref.pc == 0xfe43:
                break
            assert 0xfe24 <= ref.pc < 0xfe43, ('unsupported original boundary', hex(ref.pc))
            ref.step()
        else:
            raise AssertionError('original execution timeout')
        expected_ctx = ref.pc.to_bytes(2, 'big') + bytes((ref.a, ref.x, ref.y, ref.p, ref.sp, reserved))
        got, gotctx, writes = native(state, ctx, 1)
        assert got == bytes(bus[:2048]), ('RAM mismatch', count)
        assert gotctx == expected_ctx, ('context mismatch', count, gotctx, expected_ctx)
        assert writes == bus.writes, ('write-order mismatch', count)
        assert len(writes) == 2064
        # An explicit unsupported boundary, including a second call, must be inert.
        rejected, rejectedctx, writes = native(got, gotctx, -1)
        assert (rejected, rejectedctx, writes) == (got, gotctx, [])
        count += 1
    invalid_count = 0
    for y in range(1, 256):
        state = rng.randbytes(2048)
        context = bytes((0xfe, 0x24, 0, 0, y, 0, 0, 0))
        assert native(state, context, -1) == (state, context, [])
        invalid_count += 1
    # Every other PC is unsupported, not silently treated as a fresh reset.
    state = rng.randbytes(2048)
    for pc in range(65536):
        if pc == 0xfe24:
            continue
        context = pc.to_bytes(2, 'big') + bytes(6)
        assert native(state, context, -1) == (state, context, [])
        invalid_count += 1
    m.cleanup()
    print(f'PASS: {count} original-ROM/native differential cases; 2064 ordered byte writes each.')
    print(f'PASS: {count} completed-boundary rejections + {invalid_count} invalid-context rejections.')
    print('PASS: all 2048 RAM bytes, full 8-byte context, guards, preserved registers and stack balance.')

if __name__ == '__main__':
    main()
