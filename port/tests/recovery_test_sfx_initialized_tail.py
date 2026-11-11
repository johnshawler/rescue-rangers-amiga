"""Independent sound-header contract, with optional original-ROM proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=2
SOURCE="recovery_sfx_initialized_tail"
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
   events.append(('resource' if PREFLIGHT else 'mapper',mem.r16(at),mem.r8(at+2),0 if kind==0 else 0))
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
   je=[e for e in want[2] if e[0] in ('resource','mapper')]
   expected=len(je).to_bytes(2,'big')+b''.join(a.to_bytes(2,'big')+bytes((v,0)) for typ,a,v,k in je)
   assert bytes(mem.r_block(JOURNAL,SIZE))==expected+j[len(expected):]
   assert reads==[e[1]-0x8000 for e in want[2] if e[0]=='resource']
  else:
   assert bytes(mem.r_block(JOURNAL,SIZE))==j
   assert reads==[]
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  return got
 return check,m.cleanup
def model(s,c,r):
 sp=c[6];frame=bytes(s[256+((sp+i)&255)] for i in range(1,5));a=s[0xd0]|s[0xd1];x=s[0xdb]
 if c[:2]!=bytes.fromhex('8151') or s[0xc0]!=1 or not a or x>=8 or s[0xdc+x]!=136 or frame!=bytes.fromhex('e580f2c0'):return None
 ram=bytearray(s);ev=[]
 def w(at,v):ram[at]=v;ev.append(('ram',at,v))
 w(0xc0,0);sp=(sp+4)&255
 w(256+sp,0xc0);sp=(sp-1)&255;w(256+sp,0xf8);sp=(sp-1)&255
 w(0xc3,0);w(0xc0,4)
 w(256+sp,0x80);sp=(sp-1)&255;w(256+sp,0x5f);sp=(sp-1)&255
 q=bytes.fromhex('8224')+bytes((a,x,4,(c[5]&0x3c)|(a&128),sp,c[7]))
 return bytes(ram),q,ev

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x8224);r=bytes(16384)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 def compare(s,c,r):
  want=model(s,c,r)
  if not private or want is None:return want
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0x8151;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(100):
   ref.step()
   if ref.pc==0x8224:break
  else:raise AssertionError('ROM timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex());return got
 check,cleanup=make_checker(compare);cases=0;rejects=0
 for p in range(256):
  for sp in range(256):
   s=bytearray(rng.randbytes(2048));s[0xc0]=1;s[0xdb]=sp%8;s[0xdc+s[0xdb]]=136;s[0xd0]=p;s[0xd1]=(sp or 1)
   for i,v in enumerate(bytes.fromhex('e580f2c0'),1):s[256+((sp+i)&255)]=v
   c=bytes.fromhex('8151')+bytes((sp,p,sp,p,sp,0xa7));check(bytes(s),c,r);cases+=1
 if not private:
  for pc in range(65536):
   if pc!=0x8151:check(bytes(s),pc.to_bytes(2,'big')+c[2:],r);rejects+=1
  for at,values in ((0xc0,[v for v in range(256) if v!=1]),(0xdb,range(8,256)),(0xdc+s[0xdb],[v for v in range(256) if v!=136])):
   for v in values:
    b=s.copy();b[at]=v;check(bytes(b),c,r);rejects+=1
  b=s.copy();b[0xd0]=b[0xd1]=0;check(bytes(b),c,r);rejects+=1
  for sp in range(256):
   b=s.copy();q=c[:6]+bytes((sp,))+c[7:]
   for i,v in enumerate(bytes.fromhex('e580f2c0'),1):b[256+((sp+i)&255)]=v
   for i in range(1,5):
    at=256+((sp+i)&255)
    for v in range(256):
     if v==b[at]:continue
     bad=b.copy();bad[at]=v;check(bytes(bad),q,r);rejects+=1
 cleanup();print('PASS initialized tail',cases,'ROM' if private else 'declarative','cases',rejects,'inert rejects; exhaustive P x SP, every wrong wrapped frame byte, complete effects/ABI/bounds/canaries')
if __name__=='__main__':main()
