"""ROM-free indexed command02 contract."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=10
def make_checker(oracle):
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)/'native.bin'
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_music_active_command02.s')],check=True)
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
   assert 1<=value<=128
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
   je=[e for e in want[2] if e[0] in ('apu','resource')]
   expected=len(je).to_bytes(2,'big')+b''.join(a.to_bytes(2,'big')+bytes((v,k)) for _,a,v,k in je)
   assert bytes(mem.r_block(JOURNAL,SIZE))==expected+bytes(SIZE-len(expected))
   assert reads==[0x487,0x488]+[a-0x8000 for kind,a,*_ in je if kind=='resource']
  else:assert bytes(mem.r_block(JOURNAL,SIZE))==j
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  return got
 return check,m.cleanup
def command02(s,c,r):
 if c[:3]!=bytes.fromhex('83a002') or not 0x28<=c[3]<=0x2b or c[5]&0x30!=0x20 or r[0x487:0x489]!=bytes((0xbd,0x84)):return None
 s=bytearray(s);a,x,y,p,sp=c[2:7];e=[]
 def store(at,v):s[at]=v;e.append(('ram',at,v))
 def push(v):
  nonlocal sp
  store(0x100+sp,v);sp=(sp-1)&255
 push(0x83);push(0xa6);push(0x84);push(0x82)
 sp=(sp+1)&255;store(0xc1,s[0x100+sp]);sp=(sp+1)&255;store(0xc2,s[0x100+sp])
 e.append(('resource',0x8487,0xbd,0));push(0xbd);e.append(('resource',0x8488,0x84,0));store(0xc2,0x84)
 sp=(sp+1)&255;store(0xc1,s[0x100+sp]);a=s[0x730+x]|16;store(0x730+x,a);sp=(sp+2)&255
 p=(p&0x7c)|(a&128)|(2 if a==0 else 0)
 return bytes(s),bytes.fromhex('839d')+bytes((a,x,6,p,sp,c[7])),e

def main():
 check,cleanup=make_checker(command02);rng=random.Random(3);r=bytearray(rng.randbytes(16384));r[0x487:0x489]=bytes((0xbd,0x84));r=bytes(r)
 for case in range(4096):
  s=rng.randbytes(2048);c=bytes((0x83,0xa0,2,0x28+case%4,case&255,(case&0xcf)|32,case&255,case>>8));check(s,c,r)
 s=bytes(2048);c=bytes.fromhex('83a002280020ff00');guards=0
 for pc in range(65536):
  if pc==0x83a0:continue
  check(s,pc.to_bytes(2,'big')+c[2:],r);guards+=1
 for field in (2,3,5):
  for value in range(256):
   cc=bytearray(c);cc[field]=value
   if command02(s,cc,r) is None:check(s,bytes(cc),r);guards+=1
 for offset in (0x487,0x488):
  for value in range(256):
   if value==r[offset]:continue
   rr=bytearray(r);rr[offset]=value;check(s,c,bytes(rr));guards+=1
 cleanup();print(f'PASS4096 ROM-free command02 cases plus{guards} inert guards')
if __name__=='__main__':main()
