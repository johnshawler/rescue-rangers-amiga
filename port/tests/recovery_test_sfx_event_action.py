"""Standalone ROM-free channel ABI harness; optional cartridge instruction proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=14
SOURCE="recovery_sfx_event_action"
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
   assert 1<=value<=(SIZE-2)//4
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
   assert reads==validation_reads(s,c,r)+[e[1]-0x8000 for e in want[2] if e[0]=='resource']
  else:
   assert bytes(mem.r_block(JOURNAL,SIZE))==j
   assert reads==validation_reads(s,c,r)
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  assert bytes(mem.r_block(CODE,len(code)))==code
  return got
 return check,m.cleanup
def validation_reads(s,c,r):return []
def valid(s,c):
 return c[:2] in (bytes.fromhex('830b'),bytes.fromhex('831b')) and c[3]<=3 and (c[:2]==bytes.fromhex('830b') or c[4]&128 or 0x8000<=((s[0xc5]+256*s[0xc6]+4)&65535)<=0xbfff)
def model(state,ctx,r):
 if not valid(state,ctx):return None
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[]
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
 def ret():return ((pop()|(pop()<<8))+1)&65535
 def adc(v):
  nonlocal p,a
  t=a+v+(p&1);p=(p&0x3c)|(t>255)|(0x40 if (~(a^v)&(a^t)&128) else 0);a=nz(t)
 def cmp(reg,v):
  nonlocal p
  p=(p&254)|(reg>=v);nz(reg-v)
 def resource(at):
  v=r[at-0x8000];events.append(('resource',at,v,0));return v
 def asl(v):
  nonlocal p
  p=(p&254)|(v>>7);return nz(v<<1)
 def gate(return_address):
  nonlocal a,y,p
  jsr(return_address);ld(y);push(a);y=nz(0);ld(s[0x704+x]);ld(a&248);store(0x704+x,a)
  cmp(x,41)
  if x!=41:
   cmp(x,1)
   if x==1:
    ld(s[0xd3]);store(0xc1,a);ld(s[0x70c+x]);store(0xc4,a);jsr(0x85c5)
    ld(0);store(0xc2,a);y=nz(8)
    while y:
     store(0xc2,asl(s[0xc2]));carry=p&1;v=s[0xc1];p=(p&254)|(v>>7);store(0xc1,nz((v<<1)|carry))
     if p&1:
      p&=254;ld(s[0xc2]);adc(s[0xc4]);store(0xc2,a);ld(s[0xc1]);adc(0);store(0xc1,a)
     y=nz(y-1)
    assert ret()==0x85c6;y=nz(s[0xc1])
  if x in (1,41):
   y=nz(y+1);store(0x704+x,nz(s[0x704+x]+1));store(0x704+x,nz(s[0x704+x]+1))
  ld(y);store(0x710+x,a);ld(pop());y=nz(a);assert ret()==return_address+1
 def restart():
  ld(s[0x704+x]);ld(a&8)
  if a:
   ld(0);store(0x708+x,a);ld(s[0x704+x]);ld(a&0x37);store(0x704+x,a)
 if ctx[:2]==bytes.fromhex('830b'):
  store(0x710+x,a);ld(s[0x704+x]);ld(a&248);ld(a|4);store(0x704+x,a)
  ld(x);ld(a&3);ld(a^3);a=asl(a);a=asl(a);y=nz(a);ld(0x30);cmp(y,8)
  if y==8:ld(0)
  events.append(('apu',0x4000+y,a,1))
 else:
  ld(s[0x704+x]);ld(a|32);store(0x704+x,a);ld(s[0x718+x]);a=asl(a);ld(0x54)
  if not p&1:ld(0x0a)
  store(0x71c+x,a);ld(y)
  if p&128:
   cmp(x,1)
   if x==1:gate(0x8339)
   restart()
  else:
   gate(0x833f);ld(255);store(0x77c+x,a);y=nz(y-1);ld(x)
   if x==0:store(0xc3,a);ld(y);ld(a^15)
   else:
    ld(y);p&=254;adc(s[0xd2]);cmp(a,0x60)
    if p&1:ld(0x5f)
    store(0xc3,a);store(0xc3,nz(s[0xc3]+1));cmp(x,0x28);store(0xc3,asl(s[0xc3]));y=nz(s[0xc3]);ld(resource(0x8934+y));store(0xc3,a);ld(resource(0x8935+y))
   store(0x724+x,a);ld(s[0xc3]);store(0x720+x,a);y=nz(4);ld(resource((s[0xc5]+256*s[0xc6]+y)&65535))
   if p&128:
    ld(0);store(0x708+x,a);ld(s[0x704+x]);ld(a&0x37);store(0x704+x,a)
   else:restart()
 pc=ret()
 return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x831b)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
 else:resource=rng.randbytes(16384)
 def compare(s,c,r):
  if not private or not valid(s,c):return model(s,c,r)
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(500):
   pc=ref.pc
   if pc in (0x8626,0x862b):at=(0x8934 if pc==0x8626 else 0x8935)+ref.y;bus.events.append(('resource',at,bus[at],0))
   if pc==0x8638:at=(bus[0xc5]+256*bus[0xc6]+ref.y)&65535;bus.events.append(('resource',at,bus[at],0))
   ref.step()
   # Instruction identity, not coincidental PC or stack return address.
   if pc in (0x8643,0x8651,0x80ce):break
  else:raise AssertionError('original timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  want=model(s,c,r);assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=make_checker(compare);cases=rejects=0
 def case(p,sp,x,y,pc=0x831b,ptr=0x9000,return_pc=0x807a):
  nonlocal cases
  s=bytearray(rng.randbytes(2048));s[0xc5]=ptr&255;s[0xc6]=ptr>>8
  s[0x100+((sp+1)&255)]=(return_pc-1)&255;s[0x100+((sp+2)&255)]=((return_pc-1)&65535)>>8
  c=pc.to_bytes(2,'big')+bytes((rng.randrange(256),x,y,p,sp,0xa7));check(bytes(s),c,resource);cases+=1
  return bytes(s),c
 for p in range(256):
  for sp in range(256):case(p,sp,sp&3,(p+sp)&255,0x830b if p&1 else 0x831b)
 for x in range(4):
  for y in range(256):
   for sp in (0,1,2,253,254,255):case(y,sp,x,y)
 for ptr in (0x7ffc,0x7ffd,0x80fc,0xbffb):
  for x in range(4):
   for sp in range(256):case(sp,sp,x,sp&127,ptr=ptr)
 for dest in (0x831b,0x830b,0x85c6,0x8340,0x8643,0x8651,0,0xffff):
  for sp in range(256):case(sp,sp,sp&3,sp,return_pc=dest)
 s,c=case(255,0,2,1)
 for pc in range(65536):
  if pc not in (0x830b,0x831b):check(s,pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
 for x in range(4,256):check(s,c[:3]+bytes((x,))+c[4:],resource);rejects+=1
 for ptr in range(65536):
  if not 0x8000<=((ptr+4)&65535)<=0xbfff:
   st=bytearray(s);st[0xc5]=ptr&255;st[0xc6]=ptr>>8;check(bytes(st),c,resource);rejects+=1
 cleanup();print({'accepted':cases,'inert_rejects':rejects,'original':private})
if __name__=='__main__':main()
