#!/usr/bin/env python3
"""Independent hash-pinned original execution and literal MMC1 event adapter."""
import hashlib,random
from py65.devices.mpu6502 import MPU
from recovery_active_return_harness import Native,PORT
from test_recovery_active_return_contract import cases,expected
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
class Mapper:
    def __init__(self,control,prg,latch):
        assert control&12==12
        self.control=control;self.prg=prg;self.latch=list(latch)
    def write(self,value):
        if value&128:self.latch=[];self.control|=12;return
        self.latch.append(value&1)
        if len(self.latch)==5:
            self.prg=sum(v<<i for i,v in enumerate(self.latch));self.latch=[]
    def signature(self):return self.control,self.prg,tuple(self.latch),self.prg&7,(self.prg&16)==0
class Bus:
    def __init__(self,rom):self.rom=rom
    def __getitem__(self,a):
        if a==0xf1 or 0x100<=a<0x200:return self.ram[a]
        assert 0xc0f9<=a<=0xc114,('original read',hex(a))
        assert self.mapper.control&12==12,'fixed-bank obligation violated'
        return self.rom[16+7*16384+a-0xc000]
    def __setitem__(self,a,v):
        assert a==0xfff0,('original write',hex(a))
        self.events.append(('mapper',a,v,self.ram[0xf5]));self.mapper.write(v)

def architectural_rti_status_view(raw):
    """Comparison ONLY; never assign this normalized value to reference P."""
    return raw[:5]+bytes(((raw[5]&0xef)|0x20,))+raw[6:]

def main():
    path=PORT.parent/'input/rescue-rangers-europe.nes'
    rom=path.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    n=Native();b=Bus(rom);rng=random.Random(0xc114);ref=MPU(memory=b,pc=0xc0f9);count=0
    for ram,ctx in cases(rng):
        before=bytes(ram);b.ram=bytearray(ram);b.events=[]
        control=12|(count&19);prg=(count>>3)&31
        latch=[(count>>i)&1 for i in range(count%5)]
        b.mapper=Mapper(control,prg,latch);adapter=Mapper(control,prg,latch)
        ref.pc=0xc0f9;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        saved=bytes(ram[0x100+((ctx[6]+i)&255)] for i in range(1,8))
        for step in range(32):
            pc=ref.pc;assert 0xc0f9<=pc<=0xc114
            ref.step()
            if pc==0xc114:break
        else:raise AssertionError('reference bound')
        raw=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
        # py65 virtual B/U OR operation is asserted separately against original
        # saved hardware byte; raw oracle is neither replaced nor patched.
        assert ref.p==saved[4]|0x30
        assert bytes(b.ram)==before
        assert bytes(b.ram[0x100+((ctx[6]+i)&255)] for i in range(1,8))==saved
        want=(before,architectural_rti_status_view(raw),expected(ram,ctx)[2],1,b.events)
        got=n.run(ram,ctx,rng)
        assert got==want==expected(ram,ctx),(count,got[1],want[1])
        for _,address,value,busy in got[4]:
            assert address==0xfff0 and busy==ram[0xf5];adapter.write(value)
        assert adapter.signature()==b.mapper.signature()
        if not latch and ram[0xf1]<128:
            assert b.mapper.prg==ram[0xf1]&31 and not b.mapper.latch
        if ram[0xf1]&128:
            assert b.mapper.prg==prg and len(b.mapper.latch)==4
        count+=1
    assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
    print(f'PASS {count} independent actual-ROM returns; all saved flags, PCs, stacks, bank bytes and F6 values; MMC1 live mode3/bank/partial-latch/reset semantics; immutable cartridge/RAM/frame; raw oracle unchanged')
    n.close()
if __name__=='__main__':main()
