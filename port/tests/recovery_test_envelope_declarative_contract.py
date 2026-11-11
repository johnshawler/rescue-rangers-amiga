#!/usr/bin/env python3
"""ROM-free declarative envelope contract, synthetic caller-owned resources."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k
from recovery_music_envelope_declarative import envelope
PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=514
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
def valid(s,c,r):
 if c[:2]!=b'\x86\xb2' or c[3] not in range(0x28,0x2c) or c[5]&0x38!=32:return False
 ptr=s[0xc5]|s[0xc6]<<8
 return s[0x704+c[3]]&7<=4 and 0x8000<=ptr<=0xbff8 and r[0x92e]==0 and all(r[0x6bf+2*i]|r[0x6c0+2*i]<<8==v for i,v in enumerate((0x86c9,0x86de,0x8718,0x86fa,0x890d)))
def oracle(s,c,r):return envelope(s,c,r) if valid(s,c,r) else None

def main():
 check,cleanup=make_checker(oracle);rng=random.Random(0x86b2890d)
 targets=(0x86c9,0x86de,0x8718,0x86fa,0x890d)
 for case in range(16384):
  s=bytearray(rng.randbytes(2048));r=bytearray(rng.randbytes(16384));x=0x28+case%4
  s[0x704+x]=(s[0x704+x]&248)|(case//4)%5
  ptr=(0x8000 if case%3==0 else 0xbff8 if case%3==1 else rng.randrange(0x8000,0xbff9));s[0xc5]=ptr&255;s[0xc6]=ptr>>8
  r[0x92e]=0
  for i,v in enumerate(targets):r[0x6bf+2*i:0x6c1+2*i]=v.to_bytes(2,'little')
  c=bytes((0x86,0xb2,rng.randrange(256),x,rng.randrange(256),(case&0xc7)|32,case&255,(case>>8)&255))
  check(bytes(s),c,bytes(r))
 s=bytes(s);r=bytes(r);invalid=0
 for pc in range(65536):
  if pc!=0x86b2:check(s,pc.to_bytes(2,'big')+c[2:],r);invalid+=1
 for p in range(256):
  if p&0x38!=32:check(s,c[:5]+bytes((p,))+c[6:],r);invalid+=1
 for x in range(256):
  if x not in range(0x28,0x2c):check(s,c[:3]+bytes((x,))+c[4:],r);invalid+=1
 for ptr in range(65536):
  if not 0x8000<=ptr<=0xbff8:
   st=bytearray(s);st[0xc5]=ptr&255;st[0xc6]=ptr>>8;check(bytes(st),c,r);invalid+=1
 for v in range(256):
  if v:
   rt=bytearray(r);rt[0x92e]=v;check(s,c,bytes(rt));invalid+=1
 for at in range(0x6bf,0x6c9):
  for v in range(256):
   if v!=r[at]:
    rt=bytearray(r);rt[at]=v;check(s,c,bytes(rt));invalid+=1
 for stage in (5,6,7):
  st=bytearray(s);st[0x704+c[3]]=(st[0x704+c[3]]&248)|stage;check(bytes(st),c,r);invalid+=1
 cleanup();print(f'PASS 16384 ROM-free envelope transitions and {invalid} inert input/resource guards; full RAM/context/journal/effects/ABI/global bounds.')
if __name__=='__main__':main()
