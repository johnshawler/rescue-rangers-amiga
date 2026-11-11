#!/usr/bin/env python3
"""Private target oracle: actual ROM, serial mapper, continuous original state."""
from pathlib import Path
import hashlib,json,struct,sys
from recovery_test_gameplay_fade_entry import Ricoh2A03,advance,prove_binary_sbc
from recovery_test_stage_resource_init import Bus,SHA
from recovery_stage_resource_target_fixtures import CASES,fixture
PORT=Path(__file__).resolve().parents[1];MARKER=b'CDRSR001'
def references():
    assert prove_binary_sbc()==262144
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[16+4*16384+0x193:16+4*16384+0x338];results=[]
    for i,case in enumerate(CASES):
        state,ctx=fixture(case);bus=Bus(rom);bus.ram[:]=state;bus.bank=i;bus.serial=[]
        ref=Ricoh2A03(memory=bus);ref.pc=0xc6b5;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7];stages=[]
        for target in (0xc6bd,0xc700,0xc2a5):
            advance(ref,target);assert bus.bank==4 and not bus.serial
            context=struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7])
            journal=b''.join(struct.pack('>HBB',*e) for e in bus.events)
            stages.append((bytes(bus.ram),context,journal,len(bus.events)));bus.events=[]
        results.append(stages)
    return results,resource

def verify(chip,refs):
    refs,resource=refs
    assert len(chip)==2097152 and len(refs)==6 and chip.count(MARKER)==1
    header=chip.index(MARKER);assert struct.unpack_from('>2I',chip,header+8)==(0,6)
    records=struct.unpack_from('>6I',chip,header+16);ranges=[(header,40,'header')];stacks=set();resources=set();counts=[]
    def region(address,size,kind):
        assert address%2==0 and 16<=address and address+size+16<=len(chip)
        assert chip[address-16:address]==b'\x5a'*16,(kind,'before guard')
        assert chip[address+size:address+size+16]==b'\x5a'*16,(kind,'after guard')
        ranges.append((address-16,size+32,kind))
    for i,(record,stages) in enumerate(zip(records,refs)):
        assert len(stages)==3;region(record,424,'record')
        ram,ctx,j0,j1,j2,r0,c0,r1,c1,res,stack,end,before_sp,sp0,sp1,sp2=struct.unpack_from('>16I',chip,record)
        assert end==stack+4096 and before_sp==sp0==sp1==sp2==end
        stacks.add((stack,end));resources.add(res)
        for a,z,k in ((ram,2048,'ram'),(ctx,8,'context'),(j0,256,'journal'),(j1,256,'journal'),(j2,512,'journal'),(r0,2048,'ram'),(c0,8,'context'),(r1,2048,'ram'),(c1,8,'context')):region(a,z,k)
        for n,(r,c,j,jsize,ref) in enumerate(((r0,c0,j0,256,stages[0]),(r1,c1,j1,256,stages[1]),(ram,ctx,j2,512,stages[2]))):
            expected_regs=[0x10203040,*[0x11223300+k for k in range(1,8)],ram,ctx,j,res,0x22334404,0x22334405,record]
            before=list(struct.unpack_from('>15I',chip,record+64+120*n));after=list(struct.unpack_from('>15I',chip,record+124+120*n))
            assert before==expected_regs,(i,n,'before registers');assert after==[ref[3],*before[1:]],(i,n,'after registers')
            assert chip[r:r+2048]==ref[0],(i,n,'RAM');assert chip[c:c+8]==ref[1],(i,n,'context')
            assert len(ref[2])==4*ref[3] and len(ref[2])<=jsize
            assert chip[j:j+jsize]==ref[2]+b'\xb6'*(jsize-len(ref[2])),(i,n,'journal/tail')
        counts.append([stage[3] for stage in stages])
    assert len(stacks)==len(resources)==1
    res=next(iter(resources));region(res,421,'resource');assert chip[res:res+421]==resource
    stack,end=next(iter(stacks));region(stack,4096,'native stack');assert chip[stack:end-96]==b'\xee'*(4096-96)
    for i,(a,n,_) in enumerate(ranges):
        for b,m,_ in ranges[i+1:]:assert a+n<=b or b+m<=a,'overlap'
    return dict(cases=6,record_counts=counts,ordered_effects=sum(sum(c) for c in counts),ranges=ranges,records=records,header=header)
if __name__=='__main__':
    result=verify(Path(sys.argv[1]).read_bytes(),references());print(json.dumps({k:v for k,v in result.items() if k not in ('ranges','records','header')},indent=2))
