#!/usr/bin/env python3
"""Execute original mapper-reset slice and assembled 68020, ordered bus proof."""
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
BASE, CTX, JOURNAL, STOP, STACK = 0x10000, 0x12000, 0x13000, 0x800, 0x1f0000

class OriginalBus(list):
    def __init__(self, rom):
        super().__init__([0]*65536)
        self[0xc000:] = rom[16+7*16384:16+8*16384]
        self.events = []
        self.publications = []
    def __setitem__(self, address, value):
        if isinstance(address, int):
            if address in (0xfff0, 0x9fff, 0xbfff, 0xdfff):
                publication = (address, value, self[0xf5])
                self.events.append(('mapper', *publication))
                self.publications.append(publication)
                return  # Mapper writes must NOT alter fixed-bank ROM instructions.
            assert 0 <= address < 2048, ('unsupported write', hex(address))
            self.events.append(('ram', address, value))
        super().__setitem__(address, value)

def main():
    rom = (PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest() == SHA
    with tempfile.TemporaryDirectory(prefix='recovery-mapper-') as tmp:
        out = Path(tmp)/'mapper.bin'
        subprocess.run([os.environ['VASM'], '-quiet', '-m68020', '-Fbin', '-o', str(out),
                        str(PORT/'src/recovery_reset_mapper.s')], check=True)
        code = out.read_bytes()
    m = machine68k.Machine(machine68k.CPUType.M68EC020, 2048)
    mem, cpu = m.mem, m.cpu
    mem.w_block(0x1000, code)
    mem.w16(STOP, 0x60fe)
    rng = random.Random(0xfe43)
    bus = OriginalBus(rom)
    ref = MPU(memory=bus)
    events = []
    def trace(mode, width, address, value):
        if mode != 'W':
            return
        if BASE <= address < BASE+2048:
            assert width == 0
            events.append(('ram', address-BASE, value))
        elif address == JOURNAL:
            assert width == 1
            if value:
                assert 1 <= value <= 20
                record = JOURNAL+2+(value-1)*4
                addr = mem.r16(record)
                data, busy = mem.r8(record+2), mem.r8(record+3)
                assert busy == mem.r8(BASE+0xf5)
                events.append(('mapper', addr, data, busy))
        else:
            assert (JOURNAL+2 <= address < JOURNAL+82 or CTX <= address < CTX+8
                    or STACK-96 <= address < STACK), ('unexpected native write', address)
    mem.set_trace_func(trace)
    guard = bytes(range(16))
    def native(state, context, journal, status):
        mem.set_trace_mode(False)
        for address, data in ((BASE, state), (CTX, context), (JOURNAL, journal)):
            mem.w_block(address-16, guard+data+guard)
        regs = [rng.getrandbits(32) for _ in range(15)]
        regs[8:11] = [BASE, CTX, JOURNAL]
        cpu.w_sr(0x2700)
        cpu.w_sp(STACK)
        mem.w32(STACK, STOP)
        for i, value in enumerate(regs):
            cpu.w_reg(i, value)
        cpu.w_pc(0x1000)
        events.clear()
        mem.set_trace_mode(True)
        for _ in range(100):
            cpu.execute(1000)
            if cpu.r_pc() == STOP:
                break
        else:
            raise AssertionError('native timeout')
        mem.set_trace_mode(False)
        assert cpu.r_reg(0) == status & 0xffffffff
        assert [cpu.r_reg(i) for i in range(1,15)] == regs[1:]
        assert cpu.r_sp() == STACK+4
        for address, size in ((BASE,2048), (CTX,8), (JOURNAL,82)):
            assert bytes(mem.r_block(address-16,16)) == guard
            assert bytes(mem.r_block(address+size,16)) == guard
        return (bytes(mem.r_block(BASE,2048)), bytes(mem.r_block(CTX,8)),
                bytes(mem.r_block(JOURNAL,82)), list(events))
    count = 0
    # Every flag pattern, stack pointer, and busy byte, plus random full RAM.
    cases = [(i, i, i, bytes([v])*2048) for i in range(256) for v in (0,255,0xa5,0x5a)]
    cases += [(rng.randrange(256), rng.randrange(256), rng.randrange(256), rng.randbytes(2048)) for _ in range(1024)]
    for flags, sp, busy, initial in cases:
        state = bytearray(initial)
        state[0xf5], state[0xf6] = busy, 0
        state = bytes(state)
        a, x, y, reserved = (rng.randrange(256) for _ in range(4))
        context = bytes((0xfe,0x43,a,x,y,flags,sp,reserved))
        bus[:2048] = state
        bus.events.clear()
        bus.publications.clear()
        ref.pc, ref.a, ref.x, ref.y, ref.p, ref.sp = 0xfe43,a,x,y,flags,sp
        for _ in range(1000):
            if ref.pc == 0xfe67:
                break
            assert (0xfe43 <= ref.pc < 0xfe67 or 0xff1f <= ref.pc <= 0xff74), ('unsupported boundary', hex(ref.pc))
            ref.step()
        else:
            raise AssertionError('original timeout')
        expected_context = ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved))
        expected_journal = len(bus.publications).to_bytes(2,'big') + b''.join(
            addr.to_bytes(2,'big')+bytes((data,b)) for addr,data,b in bus.publications)
        got = native(state,context,rng.randbytes(82),1)
        assert got == (bytes(bus[:2048]),expected_context,expected_journal,bus.events), ('differential mismatch',count)
        assert len(bus.events) == 34 and len(bus.publications) == 20
        # Independently decode five-bit MMC1 commits, keeping full bytes in journal.
        commits = [sum((bus.publications[j+i][1]&1)<<i for i in range(5)) for j in range(0,20,5)]
        assert commits == [6,0x1e,0,0x10]
        assert native(got[0],got[1],got[2],-1) == (*got[:3],[])
        count += 1
    invalid = 0
    for deferred in range(1,256):
        state = bytearray(rng.randbytes(2048)); state[0xf6] = deferred
        context = bytes((0xfe,0x43))+rng.randbytes(6)
        journal = rng.randbytes(82)
        assert native(bytes(state),context,journal,-1) == (bytes(state),context,journal,[])
        invalid += 1
    state = bytearray(rng.randbytes(2048)); state[0xf6] = 0; state = bytes(state)
    for pc in range(65536):
        if pc == 0xfe43:
            continue
        context = pc.to_bytes(2,'big')+rng.randbytes(6)
        journal = rng.randbytes(82)
        assert native(state,context,journal,-1) == (state,context,journal,[])
        invalid += 1
    m.cleanup()
    print(f'PASS: {count} original-ROM/native differential cases, 34 ordered events each (14 RAM + 20 mapper).')
    print(f'PASS: {count} completed-boundary and {invalid} invalid/deferred-audio rejections.')
    print('PASS: full RAM including original stack bytes, context, journal, busy ordering, guards, native registers/stack.')

if __name__ == '__main__':
    main()
