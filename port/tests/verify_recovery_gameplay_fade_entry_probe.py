#!/usr/bin/env python3
"""Independent actual-ROM oracle for six continuous on-target compositions."""
from pathlib import Path
import hashlib,json,struct,sys
from recovery_test_gameplay_fade_entry import Ricoh2A03,Bus,SHA,advance,prove_binary_sbc
from recovery_gameplay_fade_target_fixtures import CASES,fixture
PORT=Path(__file__).resolve().parents[1];MARKER=b'CDRGF001'
def references():
    assert prove_binary_sbc()==262144
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    results=[]
    for case in CASES:
        state,ctx=fixture(case);bus=Bus(rom);bus[:2048]=state;bus.events=[]
        ref=Ricoh2A03(memory=bus);ref.pc=0xc6bd;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        stages=[]
        for target in (0xc700,0xc2a5):
            advance(ref,target)
            context=struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7])
            journal=b''.join(struct.pack('>HBB',a,v,0) for a,v in bus.events)
            stages.append((bytes(bus[:2048]),context,journal,len(bus.events)))
            bus.events=[] # Only diagnostic journal resets, never machine state.
        results.append(stages)
    return results

def verify(chip,refs):
    assert len(chip)==2097152 and len(refs)==6
    assert chip.count(MARKER)==1
    header=chip.index(MARKER)
    assert struct.unpack_from('>2I',chip,header+8)==(0,6)
    records=struct.unpack_from('>6I',chip,header+16)
    ranges=[(header,40,'header')];stacks=set();counts=[]
    def region(address,size,kind):
        assert address%2==0 and 16<=address and address+size+16<=len(chip)
        assert chip[address-16:address]==b'\x5a'*16,(kind,'before guard')
        assert chip[address+size:address+size+16]==b'\x5a'*16,(kind,'after guard')
        ranges.append((address-16,size+32,kind))
    for i,(record,stages) in enumerate(zip(records,refs)):
        assert len(stages)==2
        region(record,284,'record')
        ram,ctx,j1,j2,midram,midctx,stack,end,before_sp,mid_sp,after_sp=struct.unpack_from('>11I',chip,record)
        assert end==stack+4096 and before_sp==mid_sp==after_sp==end
        stacks.add((stack,end))
        for address,size,kind in ((ram,2048,'ram'),(ctx,8,'context'),(j1,256,'journal'),(j2,512,'journal'),(midram,2048,'ram'),(midctx,8,'context')):region(address,size,kind)
        for n,(r,c,j,jsize,ref) in enumerate(((midram,midctx,j1,256,stages[0]),(ram,ctx,j2,512,stages[1]))):
            expected_regs=[0x10203040,*[0x11223300+k for k in range(1,8)],ram,ctx,j,
                           *[0x22334400+k for k in range(3,6)],record]
            before=list(struct.unpack_from('>15I',chip,record+44+120*n))
            after=list(struct.unpack_from('>15I',chip,record+104+120*n))
            assert before==expected_regs,(i,n,'before registers')
            assert after==[ref[3],*before[1:]],(i,n,'after registers')
            assert chip[r:r+2048]==ref[0],(i,n,'RAM')
            assert chip[c:c+8]==ref[1],(i,n,'context')
            assert len(ref[2])==4*ref[3] and len(ref[2])<=jsize
            assert chip[j:j+jsize]==ref[2]+b'\xb6'*(jsize-len(ref[2])),(i,n,'journal/tail')
        counts.append([stage[3] for stage in stages])
    assert len(stacks)==1
    stack,end=next(iter(stacks));region(stack,4096,'native stack')
    assert chip[stack:end-96]==b'\xee'*(4096-96)
    for i,(a,n,_) in enumerate(ranges):
        for b,m,_ in ranges[i+1:]:assert a+n<=b or b+m<=a,'overlap'
    return dict(cases=6,record_counts=counts,ordered_writes=sum(sum(c) for c in counts),ranges=ranges,records=records,header=header)
if __name__=='__main__':
    result=verify(Path(sys.argv[1]).read_bytes(),references())
    print(json.dumps({k:v for k,v in result.items() if k not in ('ranges','records','header')},indent=2))
