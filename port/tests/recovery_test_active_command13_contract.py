"""ROM-free indexed command13 contract."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=22
def make_checker(oracle):
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)/'native.bin'
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_music_active_command13.s')],check=True)
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
   assert reads==validation_reads(s,c,r)+[a-0x8000 for kind,a,*_ in je if kind=='resource']
  else:
   assert bytes(mem.r_block(JOURNAL,SIZE))==j
   assert reads==validation_reads(s,c,r)
  assert bytes(mem.r_block(RESOURCE,16384))==r
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,SIZE),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==guard and bytes(mem.r_block(a+n,16))==guard
  return got
 return check,m.cleanup
def validation_reads(s,c,r):
 if c[:3]!=bytes.fromhex('83a013') or not 0x28<=c[3]<=0x2b:return []
 out=[0x4a9]
 if r[0x4a9]!=0xfb:return out
 out.append(0x4aa)
 if r[0x4aa]!=0x84:return out
 x=c[3];ptr=s[0x728+x]+256*s[0x72c+x]
 return out

def command13(s,c,r):
 if c[:3]!=bytes.fromhex('83a013') or not 0x28<=c[3]<=0x2b or r[0x4a9:0x4ab]!=bytes((0xfb,0x84)):return None
 x=c[3];ptr=s[0x728+x]+256*s[0x72c+x];counter=s[0x748+x]
 if not 0x8000<=ptr<=0xbfff:return None
 if ptr>0xbffd and counter==1:return None
 s=bytearray(s);a,x,y,p,sp=c[2:7];e=[]
 def store(at,v):s[at]=v;e.append(('ram',at,v))
 def push(v):
  nonlocal sp
  store(0x100+sp,v);sp=(sp-1)&255
 def pop():
  nonlocal sp
  sp=(sp+1)&255;return s[0x100+sp]
 def nz(v):
  nonlocal p
  p=(p&0x7d)|(v&128)|(2 if v==0 else 0)
 def resource(at):
  v=r[at-0x8000];e.append(('resource',at,v,0));return v
 def fetch(ret):
  nonlocal a,y
  push(ret>>8);push(ret&255)
  store(0xc1,s[0x728+x]);store(0xc2,s[0x72c+x]);y=0
  a=resource(s[0xc1]+256*s[0xc2])
  lo=(s[0x728+x]+1)&255;store(0x728+x,lo);nz(lo)
  if not lo:
   hi=(s[0x72c+x]+1)&255;store(0x72c+x,hi);nz(hi)
  pop();pop()
 push(0x83);push(0xa6);store(0xc4,19);p=(p&0x7c)|1
 fetch(0x847b);store(0xc3,a)
 push(0x84);push(0x82)
 store(0xc1,pop());store(0xc2,pop())
 a=resource(0x84a9);push(a);a=resource(0x84aa);store(0xc2,a);store(0xc1,pop())
 store(0xc2,4);y=x+4
 # ADC X+4 clears V/C; CMP #12 then binary counter-1 supplies V/C.
 old=s[0x748+x];count=(old-1)&255
 p=(p&0x3c)|(1 if old else 0)|(64 if old==128 else 0);nz(count)
 if count==0:
  store(0x748+x,0)
  push(0x85);push(0x30)
  a=(s[0x730+x]&0x97)|s[0xc3];nz(a);store(0x730+x,a)
  pop();pop()
  fetch(0x8533);store(0xc3,a);fetch(0x8538);store(0x728+x,a);a=s[0xc3];nz(a);store(0x72c+x,a)
 else:
  old=s[0x728+x];total=old+2;a=total&255
  p=(p&0x3c)|(1 if total>255 else 0)|(64 if old in (126,127) else 0);nz(a);store(0x728+x,a)
  if total>255:
   hi=(s[0x72c+x]+1)&255;store(0x72c+x,hi);nz(hi)
 pop();pop()
 return bytes(s),bytes.fromhex('839d')+bytes((a,x,y,p,sp,c[7])),e

def cases(rng,r):
 # Cross every counter and operand; raw status and stack cover all byte values.
 for counter in range(256):
  for operand in range(256):
   s=bytearray(rng.randbytes(2048));x=0x28+(operand%4);ptr=0x9000+(operand&255)
   s[0x728+x]=ptr&255;s[0x72c+x]=ptr>>8;s[0x748+x]=counter
   rr=bytearray(r);rr[ptr-0x8000]=operand
   c=bytes((0x83,0xa0,19,x,counter,operand,(counter+operand)&255,counter))
   yield bytes(s),c,bytes(rr)
 # Every stream address, including rejected addresses and both branch edges.
 for ptr in range(65536):
  s=bytearray(rng.randbytes(2048));x=0x28+ptr%4;s[0x728+x]=ptr&255;s[0x72c+x]=ptr>>8;s[0x748+x]=ptr%3
  yield bytes(s),bytes((0x83,0xa0,19,x,0,ptr&255,ptr>>8,0xa7)),r
 # Boundary preflight combinations include safe skip beyond bank end and unsafe fetches.
 for ptr in (0x7fff,0x8000,0xbffd,0xbffe,0xbfff,0xc000,0xffff):
  for counter in (0,1,2,128,255):
   for operand in (0,1,127,128,255):
    for x in range(0x28,0x2c):
     s=bytearray(rng.randbytes(2048));s[0x728+x]=ptr&255;s[0x72c+x]=ptr>>8;s[0x748+x]=counter
     rr=bytearray(r)
     if 0x8000<=ptr<0xc000:rr[ptr-0x8000]=operand
     yield bytes(s),bytes((0x83,0xa0,19,x,operand,counter,operand,0xa7)),bytes(rr)

def main():
 check,cleanup=make_checker(command13);rng=random.Random(14);r=bytearray(rng.randbytes(16384));r[0x4a9:0x4ab]=bytes((0xfb,0x84));r=bytes(r)
 accepted=rejected=0
 for s,c,rr in cases(rng,r):
  check(s,c,rr)
  if command13(s,c,rr) is None:rejected+=1
  else:accepted+=1
 s=bytearray(2048);s[0x750]=0;s[0x754]=0x90;s=bytes(s);c=bytes.fromhex('83a013280020ff00')
 for pc in range(65536):
  if pc==0x83a0:continue
  check(s,pc.to_bytes(2,'big')+c[2:],r);rejected+=1
 for field in (2,3):
  for value in range(256):
   cc=bytearray(c);cc[field]=value
   if command13(s,cc,r) is None:check(s,bytes(cc),r);rejected+=1
 for offset in (0x4a9,0x4aa):
  for value in range(256):
   if value==r[offset]:continue
   rr=bytearray(r);rr[offset]=value;check(s,c,bytes(rr));rejected+=1
 cleanup();print(f'PASS {accepted} ROM-free command13 accepted cases plus {rejected} inert guards')
if __name__=='__main__':main()
