"""Standalone ROM-free channel ABI harness; optional cartridge instruction proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=514
SOURCE="recovery_sfx_envelope"
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
from recovery_sfx_envelope_model import envelope
TARGETS=(0x86c9,0x86de,0x8718,0x86fa,0x890d)
def validation_reads(s,c,r):
 if c[:2]!=bytes.fromhex('86b2') or c[3]>3 or s[0x704+c[3]]&7>4:return []
 ptr=s[0xc5]|s[0xc6]<<8
 if not 0x8000<=ptr<=0xbff8:return []
 reads=[0x92e]
 if r[0x92e]:return reads
 for i,v in enumerate(b''.join(t.to_bytes(2,'little') for t in TARGETS)):
  at=0x6bf+i;reads.append(at)
  if r[at]!=v:break
 return reads
def valid(s,c,r):
 if c[:2]!=bytes.fromhex('86b2') or c[3]>3 or s[0x704+c[3]]&7>4:return False
 ptr=s[0xc5]|s[0xc6]<<8
 return 0x8000<=ptr<=0xbff8 and r[0x92e]==0 and r[0x6bf:0x6c9]==b''.join(t.to_bytes(2,'little') for t in TARGETS)
def model(s,c,r):return envelope(s,c,r) if valid(s,c,r) else None

def run_original(bus,ref,reserved,coverage=None):
 start=len(bus.events);depth=0
 for steps in range(20000):
  pc=ref.pc
  assert (0x86b2<=pc<=0x890d or 0x8006<=pc<=0x8037 or 0x80cf<=pc<=0x80e0),hex(pc)
  if coverage is not None:coverage.add(pc)
  addr=None
  if pc in (0x802c,0x8030,0x86cb,0x86e0,0x86ef,0x86f5,0x8703,0x8766,0x87b3,0x8838,0x88f5):
   ptr=0xc1 if pc in (0x802c,0x8030) else 0xc5
   addr=((bus[ptr]|bus[ptr+1]<<8)+ref.y)&65535
  elif pc in (0x86d1,0x86e8,0x870b,0x8846,0x88c8,0x88d0,0x88df,0x88e5):
   addr=({0x86d1:0x890e,0x86e8:0x890e,0x870b:0x890e,0x8846:0x892e,0x88c8:0x8934,0x88d0:0x8935,0x88df:0x8934,0x88e5:0x8935}[pc]+ref.y)&65535
  if addr is not None:
   assert 0x8000<=addr<0xc000
   bus.events.append(('resource',addr,bus[addr],0))
  if bus[pc]==0x20 and pc!=0x86bc:depth+=1
  final=bus[pc]==0x60 and depth==0
  if bus[pc]==0x60:depth-=1
  ref.step()
  if final:break
 else:raise AssertionError('original timeout')
 return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved)),list(bus.events[start:])

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x86b20003);coverage=set()
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_active_envelope_rom import EnvelopeBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552];bus=EnvelopeBus(rom);bus[0x8000:0xc000]=resource;ref=CPU(memory=bus)
 else:
  r=bytearray(rng.randbytes(16384));r[0x92e]=0;r[0x6bf:0x6c9]=b''.join(t.to_bytes(2,'little') for t in TARGETS);resource=bytes(r)
 def compare(s,c,r):
  if not private or not valid(s,c,r):return model(s,c,r)
  bus[:2048]=s;bus.events.clear();ref.pc=0x86b2;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  want=run_original(bus,ref,c[7],coverage)
  assert want==model(s,c,r),('independent model',c.hex(),want[1].hex(),model(s,c,r)[1].hex())
  return want
 check,cleanup=make_checker(compare);cases=rejects=0
 def trial(case,p=None,sp=None,d6=None,d8=None,stage=None,dest=None):
  nonlocal cases
  s=bytearray(rng.randbytes(2048));x=case%4
  s[0x704+x]=(s[0x704+x]&248)|(case//4%5 if stage is None else stage)
  ptr=(0x8000,0xbff8,0x80ff,0xbff7)[case%4] if not private else 0x8a80+(case%32)*8
  s[0xc5]=ptr&255;s[0xc6]=ptr>>8
  if d6 is not None:s[0xd6]=d6
  if d8 is not None:s[0xd8]=d8
  p=case%256 if p is None else p;sp=case//256%256 if sp is None else sp
  if dest is not None:
   s[0x100+((sp+1)&255)]=(dest-1)&255;s[0x100+((sp+2)&255)]=((dest-1)&65535)>>8
  c=bytes((0x86,0xb2,rng.randrange(256),x,rng.randrange(256),p,sp,0xa7));check(bytes(s),c,resource);cases+=1
  return bytes(s),c
 for i in range(65536):s,c=trial(i)
 # Every D6/D8 pair, forced sustained envelope, mixed raw flags, pitch extremes.
 for i in range(65536):s,c=trial(i,d6=i>>8,d8=i&255,stage=2)
 for dest in (0x86b2,0x890d,0x82c0,0x8006,0x80e0,0,65535):
  for sp in range(256):s,c=trial(sp,sp=sp,dest=dest)
 for pc in range(65536):
  if pc!=0x86b2:check(s,pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
 for x in range(4,256):check(s,c[:3]+bytes((x,))+c[4:],resource);rejects+=1
 for ptr in range(65536):
  if not 0x8000<=ptr<=0xbff8:
   st=bytearray(s);st[0xc5]=ptr&255;st[0xc6]=ptr>>8;check(bytes(st),c,resource);rejects+=1
 for at in [0x92e]+list(range(0x6bf,0x6c9)):
  for v in range(256):
   if v!=resource[at]:
    rt=bytearray(resource);rt[at]=v;check(s,c,bytes(rt));rejects+=1
 for stage in (5,6,7):
  st=bytearray(s);st[0x704+c[3]]=(st[0x704+c[3]]&248)|stage;check(bytes(st),c,resource);rejects+=1
 cleanup();print({'accepted':cases,'inert_rejects':rejects,'original':private,'instruction_addresses':len(coverage)})
 if private:print('Original instruction coverage:',','.join('%04x'%pc for pc in sorted(coverage)))
if __name__=='__main__':main()
