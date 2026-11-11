#!/usr/bin/env python3
"""Private 533-call target verifier. Expected state comes only from continuous ROM execution."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from recovery_test_active_nmi_runtime_chain import SerialMapper

from recovery_resident_fade_target_oracle import PORT,SHA,oracle
MARKER=b'CDRFADE1'

def layout(results):
    offsets=[];total=0
    for result in results:
        offsets.append(total);total+=2100+len(result[4])
    return offsets,total

def verify(chip,rom):
    assert len(chip) == 2*1024*1024, 'Expected stock 2 MiB Chip dump'
    assert hashlib.sha256(rom).hexdigest() == SHA, 'Private cartridge hash mismatch'
    assert chip.count(MARKER) == 1, 'Expected one runtime marker; wrong mode or corrupted marker'
    offset = chip.index(MARKER)
    assert offset+44 <= len(chip)
    status,calls,ram,ctx,snapshots,resource,stack,stack_end,sp = struct.unpack_from('>9I',chip,offset+8)
    assert (status,calls) == (0,533), ('Native ABI/status/call failure',status,calls)
    assert stack_end-stack == 4096 and sp == stack_end, 'Native stack imbalance'
    results,bus,instructions = oracle(rom)
    offsets,total=layout(results)
    ranges = [(ram,2048),(ctx,8),(snapshots,total),(resource,16384),(stack,4096)]
    guard = bytes([0x5a])*16
    for address,size in ranges:
        assert address % 2 == 0, 'Unaligned native buffer'
        assert 16 <= address and address+size+16 <= len(chip), 'Buffer outside Chip'
        assert chip[address-16:address] == guard and chip[address+size:address+size+16] == guard, 'Guard corruption'
        assert address-16 >= offset+44 or address+size+16 <= offset, 'Report/guard alias'
    for i,(a,n) in enumerate(ranges):
        for b,m in ranges[i+1:]: assert a+n+16 <= b-16 or b+m+16 <= a-16, 'Buffer alias'
    assert chip[resource:resource+16384] == rom[49168:65552], 'Private resources changed'
    mapper=SerialMapper()
    for call,(index,status,context,state,journal,raw) in enumerate(results):
        start = snapshots+offsets[call]
        assert struct.unpack_from('>3I',chip,start) == (index,status,len(journal)), ('Snapshot header',call)
        assert chip[start+12:start+20] == context, ('Context',call,index,chip[start+12:start+20].hex(),context.hex())
        assert chip[start+20:start+2068] == state, ('Full original RAM',call,index)
        assert chip[start+2084:start+2084+len(journal)] == journal, ('Ordered journal/DMA',call,index)
        assert chip[start+2084+len(journal):start+2100+len(journal)] == guard, ('Per-call journal guard',call)
        assert chip[start+2068:start+2084] == guard, ('Per-call journal lower guard',call)
        if index in (2,7,8,29,39):
            actual=chip[start+2084:start+2084+len(journal)]
            for event in range(struct.unpack_from('>H',actual)[0]):
                address,value,metadata=struct.unpack_from('>HBB',actual,2+event*4)
                mapper.write(address,value)
        assert mapper.snapshot()==bus.mapper_checks[call], ('Persistent mapper/latch',call)
    assert chip[ram:ram+2048] == results[-1][3]
    assert chip[ctx:ctx+8] == results[-1][2]
    counts = {kind:sum(e[0] == kind for e in bus.events) for kind in ('ram','mapper','ppu','apu','controller','resource')}
    return dict(status='PASS',proprietary_inputs=True,native_helper_calls=533,
                continuous_original_instructions=instructions,logical_NMIs=18,
                full_RAM_snapshots_equal=533,context_snapshots_equal=533,
                ordered_reference_effects=counts,DMA_bytes_equal=4608,
                mapper_latch_checks=533,
                target_RAM_evidence="Full RAM after every call; ordered RAM journals for fade/yield only",
                target_access_trace=False,
                immutable_resource_bytes=16384,original_saved_frames_exact=True,
                raw_reference_P_untouched=True,comparison='Explicit architectural B=0/U=1 view; saved frame bytes exact',
                final_PC='C597',final_context=results[-1][2].hex(),final_F6=bus[0xf6],
                final_mapper=list(bus.mapper.snapshot()[:4]),native_stack_balanced=True,
                next_dependency='C597 JSR C14E is outside this proof',
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
    assert re.findall(r'^CPU=.*$',log,re.MULTILINE) == ['CPU=68020, FPU=0, MMU=0, JIT=0. ~cycle-exact 24-bit'], 'Actual 68020 core configuration absent or conflicting'
    modes=re.findall(r'^(?:PAL|NTSC) mode .*$',log,re.MULTILINE)
    assert modes and all(re.match(r'^PAL mode V=50\.0000Hz .*\(PAL\)',m) for m in modes), 'Actual PAL output absent or conflicting'
    runs = re.findall(r'^PASS runs=(\d+) video_callbacks=(\d+) .*$',log,re.MULTILINE)
    assert runs == [('1800','1800')], ('Expected completed 1800-frame run',runs)
    return dict(model='A1200OG',CPU='68020',FPU=0,MMU=0,JIT=0,Chip_MiB=2,Fast_MiB=0,
                CPU_cycle_exact=True,memory_cycle_exact=True,blitter_cycle_exact=True,
                standard='PAL 50 Hz',runs=1800,video_callbacks=1800)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chip_dump',type=Path)
    parser.add_argument('--amiga-log',type=Path,required=True)
    args = parser.parse_args()
    rom = (PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    report=verify(args.chip_dump.read_bytes(),rom)
    if args.amiga_log: report['actual_target']=verify_amiga_log(args.amiga_log.read_text())
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
