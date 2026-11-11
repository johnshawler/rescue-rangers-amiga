#!/usr/bin/env python3
"""ROM-free declarative active tick control contract and global native access checks."""
from pathlib import Path
import os,random,subprocess,tempfile
import machine68k
PORT=Path(__file__).resolve().parents[1]
BASE,CTX,STOP,STACK=0x10000,0x12000,0x800,0x1f0000
class Native:
 def __init__(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'native.bin'
   subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_music_active_control.s')],check=True)
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
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[];pc=int.from_bytes(ctx[:2],'big')
 if pc not in (0xc0f6,0x8085) or p&0x38!=0x20 or s[0xcf]|s[0xd0]|s[0xd1]:return None
 if pc==0x8085 and s[0x100+((sp+1)&255)]>3:return None
 continuation=pc==0x8085 and bytes(s[0x100+((sp+i)&255)] for i in range(2,7))==bytes.fromhex("005180f8c0")
 def nz(v):
  nonlocal p
  v&=255;p=(p&0x7d)|(v&128)|(2 if v==0 else 0);return v
 def ld(v):
  nonlocal a
  a=nz(v)
 def store(at,v):s[at]=v&255;events.append(('ram',at,v&255))
 def push(v):
  nonlocal sp
  store(0x100+sp,v);sp=(sp-1)&255
 def pop():
  nonlocal sp
  sp=(sp+1)&255;return s[0x100+sp]
 def jsr(ret):push(ret>>8);push(ret&255)
 def adc(v):
  nonlocal p,a
  t=a+v+(p&1);p=(p&0x3c)|(t>255)|(0x40 if (~(a^v)&(a^t)&128) else 0);a=nz(t)
 def shift(v,left=False,rotate=False):
  nonlocal p
  old=p&1;p=(p&254)|((v>>7) if left else (v&1));return nz(((v<<1)|(old if rotate else 0)) if left else v>>1)
 def result(pc):return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events
 if pc==0xc0f6:
  jsr(0xc0f8);ld(s[0xc0]);ld(a&0xf3);store(0xc3,a);p&=254;ld(4);adc(s[0xc0]);ld(a&12);y=nz(a);ld(a|s[0xc3]);store(0xc0,a);ld(y)
  if a==0:jsr(0x8051);continuation=True
  pc=0x8052
 for rounds in range(12):
  if pc==0x8052:
   ld(s[0xc0]);a=shift(a)
   if p&1:pc=0x80ba
   else:
    ld(s[0xd0]);ld(a|s[0xd1]);assert a==0
    p&=254;ld(s[0xca]);adc(s[0xc8]);store(0xc8,a);ld(s[0xc9]);adc(0);store(0xc7,a);ld(s[0xcf]);push(a);x=nz(3);pc=0x8072
  if pc==0x8085:
   ld(pop());x=nz(a);pc=0x8087
  if pc==0x8087:
   store(0xcf,shift(s[0xcf]));x=nz(x-1);pc=0x808c if x&128 else 0x8072
  if pc==0x8072:
   ld(s[0xcf]);a=shift(a);assert not p&1
   ld(s[0xc0]);ld(a&2)
   if a:pc=0x8087;continue
   ld(x);push(a);jsr(0x8084);ld(x);ld(a|0x28);x=nz(a);ld(s[0x728+x]);ld(a|s[0x72c+x])
   if a:
    ld(s[0x738+x]);return result(0x839d if a==0 else 0x8374)
   ret=(pop()|(pop()<<8))+1;assert ret==0x8085;pc=ret;continue
  if pc==0x808c:
   ld(pop());store(0xcf,a);store(0xc0,shift(s[0xc0]));store(0xc0,shift(s[0xc0],True));ld(s[0xcc]);ld(a&127)
   if a:
    y=nz(0);store(0xc1,y);y=nz(4)
    for _ in range(4):a=shift(a,True);store(0xc1,shift(s[0xc1],True,True));y=nz(y-1)
    p&=254;adc(s[0xc0]);store(0xc0,a);ld(s[0xc1]);adc(s[0xcd])
    if p&1:ld(s[0xcc]);ld(a&128);store(0xcc,a);ld(255)
    store(0xcd,a)
   pc=0x80ba
  if pc==0x80ba:
   ret=((pop()|(pop()<<8))+1)&65535
   if ret==0x8052 and continuation:continuation=False;pc=ret;continue
   return result(ret)
 raise AssertionError('control bounds')

def return_regressions():
 # Wrapped original stack, caller return collisions, restored CF and chained returns.
 for sp in range(256):
  for cf in (0,1,128,255):
   for target in (0x8052,0x8085,0xc0f9):
    for outer in (0xc0f9,0x8052,0x8085,0):
     s=bytearray(2048);frame=(0,cf,(target-1)&255,((target-1)>>8)&255,(outer-1)&255,((outer-1)>>8)&255,255,1,0x51,0x80)
     for i,v in enumerate(frame,1):s[0x100+((sp+i)&255)]=v
     yield bytes(s),bytes.fromhex('808500000020')+bytes((sp,0))
  for offset in range(2,7):
   for mask in (1,128,255):
    s=bytearray(2048)
    for i,v in enumerate(bytes.fromhex('00005180f8c0'),1):s[0x100+((sp+i)&255)]=v
    s[0x100+((sp+offset)&255)]^=mask
    yield bytes(s),bytes.fromhex('808500000020')+bytes((sp,0))

def main():
 n=Native();rng=random.Random(0x803a)
 for case in range(16384):
  s=bytearray(rng.randbytes(2048));s[0xcf]=s[0xd0]=s[0xd1]=0;sp=case&255
  pc=0xc0f6 if case&1 else 0x8085
  s[0x100+((sp+1)&255)]=(case>>1)%4
  if case%5==0:
   s[0x750:0x758]=bytes(8)
  c=pc.to_bytes(2,'big')+bytes((rng.randrange(256),rng.randrange(256),rng.randrange(256),(case&0xc7)|32,sp,case>>8))
  want=declarative(bytes(s),c);got=n.run(bytes(s),c)
  assert got==want,('control',case,got[1],want[1],got[2],want[2])
 regressions=0
 for ss,cc in return_regressions():
  assert n.run(ss,cc)==declarative(ss,cc);regressions+=1
 ss=bytearray(2048);ss[0x100:0x104]=bytes.fromhex('00015180');cc=bytes.fromhex('808500000020ff00')
 result=n.run(bytes(ss),cc);assert result==declarative(bytes(ss),cc)
 assert result[1][:2]==bytes.fromhex('8052') and result[0][0xcf]==1
 s=bytes(2048);c=bytes.fromhex('c0f600000020ff00');guards=0
 for pc in range(65536):
  if pc in (0xc0f6,0x8085):continue
  cc=pc.to_bytes(2,'big')+c[2:];assert n.run(s,cc,-1)==(s,cc,[]);guards+=1
 for value in range(256):
  cc=bytearray(c);cc[5]=value
  if value&0x38!=32:assert n.run(s,bytes(cc),-1)==(s,bytes(cc),[]);guards+=1
 for field in (0xcf,0xd0,0xd1):
  for value in range(1,256):
   ss=bytearray(s);ss[field]=value;ss=bytes(ss);assert n.run(ss,c,-1)==(ss,c,[]);guards+=1
 n.m.cleanup();print(f'PASS 16384 ROM-free control cases plus{guards} inert guards and{regressions} bounded-return regressions')
if __name__=='__main__':main()
