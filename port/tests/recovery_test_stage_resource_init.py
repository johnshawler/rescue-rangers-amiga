#!/usr/bin/env python3
"""Execute actual private ROM instructions and serial MMC1 bank switching."""
import hashlib,random,struct
from py65.devices.mpu6502 import MPU
from recovery_stage_resource_harness import Native,PORT
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
class Bus:
    def __init__(self,rom):self.prg=rom[16:16+8*16384];self.ram=bytearray(2048);self.events=[];self.bank=0;self.serial=[]
    def __getitem__(self,a):
        if a<2048:return self.ram[a]
        assert 0x8000<=a<65536,('bad read',hex(a))
        bank=self.bank if a<0xc000 else 7
        v=self.prg[bank*16384+(a&0x3fff)]
        if 0x8193<=a<=0x8337:
            assert bank==4;self.events.append((a,v,1))
        return v
    def __setitem__(self,a,v):
        if a<2048:self.ram[a]=v;self.events.append((a,v,0));return
        assert a==0xfff0,('bad write',hex(a))
        self.events.append((a,v,2));assert not v&128
        self.serial.append(v&1)
        if len(self.serial)==5:
            self.bank=sum(b<<i for i,b in enumerate(self.serial))&7;self.serial=[]
def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[16+4*16384+0x193:16+4*16384+0x338]
    bus=Bus(rom);ref=MPU(memory=bus);n=Native();rng=random.Random(0xc6b5);count=events=0
    for idx in range(256):
        for sp in range(256):
            state=bytearray(rng.randbytes(2048));state[0xf6]=0;state[0x31]=idx;state[0xf5]=sp
            ctx=bytes((0xc6,0xb5,*rng.randbytes(3),(idx+sp)&255,sp,0x91))
            bus.ram[:]=state;bus.events=[];bus.bank=(idx+sp)&7;bus.serial=[]
            ref.pc=0xc6b5;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
            for _ in range(100):
                if ref.pc==0xc6bd:break
                ref.step()
            else:raise AssertionError('reference timeout')
            assert bus.bank==4 and not bus.serial
            context=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
            journal=b''.join(struct.pack('>HBB',*e) for e in bus.events)
            expected=(bytes(bus.ram),context,journal+b'\xb6'*(256-len(journal)),len(bus.events),[(a,v) for a,v,k in bus.events if k==0],[(a,v) for a,v,k in bus.events if k==1])
            assert n.run(state,ctx,rng,resource)==expected,(idx,sp,ctx.hex())
            count+=1;events+=len(bus.events)
    print(f'PASS actual-ROM stage init: {count} cases, {events} ordered RAM/resource/mapper events; {len(n.code)} native bytes. Full RAM/context, native stores/resource reads, guards, ABI and global read/write whitelist verified.');n.close()
if __name__=='__main__':main()
