#!/usr/bin/env python3
"""Mutation tests for actual private runtime dump; positive baseline always runs first."""
import argparse
import json
import struct
from pathlib import Path
from verify_recovery_resident_fade_probe import MARKER,PORT,layout,oracle,verify,verify_amiga_log


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chip_dump',type=Path)
    parser.add_argument('--amiga-log',type=Path)
    parser.add_argument('--old-dump',type=Path,action='append',default=[])
    args=parser.parse_args()
    original=args.chip_dump.read_bytes()
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    baseline=verify(original,rom)
    assert baseline['status']=='PASS'
    results,_,_=oracle(rom)
    offsets,total=layout(results)
    offset=original.index(MARKER)
    status,calls,ram,ctx,snapshots,resource,stack,stack_end,sp=struct.unpack_from('>9I',original,offset+8)
    tests=[]
    def patch(label,address,data): tests.append((label,address,data))
    def u32(label,address,value): patch(label,address,struct.pack('>I',value))
    for i in range(8): patch('marker byte '+str(i),offset+i,b'!')
    u32('ABI failure status',offset+8,1)
    for value in (0,532,534,0xffffffff): u32('call count '+str(value),offset+12,value)
    pointer_fields=[(offset+16,ram),(offset+20,ctx),(offset+24,snapshots),(offset+28,resource),(offset+32,stack)]
    for field,old in pointer_fields:
        for value in (0,1,15,len(original)-1,len(original),0xffffffff,offset,old+1):
            u32('pointer bounds/alignment/report '+str(field)+' '+str(value),field,value)
        for other_field,other in pointer_fields:
            if field != other_field:u32('pointer alias '+str(field)+' '+str(other_field),field,other)
    # Deliberate interior/partial/guard overlap, not merely identical starts.
    sizes={ram:2048,ctx:8,snapshots:total,resource:16384,stack:4096}
    for field,old in pointer_fields:
        size=sizes[old]
        for label,value in (('exact lower bound',16),('exact upper guarded end',len(original)-size-16),
                            ('two bytes past upper guarded end',len(original)-size-14),
                            ('report interior',offset+2),('report guard overlap',offset+44)):
            u32(label+' '+str(field),field,value)
        for other_field,other in pointer_fields:
            if field == other_field:continue
            for label,value in (('interior overlap',other+2),('end overlap',other+sizes[other]-2),
                                ('guard overlap',other+sizes[other]+14)):
                u32(label+' '+str(field)+' '+str(other_field),field,value)
    u32('stack range',offset+36,stack_end+4)
    u32('stack balance',offset+40,sp-4)
    for address,size in ((ram,2048),(ctx,8),(snapshots,total),(resource,16384),(stack,4096)):
        for point in (address-16,address-1,address+size,address+size+15):patch('guard '+str(point),point,b'\0')
    for call in range(533):
        point=snapshots+offsets[call]
        index,expected_status,size=struct.unpack_from('>3I',original,point)
        u32('helper index '+str(call),point,index^1)
        u32('helper status '+str(call),point+4,expected_status^1)
        u32('journal size '+str(call),point+8,size+1)
        for relative,label in ((12,'context'),(20,'RAM'),(20+0xf6,'F6'),(2100+size-1,'journal guard'),(2068,'journal lower guard')):
            patch(label+' '+str(call),point+relative,bytes((original[point+relative]^1,)))
        if size:
            for relative in (2084,2084+size-1):patch('journal '+str(call)+' '+str(relative),point+relative,bytes((original[point+relative]^1,)))
    for point in (ram,ram+0xf6,ram+0x1bd,ctx,ctx+5,resource,resource+16383):patch('final state/resource '+str(point),point,bytes((original[point]^1,)))
    for label,address,data in tests:
        damaged=bytearray(original);damaged[address:address+len(data)]=data
        try:verify(bytes(damaged),rom)
        except (AssertionError,struct.error):pass
        else:raise AssertionError(('Corruption accepted',label))
    for old in args.old_dump:
        old_bytes=old.read_bytes()
        assert MARKER not in old_bytes
        try:verify(old_bytes,rom)
        except (AssertionError,struct.error):pass
        else:raise AssertionError(('Cross-mode accepted',str(old)))
    # Shape, duplicate report and cartridge identity fail independently.
    extra=[original[:-1],original+b'\0']
    duplicate=bytearray(original);duplicate[-8:]=MARKER;extra.append(bytes(duplicate))
    for damaged in extra:
        try:verify(damaged,rom)
        except (AssertionError,struct.error):pass
        else:raise AssertionError('Malformed dump accepted')
    try:verify(original,rom[:-1])
    except AssertionError:pass
    else:raise AssertionError('Wrong cartridge accepted')
    assert verify(original,rom)==baseline, 'Baseline changed after corruption tests'
    log_cases=0
    if args.amiga_log:
        log=args.amiga_log.read_text()
        verify_amiga_log(log)
        mutations=[('Model: "A1200OG".','Model: "A1200".'),
                   ('cpu_model=68020','cpu_model=68030'),('fpu_model=0','fpu_model=68881'),
                   ('mmu_model=0','mmu_model=68030'),('chipmem_size=4','chipmem_size=2'),
                   ('bogomem_size=0','bogomem_size=1'),('fastmem_size=0','fastmem_size=4'),
                   ('ntsc=false','ntsc=true'),('cpu_cycle_exact=true','cpu_cycle_exact=false'),
                   ('cpu_memory_cycle_exact=true','cpu_memory_cycle_exact=false'),
                   ('blitter_cycle_exact=true','blitter_cycle_exact=false'),
                   ('CPU=68020, FPU=0, MMU=0, JIT=0.','CPU=68030, FPU=0, MMU=0, JIT=0.'),
                   ('PAL mode V=50.0000Hz','NTSC mode V=59.9400Hz'),
                   ('PASS runs=1800','PASS runs=1799'),('video_callbacks=1800','video_callbacks=1799')]
        for old,new in mutations:
            assert old in log
            for damaged in (log.replace(old,new),log.replace(old,'')):
                try:verify_amiga_log(damaged)
                except AssertionError:log_cases+=1
                else:raise AssertionError(('Invalid target log accepted',old))
        for extra_line in ('cpu_model=68030','CPU=68030, FPU=0, MMU=0, JIT=0. ~cycle-exact 24-bit',
                      'NTSC mode V=59.9400Hz (NTSC)','fastmem_size=4','Model: "A1200OG".'):
            try:verify_amiga_log(log+'\n'+extra_line+'\n')
            except AssertionError:log_cases+=1
            else:raise AssertionError(('Conflicting target log accepted',extra_line))
    print(json.dumps(dict(status='PASS',target_log_negative_cases=log_cases,positive_baselines=2,negative_cases=len(tests)+len(extra)+1,
                          cross_mode_cases=len(args.old_dump),proprietary_inputs=True),indent=2))

if __name__=='__main__':main()
