"""Standalone ROM-free channel ABI harness; optional cartridge instruction proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=30
SOURCE="recovery_sfx_channel_reconfigure"
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
   events.append(('apu',mem.r16(at),mem.r8(at+2),kind))
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
  return got
 return check,m.cleanup
def model(s,c,r):
 sp=c[6]
 if c[:2]!=bytes.fromhex('81a3'):return None
 if any(s[0x100+((sp+i)&255)]!=v for i,v in ((1,0xab),(2,0x82),(4,0x5f),(5,0x80))):return None
 ram=bytearray(s);q=bytearray(c);ev=[]
 def w(a,v):ram[a]=v&255;ev.append(('ram',a,v&255))
 def push(v):w(0x100+q[6],v);q[6]=(q[6]-1)&255
 def pop():q[6]=(q[6]+1)&255;return ram[0x100+q[6]]
 def nz(v):q[5]=(q[5]&0x7d)|(v&128)|(2 if v==0 else 0)
 if ram[0xcf]:
  w(0xcf,ram[0xcf]^15);push(0x81);push(0xad);push(ram[0xcf])
  for ch in (3,2,1,0):
   if not ram[0xcf]&1:
    push(0x81);push(0xcc);q[4]=(3-ch)*4
    ev.append(('apu',0x4000+q[4],0 if q[4]==8 else 0x30,1));q[6]=(q[6]+2)&255
    if ram[0x754+ch]|ram[0x750+ch]:w(0x77c+ch,255)
   q[5]=(q[5]&254)|(ram[0xcf]&1);w(0xcf,ram[0xcf]>>1)
  q[3]=255;w(0xcf,pop())
  ev.extend([('apu',0x4001,8,1),('apu',0x4005,8,1),('apu',0x4015,15,1)])
  q[6]=(q[6]+2)&255;w(0xcf,0)
 q[6]=(q[6]+2)&255;q[2]=pop();nz(q[2]);w(0xcf,q[2]);q[6]=(q[6]+2)&255;q[:2]=bytes.fromhex('8060')
 return bytes(ram),bytes(q),ev

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x81a3);resource=rng.randbytes(16384)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
 def compare(s,c,r):
  want=model(s,c,r)
  if not private or want is None:return want
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0x81a3;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(200):
   ref.step()
   if ref.pc==0x8060:break
  else:raise AssertionError('ROM timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=make_checker(compare);cases=rejects=0
 def case(mask,p,sp,saved,activity):
  nonlocal cases
  s=bytearray(rng.randbytes(2048));s[0xcf]=mask
  for ch in range(4):s[0x750+ch]=255 if activity&(1<<ch) else 0;s[0x754+ch]=128 if activity&(16<<ch) else 0
  for i,v in ((1,0xab),(2,0x82),(3,saved),(4,0x5f),(5,0x80)):s[0x100+((sp+i)&255)]=v
  c=bytes.fromhex('81a3')+rng.randbytes(3)+bytes((p,sp,0xa7));check(bytes(s),c,resource);cases+=1
  return s,c
 # Every raw P/SP, every mask/saved mask, and every mask/activity combination.
 for p in range(256):
  for sp in range(256):case((p+sp)&255,p,sp,p^sp,(p*7+sp)&255)
 for mask in range(256):
  for value in range(256):
   case(mask,value,(mask+value)&255,value,0x81)
   case(mask,value,value,mask,value)
 # Inert preflight failures exhaust PC and every frame byte at every wrapped SP.
 if not private:
  s,c=case(2,255,255,2,255)
  for pc in range(65536):
   if pc!=0x81a3:check(bytes(s),pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
  for sp in range(256):
   for pos,correct in ((1,0xab),(2,0x82),(4,0x5f),(5,0x80)):
    for v in range(256):
     if v==correct:continue
     for i,b in ((1,0xab),(2,0x82),(4,0x5f),(5,0x80)):s[0x100+((sp+i)&255)]=b
     s[0x100+((sp+pos)&255)]=v
     c=bytes.fromhex('81a3000000ff')+bytes((sp,0xa7));check(bytes(s),c,resource);rejects+=1
 cleanup();print('PASS channels',cases,'ROM' if private else 'declarative',rejects,'inert rejects',flush=True)
if __name__=='__main__':main()
