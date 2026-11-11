#!/usr/bin/env python3
"""ROM-free declarative duration progression contract and global native access checks."""
from pathlib import Path
import os,random,subprocess,tempfile
import machine68k
PORT=Path(__file__).resolve().parents[1]
BASE,CTX,STOP,STACK=0x10000,0x12000,0x800,0x1f0000
class Native:
 def __init__(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'native.bin'
   subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_music_duration_progress.s')],check=True)
   self.code=out.read_bytes()
  self.m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);self.mem=self.m.mem;self.cpu=self.m.cpu;self.rng=random.Random(18)
  self.mem.w_block(0x1000,self.code);self.mem.w16(STOP,0x60fe);self.events=[]
  def trace(mode,width,addr,value):
   size=1<<width
   ranges=((0x1000,0x1000+len(self.code)+8),(STOP,STOP+4),(BASE,BASE+2048),(CTX,CTX+8),(STACK-256,STACK+4)) if mode=='R' else ((BASE,BASE+2048),(CTX,CTX+8),(STACK-256,STACK))
   assert mode in ('R','W') and any(lo<=addr and addr+size<=hi for lo,hi in ranges),(mode,width,hex(addr))
   if mode=='W' and BASE<=addr<BASE+2048:
    assert width==0;self.events.append(('ram',addr-BASE,value))
  self.mem.set_trace_func(trace)
  for mode in ('R','W'):
   for addr in (0x1ffff,0x20000,0x90000):
    try:trace(mode,0,addr,0)
    except AssertionError:pass
    else:raise AssertionError('whitelist escaped')
 def run(self,state,ctx,status=1):
  mem,cpu=self.mem,self.cpu;mem.set_trace_mode(False);guard=bytes(range(16))
  for addr,data in ((BASE,state),(CTX,ctx)):mem.w_block(addr-16,guard+data+guard)
  regs=[self.rng.getrandbits(32) for _ in range(15)];regs[8:10]=[BASE,CTX]
  cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,r in enumerate(regs):cpu.w_reg(i,r)
  cpu.w_pc(0x1000);self.events.clear();mem.set_trace_mode(True)
  for _ in range(100):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('timeout')
  mem.set_trace_mode(False)
  assert cpu.r_reg(0)==status&0xffffffff
  assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  assert cpu.r_sp()==STACK+4
  for addr,size in ((BASE,2048),(CTX,8)):
   assert bytes(mem.r_block(addr-16,16))==guard and bytes(mem.r_block(addr+size,16))==guard
  return bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(self.events)

def declarative(state,ctx):
 """Duration domain transition, no ROM data or opcode interpreter."""
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[]
 def store(addr,v):s[addr]=v;events.append(('ram',addr,v))
 def subtract(v):
  nonlocal p
  delta=v-s[0xc7];r=delta&255
  p=(p&0x3c)|(delta>=0)|(2 if r==0 else 0)|(r&128)|(64 if (v^s[0xc7])&(v^r)&128 else 0)
  return r
 a=subtract(s[0x740+x]);store(0x740+x,a)
 if not a or not p&1:
  store(0x100+sp,0x83);sp=(sp-1)&255
  store(0x100+sp,0x8e);sp=(sp-1)&255
  a=(s[0x704+x]&248)|3;store(0x704+x,a);sp=(sp+2)&255
 a=subtract(s[0x738+x]);store(0x738+x,a)
 pc=0x839d
 if a and p&1:
  sp=(sp+1)&255;lo=s[0x100+sp]
  sp=(sp+1)&255;hi=s[0x100+sp];pc=((hi<<8|lo)+1)&65535
 return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events

def cases(count=65536):
 rng=random.Random(0x837f)
 for i in range(count):
  s=bytearray(rng.randbytes(2048));x=0x28+(i//256)%4
  s[0x700+x]=0;s[0xc7]=i&255;s[0x738+x]=(i>>8)&255
  s[0x740+x]=(i>>8)&255 if i%2 else rng.randrange(256)
  ctx=b'\x83\x7f'+bytes((rng.randrange(256),x,rng.randrange(256),(i&0xc7)|32,(i//257)&255,rng.randrange(256)))
  yield bytes(s),ctx

def main():
 n=Native();count=0
 for state,ctx in cases():
  want=declarative(state,ctx);got=n.run(state,ctx)
  assert got==want,(count,got[1].hex(),want[1].hex(),got[2],want[2]);count+=1
 invalid=0;state,ctx=next(cases())
 def reject(s,c):
  nonlocal invalid
  assert n.run(bytes(s),bytes(c),-1)==(bytes(s),bytes(c),[]);invalid+=1
 for pc in range(65536):
  if pc!=0x837f:reject(state,pc.to_bytes(2,'big')+ctx[2:])
 for p in range(256):
  if p&0x38!=0x20:reject(state,ctx[:5]+bytes((p,))+ctx[6:])
 for x in range(256):
  if x not in range(0x28,0x2c):reject(state,ctx[:3]+bytes((x,))+ctx[4:])
 n.m.cleanup();print(f'PASS {count} ROM-free transitions; {invalid} inert rejections; full RAM/context, ordered writes, ABI, guards, global whitelist.')
if __name__=='__main__':main()
