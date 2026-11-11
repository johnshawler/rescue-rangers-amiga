#!/usr/bin/env python3
"""Independent original-ROM execution of static active envelope, no captured state."""
import hashlib,os,random,subprocess,tempfile
from pathlib import Path
import machine68k
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
PORT=Path(__file__).resolve().parents[1]
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=514
class EnvelopeBus(OriginalBus):
 def __setitem__(self,a,v):
  if isinstance(a,int) and 0x4000<=a<=0x400f:
   self.events.append(('apu',a,v,1));return
  super().__setitem__(a,v)

def run_original(bus,ref,reserved):
 start=len(bus.events);depth=0
 for steps in range(20000):
  pc=ref.pc
  assert (0x86b2<=pc<=0x890d or 0x8006<=pc<=0x8037 or 0x80cf<=pc<=0x80e0),hex(pc)
  if pc in (0x802c,0x8030,0x86cb,0x86e0,0x86ef,0x86f5,0x8703,0x8766,0x87b3,0x8838,0x88f5):
   ptr=0xc1 if pc in (0x802c,0x8030) else 0xc5
   a=((bus[ptr]|bus[ptr+1]<<8)+ref.y)&65535
   bus.events.append(('resource',a,bus[a],0))
  elif pc in (0x86d1,0x86e8,0x870b,0x8846,0x88c8,0x88d0,0x88df,0x88e5):
   a=({0x86d1:0x890e,0x86e8:0x890e,0x870b:0x890e,0x8846:0x892e,0x88c8:0x8934,0x88d0:0x8935,0x88df:0x8934,0x88e5:0x8935}[pc]+ref.y)&65535
   bus.events.append(('resource',a,bus[a],0))
  if bus[pc]==0x20 and pc!=0x86bc:depth+=1
  final=bus[pc]==0x60 and depth==0
  if bus[pc]==0x60:depth-=1
  ref.step()
  if final:break
 else:raise AssertionError('original timeout')
 c=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,(ref.p&0xef)|0x20,ref.sp,reserved))
 return bytes(bus[:2048]),c,list(bus.events[start:])

def make_checker(oracle):
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)/'native.bin'
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_music_active_envelope.s')],check=True)
  code=out.read_bytes()
 m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
 mem.w_block(CODE,code);mem.w16(STOP,0x60fe)
 rng=random.Random(0x86b2);events=[];reads=[];guard=bytes(range(16))
 def trace(mode,width,address,value):
  n=1<<width
  if mode=='R':
   assert any(lo<=address and address+n<=hi for lo,hi in ((CODE,CODE+len(code)),(STOP,STOP+4),(BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+SIZE),(RESOURCE,RESOURCE+16384),(STACK-512,STACK+4))),('read',width,address)
   if RESOURCE<=address<RESOURCE+16384:
    assert width==0;reads.append(address-RESOURCE)
   return
  assert mode=='W'
  assert any(lo<=address and address+n<=hi for lo,hi in ((BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+SIZE),(STACK-512,STACK))),('write',width,address)
  if BASE<=address<BASE+2048:
   assert width==0;events.append(('ram',address-BASE,value))
  if address==JOURNAL and width==1 and value:
   assert 1<=value<=128
   at=JOURNAL+2+4*(value-1);kind=mem.r8(at+3)
   events.append(('apu' if kind else 'resource',mem.r16(at),mem.r8(at+2),kind))
 mem.set_trace_func(trace)
 for mode in ('R','W'):
  for a in (0,0x25000,0x90000,0x1fffff,BASE+2047):
   try:trace(mode,2,a,0)
   except AssertionError:pass
   else:raise AssertionError('unbounded access')
 def check(s,c,r):
  want=oracle(s,c,r)
  mem.set_trace_mode(False);j=rng.randbytes(SIZE)
  for a,b in ((BASE,s),(CTX,c),(JOURNAL,j),(RESOURCE,r)):mem.w_block(a-16,guard+b+guard)
  regs=[rng.getrandbits(32) for _ in range(15)];regs[8:12]=[BASE,CTX,JOURNAL,RESOURCE]
  cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_pc(CODE);events.clear();reads.clear();mem.set_trace_mode(True)
  for _ in range(300):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('native timeout')
  mem.set_trace_mode(False)
  got=(bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(events))
  assert cpu.r_reg(0)==(1 if want is not None else 0xffffffff)
  assert cpu.r_sp()==STACK+4 and [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  assert got==(want if want else (s,c,[])),('mismatch',c.hex(),got[1].hex(),None if want is None else want[1].hex(),[(i,a,b) for i,(a,b) in enumerate(zip(got[0],want[0] if want else s)) if a!=b][:20],got[2],None if want is None else want[2])
  if want:
   je=[e for e in want[2] if e[0] in ('apu','resource')]
   expected=len(je).to_bytes(2,'big')+b''.join(a.to_bytes(2,'big')+bytes((v,k)) for _,a,v,k in je)
   assert bytes(mem.r_block(JOURNAL,SIZE))==expected+bytes(SIZE-len(expected))
   assert reads==[0x92e]+list(range(0x6bf,0x6c9))+[a-0x8000 for kind,a,*_ in je if kind=='resource']
  else:assert bytes(mem.r_block(JOURNAL,SIZE))==j
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  return got
 return check,m.cleanup

def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 resource=rom[49168:65552];bus=EnvelopeBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
 def oracle(s,c,r):
  bus[:2048]=s;bus.events.clear();ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  return run_original(bus,ref,c[7])
 check,cleanup=make_checker(oracle);rng=random.Random(0x890d)
 for case in range(4096):
  s=bytearray(rng.randbytes(2048));x=0x28+case%4
  s[0x704+x]=(s[0x704+x]&0xf8)|(case//4)%5
  ptr=0x8a80+(case%32)*8;s[0xc5]=ptr&255;s[0xc6]=ptr>>8
  c=bytes((0x86,0xb2,rng.randrange(256),x,rng.randrange(256),(case&0xc7)|0x20,case&255,case>>8))
  check(bytes(s),c,resource)
 cleanup();assert hashlib.sha256((PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()).hexdigest()==SHA
 print('PASS 4096 independent original-ROM envelope cases, complete state/effects, ABI, bounded access')
if __name__=='__main__':main()
