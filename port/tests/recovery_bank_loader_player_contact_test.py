"""Public F92B contact semantics with optional private original comparison."""
import os,sys,random,struct,tempfile,subprocess
from pathlib import Path
from recovery_bank_loader_player_contact_harness import Native as Base,PORT,RAM,CTX,RUNTIME,STACK
ENTRIES=(0xf92b,0xf95a,0xf96c)
class Native(Base):
 def __init__(self,code,resource):
  super().__init__(code,resource);base=self.trace
  def trace(mode,width,address,value):
   if STACK-4096<=address<STACK:assert address>=STACK-2304
   base(mode,width,address,value)
  self.minimum_trace=trace;self.mem.set_trace_func(trace)
def assemble(source=None):
 with tempfile.TemporaryDirectory() as td:
  src=PORT/'src/recovery_bank_loader_player_contact_region.s';out=Path(td)/'out.bin'
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
 def ly(v):
  nonlocal y
  y=v;nz(y)
 def store(at,v):r[at]=v;events.append(('ram',at,v))
 def compare(v):
  nonlocal p
  p=(p&254)|(1 if a>=v else 0);nz((a-v)&255)
 def read(at):
  v=resource[at+65536];events.append(('resource',at,v,0));return v
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)&255
 def done(pc):return bytes(r),struct.pack('>H6B',pc,a,x,y,p,sp,tag),events
 def call(target,ret):push(ret>>8);push(ret&255);return done(target)
 if pc==0xf92b:
  ly(0);load(r[0x4d0+y])
  if a&128:
   load(r[0x400+y])
   if a&128:
    load(r[0x54+y]);compare(3)
    if not(p&1):push(0xf9);push(0x40);pc=0xf949
  if pc==0xf92b:pc=0xf943
 for _ in range(1024):
  if pc==0xf941:pc=0xf974 if not(p&1) else 0xf943
  if pc==0xf943:
   ly((y+1)&255);load(r[0x4d0+y]);pc=0xf949 if a&128 else 0xf973
  if pc==0xf949:
   store(16,y);load(r[0x400+x])
   if a&128:
    load(r[0x570+x]);load(a&63);store(2,a);return call(0xf696,0xf959)
   pc=0xf973
  if pc==0xf95a:
   load(r[1])
   if not a:
    load(r[0]);ly(r[2]);compare(read(0xfa18+y))
    if not(p&1):ly(r[16]);return call(0xf6dc,0xf96b)
   pc=0xf973
  if pc==0xf96c:
   ly(r[2]);compare(read(0xf9fc+y));pc=0xf974 if not(p&1) else 0xf973
  if pc==0xf973:p|=1;pc=0xf974
  assert pc==0xf974,hex(pc)
  ly(r[16]);sp=(sp+1)&255;lo=r[256+sp];sp=(sp+1)&255;pc=((r[256+sp]<<8|lo)+1)&65535
  if pc!=0xf941:return done(pc)
 raise ValueError('cyclic model')
def main():
 private='--rom' in sys.argv;rng=random.Random(154);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if private else None;resource=rom[16:131088] if private else rng.randbytes(131072);n=Native(assemble(),resource);cases=guards=0;coverage=set();maxreads=0
 for entry in ENTRIES:
  for k in range(256):
   for mode in range(8):
    r=bytearray(rng.randbytes(2048));r[0x4d0]=128 if mode&1 else 0;r[0x400]=128 if mode&2 else 0;r[0x54]=mode%4;r[0x4d1]=128 if mode&4 else 0;r[0x400+k]=128 if mode&2 else 0;r[0x570+k]=k;r[1]=0 if mode&1 else 1;r[0]=k;r[2]=k;r[16]=mode
    ret=((0x8029,0,0xffff,0xc0f3)[mode%4]-1)&65535;r[256+((k+1)&255)]=ret&255;r[256+((k+2)&255)]=ret>>8;c=struct.pack('>H6B',entry,k,k,mode,k,k,0xa7);rt=bytes((30,0,16,k%8,0,0,0xba,0xdd,0xf0,13,0xd5,1));before=(bytes(r),c,b'\xb6'*134638,rt);want=model(r,c,resource)
    if private:
     from recovery_bank_loader_player_contact_oracle import ControllerBus,log_resource
     from recovery_test_active_command0e_rom import Ricoh
     b=ControllerBus(rom);b.map_bank(k%8);b[:2048]=r;b.events.clear();m=Ricoh(memory=b);m.pc=entry;m.a,m.x,m.y,m.p,m.sp=c[2:7]
     for step in range(8192):
      old=m.pc;coverage.add(old);log_resource(m,b,154);m.step()
      if old==0xf976 and m.pc!=0xf941 or not 0xf92b<=m.pc<0xf977:break
     else:raise AssertionError('original bound')
     assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events)==want,(hex(entry),k,mode)
    n.restore(before);assert n.run()==1,(hex(entry),k,mode);after=n.snapshot();assert after[:2]==want[:2] and n.events==want[2] and after[3]==rt,(hex(entry),k,mode)
    es=[e for e in want[2] if e[0]=='resource'];maxreads=max(maxreads,len(es));j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert after[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2;cases+=1
 for pc in range(65536):
  if pc in ENTRIES:continue
  n.restore(before);n.mem.w16(CTX,pc);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 for at,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0')):
  n.restore(before);n.mem.w_block(at,v);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 n.m.cleanup();print('PASS player contact',cases,guards,'maxreads',maxreads,'PCs',len(coverage),'private' if private else 'public',flush=True)
if __name__=='__main__':main()
