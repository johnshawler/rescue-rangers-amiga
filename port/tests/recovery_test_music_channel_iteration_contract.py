#!/usr/bin/env python3
"""ROM-free declarative outer-channel contract and global native access checks."""
from pathlib import Path
import os,random,subprocess,tempfile
import machine68k
PORT=Path(__file__).resolve().parents[1]
BASE,CTX,STOP,STACK=0x10000,0x12000,0x800,0x1f0000
class Native:
 def __init__(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'native.bin'
   subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_music_channel_iteration.s')],check=True)
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
 """Domain transition model; no ROM, opcode decoder or CPU oracle."""
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[]
 def store(addr,value):s[addr]=value;events.append(('ram',addr,value))
 def nz(v):
  nonlocal p
  p=(p&0x7d)|(v&128)|(2 if v==0 else 0)
 def pop():
  nonlocal sp
  sp=(sp+1)&255;return s[0x100+sp]
 def push(v):
  nonlocal sp
  store(0x100+sp,v);sp=(sp-1)&255
 def adc(v,w):
  nonlocal p
  total=v+w+(p&1);r=total&255
  p=(p&0x3c)|(total>255)|(0x40 if (~(v^w)&(v^r)&128) else 0);nz(r);return r
 a=x=pop();nz(a)
 while True:
  old=s[0xcf];store(0xcf,old>>1);p=(p&0x7c)|(old&1)|(2 if old>>1==0 else 0)
  x=(x-1)&255;nz(x)
  if x==255:break
  assert not s[0xcf]&1
  a=s[0xcf]>>1;p&=254;nz(a)
  a=s[0xc0]&2;nz(a)
  if a:continue
  a=x;nz(a);push(a);push(0x80);push(0x84)
  a=x=x|0x28;nz(a)
  a=s[0x728+x]|s[0x72c+x];nz(a)
  if a:
   a=s[0x738+x];assert a==0;nz(a)
   pc=0x839d;break
  sp=(sp+2)&255;a=x=pop();nz(a)
 else:raise AssertionError()
 if x==255:
  a=pop();store(0xcf,a)
  store(0xc0,s[0xc0]>>1);store(0xc0,(s[0xc0]<<1)&255);p&=254
  a=s[0xcc]&127;nz(a)
  if a:
   # Four bit shifts expressed as a 12-bit phase product. Retain all stores.
   y=0;store(0xc1,0)
   for bit in range(4):store(0xc1,((s[0xc1]<<1)|(a>>(7-bit)&1))&255)
   a=(a*16)&255;p&=254
   a=adc(a,s[0xc0]);store(0xc0,a)
   a=adc(s[0xc1],s[0xcd])
   if p&1:store(0xcc,s[0xcc]&128);a=255;nz(a)
   store(0xcd,a)
  lo=pop();hi=pop();pc=((hi<<8|lo)+1)&65535
 return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events

def cases(count=16384):
 rng=random.Random(0x8085)
 for i in range(count):
  s=bytearray(rng.randbytes(2048));sp=i&255;channel=(i//256)%4
  s[0x100+((sp+1)&255)]=channel
  s[0xcf]=rng.randrange(256)&~((1<<(channel+1))-2)
  for x in range(0x28,0x2b):
   s[0x738+x]=0
   if rng.randrange(3)==0:s[0x728+x]=s[0x72c+x]=0
  # Ensure all-inactive paths and phase-tail cases are well represented.
  if i%4==0:
   for x in range(0x28,0x2b):s[0x728+x]=s[0x72c+x]=0
  ctx=b'\x80\x85'+rng.randbytes(3)+bytes(((i&0xc7)|0x20,sp,rng.randrange(256)))
  yield bytes(s),ctx

def main():
 n=Native();count=0
 for state,ctx in cases():
  want=declarative(state,ctx);got=n.run(state,ctx)
  assert got==want,(count,got[1].hex(),want[1].hex(),got[2],want[2]);count+=1
 invalid=0
 state,ctx=next(cases())
 def reject(s,c):
  nonlocal invalid
  assert n.run(bytes(s),bytes(c),-1)==(bytes(s),bytes(c),[]);invalid+=1
 for pc in range(65536):
  if pc!=0x8085:reject(state,pc.to_bytes(2,'big')+ctx[2:])
 for p in range(256):
  if p&0x38!=0x20:reject(state,ctx[:5]+bytes((p,))+ctx[6:])
 for bad in range(4,256):
  s=bytearray(state);s[0x100+((ctx[6]+1)&255)]=bad;reject(s,ctx)
 for channel in range(1,4):
  for bit in range(1,channel+1):
   s=bytearray(state);s[0x101]=channel;s[0xcf]=1<<bit;s[0xc0]=2;reject(s,ctx)
  for duration in range(1,256):
   s=bytearray(state);s[0x101]=channel;s[0xcf]=0;s[0xc0]=0;x=0x28+channel-1;s[0x728+x]=1;s[0x738+x]=duration;reject(s,ctx)
 n.m.cleanup();print(f'PASS {count} ROM-free transitions; {invalid} inert rejections; full RAM/context, ordered writes, ABI, guards, global whitelist.')
if __name__=='__main__':main()
