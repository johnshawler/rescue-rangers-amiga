#!/usr/bin/env python3
"""Private 68-call target verifier. Expected state comes only from continuous ROM execution."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from py65.devices.mpu6502 import MPU
from recovery_test_active_nmi_runtime_chain import ControllerBus, SHA

PORT = Path(__file__).resolve().parents[1]
MARKER = b'CDRRUN01'
STRIDE = 11000
SIZES = {0:30,1:0,2:82,3:8754,4:0,5:6,6:298,7:22,8:22,9:74,10:0,
         11:454,12:30,13:6,14:14,15:6,16:18,17:14,18:14,19:22,20:14,
         21:14,22:10,23:0,24:6,25:22,26:10,27:10,28:18,29:22,30:74,31:454}
PREFIX = (1,2,3,4,5,6,7,0,8,9,10,30,31,7,12,13,14,15,16,15,17,15,18,
          15,19,15,20,15,21,15,22)
TARGETS = {0:0xc0f3,1:0xfe43,2:0xfe67,3:0xfe7c,4:0xc574,5:0xfe8d,
           6:0xc0bf,7:0x8003,8:0xfe8d,9:0xc584,10:0xfe8d,12:0xc0f3,
           13:0x83a0,14:0x839d,15:0x83a0,16:0x839d,17:0x839d,
           18:0x839d,19:0x839d,20:0x839d,21:0x839d,22:0x8085,
           24:0x83a0,25:0x839d,26:0x8085,27:0x83fd,28:0x8085,
           29:0xfe90,31:0xc0bf}

def architectural_status_view(raw):
    """Comparison view ONLY. Raw reference P and original frame RAM stay untouched."""
    return raw[:5] + bytes(((raw[5] & 0xef) | 0x20,)) + raw[6:]

def oracle(rom):
    bus = ControllerBus(rom)
    bus.inputs = (0,0)
    bus.pos = [0,0]
    bus[:2048] = [0xa5]*2048
    bus.events.clear()
    ref = MPU(memory=bus)
    ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp = 0xfe24,0x17,0x33,0,0x24,0xfd
    results = []
    frames = []
    instructions = 0
    for call in range(68):
        if call < len(PREFIX):
            index = PREFIX[call]
        elif ref.pc == 0x8085: index = 23
        elif ref.pc == 0x839d: index = 24
        elif ref.pc == 0x83a0:
            index = 25 if ref.a in (4,5,6,7,8,9,24) else 26 if ref.a in range(32,256,32) else 27
        elif ref.pc == 0x83fd: index = 28
        elif ref.pc == 0xc0f9: index = 29
        elif ref.pc == 0xfe90: index = 30
        else: raise AssertionError(('unsupported boundary',call,hex(ref.pc)))
        start = len(bus.events)
        dma_start = len(bus.dma)
        status = 0 if call == 11 else 1
        if index in (6,31):
            assert ref.pc == (0xfe8d if index == 6 else 0xfe90)
            saved_sp = ref.sp
            expected_frame = bytes((ref.pc>>8,ref.pc&255,(ref.p&0xef)|0x20,ref.p|0x34,ref.a,ref.x,ref.y))
            ref.nmi()
        if index in (9,30): bus.inputs,bus.pos = (0,0),[0,0]
        target = (0xfe90 if status == 0 else 0xc2a8) if index == 30 else TARGETS.get(index)
        for count in range(50000):
            pc = ref.pc
            # Semantic resource reads, observed at the original load instruction.
            addr = None
            if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28):
                assert bus.bank == 3 and bus.mapper.control == 0x1e and not bus.mapper.bits
                if pc in (0x857a,0x802c,0x8030): addr = ((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
                elif pc in (0x868c,0x8693): addr = 0x8a02 if pc == 0x868c else 0x8a01
                elif pc in (0x83ba,0x83c1): addr = (0x8585 if pc == 0x83ba else 0x858c)+ref.y
                elif pc == 0x844d: addr = 0x8593+ref.y
                elif pc in (0x8626,0x862b): addr = (0x8934 if pc == 0x8626 else 0x8935)+ref.y
                elif pc == 0x8638: addr = ((bus[0xc5]|bus[0xc6]<<8)+ref.y)&65535
            if addr is not None:
                assert 0x8000 <= addr < 0xc000
                bus.events.append(('resource',addr,bus[addr],0))
            ref.step()
            instructions += 1
            if index == 23:
                if ref.pc == 0x839d or pc == 0x80ba: break
                assert ref.pc not in (0x82b0,0x8374), 'Untranslated envelope/callback'
            elif ref.pc == target and (index != 30 or status != 0 or pc == 0xfea3): break
        else: raise AssertionError(('original timeout',call,index,hex(ref.pc)))
        if index in (6,31):
            frame = bytes(bus[0x100+((saved_sp-i)&255)] for i in range(7))
            assert frame == expected_frame
            frames.append((saved_sp,frame))
            assert len(bus.dma) == dma_start+1
        if index in (8,29):
            saved_sp,frame = frames[-1]
            assert ref.p == frame[2] | 0x30
            assert bytes(bus[0x100+((saved_sp-i)&255)] for i in range(7)) == frame
            assert bus.bank == 6 and not bus.mapper.bits
        raw = struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
        context = architectural_status_view(raw)
        events = bus.events[start:]
        kind = ('mapper' if index in (2,7,8,29) else 'apu' if index in (0,12) else
                'controller' if index in (9,30) else 'resource' if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28) else 'ppu')
        published = [e for e in events if e[0] == kind]
        size = SIZES[index]
        journal = b''
        if size:
            journal = struct.pack('>H',len(published))+b''.join(struct.pack('>HBB',*e[1:]) for e in published)
            if index in (6,31):
                offset = 42 if index == 6 else 198
                assert len(journal) <= offset
                journal += bytes(offset-len(journal))+bus.dma[-1]
            journal += bytes(size-len(journal))
            assert len(journal) == size
        else: assert not published
        results.append((index,status,context,bytes(bus[:2048]),journal,raw))
    assert ref.pc == 0xc2a8 and ref.sp == 0xbc
    assert bus[0x1bd:0x1c0] == [4,0x93,0xc5]
    assert bus[0x80] == 2 and bus[0x18] == 0
    assert bus.bank == 6 and bus.mapper.control == 0x1e and not bus.mapper.bits
    assert len(frames) == 2
    return results,bus,instructions

def verify(chip,rom):
    assert len(chip) == 2*1024*1024, 'Expected stock 2 MiB Chip dump'
    assert hashlib.sha256(rom).hexdigest() == SHA, 'Private cartridge hash mismatch'
    assert chip.count(MARKER) == 1, 'Expected one runtime marker; wrong mode or corrupted marker'
    offset = chip.index(MARKER)
    assert offset+44 <= len(chip)
    status,calls,ram,ctx,snapshots,resource,stack,stack_end,sp = struct.unpack_from('>9I',chip,offset+8)
    assert (status,calls) == (0,68), ('Native ABI/status/call failure',status,calls)
    assert stack_end-stack == 4096 and sp == stack_end, 'Native stack imbalance'
    ranges = [(ram,2048),(ctx,8),(snapshots,68*STRIDE),(resource,16384),(stack,4096)]
    guard = bytes([0x5a])*16
    for address,size in ranges:
        assert address % 2 == 0, 'Unaligned native buffer'
        assert 16 <= address and address+size+16 <= len(chip), 'Buffer outside Chip'
        assert chip[address-16:address] == guard and chip[address+size:address+size+16] == guard, 'Guard corruption'
        assert address-16 >= offset+44 or address+size+16 <= offset, 'Report/guard alias'
    for i,(a,n) in enumerate(ranges):
        for b,m in ranges[i+1:]: assert a+n+16 <= b-16 or b+m+16 <= a-16, 'Buffer alias'
    assert chip[resource:resource+16384] == rom[49168:65552], 'Private resources changed'
    results,bus,instructions = oracle(rom)
    for call,(index,status,context,state,journal,raw) in enumerate(results):
        start = snapshots+call*STRIDE
        assert struct.unpack_from('>3I',chip,start) == (index,status,len(journal)), ('Snapshot header',call)
        assert chip[start+12:start+20] == context, ('Context',call,index,chip[start+12:start+20].hex(),context.hex())
        assert chip[start+20:start+2068] == state, ('Full original RAM',call,index)
        assert chip[start+2068:start+2068+len(journal)] == journal, ('Ordered journal/DMA',call,index)
        assert chip[start+2068+len(journal):start+STRIDE] == bytes(STRIDE-2068-len(journal)), ('Unused snapshot tail',call)
    assert chip[ram:ram+2048] == results[-1][3]
    assert chip[ctx:ctx+8] == results[-1][2]
    counts = {kind:sum(e[0] == kind for e in bus.events) for kind in ('mapper','ppu','apu','controller','resource')}
    return dict(status='PASS',proprietary_inputs=True,native_helper_calls=68,
                continuous_original_instructions=instructions,logical_NMIs=2,
                full_RAM_snapshots_equal=68,context_snapshots_equal=68,
                ordered_journal_records=counts,DMA_bytes_equal=512,
                immutable_resource_bytes=16384,original_saved_frames_exact=True,
                raw_reference_P_untouched=True,comparison='Explicit architectural B=0/U=1 view; saved frame bytes exact',
                final_PC='C2A8',final_context=results[-1][2].hex(),final_F6=bus[0xf6],
                final_mapper=list(bus.mapper.snapshot()[:4]),native_stack_balanced=True,
                next_dependency='C2A8 countdown remains untranslated',
                limit='Bounded private emulated-target checkpoint, not full boot, stage, audible output, speed or physical hardware')

def verify_amiga_log(log):
    """Verify effective configuration and actual core/run evidence, not caller labels."""
    assert re.findall(r'^Model: "(.*)"\.$',log,re.MULTILINE) == ['A1200OG'], 'Requested model not A1200OG'
    for name,value in (('cpu_model' ,'68020'),('fpu_model','0'),('mmu_model','0'),
                       ('chipmem_size','4'),('bogomem_size','0'),('fastmem_size','0'),
                       ('ntsc','false'),('cpu_cycle_exact','true'),
                       ('cpu_memory_cycle_exact','true'),('blitter_cycle_exact','true')):
        matches = re.findall(r'^'+name+r'=(.*)$',log,re.MULTILINE)
        assert matches and all(item.strip()==value for item in matches), ('Target configuration',name,matches)
    assert re.search(r'^CPU=68020, FPU=0, MMU=0, JIT=0\. ~cycle-exact 24-bit$',log,re.MULTILINE), 'Actual 68020 core configuration absent'
    assert re.search(r'^PAL mode V=50\.0000Hz .*\(PAL\)',log,re.MULTILINE), 'Actual PAL output absent'
    runs = re.findall(r'^PASS runs=(\d+) video_callbacks=(\d+) .*$',log,re.MULTILINE)
    assert runs == [('600','600')], ('Expected completed 600-frame run',runs)
    return dict(model='A1200OG',CPU='68020',FPU=0,MMU=0,JIT=0,Chip_MiB=2,Fast_MiB=0,
                CPU_cycle_exact=True,memory_cycle_exact=True,blitter_cycle_exact=True,
                standard='PAL 50 Hz',runs=600,video_callbacks=600)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chip_dump',type=Path)
    parser.add_argument('--amiga-log',type=Path)
    args = parser.parse_args()
    rom = (PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    report=verify(args.chip_dump.read_bytes(),rom)
    if args.amiga_log: report['actual_target']=verify_amiga_log(args.amiga_log.read_text())
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
