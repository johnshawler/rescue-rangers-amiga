"""Independent original-only replay. Never imported by the target builder."""
import hashlib,struct
from recovery_state_menu_sfx_oracle import ControllerBus,select_boundary,log_resource,SHA
from recovery_state_menu_sfx_harness import SIZES
from recovery_test_active_command0e_rom import Ricoh

def oracle(rom,history):
 assert hashlib.sha256(rom).hexdigest()==SHA
 bus=ControllerBus(rom);bus.inputs=(0,0);bus.pos=[0,0]
 bus[:2048]=[0xa5]*2048;bus.events.clear()
 ref=Ricoh(memory=bus);ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 results=[];instructions=nmis=event=menu=character=0;bus.runtime_checks=[]
 capture=bytearray();confirmations=[];shutdowns=[];music=[];inputs=[]
 while len(results)<12000:
  if ref.pc==0xa025:menu+=1
  if ref.pc==0xa06c:character+=1
  # Independent interval description of the previously qualified histories.
  intervals={'default':[(1,3,16),(5,128,16)],'right_hold':[(1,3,16),(5,8,1),(40,128,16)],'move_back':[(1,3,16),(5,8,1),(10,13,2),(45,48,2),(80,128,16)]}[history]
  value=next((v for lo,hi,v in intervals if lo<=character<hi),0) if character else (16 if menu else 0)
  pads=(value,0)
  status,index,target=select_boundary(ref,bus,event)
  if status==0:assert event==0;event=1;continue
  assert status==1,(hex(ref.pc),status)
  start=len(bus.events);dma_start=len(bus.dma)
  confirming=index==49 and ref.pc==0xa06c and bus[0x14]&16
  if confirming:choice=bus[0x203];table=bytes(bus[0x340:0x35e])
  if event:ref.nmi();nmis+=1
  if index in (9,21,31,50):bus.inputs=pads;bus.pos=[0,0];inputs.append(pads)
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
  if index==69:shutdowns.append(len(results))
  if index==51:music.append(len(results))
  event=0
  if ref.pc==0xc5f8:break
 assert ref.pc==0xc5f8 and len(confirmations)==1
 bus.capture=bytes(capture);bus.summary=dict(history=history,calls=len(results),logical_NMIs=nmis,original_instructions=instructions,confirmations=confirmations,shutdown_calls=shutdowns,music0e_calls=music,APU_writes=sum(e[0]=='apu' for e in bus.events),journal_capture_bytes=len(capture),character_visits=character,controller_samples=inputs)
 return results,bus,instructions
