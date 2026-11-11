"""Private continuous original FE24 to interstitial, stage, and 240 movement frames.
Only original execution selects entries. No captured states or native feedback.
"""
import hashlib,collections
from recovery_object_region_test import ROOT,Native,compare_original
from recovery_scene_continue_oracle import ControllerBus,SHA,select_boundary
from recovery_test_active_command0e_rom import Ricoh
rom=(ROOT/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
bus=ControllerBus(rom);bus.inputs=(0,0);bus.pos=[0,0];bus[:2048]=[0xa5]*2048;bus.events.clear()
m=Ricoh(memory=bus);m.pc,m.a,m.x,m.y,m.p,m.sp=0xfe24,0x17,0x33,0,0x24,0xfd
nmi=ins=menu=chars=event=0
while m.pc!=0xff53:
 if m.pc==0xa025:menu+=1
 if m.pc==0xa06c:chars+=1
 v=(16 if chars<3 else 0 if chars<5 else 16) if chars else 16 if menu else 0
 status,index,targets=select_boundary(m,bus,event);assert status>=0,(hex(m.pc),status)
 if not status:event=1;continue
 if event:m.nmi();nmi+=1
 if index in (9,21,31,50,77):bus.inputs=(v,0);bus.pos=[0,0]
 for _ in range(50000):
  m.step();ins+=1
  if m.pc in targets:break
 else:raise AssertionError('prefix bound')
 event=0;bus.events.clear();bus.dma.clear()

from collections import deque
import struct,json,sys
from pathlib import Path
from recovery_stage_scroll_test import log_read
from recovery_stage_map_test import RANGES
root=Path(sys.argv[1]);assert root.is_dir() and not any(root.iterdir()),'require new empty private output directory';frames=0;recent=deque(maxlen=24)
for _ in range(4000000):
 pc=m.pc
 if pc in (0xfe8d,0xfe90) and not any(bus[0x80+4*i] in (4,8) for i in range(4)):
  m.nmi();nmi+=1;continue
 if pc==0xfecd:bus.inputs=((1 if frames else (16 if nmi>300 and nmi%120<30 else 0)),0);bus.pos=[0,0]
 if pc==0xc77b:frames+=1
 recent.append(dict(pc=hex(pc),sp=m.sp,p=m.p))
 if pc==0xdf97 and frames>=64:
  before=(bytes(bus[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7),bytes(bus.mapper.snapshot()[:4])+bytes.fromhex('0000baddf00dd501'))
  bus.events.clear();trace=[]
  for step in range(20000):
   trace.append(dict(pc=hex(m.pc),sp=m.sp,p=m.p));log_read(m,bus);m.step()
   if not any(a<=m.pc<z for a,z in RANGES):break
  after=struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)
  assert m.pc==0xdaad,(nmi,frames,after.hex())
  for suffix,data in zip(('ram','context','runtime'),before):(root/('map_return.'+suffix+'.bin')).write_bytes(data)
  result=dict(nmi=nmi,frame=frames-1,before=before[1].hex(),after=after.hex(),preceding=list(recent),map_instructions=trace,effects=bus.events)
  (root/'map_return_trace.json').write_text(json.dumps(result,indent=2));print('ORIGINAL ONLY',nmi,frames-1,before[1].hex(),'->',after.hex(),'steps',len(trace));break
 m.step();ins+=1;bus.events.clear();bus.dma.clear()
else:raise AssertionError('original route bound')
