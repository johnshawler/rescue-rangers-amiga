#!/usr/bin/env python3
"""Independent actual-ROM oracle for six synthetic on-target C6BD calls."""
from pathlib import Path
import hashlib,json,struct,sys
from py65.devices.mpu6502 import MPU
from recovery_test_gameplay_player_init import Bus,SHA
from test_recovery_gameplay_player_init_contract import CASES,fixture
PORT=Path(__file__).resolve().parents[1];MARKER=b'CDRGP001'
def references():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    results=[]
    for case in CASES:
        state,ctx=fixture(case);bus=Bus(rom);bus[:2048]=state;bus.events=[]
        ref=MPU(memory=bus);ref.pc=0xc6bd;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        for steps in range(1000):
            if ref.pc==0xc700:break
            ref.step()
        else:raise AssertionError('reference timeout')
        context=struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7])
        journal=b''.join(bus.events)
        results.append((bytes(bus[:2048]),context,journal,len(bus.events),steps))
    return results

def verify(chip,refs):
    assert len(chip)==2097152
    assert chip.count(MARKER)==1
    header=chip.index(MARKER)
    assert struct.unpack_from('>2I',chip,header+8)==(0,6)
    records=struct.unpack_from('>6I',chip,header+16)
    ranges=[(header,40,'header')];stacks=set();counts=[]
    def region(address,size,kind):
        assert 16<=address and address+size+16<=len(chip)
        assert chip[address-16:address]==b'\x5a'*16,(kind,'before guard')
        assert chip[address+size:address+size+16]==b'\x5a'*16,(kind,'after guard')
        ranges.append((address-16,size+32,kind))
    for i,(record,ref) in enumerate(zip(records,refs)):
        region(record,148,'record')
        ram,ctx,journal,stack,end,sp_before,sp_after=struct.unpack_from('>7I',chip,record)
        assert end==stack+4096 and sp_before==sp_after==end
        stacks.add((stack,end))
        for address,size,kind in ((ram,2048,'ram'),(ctx,8,'context'),(journal,256,'journal')):region(address,size,kind)
        expected_regs=[0x10203040,*[0x11223300+r for r in range(1,8)],ram,ctx,journal,
                       *[0x22334400+r for r in range(3,6)],record]
        before=list(struct.unpack_from('>15I',chip,record+28));after=list(struct.unpack_from('>15I',chip,record+88))
        assert before==expected_regs,(i,'before registers')
        assert after==[ref[3],*before[1:]],(i,'after registers')
        assert chip[ram:ram+2048]==ref[0],(i,'RAM')
        assert chip[ctx:ctx+8]==ref[1],(i,'context')
        assert chip[journal:journal+256]==ref[2]+b'\xb6'*(256-len(ref[2])),(i,'journal/tail')
        counts.append(ref[3])
    assert len(stacks)==1
    stack,end=next(iter(stacks));region(stack,4096,'native stack')
    # Only final call stack scratch can change; lower 4,000 bytes stay untouched.
    assert chip[stack:end-96]==b'\xee'*(4096-96)
    for i,(a,n,_) in enumerate(ranges):
        for b,m,_ in ranges[i+1:]:assert a+n<=b or b+m<=a,'overlap'
    return dict(cases=6,record_counts=counts,ordered_writes=sum(counts),ranges=ranges,records=records,header=header)
if __name__=='__main__':
    result=verify(Path(sys.argv[1]).read_bytes(),references())
    print(json.dumps({k:v for k,v in result.items() if k not in ('ranges','records','header')},indent=2))
