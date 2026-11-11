"""Static fixed-bank stage scroll region differential checks, never runtime trace replay."""
import hashlib,os,struct,subprocess,tempfile,sys
from pathlib import Path
from recovery_bank_loader_dialogue_harness import Native as BaseNative,PORT,RAM,CTX,JOURNAL,RUNTIME,CODE,STACK
from recovery_stage_map_test import context,log_read,genuine_entry
sys.path.insert(0,str(PORT/'tools'))
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
RANGES=((54947, 56173), (56175, 56300), (56602, 57186))
ENTRIES=(54947, 55007, 55056, 55429, 55441, 55467, 55479, 55497, 55511, 55556, 55570, 55732, 55756, 55766, 55798, 55844, 55888, 55924, 55981, 55983, 56007, 56061, 56084, 56144, 56175, 56208, 56602, 56653, 56659, 56698, 56775, 56909, 56929, 56970, 57000, 57011, 57016, 57017, 57034, 57037, 57070, 57089, 57092)
RETURN_SITES=(55007, 55056, 55429, 55441, 55467, 55479, 55497, 55511, 55556, 55570, 55844, 55924, 55981, 56007, 56084, 56653, 56659, 56698, 56775, 56909, 56929, 57011, 57016, 57034, 57037, 57089, 57092)

class Native(BaseNative):
 """Retain every base guard and tighten stack to the documented minimum."""
 def __init__(self,code,resource):
  assert CODE+len(code)<RAM-16,'code/data overlap requires relocated harness'
  super().__init__(code,resource)
  base=self.trace
  def trace(mode,width,addr,value):
   if STACK-4096<=addr<STACK:assert addr>=STACK-2304,'minimum preflight stack exceeded'
   if RUNTIME<=addr<RUNTIME+12:assert mode=='R','runtime must be immutable'
   base(mode,width,addr,value)
  self.minimum_trace=trace;self.mem.set_trace_func(trace)

def assemble(source=None):
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'frame.bin'
  path=PORT/'src/recovery_stage_scroll_region.s'
  if source is not None:path=Path(td)/'source.s';path.write_text(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(path)],check=True);return out.read_bytes()
def compare(n,m,b,coverage=None):
 pc=m.pc;n.mem.w_block(RAM,bytes(b[:2048]));n.mem.w_block(CTX,context(m));n.mem.w_block(JOURNAL,b'\xb6'*134638)
 n.mem.w_block(RUNTIME,bytes(b.mapper.snapshot()[:4])+bytes.fromhex('0000baddf00dd501'));b.events.clear()
 for step in range(20000):
  if coverage is not None:coverage.add(m.pc)
  indirect=b[m.pc]==0x6c;outer_rts=b[m.pc]==0x60;log_read(m,b);m.step()
  if indirect or (outer_rts and m.pc not in RETURN_SITES) or not any(lo<=m.pc<hi for lo,hi in RANGES):break
 else:raise AssertionError('reference region bound')
 want=context(m);assert n.run()==1,('native rejection',hex(pc));got=n.snapshot()
 assert got[0]==bytes(b[:2048]),('RAM',hex(pc),[(hex(i),x,y) for i,(x,y) in enumerate(zip(got[0],b[:2048])) if x!=y][:10])
 assert got[1]==want,('context',hex(pc),got[1].hex(),want.hex())
 events=[('resource',*e[1:]) if e[0]=='mapper' else e for e in n.events]
 assert events==b.events,('effects',hex(pc),events[:12],b.events[:12])
 semantic=[e[1]+65536 if e[1]>=49152 else b.mapper.bank*16384+e[1]-32768 for e in b.events if e[0]=='resource']
 assert n.reads==semantic*2,('semantic resources',hex(pc),n.reads[:10],semantic[:10])
 j=int.from_bytes(got[2][:2],'big');assert j==len(semantic);assert got[2][2+j*4:]==b'\xb6'*(134636-j*4)
 return j,step+1

def main():
 code=assemble();private='--rom' in sys.argv
 if not private:
  n=Native(code,bytes(131072));n.mem.w_block(RUNTIME,bytes.fromhex('1e0000060000baddf00dd501'))
  for pc in (() if '--quick' in sys.argv else range(65536)):
   if pc in ENTRIES:continue
   n.mem.w16(CTX,pc);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads
  # Synthetic raw flags, stack wrapping and exact inert RTS.
  for k in range(256):
   r=bytearray(2048);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12
   c=struct.pack('>H6B',0xd9b4,73,211,55,k,k,0xa7)
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638)
   assert n.run()==1
   assert n.snapshot()[:2]==(bytes(r),struct.pack('>H6B',0x1235,73,211,55,k,(k+2)&255,0xa7))
  # D9F6 original branch computes indirect pointer read. Reject IO/holes, admit mirrors/PRG.
  for address in (0x2000,0x4016,0x7fff,0x0800,0x1fff,0x8000,0xffff):
   r=bytearray(2048);r[0x34]=address&255;r[0x35]=address>>8;r[0x22]=255;r[0x100:0x103]=bytes([0,0x34,0x12])
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,struct.pack('>H6B',0xd9f6,0,0,0,0,255,0xa7));before=n.snapshot()
   if 0x2000<=address<0x8000:assert n.run()==0xffffffff and n.snapshot()==before and not n.events
   else:assert n.run()==1
  for a,v in ((RUNTIME,b'\x1f'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\x00')):n.reject(a,v)
  n.m.cleanup()
  # Shrunk compile-time budgets exercise the same reject paths without 20k-step test cost.
  source=(PORT/'src/recovery_stage_scroll_region.s').read_text()
  for limited,entry in ((source.replace('#20000,a4','#1,a4'),0xd6a3),(source.replace('#15000,(a2)','#0,(a2)'),0xd9f6)):
   n=Native(assemble(limited),bytes(131072));n.mem.w_block(RUNTIME,bytes.fromhex('1e0000060000baddf00dd501'))
   r=bytearray(2048);r[0x35]=0x80;n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,struct.pack('>H6B',entry,0,0,0,0,255,0xa7));before=n.snapshot()
   assert n.run()==0xffffffff and n.snapshot()==before and not n.events
   n.m.cleanup()
  print('PASS stage scroll public',0 if '--quick' in sys.argv else 65536-len(ENTRIES),'invalid PCs; 256 raw-P/SP; pointer/mirror/budget/runtime guards; USER/register/bounds/immutability');return
 from recovery_stage_scroll_generate import generate
 assert generate()==(PORT/'src/recovery_stage_scroll_region.s').read_text(),'generator exactness'
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 if '--fixture' in sys.argv:
  from recovery_scene_continue_oracle import ControllerBus
  from recovery_test_active_command0e_rom import Ricoh
  p=Path(sys.argv[sys.argv.index('--fixture')+1]);b=ControllerBus(rom);m=Ricoh(memory=b)
  b[:2048]=p.with_suffix('.ram.bin').read_bytes();c=p.with_suffix('.context.bin').read_bytes();rt=p.with_suffix('.runtime.bin').read_bytes()
  m.pc,m.a,m.x,m.y,m.p,m.sp,_=struct.unpack('>H6B',c)
  b.mapper.control,b.mapper.chr0,b.mapper.chr1,b.mapper.prg=rt[:4];b.map_bank(b.mapper.bank)
  n=Native(code,rom[16:131088]);result=compare(n,m,b);n.m.cleanup()
  print('PASS genuine fixture',result,'exit context',context(m).hex());return
 frame_limit=int(sys.argv[sys.argv.index('--frames')+1]) if '--frames' in sys.argv else 240
 pad=int(sys.argv[sys.argv.index('--pad')+1],0) if '--pad' in sys.argv else 1
 m,b,nmi=genuine_entry(rom);n=Native(code,rom[16:131088]);cases=reads=maxjournal=maxsteps=frames=0;visits={};fixtures={};coverage=set();scroll_positions=set()
 for _ in range(max(3000000,frame_limit*16000)):
  if m.pc in (0xfe8d,0xfe90) and not any(b[0x80+4*i] in (4,8) for i in range(4)):m.nmi();nmi+=1;continue
  if m.pc==0xfecd:b.inputs=((pad|(128 if nmi%90<30 else 0)) if frames else 0,0);b.pos=[0,0]
  if m.pc==0xc77b:
   scroll_positions.add((b[0xfd]<<8)|b[0xfc]);frames+=1
   if frames==frame_limit+1:break
  if m.pc in ENTRIES :
   pc=m.pc;visits[hex(pc)]=visits.get(hex(pc),0)+1
   if pc not in fixtures:fixtures[pc]=(bytes(b[:2048]),context(m),b.mapper.snapshot())
   j,steps=compare(n,m,b,coverage);cases+=1;reads+=j;maxjournal=max(maxjournal,j);maxsteps=max(maxsteps,steps)
  else:m.step()
  b.events.clear();b.dma.clear()
 else:raise AssertionError('stage sequence bound')
 assert frames==frame_limit+1 and visits.get('0xd6a3',0)>0
 print('PASS genuine stage scroll entries',cases,'resources',reads,'max journal',maxjournal,'max original steps',maxsteps,'NMI',nmi,'frames',frames-1,'visits',visits,'camera range',(min(scroll_positions),max(scroll_positions)),flush=True)
 if '--route-only' in sys.argv:n.m.cleanup();return
 synthetic=0
 for ram,ctx,mapper in fixtures.values():
  b.mapper.control,b.mapper.chr0,b.mapper.chr1,b.mapper.prg,bits=mapper;b.mapper.bits[:]=bits;b.map_bank(b.mapper.bank)
  for k in range(256):
   r=bytearray(ram);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12;b[:2048]=r
   m.pc,m.a,m.x,m.y,m.p,m.sp,_=struct.unpack('>H6B',ctx);m.p=k;m.sp=k
   compare(n,m,b,coverage);synthetic+=1
 # Additional clearly synthetic instruction-aligned entries, no route claim.
 for entry in ENTRIES:
  for k in range(256):
   r=bytearray(2048);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12
   b[:2048]=r;m.pc=entry;m.a=k;m.x=k;m.y=k;m.p=k;m.sp=k
   compare(n,m,b,coverage);synthetic+=1
 # Synthetic indirect resources cover every mapped bank, mirrors and 16-bit wrap.
 for address,y in ((0x0800,0),(0x1fff,0),(0x8000,0),(0xffff,0),(0xff01,255),(0x7fff,1)):
  for bank in range(8):
   r=bytearray(2048);r[0x34]=address&255;r[0x35]=address>>8;r[0x22]=(y-1)&255;r[0x100:0x103]=bytes([0,0x34,0x12]);b[:2048]=r
   b.mapper.prg=bank;b.map_bank(bank);m.pc=0xd9f6;m.a=m.x=m.y=m.p=0;m.sp=255
   compare(n,m,b,coverage);synthetic+=1
 # Synthetic camera page, direction, player-count and raw status branches.
 for ram,ctx,mapper in fixtures.values():
  b.mapper.control,b.mapper.chr0,b.mapper.chr1,b.mapper.prg,bits=mapper;b.mapper.bits[:]=bits;b.map_bank(b.mapper.bank)
  for field in (0x22,0x23,0x28,0x29,0x2f,0x50,0xfa,0xfb,0xfc,0xfd):
   for value in (0,1,2,15,16,127,128,239,240,255):
    r=bytearray(ram);r[field]=value;b[:2048]=r
    m.pc,m.a,m.x,m.y,m.p,m.sp,_=struct.unpack('>H6B',ctx)
    compare(n,m,b,coverage);synthetic+=1
 n.m.cleanup();print('PASS synthetic raw-flag/stack variants',synthetic,'instruction PCs covered',len(coverage))
if __name__=='__main__':main()
