#!/usr/bin/env python3
"""ROM-free synthetic ABI/contract checks for the complete music command04 helper.

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
    """Declarative final-state/effect contract; no CPU replay or ROM-derived data."""
    result = bytearray(state)
    pointer = state[0x753] | state[0x757] << 8
    advanced = pointer + 1
    operand = resource[pointer - 0x8000]
    flags = (state[0x75b] & 0x97) | operand
    sp = context[6]
    stack = lambda offset: 0x100 + ((sp - offset) & 255)
    # Explicit ordered semantic stores, including overwritten stack residue.
    stores = [(stack(0), 0x83), (stack(1), 0xa6), (0xc4, 4),
              (stack(2), 0x84), (stack(3), 0x7b),
              (0xc1, pointer & 255), (0xc2, pointer >> 8),
              (0x753, advanced & 255)]
    if pointer & 255 == 255:
        stores.append((0x757, advanced >> 8))
    stores += [(0xc3, operand), (stack(2), 0x84), (stack(3), 0x82),
               (0xc1, 0x82), (0xc2, 0x84), (stack(2), 0x51),
               (0xc2, 0x85), (0xc1, 0x51), (0x75b, flags)]
    for address, value in stores:
        result[address] = value
    status = (context[5] & 0x6c) | (flags & 0x80) | (2 if flags == 0 else 0)
    context_out = bytes((0x83, 0x9d, flags, 0x2b, 10, status, sp, context[7]))
    records = [(pointer, operand, 0), (0x848b, 0x51, 0), (0x848c, 0x85, 0)]
    journal = struct.pack('>H', 3) + b''.join(struct.pack('>HBB', *r) for r in records)
    return bytes(result), context_out, journal, stores, records


def main():
    with tempfile.TemporaryDirectory(prefix='music-command04-contract-') as directory:
        binary = Path(directory) / 'helper.bin'
        subprocess.run([os.environ['VASM'], '-quiet', '-m68020', '-Fbin',
                        '-o', str(binary), str(PORT / 'src/recovery_music_command04.s')], check=True)
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
                    or JOURNAL <= address < JOURNAL + 14 or STACK - 128 <= address < STACK)
            if RAM <= address < RAM + 2048:
                assert width == 0
            if address == JOURNAL:
                assert width == 1 and 0 <= value <= 3
                if value:
                    record = JOURNAL + 2 + (value - 1) * 4
                    published.append((mem.r16(record), mem.r8(record + 2), mem.r8(record + 3)))

    mem.set_trace_func(trace)

    def call(state, context, resource, success, allowed_reads=()):
        mem.set_trace_mode(False)
        initial_journal = rng.randbytes(14)
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
            expected_ram, expected_context, expected_journal, stores, records = expected_result(state, context, resource)
            assert bytes(mem.r_block(RAM, 2048)) == expected_ram
            assert bytes(mem.r_block(CTX, 8)) == expected_context
            assert bytes(mem.r_block(JOURNAL, 14)) == expected_journal
            pointer = state[0x753] | state[0x757] << 8
            assert published == records
            assert reads == [0x48b, 0x48c, pointer - 0x8000, 0x48b, 0x48c]
            assert [(address - RAM, value) for _, address, value in writes if RAM <= address < RAM + 2048] == stores
            assert [mem.r8(RAM + 0x100 + ((context[6] - i) & 255)) for i in range(4)] == [0x83, 0xa6, 0x51, 0x82]
        else:
            for address, data in buffers:
                assert bytes(mem.r_block(address, len(data))) == data
            assert not published and reads == list(allowed_reads)
            assert all(STACK - 128 <= address < STACK for _, address, _ in writes)

    # All data is invented. The two required dispatch bytes are code-path
    # constants, not an extracted resource. No private file is accessed.
    cases = ((0, 0), (0, 0xff), (0x68, 0), (0xff, 0),
             (0, 0x80), (0x80, 0x7f), (0x17, 0x68), (0x68, 0x68))

    def fixture(case, pointer, pair=(0, 0)):
        state = bytearray(rng.randbytes(2048))
        state[0x753], state[0x757] = pointer & 255, pointer >> 8
        state[0x75b] = pair[0]
        context = bytes((0x83, 0xa0, 4, 0x2b, rng.randrange(256),
                         (case & 0xcf) | 0x20, case & 255, rng.randrange(256)))
        resource = bytearray(rng.randbytes(16384))
        resource[pointer - 0x8000] = pair[1]
        resource[0x48b:0x48d] = bytes((0x51, 0x85))
        return state, context, resource

    positive = 0
    for pointer in (0x8000, 0x807f, 0x80fe, 0x80ff, 0x848b, 0x848c, 0xbffe, 0xbfff):
        for case in range(256):
            for pair in cases:
                state, context, resource = fixture(case, pointer, pair)
                call(state, context, resource, True)
                positive += 1
    state, context, resource = fixture(7, 0x9237)
    negative = 0

    def reject(s=state, c=context, r=resource, reads=()):
        nonlocal negative
        call(s, c, r, False, reads)
        negative += 1

    for pc in range(65536):
        if pc != 0x83a0:
            reject(c=pc.to_bytes(2, 'big') + context[2:])
    for value in range(256):
        if value & 0x30 != 0x20:
            reject(c=context[:5] + bytes((value,)) + context[6:])
        for offset, allowed in ((2, 4), (3, 0x2b)):
            if value != allowed:
                changed = bytearray(context); changed[offset] = value; reject(c=changed)
        if value < 0x80 or value >= 0xc0:
            changed = bytearray(state); changed[0x757] = value; reject(s=changed)
        for offset, required in ((0x48b, 0x51), (0x48c, 0x85)):
            if value != required:
                changed = bytearray(resource); changed[offset] = value
                reject(r=changed, reads=(0x48b,) if offset == 0x48b else (0x48b, 0x48c))
    for pointer in (0, 0x7fff, 0xc000, 0xffff):
        changed = bytearray(state)
        changed[0x753], changed[0x757] = pointer & 255, pointer >> 8
        reject(s=changed)
    completed_ram, completed_ctx, _, _, _ = expected_result(state, context, resource)
    reject(s=completed_ram, c=completed_ctx)
    machine.cleanup()
    print(f'PASS: {positive} ROM-free synthetic command04 cases, every SP/canonical status, flag/operand masks and pointer/window edges.')
    print(f'PASS: {negative} inert negatives including malformed dispatch resources; full RAM/context/read journal, ordered stores/stack residue, ABI/guards, immutable resources.')


if __name__ == '__main__':
    main()
