"""Private original-only reference. Never imported by the production builder."""
import struct
from py65.devices.mpu6502 import MPU
from recovery_state_dispatch_startup_oracle import ControllerBus,select_boundary,log_resource,SHA
from recovery_state_dispatch_startup_harness import SIZES

def oracle(rom):
 bus=ControllerBus(rom);bus.inputs=(0,0);bus.pos=[0,0]
 bus[:2048]=[0xa5]*2048;bus.events.clear()
 ref=MPU(memory=bus);ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 results=[];instructions=nmis=event=0;bus.runtime_checks=[]
 while len(results)<4096:
  status,index,target=select_boundary(ref,bus,event)
  if status==0:event=1;continue
  assert status==1
  start=len(bus.events);dma_start=len(bus.dma)
  if event:ref.nmi();nmis+=1
  if index in (9,21,31):bus.inputs=(0,0);bus.pos=[0,0]
  for _ in range(50000):
   log_resource(ref,bus,index);ref.step();instructions+=1
   if ref.pc in target:break
  else:raise AssertionError('Original timeout')
  effects=[e for e in bus.events[start:] if e[0]!='ram']
  expected=b''
  if SIZES[index]:
   expected=struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',e[1],e[2],2 if index==36 and e[0]=='ppu' and e[3]==0 else e[3]) for e in effects)
   if index in (6,11,40):
    assert len(bus.dma)==dma_start+1
    offset={6:42,11:198,40:238}[index];expected+=bytes(offset-len(expected))+bus.dma[-1]
   expected+=bytes(SIZES[index]-len(expected))
  else:assert not effects
  ctx=struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,(ref.p&0xef)|0x20,ref.sp,0xa7)
  results.append((index,1,ctx,bytes(bus[:2048]),expected,None))
  bus.runtime_checks.append(bytes(bus.mapper.snapshot()[:4])+bytes(2)+struct.pack('>HHH',index,SIZES[index],0xd501))
  event=0
  if ref.pc==0xc5d1:break
 assert len(results)==990 and nmis==35 and ref.pc==0xc5d1
 return results,bus,instructions
