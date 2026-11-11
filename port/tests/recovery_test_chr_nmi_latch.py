#!/usr/bin/env python3
"""Independent MMC1 adapters retain every initial partial serial latch."""
import hashlib,random
from recovery_test_chr_nmi_rom import Bus,compare,SHA,MPU
from recovery_chr_nmi_harness import Native,PORT
from recovery_test_active_nmi_runtime_chain import SerialMapper

class LatchedBus(Bus):
    def seed(self,fields,bits):
        self.fields=list(fields);self.count=len(bits);self.shift=sum(b<<i for i,b in enumerate(bits))
    def __setitem__(self,a,v):
        super().__setitem__(a,v)
        if a not in (0xbfff,0xdfff):return
        # Independent counter/integer-latch formulation, not SerialMapper.
        assert not v&128
        self.shift|=(v&1)<<self.count;self.count+=1
        if self.count==5:
            self.fields[(a>>13)&3]=self.shift;self.count=self.shift=0
    def snapshot(self):return (*self.fields,tuple((self.shift>>i)&1 for i in range(self.count)))

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    b=LatchedBus(rom);ref=MPU(memory=b,pc=0);n=Native();rng=random.Random(0x1a1b);cases=0
    for length in range(5):
      for raw in range(1<<length):
       for pair in ((0,0),(0x9f,0),(0,0x9f),(0x9f,0x9f),(1,2),(0x80,0xff),(0xff,0x80),(0xff,0xff)):
        for skip in (False,True):
         r=bytearray(rng.randbytes(2048));r[0xf0]=int(skip);r[0x9a]=r[0x19]=r[0x1c]=r[0x1d]=0;r[0x1a],r[0x1b]=pair
         c=rng.randbytes(8);b.ram[:]=r;b.status=rng.randrange(256)
         fields=tuple(rng.randrange(32) for _ in range(4));bits=tuple((raw>>i)&1 for i in range(length));b.seed(fields,bits)
         mapper=SerialMapper();mapper.control,mapper.chr0,mapper.chr1,mapper.prg=fields;mapper.bits=list(bits)
         ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
         for repeat in range(2):
          got=compare(n,b,ref,r,c,rng,resume=bool(repeat))
          journal=got[2]
          for i in range(int.from_bytes(journal[:2],'big')):
           offset=2+4*i;a=int.from_bytes(journal[offset:offset+2],'big')
           if a in (0xbfff,0xdfff):mapper.write(a,journal[offset+2])
          assert mapper.snapshot()==b.snapshot(),(length,raw,pair,skip,repeat)
          if skip:assert got[0][0x1a:0x1c]==bytes(pair)
          else:assert got[0][0x1a:0x1c]==bytes(2)
          r,c=got[:2]
         cases+=1
    n.close();print(f'PASS {cases} seeded latch cases / {cases*2} continuous NMIs, all31 empty/partial latch bit patterns; independent serial adapters, no latch reset or between-NMI state reload.')
if __name__=='__main__':main()
