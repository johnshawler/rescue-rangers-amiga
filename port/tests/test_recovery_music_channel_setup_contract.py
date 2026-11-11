#!/usr/bin/env python3
"""ROM-free synthetic ABI/contract checks for stream channel command06 and command07 volume/control.

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
def expected_result(state, context, resource, helper):
    """Declarative semantic stores/final state, not an original CPU replay."""
    result = bytearray(state)
    pointer = state[0x753] | state[0x757] << 8
    operand = resource[pointer - 0x8000]
    sp = context[6]
    stack = lambda offset: 0x100 + ((sp - offset) & 255)
    def increment(address):
        stores = [(0x753, (address + 1) & 255)]
        if address & 255 == 255:
            stores += [(0x757, (address + 1) >> 8)]
        return stores
    command = 6 + helper
    target = 0x84db if helper == 0 else 0x8652
    dispatch = 0x848f + helper * 2
    lo, hi = target & 255, target >> 8
    stores = [(stack(0), 0x83), (stack(1), 0xa6), (0xc4, command),
              (stack(2), 0x84), (stack(3), 0x7b),
              (0xc1, pointer & 255), (0xc2, pointer >> 8)] + increment(pointer)
    stores += [(0xc3, operand), (stack(2), 0x84), (stack(3), 0x82),
               (0xc1, 0x82), (0xc2, 0x84), (stack(2), lo),
               (0xc2, hi), (0xc1, lo)]
    value = operand if helper == 0 else ((state[0x737] & 0xc0) | operand | 0x30)
    stores += [(0x767 if helper == 0 else 0x737, value)]
    status = (context[5] & 0x6c) | helper | (value & 0x80) | (2 if value == 0 else 0)
    context_out = bytes((0x83, 0x9d, value, 0x2b, 14 + helper * 2, status, sp, context[7]))
    records = [(pointer, operand, 0), (dispatch, lo, 0), (dispatch + 1, hi, 0)]
    reads = [dispatch - 0x8000, dispatch + 1 - 0x8000, pointer - 0x8000,
             dispatch - 0x8000, dispatch + 1 - 0x8000]
    residue = [0x83, 0xa6, lo, 0x82]
    for address, value in stores:
        result[address] = value
    journal = struct.pack('>H', len(records)) + b''.join(struct.pack('>HBB', *r) for r in records)
    return bytes(result), context_out, journal, stores, records, reads, residue


def main():
    names = ('recovery_music_command06', 'recovery_music_stream_command07_volume')
    with tempfile.TemporaryDirectory(prefix='music-channel-setup-contract-') as directory:
        binary, source = Path(directory) / 'helper.bin', Path(directory) / 'helper.s'
        source.write_text(''.join(' bra.w ' + name + '\n' for name in names) +
                          '\n'.join((PORT / 'src' / (name + '.s')).read_text() for name in names))
        subprocess.run([os.environ['VASM'], '-quiet', '-m68020', '-Fbin',
                        '-o', str(binary), str(source)], check=True)
        code = binary.read_bytes()
    machine = machine68k.Machine(machine68k.CPUType.M68EC020, 2048)
    mem, cpu = machine.mem, machine.cpu
    mem.w_block(0x1000, code)
    mem.w16(STOP, 0x60fe)
    rng = random.Random(0x140e)
    guard = bytes(range(16))
    writes, reads, published = [], [], []
    active = 0
    journal_size = 14

    def trace(mode, width, address, value):
        if RESOURCE <= address < RESOURCE + 16384:
            assert mode == 'R' and width == 0, 'Resource must be read-only byte data'
            reads.append(address - RESOURCE)
        elif mode == 'R':
            size = 1 << width
            ranges = ((0x1000, 0x1000+len(code)+8), (STOP, STOP+4),
                      (RAM, RAM+2048), (CTX, CTX+8),
                      (JOURNAL, JOURNAL+journal_size), (STACK-256, STACK+4))
            assert any(lo <= address and address+size <= hi for lo, hi in ranges), ('Unexpected native read', width, address)
        elif mode == 'W':
            writes.append((width, address, value))
            assert (RAM <= address < RAM + 2048 or CTX <= address < CTX + 8
                    or JOURNAL <= address < JOURNAL + journal_size or STACK - 128 <= address < STACK)
            if RAM <= address < RAM + 2048:
                assert width == 0
            if address == JOURNAL:
                assert width == 1 and 0 <= value <= 3
                if value:
                    record = JOURNAL + 2 + (value - 1) * 4
                    published.append((mem.r16(record), mem.r8(record + 2), mem.r8(record + 3)))

    # Explicitly prove distant resource-window overruns cannot evade the tracer.
    for address in (RESOURCE-1, RESOURCE-0x5000, RESOURCE+16384, RESOURCE+16400, RESOURCE+0x5000, RESOURCE+0x10000, 0x90000):
        try:
            trace('R', 0, address, 0)
        except AssertionError:
            pass
        else:
            raise AssertionError('Unmapped read escaped the trace whitelist')

    mem.set_trace_func(trace)

    def call(state, context, resource, success, helper, allowed_reads=()):
        nonlocal active, journal_size
        active = helper
        journal_size = 14
        mem.set_trace_mode(False)
        initial_journal = rng.randbytes(journal_size)
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
        cpu.w_pc(0x1000 + helper * 4)
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
            expected_ram, expected_context, expected_journal, stores, records, expected_reads, residue = expected_result(state, context, resource, helper)
            assert bytes(mem.r_block(RAM, 2048)) == expected_ram
            assert bytes(mem.r_block(CTX, 8)) == expected_context
            assert bytes(mem.r_block(JOURNAL, journal_size)) == expected_journal
            pointer = state[0x753] | state[0x757] << 8
            assert published == records
            assert reads == expected_reads
            assert [(address - RAM, value) for _, address, value in writes if RAM <= address < RAM + 2048] == stores
            assert [mem.r8(RAM + 0x100 + ((context[6] - i) & 255)) for i in range(len(residue))] == residue
        else:
            for address, data in buffers:
                assert bytes(mem.r_block(address, len(data))) == data
            assert not published and reads == list(allowed_reads)
            assert all(STACK - 128 <= address < STACK for _, address, _ in writes)

    # Entire resource views are invented. Required target bytes are semantic
    # code-path constants, not copied ROM assets. Aliases intentionally see the
    # final guarded target bytes when an operand overlaps the dispatch table.
    def fixture(case, pointer, operand=0, helper=0):
        state = bytearray(rng.randbytes(2048))
        state[0x753], state[0x757] = pointer & 255, pointer >> 8
        context = bytes((0x83, 0xa0, 6 + helper, 0x2b, rng.randrange(256),
                         (case & 0xcf) | 0x20, case & 255, rng.randrange(256)))
        resource = bytearray(rng.randbytes(16384))
        resource[pointer - 0x8000] = operand
        resource[0x48f:0x493] = bytes((0xdb, 0x84, 0x52, 0x86))
        return state, context, resource

    positive = negative = 0
    operands = (0, 1, 0x0f, 0x30, 0x3f, 0x7f, 0x80, 0xff)
    for helper in (0, 1):
        pointers = (0x8000, 0x80fe, 0x80ff, 0x848e, 0x848f, 0x8490,
                    0x8491, 0x8492, 0xbffe, 0xbfff)
        for pointer in pointers:
            for case in range(256):
                for operand in operands:
                    state, context, resource = fixture(case, pointer, operand, helper)
                    state[0x737] = (case & 3) << 6
                    call(state, context, resource, True, helper)
                    positive += 1
        for operand in range(256):
            for top in (0, 0x40, 0x80, 0xc0):
                state, context, resource = fixture(operand, 0x9876, operand, helper)
                state[0x737] = top | (operand & 0x3f)
                call(state, context, resource, True, helper)
                positive += 1
        state, context, resource = fixture(7, 0x9237, helper=helper)
        def reject(s=state, c=context, r=resource, reads=()):
            nonlocal negative
            call(s, c, r, False, helper, reads)
            negative += 1
        pc_expected = 0x83a0
        for pc in range(65536):
            if pc != pc_expected:
                reject(c=pc.to_bytes(2, 'big') + context[2:])
        for value in range(256):
            if value & 0x30 != 0x20:
                reject(c=context[:5] + bytes((value,)) + context[6:])
            for offset, allowed in ((3, 0x2b), (2, 6 + helper)):
                if value != allowed:
                    changed = bytearray(context); changed[offset] = value; reject(c=changed)
            if value < 0x80 or value >= 0xc0:
                changed = bytearray(state); changed[0x757] = value; reject(s=changed)
            dispatch = 0x48f + 2 * helper
            target = (0xdb, 0x84) if helper == 0 else (0x52, 0x86)
            for offset, required in zip((dispatch, dispatch + 1), target):
                if value != required:
                    changed = bytearray(resource); changed[offset] = value
                    reject(r=changed, reads=(dispatch,) if offset == dispatch else (dispatch, dispatch + 1))
        for pointer in (0, 0x7fff, 0xc000, 0xffff):
            changed = bytearray(state)
            changed[0x753], changed[0x757] = pointer & 255, pointer >> 8
            reject(s=changed)
        completed = expected_result(state, context, resource, helper)
        reject(s=completed[0], c=completed[1])
    machine.cleanup()
    print(f'PASS: {positive} ROM-free channel-setup cases; all SP/canonical statuses, all operand values/control-high-bit/flag edges, pointer wrap/window/dispatch aliases.')
    print(f'PASS: {negative} inert negatives; exact full RAM/context/journal, ordered stack residue/stores, native ABI/guards, bounded immutable reads; preflight distinguished.')


if __name__ == '__main__':
    main()
