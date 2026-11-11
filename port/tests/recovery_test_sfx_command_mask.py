"""Standalone ROM-free channel ABI harness; optional cartridge instruction proof."""
import os,random,subprocess,tempfile
from pathlib import Path
import machine68k

PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZE=78
SOURCE="recovery_sfx_command_mask"
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
   events.append(('resource',mem.r16(at),mem.r8(at+2),kind))
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
TARGETS=(0x8667,0x86a5,0x8652,0x869f,0x8699)
def validation_reads(s,c,r):
 if c[:2]!=bytes.fromhex('82dc') or c[3]>3:return []
 ptr=s[0xd0]+256*s[0xd1]
 if not 0x8000<=ptr<=0xbffe:return []
 reads=[ptr-0x8000];mask=r[ptr-0x8000]
 if mask>31 or ptr+1+mask.bit_count()>0xbfff:return reads
 for i,t in enumerate(TARGETS):
  for j,v in enumerate((t&255,t>>8)):
   at=0x2fb+2*i+j;reads.append(at)
   if r[at]!=v:return reads
 return reads

def model(state,ctx,r):
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[]
 ptr=s[0xd0]+256*s[0xd1]
 if ctx[:2]!=bytes.fromhex('82dc') or x>3 or not 0x8000<=ptr<=0xbffe:return None
 mask=r[ptr-0x8000]
 if mask>31 or ptr+1+mask.bit_count()>0xbfff:return None
 if any(r[0x2fb+2*i+j]!=v for i,t in enumerate(TARGETS) for j,v in enumerate((t&255,t>>8))):return None
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
 def ret():return ((pop()|(pop()<<8))+1)&65535
 def adc(v):
  nonlocal p,a
  t=a+v+(p&1);p=(p&0x3c)|(t>255)|(0x40 if (~(a^v)&(a^t)&128) else 0);a=nz(t)
 def cmp(reg,v):
  nonlocal p
  p=(p&254)|(reg>=v);nz(reg-v)
 def resource(at):
  v=r[at-0x8000];events.append(('resource',at,v,0));return v
 def shift():
  nonlocal p,a
  p=(p&254)|(a&1);a=nz(a>>1)
 def stream(return_address):
  nonlocal y
  jsr(return_address);y=nz(0);ld(resource(s[0xd0]+256*s[0xd1]));store(0xd0,nz(s[0xd0]+1))
  if s[0xd0]==0:store(0xd1,nz(s[0xd1]+1))
  assert ret()==return_address+1
 def instrument():
  nonlocal y,p,a
  y=nz(y-1);ld(0);store(0xc3,a);ld(y)
  for _ in range(3):
   carry=a>>7;p=(p&254)|carry;a=nz(a<<1)
   t=s[0xc3];p=(p&254)|(t>>7);store(0xc3,nz((t<<1)|carry))
  p&=254;adc(resource(0x8a02));store(0xc5,a);ld(s[0xc3]);adc(resource(0x8a01));store(0xc6,a)
 ld(0);store(0xc4,a);stream(0x82e2)
 while True:
  shift()
  if p&1:
   push(a);stream(0x82e9);store(0xc3,a);ld(s[0xc4]);jsr(0x82f0);jsr(0x82fa)
   # Authentic inline-table dispatch, including destructive return-frame pops.
   p=(p&254)|(a>>7);a=nz(a<<1);y=nz(a);y=nz(y+1);ld(pop());store(0xc1,a);ld(pop());store(0xc2,a)
   ld(resource((s[0xc1]+256*s[0xc2]+y)&65535));push(a);y=nz(y+1);ld(resource((s[0xc1]+256*s[0xc2]+y)&65535));store(0xc2,a);ld(pop());store(0xc1,a)
   target=s[0xc1]+256*s[0xc2]
   if target==0x8667:
    store(0xc3,nz(s[0xc3]+1));ld(s[0xc3]);cmp(a,s[0x700+x])
    if not p&2:store(0x700+x,a);y=nz(a);ld(s[0x704+x]);ld(a|8);store(0x704+x,a);instrument()
   elif target==0x86a5:ld(s[0x70c+x]);ld(a&15);ld(a|s[0xc3]);ld(a|0x30);store(0x70c+x,a)
   elif target==0x8652:
    cmp(x,1)
    if x==1:ld(s[0xc3])
    if x!=1 or a==0:ld(s[0x70c+x]);ld(a&0xc0);ld(a|s[0xc3]);ld(a|0x30)
    store(0x70c+x,a)
   elif target==0x869f:ld(s[0xc3]);store(0x718+x,a)
   elif target==0x8699:ld(s[0xc3]);store(0x714+x,a)
   else:raise AssertionError('unsupported callback')
   assert ret()==0x82f1;ld(pop())
  if p&2:break
  store(0xc4,nz(s[0xc4]+1))
 stream(0x8307);y=nz(a)
 return bytes(s),(0x830b if y==0 else 0x831b).to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events

def main():
 import sys,hashlib
 private='--rom' in sys.argv;rng=random.Random(0x82dc)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  base_resource=rom[49168:65552]
 else:
  r=bytearray(rng.randbytes(16384))
  for i,t in enumerate(TARGETS):r[0x2fb+2*i:0x2fd+2*i]=t.to_bytes(2,'little')
  base_resource=bytes(r)
 def compare(s,c,r):
  ptr=s[0xd0]+256*s[0xd1]
  valid=c[:2]==bytes.fromhex('82dc') and c[3]<=3 and 0x8000<=ptr<=0xbffe
  valid=valid and r[ptr-0x8000]<=31 and ptr+1+r[ptr-0x8000].bit_count()<=0xbfff
  valid=valid and all(r[0x2fb+2*i+j]==v for i,t in enumerate(TARGETS) for j,v in enumerate((t&255,t>>8)))
  if not private or not valid:return model(s,c,r)
  # Deliberately do not choose original exits from model output.
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0x82dc;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(400):
   pc=ref.pc;at=None
   if pc==0x835a:at=bus[0xd0]+256*bus[0xd1]
   elif pc in (0x802c,0x8030):at=(bus[0xc1]+256*bus[0xc2]+ref.y)&65535
   elif pc in (0x868c,0x8693):at=0x8a02 if pc==0x868c else 0x8a01
   if at is not None:bus.events.append(('resource',at,bus[at],0))
   ref.step()
   if ref.pc in (0x830b,0x831b):break
  else:raise AssertionError('ROM timeout')
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  want=model(s,c,r)
  assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=make_checker(compare);cases=rejects=0
 def case(p,sp,ch,mask,ptr=0x9000,value=0,note=0):
  nonlocal cases
  s=bytearray(rng.randbytes(2048));s[0xd0]=ptr&255;s[0xd1]=ptr>>8
  c=bytes.fromhex('82dc')+bytes((rng.randrange(256),ch,rng.randrange(256),p,sp,0xa7))
  if private:r=base_resource
  else:
   r=bytearray(base_resource);r[ptr-0x8000:ptr-0x8000+mask.bit_count()+2]=bytes((mask,))+bytes([value])*mask.bit_count()+bytes((note,));r=bytes(r)
  if not private:assert model(bytes(s),c,r) is not None
  check(bytes(s),c,r);cases+=1;return bytes(s),c,r
 if private:
  pointers=[0x8000+i for i,v in enumerate(base_resource[:-7]) if v<=31]
  for p in range(256):
   for sp in range(256):case(p,sp,sp&3,0,pointers[(p*256+sp)%len(pointers)])
 else:
  for p in range(256):
   for sp in range(256):case(p,sp,sp&3,(p+sp)&31,0x90fc,(p+sp)&255,p)
  for mask in range(32):
   for ch in range(4):
    for value in (0,1,15,127,128,254,255):
     for sp in (0,1,2,3,4,5,6,7,254,255):case(value,sp,ch,mask,0x90ff,value,value)
  s,c,r=case(255,0,3,31,0xbff9,255,255)
  # Exact last-byte bounds: accepted equality and atomic insufficient-stream rejects.
  for mask in range(32):
   for ptr in range(0xbff8,0xbfff):
    st=bytearray(s);st[0xd0]=ptr&255;st[0xd1]=ptr>>8
    rr=bytearray(r);rr[ptr-0x8000]=mask
    check(bytes(st),c,bytes(rr))
    if ptr+1+mask.bit_count()<=0xbfff:cases+=1
    else:rejects+=1
  # Instrument unchanged/changed paths, zero wrap, all SP/channel pairs.
  for sp in range(256):
   for ch in range(4):
    for val,equal in ((0,True),(255,True),(255,False)):
     st=bytearray(s);st[0xd0]=0;st[0xd1]=0x90;st[0x700+ch]=(val+1)&255 if equal else 1
     rr=bytearray(r);rr[0x1000:0x1003]=bytes((1,val,128));rr[0xa01]=255;rr[0xa02]=sp
     cc=c[:3]+bytes((ch,c[4],sp,sp,c[7]));check(bytes(st),cc,bytes(rr));cases+=1
  for pc in range(65536):
   if pc!=0x82dc:check(s,pc.to_bytes(2,'big')+c[2:],r);rejects+=1
  for x in range(4,256):check(s,c[:3]+bytes((x,))+c[4:],r);rejects+=1
  for ptr in range(65536):
   if 0x8000<=ptr<=0xbffe:continue
   st=bytearray(s);st[0xd0]=ptr&255;st[0xd1]=ptr>>8;check(bytes(st),c,r);rejects+=1
  for mask in range(32,256):
   rr=bytearray(r);rr[0x3ff9]=mask;check(s,c,bytes(rr));rejects+=1
  for off in range(10):
   for v in range(256):
    at=0x2fb+off
    if v==r[at]:continue
    rr=bytearray(r);rr[at]=v;check(s,c,bytes(rr));rejects+=1
 cleanup();print('PASS SFX command mask',cases,'ROM' if private else 'declarative',rejects,'inert rejects',flush=True)
if __name__=='__main__':main()
