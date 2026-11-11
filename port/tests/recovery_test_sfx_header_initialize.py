"""Independent sound-header contract, with optional original-ROM proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=6
SOURCE="recovery_sfx_header_initialize"
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
 pointer=s[0xc1]+256*s[0xc2]
 if c[:2]!=bytes.fromhex('810d') or c[4] or not 0x8000<=pointer<0xc000:return None
 ram=bytearray(s);q=bytearray(c);h=r[pointer-0x8000];ev=[('resource',pointer,h,0)]
 def w(a,v):ram[a]=v;ev.append(('ram',a,v))
 q[2]=h
 if h==0:
  q[:2]=bytes.fromhex('8152');q[5]=(c[5]&0x7d)|2
 else:
  q[3]=(q[3]+1)&255;w(0xc4,h);priority=h&127;q[2]=priority
  q[:2]=bytes.fromhex('8151')
  if priority<s[0xce]:q[5]=(c[5]&0x7c)|((priority-s[0xce])&128)
  else:
   w(0xce,priority)
   if priority==s[0xce] and ram[0xd6]&128 and not h&128:w(0xd7,0)
   w(0xd6,0);w(0xc4,(h*2)&255);w(0xd6,h&128)
   if h&128:w(0xd7,q[3])
   w(0xc1,(ram[0xc1]+1)&255);w(0xd0,ram[0xc1])
   if ram[0xc1]==0:w(0xc2,(ram[0xc2]+1)&255)
   w(0xd1,ram[0xc2])
   for a in range(0xd2,0xd6):w(a,0)
   for a in range(0x727,0x6ff,-1):w(a,0)
   q[2]=0;q[4]=255;q[5]=(c[5]&0x7c)|128
 return bytes(ram),bytes(q),ev

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x8151)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
 def compare(s,c,r):
  want=model(s,c,r)
  if not private or want is None:return want
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0x810d;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  a=s[0xc1]+256*s[0xc2];bus.events.append(('resource',a,bus[a],0))
  for _ in range(250):
   ref.step()
   if ref.pc in (0x8151,0x8152):break
  else:raise AssertionError('ROM timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=make_checker(compare);cases=0;rejects=0
 r=bytearray(resource if private else rng.randbytes(16384))
 for p in range(256):
  for sp in range(256):
   s=bytearray(rng.randbytes(2048));ptr=(0x8000,0x80ff,0x81ff,0xaf5b,0xbfff,0xbf00,0x8001,0x8100)[sp%8]
   s[0xc1]=ptr&255;s[0xc2]=ptr>>8
   h=r[ptr-0x8000] if private else (p+sp)&255
   if not private:r[ptr-0x8000]=h
   s[0xce]=(0,h&127,((h&127)+1)&255,255)[sp%4]
   c=bytes.fromhex('810d')+bytes((sp,sp,0,p,sp,p^sp));check(bytes(s),c,bytes(r));cases+=1
 # Every readable bank3 address, including page rollover and final-byte carry.
 for ptr in range(0x8000,0xc000):
  s=bytearray(rng.randbytes(2048));s[0xc1]=ptr&255;s[0xc2]=ptr>>8;s[0xce]=0
  c=bytes.fromhex('810d')+bytes((ptr&255,(ptr>>6)&255,0,ptr&255,(ptr>>8)&255,0xa7))
  check(bytes(s),c,bytes(r));cases+=1
 if not private:
  # Exhaust every header/priority pair; vary prior latch sign and wrapped X.
  for h in range(256):
   for priority in range(256):
    s=bytearray(rng.randbytes(2048));s[0xc1]=255;s[0xc2]=191;s[0xce]=priority;s[0xd6]=128 if priority&1 else 0
    r[-1]=h;c=bytes.fromhex('810d')+bytes((0,255,0,priority,h,0xa7))
    check(bytes(s),c,bytes(r));cases+=1
 if not private:
  s=bytearray(rng.randbytes(2048));s[0xc1]=0;s[0xc2]=128;c=bytes.fromhex('810d00ff00ff00a7')
  for pc in range(65536):
   if pc!=0x810d:check(bytes(s),pc.to_bytes(2,'big')+c[2:],bytes(r));rejects+=1
  for y in range(1,256):check(bytes(s),c[:4]+bytes((y,))+c[5:],bytes(r));rejects+=1
  for ptr in range(65536):
   if not 0x8000<=ptr<0xc000:
    s[0xc1]=ptr&255;s[0xc2]=ptr>>8;check(bytes(s),c,bytes(r));rejects+=1
 cleanup();print('PASS header',cases,'ROM' if private else 'declarative','cases',rejects,'inert rejects; exhaustive P x SP, RAM/context/ordered effects/journal/resource/ABI/bounds/canaries')
if __name__=='__main__':main()
