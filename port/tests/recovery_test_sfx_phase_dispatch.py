"""Standalone ROM-free channel ABI harness; optional cartridge instruction proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=30
SOURCE="recovery_sfx_phase_dispatch"
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
def model(state,ctx,r):
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[];pc=int.from_bytes(ctx[:2],'big')
 if pc not in (0x8060,0x807a,0x8085):return None
 if pc==0x807a and x>3:return None
 if pc==0x8085 and s[0x100+((sp+1)&255)]>3:return None
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
 if pc==0x8060:
  p&=254;ld(s[0xca]);adc(s[0xc8]);store(0xc8,a);ld(s[0xc9]);adc(0);store(0xc7,a);ld(s[0xcf]);push(a);x=nz(3);pc=0x8072
 for rounds in range(12):
  if pc==0x8085:
   ld(pop());x=nz(a);pc=0x8087
  if pc==0x8087:
   store(0xcf,shift(s[0xcf]));x=nz(x-1);pc=0x808c if x&128 else 0x8072
  if pc==0x8072:
   ld(s[0xcf]);a=shift(a)
   if p&1:jsr(0x8079);return result(0x82b0)
   pc=0x807a
  if pc==0x807a:
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
   return result(ret)
 raise AssertionError('control bounds')

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x8060);resource=rng.randbytes(16384)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
 def compare(s,c,r):
  valid=int.from_bytes(c[:2],'big') in (0x8060,0x807a,0x8085)
  valid=valid and (c[:2]!=b'\x80\x7a' or c[3]<=3) and (c[:2]!=b'\x80\x85' or s[0x100+((c[6]+1)&255)]<=3)
  if not private or not valid:return model(s,c,r)
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(500):
   pc=ref.pc;ref.step()
   if pc==0x80ba or ref.pc in (0x82b0,0x8374,0x839d):break
  else:raise AssertionError('ROM timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  want=model(s,c,r);assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=make_checker(compare);cases=rejects=0
 def case(pc,p,sp,mask,control,channel,empty=False,phase=None):
  nonlocal cases
  s=bytearray(rng.randbytes(2048));s[0xcf]=mask;s[0xc0]=control
  if empty:s[0x750:0x758]=bytes(8)
  if phase is not None:s[0xca],s[0xc8],s[0xc9]=phase
  s[0x100+((sp+1)&255)]=channel
  c=pc.to_bytes(2,'big')+bytes((rng.randrange(256),channel,rng.randrange(256),p,sp,0xa7))
  check(bytes(s),c,resource);cases+=1;return s,c
 for p in range(256):
  for sp in range(256):
   for pc in (0x8060,0x807a,0x8085):case(pc,p,sp,(p+sp)&255,(p*3+sp)&255,sp&3,(p+sp)%3==0)
 # Binary phase arithmetic exhaustive low-byte operands, alternating carry into FF high byte.
 for a in range(256):
  for b in range(256):case(0x8060,a,b,0,2,b&3,True,(a,b,255 if (a+b)&1 else 0))
 # Every mask at each channel and each entry, with active/empty music and disabled music.
 for mask in range(256):
  for ch in range(4):
   for control,empty in ((0,False),(0,True),(2,False),(255,True)):
    for pc in (0x8060,0x807a,0x8085):case(pc,mask,ch*64,mask,control,ch,empty)
 if not private:
  s,c=case(0x8060,255,255,2,5,3)
  for pc in range(65536):
   if pc not in (0x8060,0x807a,0x8085):check(bytes(s),pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
  for sp in range(256):
   for v in range(4,256):
    s[0x100+((sp+1)&255)]=v
    check(bytes(s),bytes.fromhex('8085000000ff')+bytes((sp,0xa7)),resource);rejects+=1
    check(bytes(s),bytes((0x80,0x7a,0,v,0,255,sp,0xa7)),resource);rejects+=1
 cleanup();print('PASS phase dispatch',cases,'ROM' if private else 'declarative',rejects,'inert rejects',flush=True)
if __name__=='__main__':main()
