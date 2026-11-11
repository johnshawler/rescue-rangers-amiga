"""Independent cursor/resource and sound request contracts, with optional original-ROM proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=6
def make_checker(oracle):
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)/'native.bin'
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_character_cursor_sound_request.s')],check=True)
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
   events.append(('resource' if kind==0 else 'ppu',mem.r16(at),mem.r8(at+2),0 if kind in (0,2) else 1))
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
   je=[e for e in want[2] if e[0] in ('resource','ppu')]
   expected=len(je).to_bytes(2,'big')+b''.join(a.to_bytes(2,'big')+bytes((v,0 if typ=='resource' else 1 if k else 2)) for typ,a,v,k in je)
   assert bytes(mem.r_block(JOURNAL,SIZE))==expected+j[len(expected):]
   assert reads==[e[1]-0x8000 for e in want[2] if e[0]=='resource']
  else:assert bytes(mem.r_block(JOURNAL,SIZE))==j and reads==[]
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  return got
 return check,m.cleanup
def model(s,c,r):
 pc=int.from_bytes(c[:2],'big')
 if pc not in (0xa07b,0xf379,0xa086):return None
 ram=bytearray(s);q=bytearray(c);ev=[];a,x,y,p,sp=c[2:7]
 def w(at,v):ram[at]=v;ev.append(('ram',at,v))
 def nz(v,p):return (p&0x7d)|(v&128)|(2 if v==0 else 0)
 def push(v):
  nonlocal sp
  w(256+sp,v);sp=(sp-1)&255
 if pc==0xa07b:
  a=r[0x20e1+y];ev.append(('resource',0xa0e1+y,a,0));w(0x203,a);a=39;p=nz(a,p);push(0xa0);push(0x85);pc=0xf379
 elif pc==0xa086:push(0xa0);push(0x88);pc=0xff04
 else:
  w(0,x);x=ram[0xda];w(1,a);a=ram[(0xdc+x)&255];p=nz((a-136)&255,(p&0x7c)|(a>=136))
  if a==136:
   a=ram[1];w((0xdc+x)&255,a);x=(x+1)&255;a=x&7;w(0xda,a)
  x=ram[0];p=nz(x,p);sp=(sp+1)&255;lo=ram[256+sp];sp=(sp+1)&255;pc=((ram[256+sp]<<8|lo)+1)&65535
 q[:]=pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,c[7]))
 return bytes(ram),bytes(q),ev

def main():
 import sys,hashlib
 rng=random.Random(0xf379);private='--rom' in sys.argv;oracle=model
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_title_chr_fade import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[32784:49168]
  def oracle(s,c,r):
   want=model(s,c,r)
   if want is None:return None
   bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
   for _ in range(50):
    at=ref.pc
    if at==0xa07b:
     addr=0xa0e1+ref.y;bus.events.append(('resource',addr,bus[addr],0))
    ref.step()
    if at in (0xa083,0xa086,0xf391):break
   else:raise AssertionError('timeout')
   got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
   assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex());return got
 check,cleanup=make_checker(oracle);cases=0
 for p in range(256):
  for k in range(24):
   pc=(0xa07b,0xf379,0xa086)[k%3];s=bytearray(rng.randbytes(2048));s[0xda]=(p+31*k)&255;s[(0xdc+s[0xda])&255]=136 if k%2 else (p+19*k)&255
   c=pc.to_bytes(2,'big')+rng.randbytes(2)+bytes((p,p,(p+13*k)&255,k));r=resource if private else rng.randbytes(16384)
   check(bytes(s),c,r);cases+=1
 guards=0
 if not private:
  s=rng.randbytes(2048);r=rng.randbytes(16384)
  for pc in range(65536):
   if pc in (0xa07b,0xf379,0xa086):continue
   check(s,pc.to_bytes(2,'big')+rng.randbytes(6),r);guards+=1
 cleanup();print('PASS',cases,'ROM' if private else 'synthetic','cases;',guards,'inert PC guards; full RAM/raw context/ordered effects/resource journal/ABI/bounds/canaries/wrapped stack')
if __name__=='__main__':main()
