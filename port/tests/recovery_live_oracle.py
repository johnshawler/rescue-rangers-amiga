"""Independent original-only replay. Never imported by the target builder."""
import hashlib,struct
from recovery_state_menu_sfx_oracle import ControllerBus,select_boundary,log_resource,SHA
from recovery_state_menu_sfx_harness import SIZES as OLD_SIZES
SIZES=OLD_SIZES+(0,0,0,0,0,74,4382)
from recovery_test_active_command0e_rom import Ricoh

def oracle(rom,changes,max_calls,native=None,scene=False):
 if scene:
  from recovery_scene_continue_oracle import select_boundary as selector
 else:selector=select_boundary
 assert 0<max_calls<=1000000 and len(changes)<=128
 previous=(-1,-1)
 for call,phase,tick,pad in changes:
  assert 0<=call<=max_calls and phase in (0,1) and 0<=tick<=4096 and 0<=pad<=255
  assert (call,phase)>previous
  previous=(call,phase)
 completed_rtis=0
 history="live"
 change_index=0
 value=0
 assert hashlib.sha256(rom).hexdigest()==SHA
 bus=ControllerBus(rom);bus.inputs=(0,0);bus.pos=[0,0]
 bus[:2048]=[0xa5]*2048;bus.events.clear()
 ref=Ricoh(memory=bus);ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 results=[];instructions=nmis=event=menu=character=0;bus.runtime_checks=[];bus.event_ends=[]
 capture=bytearray();confirmations=[];shutdowns=[];music=[];inputs=[]
 while len(results)<max_calls:
  if ref.pc==0xa025:menu+=1
  if ref.pc==0xa06c:character+=1
  while change_index<len(changes) and tuple(changes[change_index][:2])==(len(results),event):
   assert changes[change_index][2]==completed_rtis, "input RTI timestamp"
   value=changes[change_index][3];change_index+=1
  pads=(value,0)
  status,index,target=(1,72,(0xff04,)) if ref.pc==0xa055 and event==0 else selector(ref,bus,event)
  if status==0:
   assert event==0
   if native:
    before=native.snapshot();assert native.run(event,pads)==0 and native.snapshot()==before and not native.events
   event=1;continue
  assert status==1,(hex(ref.pc),status)
  start=len(bus.events);dma_start=len(bus.dma)
  confirming=index==49 and ref.pc==0xa06c and bus[0x14]&16
  if confirming:choice=bus[0x203];table=bytes(bus[0x340:0x35e])
  if event:ref.nmi();nmis+=1
  if index in (9,21,31,50,77):bus.inputs=pads;bus.pos=[0,0];inputs.append(pads)
  for _ in range(50000):
   log_resource(ref,bus,index);ref.step();instructions+=1
   if ref.pc in target:break
  else:raise AssertionError('Original timeout')
  if confirming:
   want=table if choice==40 else b''.join(table[i:i+2][::-1] for i in range(0,30,2))
   assert bytes(bus[0x340:0x35e])==want
   if choice==136:assert [bus[a] for a in (0x5a2,0x5a4,0x5a6,0x5a8)]==[0x8d,0x8a,0x95,0x8e]
   confirmations.append(dict(cursor_x=choice,selection='original' if choice==40 else 'alternate',table_sha256=hashlib.sha256(want).hexdigest()))
  effects=[e for e in bus.events[start:] if e[0]!='ram'];expected=b''
  if SIZES[index]:
   expected=struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',e[1],e[2],2 if index==36 and e[0]=='ppu' and e[3]==0 else e[3]) for e in effects)
   capture+=struct.pack('>H',index)+expected
   if index in (6,11,40,48):
    assert len(bus.dma)==dma_start+1
    offset={6:42,11:198,40:238,48:134382}[index]
    expected+=bytes(offset-len(expected))+bus.dma[-1];capture+=bus.dma[-1]
   expected+=bytes(SIZES[index]-len(expected))
  else:
   assert not effects;capture+=struct.pack('>HH',index,0)
  ctx=struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,(ref.p&0xef)|0x20,ref.sp,0xa7)
  results.append((index,1,ctx,bytes(bus[:2048]),expected,pads,event))
  bus.runtime_checks.append(bytes(bus.mapper.snapshot()[:4])+bytes(2)+struct.pack('>HHH',index,65535 if index==48 else SIZES[index],0xd501))
  bus.event_ends.append(len(bus.events))
  if index==69:shutdowns.append(len(results))
  if index==51:music.append(len(results))
  if native:
   assert native.run(event,pads)==1
   actual=native.snapshot()
   assert actual[0]==bytes(bus[:2048]) and actual[1]==ctx
   assert native.events==bus.events[start:], ('ordered effects',index)
   assert actual[3]==bus.runtime_checks[-1]
   if expected:
    n=2+4*struct.unpack_from('>H',expected)[0]
    assert actual[2][:n]==expected[:n]
    if index in (6,11,40,48):
     off={6:42,11:198,40:238,48:134382}[index]
     assert actual[2][off:off+256]==expected[off:off+256]
  if index in (8,20,42):completed_rtis+=1
  event=0
  if ref.pc==(0xff53 if scene else 0xc5f8):break
 assert change_index==len(changes)
 assert len(results)==max_calls
 bus.capture=bytes(capture);bus.summary=dict(history=history,calls=len(results),logical_NMIs=nmis,original_instructions=instructions,confirmations=confirmations,shutdown_calls=shutdowns,music0e_calls=music,APU_writes=sum(e[0]=='apu' for e in bus.events),journal_capture_bytes=len(capture),character_visits=character,controller_samples=inputs)
 return results,bus,instructions
