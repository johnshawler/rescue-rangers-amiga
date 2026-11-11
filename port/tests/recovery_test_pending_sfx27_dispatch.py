"""Independent cursor/resource and sound request contracts, with optional original-ROM proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=14
SOURCE="recovery_sfx27_table_dispatch"
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
   assert reads==([0xa00] if PREFLIGHT else [])+[e[1]-0x8000 for e in want[2] if e[0]=='resource']
  else:
   assert bytes(mem.r_block(JOURNAL,SIZE))==j
   assert reads==([0xa00] if PREFLIGHT and c[:3]==bytes.fromhex('800327') else [])
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  return got
 return check,m.cleanup
def model(s,c,r):
 pc=int.from_bytes(c[:2],'big')
 if pc!=0x8003 or c[2]!=0x27 or r[0xa00]<=0x27:return None
 ram=bytearray(s);q=bytearray(c);ev=[];sp=c[6]
 def w(at,v):ram[at]=v;ev.append(('ram',at,v))
 def rd(at):
  v=r[at-0x8000];ev.append(('resource',at,v,0));return v
 w(0xc0,(ram[0xc0]+1)&255)
 w(256+sp,0x80);sp=(sp-1)&255;w(256+sp,0xe5);sp=(sp-1)&255
 rd(0x8a00);lo=rd(0x8a52);w(0xc1,lo);hi=rd(0x8a51);w(0xc2,hi)
 a=hi|lo;pc=0x810d if a else 0x8151
 q[:]=pc.to_bytes(2,'big')+bytes((a,0x4e,0 if a else c[4],(c[5]&0x7c)|2,sp,c[7]))
 return bytes(ram),bytes(q),ev

def dequeue(s,c,r):
 if c[:2]!=bytes.fromhex('c0bf') or s[0xf5] or s[0xdb]>=8 or s[0xdc+s[0xdb]]==136:return None
 ram=bytearray(s);q=bytearray(c);ev=[('mapper',0xfff0,v,0) for v in (3,1,0,0,0)]
 def w(at,v):ram[at]=v;ev.append(('ram',at,v))
 x=s[0xdb];a=s[0xdc+x];sp=c[6]
 w(256+sp,a);w(0xdc+x,136);x+=1;w(0xdb,x&7)
 w(256+sp,0xc0);sp=(sp-1)&255;w(256+sp,0xf2);sp=(sp-1)&255
 q[:]=bytes.fromhex('8003')+bytes((a,x,c[4],(c[5]&0x7c)|(a&128)|(2 if a==0 else 0)|(a>=136),sp,c[7]))
 return bytes(ram),bytes(q),ev

def main():
 import sys,hashlib
 global SIZE,SOURCE,PREFLIGHT
 private='--rom' in sys.argv;rng=random.Random(0x810d)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_character_cursor_sound import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
 def compare(s,c,r):
  want=contract(s,c,r)
  if not private or want is None:return want
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  target=int.from_bytes(want[1][:2],'big')
  for _ in range(100):
   if ref.pc in (0x80f0,0x80fd,0x8102):
    addr={0x80f0:0x8a00,0x80fd:0x8a04+ref.x,0x8102:0x8a03+ref.x}[ref.pc];bus.events.append(('resource',addr,bus[addr],0))
   ref.step()
   if ref.pc==target:break
  else:raise AssertionError('ROM timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex());return got
 for dispatch in (True,False):
  PREFLIGHT=dispatch;SIZE=14 if dispatch else 22;SOURCE='recovery_sfx27_table_dispatch' if dispatch else 'recovery_nmi_audio_entry';contract=model if dispatch else dequeue
  check,cleanup=make_checker(compare);cases=0;rejects=0
  for p in range(256):
   for k in range(16):
    s=bytearray(rng.randbytes(2048));s[0xc0]=p;s[0xf5]=0;s[0xdb]=k%8;s[0xdc+k%8]=p if p!=136 else 39
    c=(bytes.fromhex('800327')+rng.randbytes(1) if dispatch else bytes.fromhex('c0bf')+rng.randbytes(2))+bytes((k,p,(p+k)&255,k))
    r=bytearray(resource if private else rng.randbytes(16384))
    if not private:
     r[0xa00]=40+(p%216)
     pointer=(0,0x8000,0xbfff,0xffff,0x007f,0xff00,0x8001,0x7fff)[k%8];r[0xa51:0xa53]=pointer.to_bytes(2,'big')
    check(bytes(s),c,bytes(r));cases+=1
  if not private:
   s=bytearray(rng.randbytes(2048));s[0xf5]=0;s[0xdb]=0;s[0xdc]=39;r=bytearray(rng.randbytes(16384));r[0xa00]=40
   good=bytes.fromhex('800327ffffff00a7') if dispatch else bytes.fromhex('c0bf27ffffff00a7')
   for pc in range(65536):
    if pc==int.from_bytes(good[:2],'big'):continue
    check(bytes(s),pc.to_bytes(2,'big')+good[2:],bytes(r));rejects+=1
   if dispatch:
    for a in range(256):
     if a!=39:check(bytes(s),good[:2]+bytes((a,))+good[3:],bytes(r));rejects+=1
    for n in range(40):r[0xa00]=n;check(bytes(s),good,bytes(r));rejects+=1
   else:
    for at,values in ((0xf5,range(1,256)),(0xdb,range(8,256)),(0xdc,(136,))):
     for v in values:
      bad=s.copy();bad[at]=v;check(bytes(bad),good,bytes(r));rejects+=1
  cleanup();print('PASS',SOURCE,cases,'ROM' if private else 'declarative','cases',rejects,'inert rejects; RAM/rawP/ordered effects/journal tails/resources/ABI/bounds/stack')
if __name__=='__main__':main()
