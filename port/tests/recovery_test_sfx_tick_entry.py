"""Standalone ROM-free channel ABI harness; optional cartridge instruction proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=30
SOURCE="recovery_sfx_tick_entry"
PREFLIGHT=True
def make_checker(oracle):
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)/'native.bin'
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src'/(SOURCE+'.s'))],check=True)
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
   assert 1<=value<=24
   at=JOURNAL+2+4*(value-1);kind=mem.r8(at+3)
   events.append(('resource',mem.r16(at),mem.r8(at+2),kind))
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
  mem.w_block(STACK-528,bytes([105])*528)
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
  assert bytes(mem.r_block(STACK-528,16))==bytes([105])*16
  assert cpu.r_sp()==STACK+4 and [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  assert got==(want if want else (s,c,[])),('mismatch',c.hex(),got[1].hex(),None if want is None else want[1].hex(),[(i,a,b) for i,(a,b) in enumerate(zip(got[0],want[0] if want else s)) if a!=b][:20],got[2],None if want is None else want[2])
  if want:
   je=[e for e in want[2] if e[0] in ('resource','mapper','apu')]
   expected=len(je).to_bytes(2,'big')+b''.join(a.to_bytes(2,'big')+bytes((v,k)) for typ,a,v,k in je)
   assert bytes(mem.r_block(JOURNAL,SIZE))==expected+j[len(expected):]
   assert reads==[e[1]-0x8000 for e in want[2] if e[0]=='resource']
  else:
   assert bytes(mem.r_block(JOURNAL,SIZE))==j
   assert reads==[]
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  assert bytes(mem.r_block(CODE,len(code)))==code
  return got
 return check,m.cleanup
def model(state,ctx,r):
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[];pc=int.from_bytes(ctx[:2],'big')
 if pc not in (0x82b0,0x82c0) or x>3:return None
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
 def ret():return ((pop()|(pop()<<8))+1)&65535
 def adc(v):
  nonlocal p,a
  t=a+v+(p&1);p=(p&0x3c)|(t>255)|(0x40 if (~(a^v)&(a^t)&128) else 0);a=nz(t)
 def resource(at):
  v=r[at-0x8000];events.append(('resource',at,v,0));return v
 def result(pc):return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events
 if pc==0x82b0:
  y=nz(s[0x700+x])
  if y:
   push(0x82);push(0xb7);y=nz(y-1);ld(0);store(0xc3,a);ld(y)
   for _ in range(3):
    carry=a>>7;p=(p&254)|carry;a=nz(a<<1)
    t=s[0xc3];p=(p&254)|(t>>7);store(0xc3,nz((t<<1)|carry))
   p&=254;adc(resource(0x8a02));store(0xc5,a);ld(s[0xc3]);adc(resource(0x8a01));store(0xc6,a);assert ret()==0x82b8
  ld(s[0xc0]);p=(p&254)|(a&1);a=nz(a>>1)
  if p&1:return result(0x82dc)
  push(0x82);push(0xbf);return result(0x86b2)
 ld(s[0xd3])
 if not a:return result(ret())
 p=(p&254)|(x>=1);nz(x-1)
 if x==1:
  v=nz(s[0x710+x]-1);store(0x710+x,v)
  if v:return result(ret())
 else:
  ld(s[0xd5])
  if a:return result(ret())
 ld(s[0x704+x]);ld(a&4)
 if a:return result(ret())
 ld(s[0x704+x]);ld(a&0xf8);ld(a|3);store(0x704+x,a)
 return result(ret())

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x82b0);resource=rng.randbytes(16384)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
 def compare(s,c,r):
  if not private or c[3]>3 or int.from_bytes(c[:2],'big') not in (0x82b0,0x82c0):return model(s,c,r)
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(100):
   pc=ref.pc
   if pc in (0x868c,0x8693):
    at=0x8a02 if pc==0x868c else 0x8a01;bus.events.append(('resource',at,bus[at],0))
   ref.step()
   if pc in (0x82cc,0x85a5) or ref.pc in (0x82dc,0x86b2):break
  else:raise AssertionError('ROM timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  want=model(s,c,r);assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=make_checker(compare);cases=rejects=0
 def case(pc,p,sp,ch,inst,control,d3,d5,duration,flags):
  nonlocal cases
  s=bytearray(rng.randbytes(2048));s[0x700+ch]=inst;s[0xc0]=control;s[0xd3]=d3;s[0xd5]=d5;s[0x710+ch]=duration;s[0x704+ch]=flags
  c=pc.to_bytes(2,'big')+bytes((rng.randrange(256),ch,rng.randrange(256),p,sp,0xa7));check(bytes(s),c,resource);cases+=1;return s,c
 for p in range(256):
  for sp in range(256):
   for pc in (0x82b0,0x82c0):case(pc,p,sp,sp&3,(p+sp)&255,p,p&1,sp&1,p,(p+sp)&255)
 for ch in range(4):
  for v in range(256):
   for control in (0,1,254,255):case(0x82b0,v,255-v,ch,v,control,0,0,0,0)
   for d3,d5 in ((0,0),(1,0),(1,1),(255,255)):
    for flags in (0,4,255):case(0x82c0,v,255-v,ch,0,0,d3,d5,v,flags)
 if not private:
  s,c=case(0x82b0,255,255,3,255,0,0,0,0,0)
  for pc in range(65536):
   if pc not in (0x82b0,0x82c0):check(bytes(s),pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
  for sp in range(256):
   for x in range(4,256):
    for pc in (0x82b0,0x82c0):check(bytes(s),pc.to_bytes(2,'big')+bytes((0,x,0,sp,sp,0xa7)),resource);rejects+=1
 cleanup();print('PASS SFX tick entry',cases,'ROM' if private else 'declarative',rejects,'inert rejects',flush=True)
if __name__=='__main__':main()
