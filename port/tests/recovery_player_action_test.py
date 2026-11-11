"""Static fixed-bank player action region differential checks, never runtime trace replay."""
import hashlib,os,struct,subprocess,tempfile,sys
from pathlib import Path
from recovery_bank_loader_dialogue_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME
from recovery_stage_map_test import context,log_read,genuine_entry
sys.path.insert(0,str(PORT/'tools'))
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
RANGES=((0xc940,0xcba2),(0xcbac,0xcc9f),(0xd50f,0xd5fc),(0xd604,0xd657))
ENTRIES=(51520, 51526, 51532, 51563, 51664, 51743, 51761, 51790, 51874, 51910, 51930, 51940, 52080, 52083, 52088, 52110, 52127, 52140, 52147, 52172, 52185, 52233, 52248, 52257, 52320, 52333, 54543, 54544, 54617, 54650, 54659, 54664, 54682, 54693, 54704, 54712, 54723, 54734, 54738, 54788, 54831)
RETURN_SITES=tuple(e for e in ENTRIES if e not in (0xc940,0xcaa2,0xcac6,0xcbac,0xd50f,0xd510,0xd559,0xd59a,0xd5d2,0xd604))

def assemble():
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'frame.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_player_action_region.s')],check=True);return out.read_bytes()
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
  for k in range(256):
   r=bytearray(2048);r[0x100+((k+1)&255)]=0x34;r[0x100+((k+2)&255)]=0x12
   c=struct.pack('>H6B',0xd50f,73,211,55,k,k,0xa7);n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638)
   assert n.run()==1
   assert n.snapshot()[:2]==(bytes(r),struct.pack('>H6B',0x1235,73,211,55,k,(k+2)&255,0xa7))
  for a,v in ((RUNTIME,b'\x1f'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\x00')):n.reject(a,v)
  # Genuine pointer opcode at D58A, entered via real JSR continuation D588.
  for address in (0x2000,0x4016,0x7fff):
   r=bytearray(2048);r[0]=address&255;r[1]=address>>8
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,struct.pack('>H6B',0xd588,0,0,0,0,255,0xa7));before=n.snapshot()
   assert n.run()==0xffffffff and n.snapshot()==before and not n.events
  for address in (0x0800,0x1fff,0x8000,0xffff):
   r=bytearray(2048);r[0]=address&255;r[1]=address>>8
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,struct.pack('>H6B',0xd588,0,0,0,0,255,0xa7));assert n.run()==1
  r=bytearray(2048);r[0x100:0x200]=bytes([0xcd,0xd5])*128
  n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,struct.pack('>H6B',0xd5ce,0,0,0,0,255,0xa7));before=n.snapshot()
  assert n.run()==0xffffffff and n.snapshot()==before and not n.events
  n.m.cleanup();print('PASS player action public nonentry sweep and 256 raw-P/SP RTS; runtime guards; USER/register/bounds/immutability');return
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 m,b,nmi=genuine_entry(rom);n=Native(code,rom[16:131088]);cases=reads=maxjournal=maxsteps=frames=0;visits={};fixtures={};coverage=set()
 for _ in range(3000000):
  if m.pc in (0xfe8d,0xfe90) and not any(b[0x80+4*i] in (4,8) for i in range(4)):m.nmi();nmi+=1;continue
  if m.pc==0xfecd:b.inputs=((1|(128 if nmi%90<30 else 0)) if frames else 0,0);b.pos=[0,0]
  if m.pc==0xc77b:
   frames+=1
   if frames==241:break
  if m.pc in ENTRIES :
   pc=m.pc;visits[hex(pc)]=visits.get(hex(pc),0)+1
   if pc not in fixtures:fixtures[pc]=(bytes(b[:2048]),context(m),b.mapper.snapshot())
   j,steps=compare(n,m,b,coverage);cases+=1;reads+=j;maxjournal=max(maxjournal,j);maxsteps=max(maxsteps,steps)
  else:m.step()
  b.events.clear();b.dma.clear()
 else:raise AssertionError('stage sequence bound')
 assert frames==241 and visits.get('0xc940',0)>0
 print('PASS genuine player action entries',cases,'resources',reads,'max journal',maxjournal,'max original steps',maxsteps,'NMI',nmi,'frames',frames-1,'visits',visits,flush=True)
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
 for address,y in ((0x0800,0),(0x1fff,0),(0x8000,0),(0xffff,0),(0xff01,255),(0x7fff,1)):
  for bank in range(8):
   r=bytearray(2048);r[0]=address&255;r[1]=address>>8;r[0x4c]=y;r[0x100:0x103]=bytes([0,0x34,0x12]);b[:2048]=r
   b.mapper.prg=bank;b.map_bank(bank);m.pc=0xd588;m.a=m.x=m.y=m.p=0;m.sp=255
   compare(n,m,b,coverage);synthetic+=1
 n.m.cleanup();print('PASS synthetic raw-flag/stack variants',synthetic,'instruction PCs covered',len(coverage))
if __name__=='__main__':main()
