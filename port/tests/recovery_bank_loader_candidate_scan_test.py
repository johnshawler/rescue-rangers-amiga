"""ROM-free F977 scan model and private raw original-first comparisons."""
import os,sys,random,struct,tempfile,subprocess
from pathlib import Path
from recovery_bank_loader_candidate_scan_harness import Native as Base,PORT,RAM,CTX,RUNTIME,STACK
ENTRIES=(0xf977,0xf9d7,0xf9e4)
class Native(Base):
 def __init__(self,code,resource):
  super().__init__(code,resource);base=self.trace
  def trace(mode,width,address,value):
   if STACK-4096<=address<STACK:assert address>=STACK-2304
   base(mode,width,address,value)
  self.minimum_trace=trace;self.mem.set_trace_func(trace)
def assemble(source=None):
 with tempfile.TemporaryDirectory() as td:
  src=PORT/'src/recovery_bank_loader_candidate_scan_region.s';out=Path(td)/'out.bin'
  if source is not None:src=Path(td)/'in.s';src.write_text(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);return out.read_bytes()
def model(state,context,resource):
 r=bytearray(state);pc=int.from_bytes(context[:2],'big');a,x,y,p,sp,tag=context[2:];events=[]
 def nz(v):
  nonlocal p
  p=(p&125)|(v&128)|(2 if not v else 0)
 def load(v):
  nonlocal a
  a=v;nz(a)
 def store(at,v):r[at]=v;events.append(('ram',at,v))
 def compare(v):
  nonlocal p
  p=(p&254)|(1 if a>=v else 0);nz((a-v)&255)
 def read(at):
  v=resource[at+65536];events.append(('resource',at,v,0));return v
 def math(v,subtract):
  nonlocal a,p
  old=a;z=a-v-(not(p&1)) if subtract else a+v+(p&1);a=z&255
  overflow=((old^a)&(old^v)&128) if subtract else (~(old^v)&(old^a)&128)
  p=(p&60)|(1 if (z>=0 if subtract else z>255) else 0)|(64 if overflow else 0);nz(a)
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)&255
 def done(pc):return bytes(r),struct.pack('>H6B',pc,a,x,y,p,sp,tag),events
 def call(target,ret):push(ret>>8);push(ret&255);return done(target)
 def finish():
  nonlocal sp
  sp=(sp+1)&255;lo=r[256+sp];sp=(sp+1)&255;return done(((r[256+sp]<<8|lo)+1)&65535)
 if pc==0xf977:store(5,x);y=2;nz(y);scan=True
 else:
  scan=False
  if pc==0xf9d7:
   load(r[1])
   if not a:
    load(r[0]);compare(r[4])
    if not(p&1):return call(0xf6dc,0xf9e3)
  else:
   compare(r[3])
   if not(p&1):return finish()
 for _ in range(256):
  if not scan:
   while True:
    y=(y+1)&255;nz(y);p=(p&254)|(1 if y>=r[5] else 0);nz((y-r[5])&255)
    if y!=r[5]:break
   p=(p&254)|(1 if y>=16 else 0);nz((y-16)&255)
   if y==16:return finish()
  scan=False;load(r[0x4d0+y])
  if not(a&128):continue
  load(r[0x400+y])
  if not(a&128):continue
  load(r[0x4e0+y]);compare(1)
  if a==1:
   store(16,y);load(r[0x420+y]);y=a;nz(y);load(read(0xf9d0+y));store(3,a);load(read(0xf9d5+y));store(4,a)
  else:
   compare(0x60)
   if a!=0x60:
    compare(0x3a)
    if a!=0x3a:continue
    store(16,y);load(0xfc);store(3,a);load(8);store(4,a)
   # The 3A path falls through the following 60 setup: BEQ after LDA08 is false.
   store(16,y);load(4);store(3,a);load(0);store(4,a)
  load(r[0x570+x]);load(a&63);y=a;nz(y);load(read(0xf9fc+y));p|=1;math(r[3],True);store(3,a);load(read(0xfa18+y));p&=254;math(r[4],False);store(4,a);y=r[16];nz(y);return call(0xf696,0xf9d6)
 raise AssertionError('model bound')
def main():
 private='--rom' in sys.argv;rng=random.Random(153);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if private else None;resource=rom[16:131088] if private else rng.randbytes(131072);n=Native(assemble(),resource);cases=guards=0;coverage=set();maxreads=0
 for entry in ENTRIES:
  for k in range(256):
   for mode in range(4):
    r=bytearray(rng.randbytes(2048));r[0x4d0:0x5d0]=bytes(256);r[0x400:0x500]=bytes(256);r[5]=k;r[3]=k;r[4]=255;r[0]=mode;r[1]=0 if mode else 1
    y=(2,15,16,255)[mode];r[0x4d0+y]=128;r[0x400+y]=128;r[0x4e0+y]=(1,0x60,0x3a,0)[mode];r[0x420+y]=k;r[0x570+k]=k
    ret=((0x8e18,0,0xffff,0xc0f3)[mode]-1)&65535;r[256+((k+1)&255)]=ret&255;r[256+((k+2)&255)]=ret>>8
    c=struct.pack('>H6B',entry,k,k,y,k,k,0xa7);rt=bytes((30,0,16,k%8,0,0,0xba,0xdd,0xf0,13,0xd5,1));before=(bytes(r),c,b'\xb6'*134638,rt);
    try:want=model(r,c,resource)
    except AssertionError:
     n.restore(before);assert n.run()==0xffffffff and n.snapshot()==before and not n.events;guards+=1;continue
    if private:
     from recovery_bank_loader_candidate_scan_oracle import ControllerBus,log_resource
     from recovery_test_active_command0e_rom import Ricoh
     b=ControllerBus(rom);b.map_bank(k%8);b[:2048]=r;b.events.clear();m=Ricoh(memory=b);m.pc=entry;m.a,m.x,m.y,m.p,m.sp=c[2:7]
     for step in range(8192):
      old=m.pc;coverage.add(old);log_resource(m,b,153);m.step()
      if old==0xf9f1 or not 0xf977<=m.pc<0xf9f2:break
     else:raise AssertionError('original bound')
     assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events)==want,(hex(entry),k,mode)
    n.restore(before);assert n.run()==1,(hex(entry),k,mode);after=n.snapshot();assert after[:2]==want[:2] and n.events==want[2] and after[3]==rt,(hex(entry),k,mode)
    es=[e for e in want[2] if e[0]=='resource'];maxreads=max(maxreads,len(es));j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert after[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2;cases+=1
 for pc in range(65536):
  if pc in ENTRIES:continue
  n.restore(before);n.mem.w16(CTX,pc);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 for at,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0')):
  n.restore(before);n.mem.w_block(at,v);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 n.m.cleanup();print('PASS candidate scan',cases,guards,'maxreads',maxreads,'PCs',len(coverage),'private' if private else 'public',flush=True)
if __name__=='__main__':main()
