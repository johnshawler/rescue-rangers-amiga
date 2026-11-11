#!/usr/bin/env python3
"""Private actual-ROM NMI with bounded bus, independent of declarative expected."""
import hashlib,random,struct
from py65.devices.mpu6502 import MPU
from recovery_chr_nmi_harness import Native,PORT
from recovery_test_chr_nmi_contract import cases
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
class Bus:
    def __init__(self,rom):self.fixed=rom[16+7*16384:16+8*16384];self.ram=bytearray(2048);self.events=[];self.dma=[];self.status=0
    def __getitem__(self,a):
        if 0<=a<2048:return self.ram[a]
        if 0xc000<=a<0xc0bf or 0xff1f<=a<0xff53 or a in (0xfffa,0xfffb):return self.fixed[a-0xc000]
        if a==0x2002:self.events.append(('ppu',a,0,0));return self.status
        raise AssertionError(('original read',hex(a)))
    def __setitem__(self,a,v):
        if 0<=a<2048:self.ram[a]=v;self.events.append(('ram',a,v));return
        if a in (0xbfff,0xdfff):self.events.append(('mapper',a,v,self.ram[0xf5]));return
        assert a in (0x2000,0x2001,0x2003,0x2005,0x2006,0x2007,0x4014)
        if a==0x4014:assert v==2;self.dma.append(bytes(self.ram[512:768]))
        self.events.append(('ppu',a,v,1))
def advance(ref):
    ref.nmi()
    for _ in range(512):
        if ref.pc==0xc0bf:return
        assert 0xc000<=ref.pc<0xc0bf or 0xff1f<=ref.pc<0xff53,hex(ref.pc);ref.step()
    raise AssertionError('reference timeout')
def compare(n,b,ref,r,c,rng,entry=0x1000,resume=False):
    b.events=[];b.dma=[];advance(ref)
    got=n.run(r,c,rng,entry=entry,resume=resume)
    out=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7]))
    assert got[0]==b.ram and got[1]==out and got[3]==1 and got[4]==b.events,(c.hex(),got[1].hex(),out.hex())
    hw=[e[1:] for e in b.events if e[0] in ('ppu','mapper')];journal=bytearray(b'\xb6'*494)
    data=struct.pack('>H',len(hw))+b''.join(struct.pack('>HBB',*e) for e in hw);journal[:len(data)]=data
    if b.dma:assert len(b.dma)==1;journal[238:]=b.dma[0]
    assert got[2]==journal
    return got

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    b=Bus(rom);ref=MPU(memory=b,pc=0);n=Native();rng=random.Random(0x90c0);count=0
    for r,c in cases(rng):
        b.ram[:]=r;b.status=rng.randrange(256);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
        compare(n,b,ref,r,c,rng);count+=1
    print(f'PASS {count} actual-ROM NMI cases, full state and ordered RAM/PPU/DMA effects; exact CHR mapper effects; no audio effects');n.close()
if __name__=='__main__':main()
