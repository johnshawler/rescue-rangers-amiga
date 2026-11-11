"""ROM-free title-engine table contract with optional original-ROM proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=362
def make_checker(oracle):
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)/'native.bin'
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_title_engine_tables.s')],check=True)
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
   assert 1<=value<=90
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
   je=[e for e in want[2] if e[0] in ('resource','ppu')]
   expected=len(je).to_bytes(2,'big')+b''.join(a.to_bytes(2,'big')+bytes((v,0 if typ=='resource' else 1 if k else 2)) for typ,a,v,k in je)
   assert bytes(mem.r_block(JOURNAL,SIZE))==expected+j[len(expected):]
   assert reads==[e[1]-0xc000 for e in want[2] if e[0]=='resource']
  else:assert bytes(mem.r_block(JOURNAL,SIZE))==j
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  return got
 return check,m.cleanup
def model(s,c,r):
 if c[:2]!=bytes.fromhex('c5d1'):return None
 ram=bytearray(s);cc=bytearray(c);events=[]
 def w(a,v):ram[a]=v;events.append(('ram',a,v))
 def read(a):
  v=r[a-0xc000];events.append(('resource',a,v,0));return v
 for x in range(29,-1,-1):w(0x340+x,read(0xd657+x))
 for y in range(29,-1,-1):
  w(0x5a0+y,read(0xc73f+y));w(0x5d0+y,read(0xc75d+y))
 w(0xbe,0x84);w(0xbf,3)
 w(256+c[6],0xc5);w(256+((c[6]-1)&255),0xf7)
 cc[:5]=bytes.fromhex('a00003ffff');cc[5]&=0x7d;cc[6]=(c[6]-2)&255
 return bytes(ram),bytes(cc),events

def main():
 import sys,hashlib
 rng=random.Random(0xc5d1);oracle=model;private='--rom' in sys.argv
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_title_chr_fade import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[16+7*16384:16+8*16384]
  def oracle(s,c,r):
   want=model(s,c,r)
   if want is None:return None
   bus=CompleteBus(rom);bus.map_bank(2);ref=CPU(memory=bus)
   bus[:2048]=s;bus.events.clear();ref.pc=0xc5d1;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
   for _ in range(2000):
    if ref.pc==0xa000:break
    if ref.pc in (0xc5d3,0xc5de,0xc5e4):
     a=0xd657+ref.x if ref.pc==0xc5d3 else (0xc73f if ref.pc==0xc5de else 0xc75d)+ref.y
     bus.events.append(('resource',a,bus[a],0))
    ref.step()
   else:raise AssertionError('timeout')
   actual=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
   assert actual==want;return actual
 check,cleanup=make_checker(oracle)
 for case in range(256):
  if not private:resource=rng.randbytes(16384)
  c=bytes.fromhex('c5d1')+rng.randbytes(3)+bytes((case,(case*73)&255,case));check(rng.randbytes(2048),c,resource)
 guards=0
 if not private:
  s=rng.randbytes(2048);c=bytes.fromhex('c5d100112224ff00')
  for pc in range(65536):
   if pc==0xc5d1:continue
   check(s,pc.to_bytes(2,'big')+c[2:],resource);guards+=1
 cleanup();print(f'PASS 256 {"original-ROM" if private else "ROM-free"} table cases and {guards} inert PC guards; full raw RAM/context, resource effects, ABI and bounds.')
if __name__=='__main__':main()
