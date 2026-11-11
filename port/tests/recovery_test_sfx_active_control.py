"""Standalone ROM-free channel ABI harness; optional cartridge instruction proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=2
SOURCE="recovery_sfx_active_control"
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
def valid(s,c):return int.from_bytes(c[:2],'big') in (0xc0f6,0x8052)
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
 if ctx[:2]==bytes.fromhex('c0f6'):
  jsr(0xc0f8);ld(s[0xc0]);ld(a&243);store(0xc3,a);p&=254;ld(4)
  v=s[0xc0];t=a+v;p=(p&0x3c)|(t>255)|(64 if (~(a^v)&(a^t)&128) else 0);a=nz(t)
  ld(a&12);y=nz(a);ld(a|s[0xc3]);store(0xc0,a);ld(y)
  if not a:jsr(0x8051)
 ld(s[0xc0]);p=(p&254)|(a&1);a=nz(a>>1)
 if p&1:pc=((pop()|(pop()<<8))+1)&65535
 else:
  ld(s[0xd0]);ld(a|s[0xd1]);pc=0x8060
  if a:jsr(0x805f);pc=0x8224
 return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0xc0f6);resource=rng.randbytes(16384)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 def compare(s,c,r):
  if not private or not valid(s,c):return model(s,c,r)
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(100):
   pc=ref.pc;ref.step()
   if pc==0x80ba or ref.pc in (0x8224,0x8060):break
  else:raise AssertionError('original timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert got==model(s,c,r);return got
 check,cleanup=make_checker(compare);cases=rejects=0
 for p in range(256):
  for sp in range(256):
   for pc in (0xc0f6,0x8052):
    s=bytearray(rng.randbytes(2048));s[0xc0]=(p+sp)&255
    if sp&2:s[0xd0]=s[0xd1]=0
    c=pc.to_bytes(2,'big')+bytes((rng.randrange(256),rng.randrange(256),rng.randrange(256),p,sp,0xa7));check(bytes(s),c,resource);cases+=1
 for dest in (0x8052,0x8224,0x8060,0x80ba,0xc0f6,0,65535):
  for sp in range(256):
   s=bytearray(rng.randbytes(2048));s[0xc0]=1
   s[0x100+((sp+1)&255)]=(dest-1)&255;s[0x100+((sp+2)&255)]=((dest-1)&65535)>>8
   c=bytes.fromhex('8052000000')+bytes((sp,sp,0xa7));check(bytes(s),c,resource);cases+=1
 for pc in range(65536):
  if pc not in (0xc0f6,0x8052):check(bytes(s),pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
 cleanup();print({'accepted':cases,'inert_rejects':rejects,'original':private})
if __name__=='__main__':main()
