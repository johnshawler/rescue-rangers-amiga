"""USER-mode native object region checks. Original-first private differential route.
No state loaded from captures; original routine runs first from continuously reached state.
"""
import hashlib,os,random,struct,subprocess,tempfile
from pathlib import Path
import machine68k
ROOT=Path(__file__).resolve().parents[2]
CODE,STOP,RAM,CTX,JOURNAL,RUNTIME,RESOURCE,STACK=0x1000,0x800,0x10000,0x12000,0x20000,0x40000,0x80000,0x1f0000
JSIZE=60002
class Native:
 def __init__(self,resource,source=None):
  self.resource=bytes(resource);assert len(resource)==131072
  with tempfile.TemporaryDirectory() as td:
   src=ROOT/'port/src/recovery_object_region.s'
   if source is not None:src=Path(td)/'fault.s';src.write_text(source)
   out=Path(td)/'region.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);self.code=out.read_bytes()
  self.m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);self.mem,self.cpu=self.m.mem,self.m.cpu;self.rng=random.Random(0x8000)
  self.regions=((RAM,2048),(CTX,8),(JOURNAL,JSIZE),(RUNTIME,12));self.guard=bytes(range(16));self.events=[];self.reads=[]
  self.mem.w_block(CODE,self.code);self.mem.w16(STOP,0x60fe);self.mem.w_block(RESOURCE-16,self.guard+self.resource+self.guard)
  def trace(mode,width,a,v):
   n=1<<width;ranges=[(x,x+y) for x,y in self.regions]+[(STACK-4096,STACK)]
   if mode=='R':ranges += [(CODE,CODE+len(self.code)),(STOP,STOP+4),(STACK,STACK+4),(RESOURCE,RESOURCE+131072)]
   assert mode in ('R','W') and any(x<=a and a+n<=y for x,y in ranges),(mode,width,hex(a))
   if mode=='R' and RESOURCE<=a<RESOURCE+131072:
    assert width==0
    if self.cpu.r_reg(8)==RAM:self.reads.append(a-RESOURCE)
   if mode=='W' and RAM<=a<RAM+2048:assert width==0;self.events.append(('ram',a-RAM,v))
   if mode=='W' and a==JOURNAL and width==1 and v:
    assert 1<=v<=15000
    p=JOURNAL+2+4*(v-1);self.events.append(('resource',self.mem.r16(p),self.mem.r8(p+2),self.mem.r8(p+3)))
  self.trace=trace;self.mem.set_trace_func(trace)
 def run(self,s,c,runtime=None):
  mem,cpu=self.mem,self.cpu
  if runtime is None:runtime=bytes.fromhex('1e0000050000ffff0000d501')
  blobs=(s,c,b'\xb6'*JSIZE,runtime)
  for (a,n),v in zip(self.regions,blobs):assert len(v)==n;mem.w_block(a-16,self.guard+v+self.guard)
  regs=[self.rng.getrandbits(32) for _ in range(15)];regs[8:11]=[RAM,CTX,JOURNAL];regs[12:14]=[RUNTIME,RESOURCE]
  cpu.w_sr(0);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  self.events.clear();self.reads.clear();cpu.w_pc(CODE);mem.set_trace_mode(True)
  for _ in range(100000):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('native timeout')
  mem.set_trace_mode(False)
  assert cpu.r_sr()&0x2000==0 and cpu.r_sp()==STACK+4
  assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  for a,n in self.regions:assert bytes(mem.r_block(a-16,16))==self.guard and bytes(mem.r_block(a+n,16))==self.guard
  assert bytes(mem.r_block(CODE,len(self.code)))==self.code
  assert bytes(mem.r_block(RESOURCE-16,131104))==self.guard+self.resource+self.guard
  assert bytes(mem.r_block(RUNTIME,12))==runtime
  return bytes(mem.r_block(RAM,2048)),bytes(mem.r_block(CTX,8)),list(self.events),cpu.r_reg(0)
 def close(self):self.m.cleanup()

def compare_original(n,bus,m):
 s=bytes(bus[:2048]);c=struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)
 ret=(bus[256+((m.sp+1)&255)]|(bus[256+((m.sp+2)&255)]<<8))+1;ret&=65535
 bus.events.clear();reads=[];steps=0
 while True:
  assert 0x8000<=m.pc<0x81e0,hex(m.pc)
  # Original data addresses are decoded independently for semantic read evidence.
  pc=m.pc;op=bus[pc];address=None
  if op in (0xb9,0xbd):address=((bus[pc+1]|bus[pc+2]<<8)+(m.y if op==0xb9 else m.x))&65535
  elif op in (0xb1,0xd1,0x71):
   z=bus[pc+1];address=((bus[z]|bus[(z+1)&255]<<8)+m.y)&65535
  if address is not None and address>=0x8000:
   bus.events.append(('resource',address,bus[address],0));reads.append(5*16384+address-0x8000 if address<0xc000 else 7*16384+address-0xc000)
  m.step();steps+=1
  if m.pc==ret:break
  assert steps<200000
 want=(bytes(bus[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7),list(bus.events),1)
 got=n.run(s,c)
 if got!=want:
  mismatch=[(hex(i),a,b) for i,(a,b) in enumerate(zip(got[0],want[0])) if a!=b]
  raise AssertionError((c.hex(),got[1].hex(),want[1].hex(),mismatch[:12],next(((i,a,b) for i,(a,b) in enumerate(zip(got[2],want[2])) if a!=b),None),len(got[2]),len(want[2]),got[3]))
 assert n.reads==reads,(n.reads[:8],reads[:8])
 return steps,len(reads)

def transaction_checks():
 """Positive controls distinguish budget enforcement from unrelated rejection."""
 source=(ROOT/'port/src/recovery_object_region.s').read_text()
 c=bytes.fromhex('800017334d2400a7')
 active=bytearray(2048)
 for a,v in ((0x101,0x34),(0x102,0xc1),(0x4d0,128),(0x420,1),(0x430,128)):active[a]=v
 inactive=bytearray(active);inactive[0x4d0]=0
 resource=bytes(131072)
 def reject(state,data,code=None):
  n=Native(data,code)
  assert n.run(state,c)==(state,c,[],0xffffffff)
  assert bytes(n.mem.r_block(JOURNAL,JSIZE))==b'\xb6'*JSIZE and not n.reads
  n.close()
 malformed=bytearray(resource);malformed[5*16384+0x3560]=0x40
 reject(active,malformed)
 for state,has_reads in ((inactive,False),(active,True)):
  n=Native(resource);got=n.run(state,c)
  assert got[3]==1
  assert (len(n.reads)>5) if has_reads else not n.reads
  n.close()
 for token,limits,state in (('#200000,a4',(20,40),inactive),('#15000,(a2)',(1,5),active)):
  assert source.count(token)==1,(token,source.count(token))
  for limit in limits:
   replacement=token.replace(token.split(',')[0],'#'+str(limit))
   code=source.replace(token,replacement)
   assert code!=source and token not in code
   reject(state,resource,code)
 return 5

if __name__=='__main__':
 rng=random.Random(90);n=Native(bytes(131072));count=0
 # Full unsupported-PC domain and mapper-contract corruption reject without mutation.
 for pc in range(65536):
  if pc==0x8000:continue
  s=rng.randbytes(2048);c=pc.to_bytes(2,'big')+rng.randbytes(6)
  got=n.run(s,c);assert got==(s,c,[],0xffffffff);assert bytes(n.mem.r_block(JOURNAL,JSIZE))==b'\xb6'*JSIZE;count+=1
 for pos in (0,3,4,5,10,11):
  rt=bytearray.fromhex('1e0000050000ffff0000d501');rt[pos]^=1;s=rng.randbytes(2048);c=b'\x80\x00'+rng.randbytes(6)
  assert n.run(s,c,rt)==(s,c,[],0xffffffff);count+=1
 # Width-aware trace itself rejects crossing each boundary and resource mutation.
 for a,size in n.regions+((RESOURCE,131072),):
  for mode in ('R','W'):
   try:n.trace(mode,1,a+size-1,0)
   except AssertionError:pass
   else:raise AssertionError('cross-boundary access accepted')
 # Reject all 480 top-level reentry destinations without mutation.
 for ret in range(0x8000,0x81e0):
  s=bytearray(2048);s[0x101]=(ret-1)&255;s[0x102]=((ret-1)>>8)&255;c=bytes.fromhex('800017334d2400a7')
  assert n.run(s,c)==(s,c,[],0xffffffff);count+=1
 active=0
 for rawp in range(256):
  for sp in (0,1,254,255,rawp):
   for parity in (0,1):
    s=bytearray(rng.randbytes(2048));s[0x95]=parity
    for i in range(16):s[0x4d0+i]&=127
    s[256+((sp+1)&255)]=0x34;s[256+((sp+2)&255)]=0xc1
    c=bytes((128,0,23,65,77,rawp,sp,0xa7));r=bytearray(s);events=[]
    def store(a,v):r[a]=v;events.append(('ram',a,v))
    value=(parity+1)&255;store(0x95,value)
    reverse=bool(value&1);store(0x96,15 if reverse else 0)
    for i in range(16):store(0x96,(14-i)&255 if reverse else i+1)
    q=bytes((0xc1,0x35,s[0x4d0 if reverse else 0x4df],255 if reverse else 16,77,(rawp&124)|(129 if reverse else 3),(sp+2)&255,0xa7))
    assert n.run(s,c)==(bytes(r),q,events,1),(rawp,sp,parity)
    assert not n.reads;active+=1
 n.close()
 count+=transaction_checks()
 print('PASS',active,'synthetic supported all rawP/all SP with both scan directions;',count,'inert rejects, USER ABI, immutable code/resource, width-aware bounds')
