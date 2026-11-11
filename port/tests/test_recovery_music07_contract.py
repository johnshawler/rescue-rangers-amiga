#!/usr/bin/env python3
"""ROM-free synthetic ABI/contract checks for command07's native helper.

This supplements, and cannot replace, the private original-ROM differential
proof. All resource bytes here are invented test data. No ROM or py65 is used.
"""
from pathlib import Path
import os
import random
import struct
import subprocess
import tempfile
import machine68k

PORT = Path(__file__).resolve().parents[1]
RAM, CTX, JOURNAL, RESOURCE = 0x10000, 0x12000, 0x13000, 0x20000
STACK, STOP = 0x1f0000, 0x800
APU = ((0x4000, 0x30), (0x4004, 0x30), (0x4008, 0),
       (0x400c, 0x30), (0x4001, 8), (0x4005, 8), (0x4015, 15))
EXPECTED_JOURNAL = struct.pack('>H', 7) + b''.join(
    struct.pack('>HBB', address, value, 1) for address, value in APU)


def expected_result(state, context, pointer, channels):
    """Independent declarative final-state contract, not native-code replay.

Only these RAM fields may differ. Original temporary stack bytes remain even
though the logical stack has returned; all four mute calls reuse one frame.
    """
    expected = bytearray(state)
    expected[0xc1:0xc3] = bytes((pointer & 255, pointer >> 8))
    expected[0xc8:0xce] = bytes((0, 1, 0x99, 0, 0, 0))
    expected[0x728:0x77c] = bytes(84)
    for channel, (high, low) in enumerate(channels):
        expected[0x754 + channel] = high
        expected[0x750 + channel] = low
        if high or low:
            expected[0x77c + channel] = 255
    sp = context[6]
    for offset, value in enumerate((0x80, 0xe5, 0, 0x81, 0xcc)):
        expected[0x100 + ((sp - offset) & 255)] = value
    nesting = state[0xc0]
    p = (context[5] & 0x7c) | (nesting & 128) | (2 if nesting == 0 else 0)
    out_context = bytes((0xc0, 0xf3, 15, 255, 12, p, (sp + 2) & 255, context[7]))
    return bytes(expected), out_context


def main():
    with tempfile.TemporaryDirectory(prefix='music07-contract-') as directory:
        binary = Path(directory) / 'helper.bin'
        subprocess.run([os.environ['VASM'], '-quiet', '-m68020', '-Fbin',
                        '-o', str(binary), str(PORT / 'src/recovery_music07_command.s')], check=True)
        code = binary.read_bytes()
    machine = machine68k.Machine(machine68k.CPUType.M68EC020, 2048)
    mem, cpu = machine.mem, machine.cpu
    mem.w_block(0x1000, code)
    mem.w16(STOP, 0x60fe)
    rng = random.Random(0x1307)
    guard = bytes(range(16))
    writes, reads, published = [], [], []

    def trace(mode, width, address, value):
        if RESOURCE <= address < RESOURCE + 16384:
            assert mode == 'R' and width == 0, 'Resource must be read-only byte data'
            reads.append(address - RESOURCE)
        elif mode == 'W':
            writes.append((width, address, value))
            assert (RAM <= address < RAM + 2048 or CTX <= address < CTX + 8
                    or JOURNAL <= address < JOURNAL + 30 or STACK - 128 <= address < STACK)
            if RAM <= address < RAM + 2048:
                assert width == 0
            if address == JOURNAL:
                assert width == 1 and 0 <= value <= 7
                if value:
                    record = JOURNAL + 2 + (value - 1) * 4
                    published.append((mem.r16(record), mem.r8(record + 2), mem.r8(record + 3)))

    mem.set_trace_func(trace)

    def call(state, context, resource, success, pointer=None, channels=None):
        mem.set_trace_mode(False)
        initial_journal = rng.randbytes(30)
        buffers = ((RAM, bytes(state)), (CTX, bytes(context)),
                   (JOURNAL, initial_journal), (RESOURCE, bytes(resource)))
        for address, data in buffers:
            mem.w_block(address - 16, guard + data + guard)
        regs = [rng.getrandbits(32) for _ in range(15)]
        regs[8:12] = [RAM, CTX, JOURNAL, RESOURCE]
        cpu.w_sr(0x2700)
        cpu.w_sp(STACK)
        mem.w32(STACK, STOP)
        for index, value in enumerate(regs):
            cpu.w_reg(index, value)
        cpu.w_pc(0x1000)
        writes.clear(); reads.clear(); published.clear()
        mem.set_trace_mode(True)
        for _ in range(100):
            cpu.execute(1000)
            if cpu.r_pc() == STOP:
                break
        else:
            raise AssertionError('Native helper failed bounded execution')
        mem.set_trace_mode(False)
        assert cpu.r_reg(0) == (1 if success else 0xffffffff)
        assert [cpu.r_reg(i) for i in range(1, 15)] == regs[1:]
        assert cpu.r_sp() == STACK + 4
        for address, data in buffers:
            assert bytes(mem.r_block(address - 16, 16)) == guard
            assert bytes(mem.r_block(address + len(data), 16)) == guard
        assert bytes(mem.r_block(RESOURCE, 16384)) == bytes(resource)
        if success:
            expected_ram, expected_context = expected_result(state, context, pointer, channels)
            assert bytes(mem.r_block(RAM, 2048)) == expected_ram
            assert bytes(mem.r_block(CTX, 8)) == expected_context
            assert bytes(mem.r_block(JOURNAL, 30)) == EXPECTED_JOURNAL
            assert published == [(address, value, 1) for address, value in APU]
            offset = pointer - 0x8000
            assert reads == [0xa00, 0xa11, 0xa12] + list(range(offset, offset + 9))
            # Includes repeated original stack/CF stores, not just final deltas.
            assert sum(RAM <= address < RAM + 2048 for _, address, _ in writes) == 118 + sum(bool(h or l) for h, l in channels)
        else:
            for address, data in buffers:
                assert bytes(mem.r_block(address, len(data))) == data
            assert not published
            assert all(STACK - 128 <= address < STACK for _, address, _ in writes)

    def fixture(case, pointer):
        state = bytearray(rng.randbytes(2048)); state[0xcf] = 0
        state[0xc0] = case & 255
        sp = case & 255
        state[0x100 + ((sp + 1) & 255)] = 0xf2
        state[0x100 + ((sp + 2) & 255)] = 0xc0
        context = bytes((0x80, 3, 7, rng.randrange(256), rng.randrange(256),
                         (case & 0xcf) | 0x20, sp, rng.randrange(256)))
        resource = bytearray(rng.randbytes(16384))
        resource[0xa00] = 8 + case % 248
        resource[0xa11:0xa13] = bytes((pointer >> 8, pointer & 255))
        channels = []
        for channel in range(4):
            enabled = case & (1 << channel)
            # Exercise high-only, low-only, and both-byte nonempty pointers.
            style = (case // 16 + channel) % 3
            channels.append((rng.randrange(1, 256) if enabled and style != 1 else 0,
                             rng.randrange(1, 256) if enabled and style != 0 else 0))
        header = bytes((0,)) + b''.join(bytes(pair) for pair in reversed(channels))
        resource[pointer - 0x8000:pointer - 0x8000 + 9] = header
        return state, context, resource, channels

    positive = 0
    for pointer in (0x8000, 0x80ff, 0x9237, 0xbff7):
        for case in range(256):
            state, context, resource, channels = fixture(case, pointer)
            call(state, context, resource, True, pointer, channels)
            positive += 1
    state, context, resource, channels = fixture(7, 0x9237)
    negative = 0

    def reject(s=state, c=context, r=resource):
        nonlocal negative
        call(s, c, r, False)
        negative += 1

    for pc in (0, 0x8002, 0x8004, 0xc0bf, 0xc0f3, 0xffff):
        reject(c=pc.to_bytes(2, 'big') + context[2:])
    for value in range(256):
        if value != 7:
            reject(c=context[:2] + bytes((value,)) + context[3:])
        if value & 0x30 != 0x20:
            reject(c=context[:5] + bytes((value,)) + context[6:])
        if value:
            changed = bytearray(state); changed[0xcf] = value; reject(s=changed)
            changed = bytearray(resource); changed[0x1237] = value; reject(r=changed)
        for delta, expected in ((1, 0xf2), (2, 0xc0)):
            if value != expected:
                changed = bytearray(state)
                changed[0x100 + ((context[6] + delta) & 255)] = value
                reject(s=changed)
    for count in range(8):
        changed = bytearray(resource); changed[0xa00] = count; reject(r=changed)
    for pointer in (0, 0x7fff, 0xbff8, 0xc000, 0xffff):
        changed = bytearray(resource)
        changed[0xa11:0xa13] = bytes((pointer >> 8, pointer & 255))
        reject(r=changed)
    machine.cleanup()
    print(f'PASS: {positive} ROM-free synthetic command07 cases, every SP/counter byte, all canonical status patterns and 16 channel masks.')
    print(f'PASS: {negative} inert negative cases; full RAM/context/journal, ABI/stack/guards and immutable bounded resources.')


if __name__ == '__main__':
    main()
