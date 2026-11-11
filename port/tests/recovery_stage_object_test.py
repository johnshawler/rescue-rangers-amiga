"""Standalone bank4 object region differential checks. Private ROM is optional.
Genuine fixtures are reached original-first; never repair native state.
"""
import hashlib,os,struct,subprocess,tempfile,sys,random
from pathlib import Path
from recovery_bank_loader_dialogue_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME
from recovery_stage_map_test import context,log_read,genuine_entry
ENTRIES=(0x8040,0x8090)
RANGES=((0x8040,0x8088),(0x8090,0x8193),(0xf31d,0xf328))
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def assemble():
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'object.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_stage_object_region.s')],check=True);return out.read_bytes()
def compare(n,m,b,coverage=None):
 pc=m.pc
 n.mem.w_block(RAM,bytes(b[:2048]));n.mem.w_block(CTX,context(m));n.mem.w_block(JOURNAL,b'\xb6'*134638)
 n.mem.w_block(RUNTIME,bytes(b.mapper.snapshot()[:4])+bytes.fromhex('0000baddf00dd501'))
 b.events.clear()
 for step in range(20000):
  if coverage is not None:coverage.add(m.pc)
  log_read(m,b);m.step()
  if not any(lo<=m.pc<hi for lo,hi in RANGES):break
 else:raise AssertionError('reference region bound')
 want=context(m);assert n.run()==1,('native rejection',hex(pc));got=n.snapshot()
 assert got[0]==bytes(b[:2048]),('RAM',hex(pc),[(hex(i),x,y) for i,(x,y) in enumerate(zip(got[0],b[:2048])) if x!=y][:10])
 assert got[1]==want,('context',hex(pc),got[1].hex(),want.hex())
 events=[('resource',*e[1:]) if e[0]=='mapper' else e for e in n.events]
 assert events==b.events,('effects',hex(pc),events[:10],b.events[:10])
 semantic=[e[1]+65536 if e[1]>=49152 else b.mapper.bank*16384+e[1]-32768 for e in b.events if e[0]=='resource']
 assert n.reads==semantic*2,('semantic resources',hex(pc),n.reads[:10],semantic[:10])
 j=int.from_bytes(got[2][:2],'big');assert j==len(semantic);assert got[2][2+j*4:]==b'\xb6'*(134636-j*4)
 return j,step+1

def main():
 code=assemble();private='--rom' in sys.argv
 if not private:
  n=Native(code,bytes(131072));n.mem.w_block(RUNTIME,bytes.fromhex('1e0000040000baddf00dd501'))
  for pc in (() if "--quick" in sys.argv else range(65536)):
   if pc in ENTRIES:continue
   n.mem.w16(CTX,pc);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads
   if pc%16384==0:print('invalid PC sweep',pc,flush=True)
  # 8090 fast return with each raw flag and every possible wrapped SP.
  for k in range(256):
   r=bytearray(2048);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12
   c=struct.pack('>H6B',0x8090,73,211,55,k,k,0xa7)
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638)
   assert n.run()==1
   assert n.snapshot()[:2]==(bytes(r),struct.pack('>H6B',0x1235,0,211,55,(k&0x7d)|2,(k+2)&255,0xa7))
  # Invalid pointer reaches IO and rejects before publishing scratch writes.
  n.mem.w_block(RAM,bytes(2048));n.mem.w16(CTX,0x8040);n.mem.w8(RAM+0x7d,0x20)
  before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events
  n.mem.w16(CTX,0x8090)
  for a,v in ((RUNTIME,b'\x1f'),(RUNTIME+3,b'\x03'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\x00')):n.reject(a,v)
  # Malformed all-zero object tables cause an endless original scan. Native
  # budget must reject atomically despite scratch JSR/array writes and reads.
  r=bytearray(2048);r[0x2f]=2;r[0x73]=r[0x75]=r[0x77]=r[0x79]=r[0x7b]=0x80
  n.mem.w_block(RAM,bytes(r));n.mem.w16(CTX,0x8090);before=n.snapshot()
  assert n.run()==0xffffffff and n.snapshot()==before and not n.events
  n.m.cleanup();print('PASS object public:', 'invalid PC sweep skipped;' if '--quick' in sys.argv else '65534 invalid PCs;', ' 256 raw flags/stack wraps, IO/runtime guards, bounded inert malformed scan; USER/register/full-width bounds/immutability');return
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 m,b,nmi=genuine_entry(rom);n=Native(code,rom[16:131088]);cases=reads=maxjournal=maxsteps=0;visits={};fixtures=[];coverage=set()
 for _ in range(1000000):
  if m.pc in ENTRIES and b.mapper.bank==4:
   pc=m.pc;visits[hex(pc)]=visits.get(hex(pc),0)+1
   fixtures.append((bytes(b[:2048]),context(m)))
   j,steps=compare(n,m,b,coverage);cases+=1;reads+=j;maxjournal=max(maxjournal,j);maxsteps=max(maxsteps,steps)
  else:m.step()
  if m.pc==0xe106:break
 else:raise AssertionError('stage sequence bound')
 assert visits.get('0x8040',0)>0 and visits.get('0x8090',0)>0
 print('PASS genuine object entries',cases,'resources',reads,'max journal',maxjournal,'max original steps',maxsteps,'NMI',nmi,'exit',hex(m.pc),'visits',visits)
 # Adversarial fixtures are explicitly synthetic variants, separate from the
 # genuine route evidence. Original semantics determine every expected result.
 synthetic=0
 for ram,ctx in fixtures:
  for k in range(256):
   r=bytearray(ram);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12
   b[:2048]=r
   m.pc,m.a,m.x,m.y,m.p,m.sp,_=struct.unpack('>H6B',ctx);m.p=k;m.sp=k
   compare(n,m,b,coverage);synthetic+=1
 n.m.cleanup();print('PASS synthetic raw-flag/stack variants',synthetic,'instruction PCs covered',len(coverage))
if __name__=='__main__':main()
