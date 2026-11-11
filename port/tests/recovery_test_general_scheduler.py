#!/usr/bin/env python3
"""Private actual-ROM oracle with bounded scheduler and bus address whitelists."""
import hashlib,random
from py65.devices.mpu6502 import MPU
from recovery_general_scheduler_harness import Native,PORT
from test_recovery_general_scheduler_contract import cases
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
class Bus:
    def __init__(self,rom):self.fixed=rom[16+7*16384:16+8*16384];self.ram=bytearray(2048);self.events=[];self.pos=[0,0];self.inputs=(0,0)
    def __getitem__(self,a):
        if 0<=a<2048:return self.ram[a]
        if 0xfe8d<=a<0xfed5 or 0xc162<=a<0xc1ba:return self.fixed[a-0xc000]
        if a in (0x4016,0x4017):
            i=a-0x4016;assert self.pos[i]<8;v=(self.inputs[i]>>(7-self.pos[i]))&1;self.pos[i]+=1
            self.events.append(('controller',a,v,0));return v
        raise AssertionError(('original read',hex(a)))
    def __setitem__(self,a,v):
        if 0<=a<2048:self.ram[a]=v;self.events.append(('ram',a,v));return
        assert a==0x4016;self.pos=[0,0];self.events.append(('controller',a,v,1))

def advance(ref):
    for _ in range(1000):
        pc=ref.pc;assert 0xfe8d<=pc<0xfed5 or 0xc162<=pc<0xc1ba,hex(pc)
        ref.step()
        if pc in (0xfea3,0xfec2,0xfed4):return {0xfea3:0,0xfec2:2,0xfed4:1}[pc]
    raise AssertionError('reference bound')

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    b=Bus(rom);ref=MPU(memory=b,pc=0xfe8d);n=Native();rng=random.Random(0x1234);count=0
    for ram,ctx,inputs in cases(rng):
        b.ram[:]=ram;b.events=[];b.inputs=inputs;b.pos=[0,0];ref.pc=int.from_bytes(ctx[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        status=advance(ref);got=n.run(ram,ctx,rng,inputs=inputs)
        out=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
        assert got[0]==b.ram and got[1]==out and got[3]==status and got[4]==b.events,(count,got[1],out)
        count+=1
    print(f'PASS {count} actual-ROM four-slot/fresh/resume/idle/raw-status/controller cases');n.close()
if __name__=='__main__':main()
