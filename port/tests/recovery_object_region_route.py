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
n=Native(rom[16:16+131072]);frames=calls=steps=reads=0;returns=collections.Counter();maxreads=0
for _ in range(4000000):
 pc=m.pc
 if pc in (0xfe8d,0xfe90) and not any(bus[0x80+4*i] in (4,8) for i in range(4)):
  m.nmi();nmi+=1;continue
 if pc==0xfecd:bus.inputs=((1|(128 if nmi%90<30 else 0)) if frames else (16 if nmi>300 and nmi%120<30 else 0),0);bus.pos=[0,0]
 if pc==0xc77b:
  frames+=1
  if frames==241:break
 if pc==0x8000 and bus.mapper.bank==5:
  a,b=compare_original(n,bus,m);steps+=a;reads+=b;maxreads=max(maxreads,b);calls+=1;returns[m.pc]+=1
  if calls<=3:print('FIRST',calls,hex(m.pc),nmi,a,b,flush=True)
 else:m.step();ins+=1
 bus.events.clear();bus.dma.clear()
else:raise AssertionError('route bound')
n.close();print('PASS continuous original-first',dict(calls=calls,object_instructions=steps,semantic_reads=reads,max_reads=maxreads,frames=frames-1,nmi=nmi,other_instructions=ins,returns={hex(k):v for k,v in returns.items()}))
