"""Static bank6 frame region differential checks, never runtime trace replay."""
import hashlib,os,struct,subprocess,tempfile,sys
from pathlib import Path
from recovery_bank_loader_dialogue_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME
from recovery_stage_map_test import context,log_read,genuine_entry
sys.path.insert(0,str(PORT/'tools'))
from recovery_player_frame_generate import ENTRIES,RANGES,SHA
RETURN_SITES=(0x801f,0x8029,0x8033,0x8050,0x8bd6,0x8c22,0x8e18,0x8e32,0x8f4c,0x8f7c,0x8f83,0x8f92,0x8f9a)

def assemble():
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'frame.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_player_frame_region.s')],check=True);return out.read_bytes()
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
  # Every raw flag byte and wrapped stack on the inactive dispatcher.
  for k in range(256):
   r=bytearray(2048);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12
   c=struct.pack('>H6B',0x8000,73,211,55,k,k,0xa7);n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638)
   assert n.run()==1;r[0x4d]=16
   assert n.snapshot()[:2]==(bytes(r),struct.pack('>H6B',0x1235,0,16,55,(k&0x7c)|3,(k+2)&255,0xa7))
  for a,v in ((RUNTIME,b'\x1f'),(RUNTIME+3,b'\x04'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\x00')):n.reject(a,v)
  # Deliberately cyclic synthetic RTS stack exhausts instruction budget inertly.
  r=bytearray(2048);r[0x100:0x200]=bytes([0x21,0x8c])*128;r[0x4d2]=1;r[0x4df]=0x80;r[0x40f]=0x80;r[0x4ef]=0x10;r[0x42f]=0x22
  n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,struct.pack('>H6B',0x8c22,0,2,0,0,255,0xa7));before=n.snapshot()
  assert n.run()==0xffffffff and n.snapshot()==before and not n.events
  n.m.cleanup()
  # A table target outside translated code is an honest external exit, not fetched.
  for target in (0,0x2000,0x7fff,0xffff):
   resource=bytearray(131072);resource[6*16384+0xa7]=target&255;resource[6*16384+0x10c]=target>>8
   t=Native(code,resource);r=bytearray(2048);r[0x4d2]=0x80;t.mem.w_block(RAM,bytes(r));t.mem.w_block(CTX,struct.pack('>H6B',0x8000,0,0,0,0,0,0xa7));t.mem.w_block(RUNTIME,bytes.fromhex('1e0000060000baddf00dd501'))
   assert t.run()==1 and t.mem.r16(CTX)==target and t.mem.r8(CTX+6)==254
   assert t.reads==[6*16384+0xa7,6*16384+0x10c]*2;t.m.cleanup()
  print('PASS frame public: invalid-PC sweep', '--quick' not in sys.argv,'256 raw flags/SP; honest indirect targets; runtime guards; inert cyclic-budget; USER/register/bounds/immutability');return
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 m,b,nmi=genuine_entry(rom);n=Native(code,rom[16:131088]);cases=reads=maxjournal=maxsteps=frames=0;visits={};fixtures={};coverage=set()
 for _ in range(3000000):
  if m.pc in (0xfe8d,0xfe90) and not any(b[0x80+4*i] in (4,8) for i in range(4)):m.nmi();nmi+=1;continue
  if m.pc==0xfecd:b.inputs=((1|(128 if nmi%90<30 else 0)) if frames else 0,0);b.pos=[0,0]
  if m.pc==0xc77b:
   frames+=1
   if frames==241:break
  if m.pc in ENTRIES and b.mapper.bank==6:
   pc=m.pc;visits[hex(pc)]=visits.get(hex(pc),0)+1
   if pc not in fixtures:fixtures[pc]=(bytes(b[:2048]),context(m),b.mapper.snapshot())
   j,steps=compare(n,m,b,coverage);cases+=1;reads+=j;maxjournal=max(maxjournal,j);maxsteps=max(maxsteps,steps)
  else:m.step()
  b.events.clear();b.dma.clear()
 else:raise AssertionError('stage sequence bound')
 assert frames==241 and visits.get('0x8000',0)==240
 print('PASS genuine frame entries',cases,'resources',reads,'max journal',maxjournal,'max original steps',maxsteps,'NMI',nmi,'frames',frames-1,'visits',visits,flush=True)
 synthetic=0
 for ram,ctx,mapper in fixtures.values():
  b.mapper.control,b.mapper.chr0,b.mapper.chr1,b.mapper.prg,bits=mapper;b.mapper.bits[:]=bits;b.map_bank(b.mapper.bank)
  for k in range(256):
   r=bytearray(ram);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12;b[:2048]=r
   m.pc,m.a,m.x,m.y,m.p,m.sp,_=struct.unpack('>H6B',ctx);m.p=k;m.sp=k
   compare(n,m,b,coverage);synthetic+=1
 n.m.cleanup();print('PASS synthetic raw-flag/stack variants',synthetic,'instruction PCs covered',len(coverage))
if __name__=='__main__':main()
