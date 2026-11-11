#!/usr/bin/env python3
"""ROM-free synthetic ABI/contract checks for the first music-byte fetch helper.

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
def expected_result(state, context, resource):
    """Declarative final-state contract using integer arithmetic, not CPU replay."""
    result = bytearray(state)
    pointer = state[0x753] | state[0x757] << 8
    advanced = pointer + 1
    low_sum = state[0xca] + state[0xc8]
    carry = int(low_sum > 255)
    high_sum = state[0xc9] + carry
    # Signed overflow is possible only for positive127 plus carry1.
    overflow = 0x40 if state[0xc9] == 127 and carry else 0
    increment_result = (advanced >> 8) if pointer & 255 == 255 else (advanced & 255)
    status = ((context[5] & 0x24) | overflow | (increment_result & 0x80)
              | (2 if increment_result == 0 else 0))
    result[0xc0] = state[0xc0] + 4
    result[0xc3] = 0
    result[0xc8] = low_sum & 255
    result[0xc7] = high_sum & 255
    result[0xc1:0xc3] = bytes((pointer & 255, pointer >> 8))
    result[0x753] = advanced & 255
    result[0x757] = advanced >> 8
    sp = context[6]
    for offset, value in enumerate((0xc0, 0xf8, 0, 3, 0x80, 0x84, 0x83, 0x9f)):
        result[0x100 + ((sp - offset) & 255)] = value
    value = resource[pointer - 0x8000]
    context_out = bytes((0x83, 0xa0, value, 0x2b, 0, status, (sp - 6) & 255, context[7]))
    journal = struct.pack('>HHBB', 1, pointer, value, 0)
    return bytes(result), context_out, journal


def main():
    with tempfile.TemporaryDirectory(prefix='music-fetch-contract-') as directory:
        binary = Path(directory) / 'helper.bin'
        subprocess.run([os.environ['VASM'], '-quiet', '-m68020', '-Fbin',
                        '-o', str(binary), str(PORT / 'src/recovery_music_tick_fetch.s')], check=True)
        code = binary.read_bytes()
    machine = machine68k.Machine(machine68k.CPUType.M68EC020, 2048)
    mem, cpu = machine.mem, machine.cpu
    mem.w_block(0x1000, code)
    mem.w16(STOP, 0x60fe)
    rng = random.Random(0x140e)
    guard = bytes(range(16))
    writes, reads, published = [], [], []

    def trace(mode, width, address, value):
        if RESOURCE - 16 <= address < RESOURCE + 16400:
            assert RESOURCE <= address < RESOURCE + 16384, 'Out-of-window resource access'
            assert mode == 'R' and width == 0, 'Resource must be read-only byte data'
            reads.append(address - RESOURCE)
        elif mode == 'W':
            writes.append((width, address, value))
            assert (RAM <= address < RAM + 2048 or CTX <= address < CTX + 8
                    or JOURNAL <= address < JOURNAL + 6 or STACK - 128 <= address < STACK)
            if RAM <= address < RAM + 2048:
                assert width == 0
            if address == JOURNAL:
                assert width == 1 and 0 <= value <= 1
                if value:
                    record = JOURNAL + 2 + (value - 1) * 4
                    published.append((mem.r16(record), mem.r8(record + 2), mem.r8(record + 3)))

    mem.set_trace_func(trace)

    def call(state, context, resource, success):
        mem.set_trace_mode(False)
        initial_journal = rng.randbytes(6)
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
            expected_ram, expected_context, expected_journal = expected_result(state, context, resource)
            assert bytes(mem.r_block(RAM, 2048)) == expected_ram
            assert bytes(mem.r_block(CTX, 8)) == expected_context
            assert bytes(mem.r_block(JOURNAL, 6)) == expected_journal
            pointer = state[0x753] | state[0x757] << 8
            assert published == [(pointer, resource[pointer - 0x8000], 0)]
            assert reads == [pointer - 0x8000]
            assert sum(RAM <= address < RAM + 2048 for _, address, _ in writes) == 15 + (pointer & 255 == 255)
        else:
            for address, data in buffers:
                assert bytes(mem.r_block(address, len(data))) == data
            assert not published and not reads
            assert all(STACK - 128 <= address < STACK for _, address, _ in writes)

    # Invented values deliberately cover both tempo-ADC carry outcomes,
    # second-ADC signed overflow and unsigned wrap, and input V preservation bugs.
    arithmetic = ((0, 0, 0), (255, 1, 127), (255, 1, 255), (127, 1, 128),
                  (128, 128, 127), (255, 255, 128), (0, 255, 127), (1, 0, 255))

    def fixture(case, pointer, operand_index=None):
        state = bytearray(rng.randbytes(2048))
        state[0xc0] = (case % 3) * 4
        for address in (0xd0, 0xd1, 0xcf, 0x763): state[address] = 0
        state[0xdb] = case % 8
        state[0xdc + state[0xdb]] = 0x88
        state[0xca], state[0xc8], state[0xc9] = arithmetic[case % len(arithmetic) if operand_index is None else operand_index]
        state[0x753], state[0x757] = pointer & 255, pointer >> 8
        context = bytes((0xc0, 0xf3, rng.randrange(256), rng.randrange(256), rng.randrange(256),
                         (case & 0xc7) | 0x20, case & 255, rng.randrange(256)))
        resource = rng.randbytes(16384)
        return state, context, resource

    positive = 0
    for pointer in (0x8000, 0x807e, 0x807f, 0x80fe, 0x80ff, 0xbffe, 0xbfff):
        for case in range(256):
            for operand_index in range(len(arithmetic)):
                state, context, resource = fixture(case, pointer, operand_index)
                call(state, context, resource, True)
                positive += 1
    state, context, resource = fixture(7, 0x9237)
    negative = 0

    def reject(s=state, c=context):
        nonlocal negative
        call(s, c, resource, False)
        negative += 1

    for pc in range(65536):
        if pc != 0xc0f3:
            reject(c=pc.to_bytes(2, 'big') + context[2:])
    for value in range(256):
        if value & 0x38 != 0x20:
            reject(c=context[:5] + bytes((value,)) + context[6:])
        for address, allowed in ((0xc0, (0, 4, 8)), (0xd0, (0,)), (0xd1, (0,)),
                                 (0xcf, (0,)), (0x763, (0,)), (0xe3, (0x88,))):
            if value not in allowed:
                changed = bytearray(state); changed[address] = value; reject(s=changed)
        if value > 7:
            changed = bytearray(state); changed[0xdb] = value; reject(s=changed)
        if value < 0x80 or value >= 0xc0:
            changed = bytearray(state); changed[0x757] = value; reject(s=changed)
    # Explicit out-of-window endpoints and a completed-boundary re-entry.
    for pointer in (0, 0x7fff, 0xc000, 0xffff):
        changed = bytearray(state)
        changed[0x753], changed[0x757] = pointer & 255, pointer >> 8
        reject(s=changed)
    completed_ram, completed_ctx, _ = expected_result(state, context, resource)
    reject(s=completed_ram, c=completed_ctx)
    machine.cleanup()
    print(f'PASS: {positive} ROM-free synthetic first-fetch cases, every SP and canonical D=0 status, tempo overflow/carry and pointer/window edges.')
    print(f'PASS: {negative} inert negative cases without resource reads; complete RAM/context/read journal, ABI/stack/guards and immutable resources.')


if __name__ == '__main__':
    main()
