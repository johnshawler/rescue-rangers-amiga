"""Private genuine-entry map-region differential test; not whole-native reachability.
All admitted fixtures come from a continuous original FE24 run. Fixtures are
host test inputs only. The native module never consumes trace/state files.
"""
import hashlib,os,struct,subprocess,tempfile,sys
from pathlib import Path
from recovery_bank_loader_dialogue_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME
ENTRIES=(0xe179,0xe17c,0xe1d3,0xe1e4,0xe1e7,0xe1ea,0xdbec,0xdc5c,0xdc5f,0xdf97,0xe028)
RANGES=((0xc235,0xc247),(0xdbec,0xdd0a),(0xdf8a,0xe047),(0xe06b,0xe096),(0xe179,0xe1eb))
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def assemble():
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'map.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_stage_map_region.s')],check=True);return out.read_bytes()
def context(m):return struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)
def log_read(m,b):
 op,mode=m.disassemble[b[m.pc]]
 if op not in ('LDA','LDX','LDY','AND','ORA','EOR','ADC','SBC','CMP','CPX','CPY'):return
 pc=m.pc;a=None
 if mode in ('abs','abx','aby'):
  a=(b[pc+1]|b[pc+2]<<8)+(m.x if mode=='abx' else m.y if mode=='aby' else 0);a&=65535
 elif mode=='iny':
  z=b[pc+1];a=((b[z]|b[(z+1)&255]<<8)+m.y)&65535
 if a is not None and a>=32768:b.events.append(('resource',a,b[a],0))
def genuine_entry(rom):
 from recovery_scene_continue_oracle import ControllerBus,select_boundary
 from recovery_test_active_command0e_rom import Ricoh
 b=ControllerBus(rom);b.inputs=(0,0);b.pos=[0,0];b[:2048]=[0xa5]*2048;b.events.clear()
 m=Ricoh(memory=b);m.pc,m.a,m.x,m.y,m.p,m.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 nmi=menu=chars=event=0
 while m.pc!=0xff53:
  if m.pc==0xa025:menu+=1
  if m.pc==0xa06c:chars+=1
  v=(16 if chars<3 else 0 if chars<5 else 16) if chars else 16 if menu else 0
  s,i,targets=select_boundary(m,b,event);assert s>=0
  if not s:event=1;continue
  if event:m.nmi();nmi+=1
  if i in (9,21,31,50,77):b.inputs=(v,0);b.pos=[0,0]
  for _ in range(50000):
   m.step()
   if m.pc in targets:break
  else:raise AssertionError('prefix bound')
  event=0;b.events.clear();b.dma.clear()
 for step in range(2000000):
  if m.pc==0xe179:return m,b,nmi
  if m.pc in (0xfe8d,0xfe90) and not any(b[0x80+4*i] in (4,8) for i in range(4)):
   m.nmi();nmi+=1;continue
  if m.pc==0xfecd:b.inputs=(16 if nmi>300 and nmi%120<30 else 0,0);b.pos=[0,0]
  m.step();b.events.clear();b.dma.clear()
 raise AssertionError('genuine route bound')
def main():
 code=assemble();private='--rom' in sys.argv
 if not private:
  n=Native(code,bytes(131072));n.mem.w_block(RUNTIME,bytes.fromhex('1e0000040000baddf00dd501'))
  for pc in range(65536):
   if pc in ENTRIES:continue
   n.mem.w16(CTX,pc);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads
  # Every raw flag byte and stack wrap, preserving real JSR writes.
  for k in range(256):
   r=bytes(2048);c=struct.pack('>H6B',0xe1e4,73,211,55,k,k,0xa7)
   n.mem.w_block(RAM,r);n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638)
   assert n.run()==1
   want=bytearray(r);want[256+k]=0xe1;want[256+((k-1)&255)]=0xe6
   assert n.snapshot()[:2]==(bytes(want),struct.pack('>H6B',0x8040,73,211,55,k,(k-2)&255,0xa7))
  # Unsupported IO via genuine addressing logic must reject atomically.
  n.mem.w_block(RAM,bytes(2048));n.mem.w16(CTX,0xe028)
  n.mem.w8(RAM+0x27,0x20)
  before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events
  # Mapper/control/magic/serial guards never mutate caller state.
  n.mem.w16(CTX,0xe179)
  for a,v in ((RUNTIME,b'\x1f'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\x00')):
   n.reject(a,v)
  n.m.cleanup();print('PASS map: 65525 invalid-PC guards, 256 raw-flag/stack cases, IO atomic rejection, five runtime guards; assembly/user-mode/register/bounds/immutability checks');return
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 m,b,nmi=genuine_entry(rom);n=Native(code,rom[16:131088]);cases=reads=maxjournal=0;visits={};dbec=0
 for _ in range(1000000):
  if m.pc in ENTRIES:
   pc=m.pc;visits[hex(pc)]=visits.get(hex(pc),0)+1
   n.mem.w_block(RAM,bytes(b[:2048]));n.mem.w_block(CTX,context(m));n.mem.w_block(JOURNAL,b'\xb6'*134638)
   n.mem.w_block(RUNTIME,bytes(b.mapper.snapshot()[:4])+bytes.fromhex('0000baddf00dd501'))
   b.events.clear();semantic=[]
   for step in range(200000):
    if m.pc==0xdbec:dbec+=1
    log_read(m,b);m.step()
    if not any(lo<=m.pc<hi for lo,hi in RANGES):break
   else:raise AssertionError('region bound')
   want=context(m);assert n.run()==1,('native rejection',hex(pc));got=n.snapshot()
   assert got[0]==bytes(b[:2048]),('RAM',hex(pc),[(hex(i),x,y) for i,(x,y) in enumerate(zip(got[0],b[:2048])) if x!=y][:10])
   assert got[1]==want,('context',hex(pc),got[1].hex(),want.hex())
   events=[('resource',*e[1:]) if e[0]=='mapper' else e for e in n.events]
   assert events==b.events,('effects',hex(pc),events[:10],b.events[:10])
   for e in b.events:
    if e[0]=='resource':semantic.append(e[1]+65536 if e[1]>=49152 else b.mapper.bank*16384+e[1]-32768)
   assert n.reads==semantic*2,('semantic resources',hex(pc),n.reads[:10],semantic[:10])
   j=int.from_bytes(got[2][:2],'big');assert j==len(semantic);assert got[2][2+j*4:]==b'\xb6'*(134636-j*4)
   cases+=1;reads+=j;maxjournal=max(maxjournal,j)
   if pc==0xe1ea:break
  else:m.step()
 else:raise AssertionError('map sequence bound')
 n.m.cleanup();print('PASS genuine map entries',cases,'DBEC calls',dbec,'resources',reads,'max journal',maxjournal,'NMI',nmi,'exit',hex(m.pc),'visits',visits)
if __name__=='__main__':main()
