"""Public closed F328 semantics; optional original-first differential proof."""
import sys,random,struct,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_target_choice_harness import Native as BaseNative,PORT,RAM,CTX,RUNTIME,STACK

class Native(BaseNative):
 def __init__(self,code,resource):
  super().__init__(code,resource);base=self.trace
  def trace(mode,width,address,value):
   if STACK-4096<=address<STACK:assert address>=STACK-2304,'minimum stack exceeded'
   base(mode,width,address,value)
  self.minimum_trace=trace;self.mem.set_trace_func(trace)

def model(state,context):
 r=bytearray(state);c=bytearray(context);a,x,y,p,sp=c[2:7];events=[]
 def store(at,v):r[at]=v&255;events.append(('ram',at,v&255))
 def nz(v):
  nonlocal p
  p=(p&125)|(128 if v&128 else 0)|(2 if not v else 0)
 def lda(v):
  nonlocal a
  a=v;nz(a)
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)&255
 def pop():
  nonlocal sp
  sp=(sp+1)&255;return r[256+sp]
 def sub(v):
  nonlocal a,p
  before=a;z=a-v-(0 if p&1 else 1);value=z&255;p=(p&60)|(1 if z>=0 else 0)|(64 if ((before^value)&(before^v)&128) else 0);a=value;nz(a)
 def add(v):
  nonlocal a,p
  before=a;z=a+v+(p&1);value=z&255;p=(p&60)|(1 if z>255 else 0)|(64 if (~(before^v)&(before^value)&128) else 0);a=value;nz(a)
 def distance(ret):
  nonlocal a,p
  push(ret>>8);push(ret&255)
  lda(r[0x4d0+y])
  if a&128:
   lda(1);store(0,a);lda(r[0x4f0+x]);p|=1;sub(r[0x4f0+y]);push(a);lda(r[0x500+x]);sub(r[0x500+y]);lda(pop())
   if p&1:lda(2);store(0,a)
   else:lda(a^255);add(1)
  else:lda(255)
  lo=pop();hi=pop();assert (hi<<8|lo)==ret
 y=0;nz(y);distance(0xf32c);store(1,a);lda(r[0]);store(2,a);y=1;nz(y);distance(0xf336)
 value=(a-r[1])&255;p=(p&254)|(1 if a>=r[1] else 0);nz(value)
 if p&1:lda(r[2]);store(0,a)
 lda(r[0]);store(0x580+x,a);lo=pop();hi=pop();pc=((hi<<8|lo)+1)&65535
 return bytes(r),struct.pack('>H6B',pc,a,x,y,p,sp,c[7]),events

def assemble(source=None):
 with tempfile.TemporaryDirectory() as td:
  src=PORT/'src/recovery_bank_loader_target_choice_region.s';out=Path(td)/'region.bin'
  if source is not None:src=Path(td)/'region.s';src.write_text(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);return out.read_bytes()

def main():
 private='--rom' in sys.argv;rng=random.Random(0xf328);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if private else None;resource=rom[16:131088] if private else bytes(131072);code=assemble();n=Native(code,resource);cases=guards=0;coverage=set();max_steps=0;edges={0xf348:set(),0xf35d:set(),0xf339:set()}
 for k in range(256):
  for flags in range(4):
   s=bytearray(rng.randbytes(2048));s[0x4d0]=(s[0x4d0]&127)|(128 if flags&1 else 0);s[0x4d1]=(s[0x4d1]&127)|(128 if flags&2 else 0);ret=((0x8f4c,0,0xffff,0xc0f3)[k%4]-1)&65535;s[256+((k+1)&255)]=ret&255;s[256+((k+2)&255)]=ret>>8
   c=bytes.fromhex('f328')+bytes((rng.randrange(256),k,rng.randrange(256),k,k,0xa7));rt=bytes((30,0,16,k%8,0,0,0xba,0xdd,0xf0,0x0d,0xd5,1));before=(bytes(s),c,b'\xb6'*134638,rt);want=model(s,c)
   if private:
    from recovery_bank_loader_target_choice_oracle import ControllerBus,REGIONS,RETURNS
    from recovery_test_active_command0e_rom import Ricoh
    b=ControllerBus(rom);b.map_bank(k%8);b[:2048]=s;b.events.clear();m=Ricoh(memory=b);m.pc=0xf328;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for steps in range(512):
     pc=m.pc;coverage.add(pc);op=b[pc];m.step()
     if pc in edges:edges[pc].add(m.pc)
     if op==0x60 and m.pc not in RETURNS[152] or not any(lo<=m.pc<hi for lo,hi in REGIONS[152]):break
    else:raise AssertionError('original bound')
    max_steps=max(max_steps,steps+1);assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events)==want,(k,flags)
   n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==want[:2] and n.events==want[2] and not n.reads and after[3]==rt;assert after[2]==b'\0\0'+b'\xb6'*134636;cases+=1
  for at,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0')):
   n.restore(before);n.mem.w_block(at,v);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 # Every wrong entry is rejected before scratch copying or visible mutation.
 for pc in range(65536):
  if pc==0xf328:continue
  n.restore(before);n.mem.w16(CTX,pc);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 # Top-level callers inside the owned routine are explicitly outside this ABI.
 for target in range(0xf328,0xf36c):
  n.restore(before);sp=c[6];ret=target-1;n.mem.w8(RAM+256+((sp+1)&255),ret&255);n.mem.w8(RAM+256+((sp+2)&255),ret>>8);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 n.m.cleanup()
 source=(PORT/'src/recovery_bank_loader_target_choice_region.s').read_text();assert '#512,a4' in source;n=Native(assemble(source.replace('#512,a4','#8,a4')),resource);n.restore(before);assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;n.m.cleanup();guards+=1
 if private:
  assert len(coverage)==34 and edges=={0xf348:{0xf34a,0xf369},0xf35d:{0xf35f,0xf364},0xf339:{0xf33b,0xf33f}},edges
 print('PASS F328',cases,'rawP/SP/X/player-activity cases;',guards,'inert guards; original PCs',len(coverage),'max original steps',max_steps,'conditional outcomes',sum(map(len,edges.values())),'private' if private else 'public')
if __name__=='__main__':main()
