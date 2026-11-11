#!/usr/bin/env python3
"""PRIVATE continuous original-ROM comparison; reference executes first.
No reference state is reloaded into the native successful chain.
"""
from recovery_state_dispatch_scheduler_harness import *
from recovery_state_dispatch_scheduler_oracle import ControllerBus,SHA,select_boundary,log_resource
from py65.devices.mpu6502 import MPU

def context(ref):return struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,(ref.p&0xef)|0x20,ref.sp,0xa7)

def run_case(rom,code,pads,delay,resume_pads):
 native=Native(code,rom[16:16+131072])
 bus=ControllerBus(rom);bus.inputs=(0,0);bus.pos=[0,0]
 bus[:2048]=[0xa5]*2048;bus.events.clear()
 ref=MPU(memory=bus);ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 event=count=instructions=nmis=waits=0;checkpoints=[];completed={};new_boundaries=[];apu_writes=0
 while count<4096:
  assert native.mem.r16(CTX)==ref.pc
  native.mem.w_block(RUNTIME+6,bytes.fromhex('baddf00d'))
  native.mem.w_block(JOURNAL,bytes(8754))
  before=native.snapshot();checkpoints.append((before,event))
  start=len(bus.events);dma_start=len(bus.dma)
  status,index,target=select_boundary(ref,bus,event)
  before_instructions=instructions
  # Reference chooses AND completes its original instructions before native.
  if status==1:
   if event:ref.nmi();nmis+=1
   if index in (9,21):bus.inputs=pads if index==9 else resume_pads;bus.pos=[0,0]
   for _ in range(50000):
    if 13<=index<=20 or index in (26,27):log_resource(ref,bus)
    ref.step();instructions+=1
    if ref.pc in target:break
   else:raise AssertionError(('original timeout',index,before[1].hex(),target,hex(ref.pc),before[0][0xc0],before[0][0x763]))
  result=native.run(event,resume_pads if index==21 else pads)
  assert result==status&0xffffffff,(count,index,before[1].hex(),result,status,before[0][0x80],before[0][0xf1],before[0][0x1b2:0x1b9].hex())
  if status!=1:
   assert native.snapshot()==before and not native.events and not native.reads
   if status<0:break
   for _ in range(delay):
    assert native.run(0,pads)==0 and native.snapshot()==before and not native.events
    waits+=1
   event=1;waits+=1;continue
  assert native.mem.r16(RUNTIME+6)==index
  assert native.mem.r16(RUNTIME+8)==SIZES[index]
  ram,ctx,journal,runtime=native.snapshot()
  assert ram==bytes(bus[:2048]),('RAM',index)
  assert ctx==context(ref),('context',index,ctx.hex(),context(ref).hex())
  assert tuple(runtime[:4])==bus.mapper.snapshot()[:4] and runtime[4:6]==b'\0\0'
  assert not bus.mapper.bits
  assert native.events==bus.events[start:],('effects',index)
  effects=[e for e in bus.events[start:] if e[0]!='ram']
  apu_writes+=sum(e[0]=='apu' for e in effects)
  expected=b''
  if SIZES[index]:
   expected=struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',*e[1:]) for e in effects)
   if index in (6,11):
    assert len(bus.dma)==dma_start+1
    expected+=bus.dma[-1]
   expected+=bytes(SIZES[index]-len(expected))
  else:assert not effects
  assert journal==expected+bytes(8754-len(expected))
  if index==12:
   bank=bus.mapper.bank;offset=bank*16384
   pointer=(rom[16+offset+0xa11]<<8)|rom[16+offset+0xa12]
   assert native.reads==[offset+i for i in [0xa00,0xa11,0xa12,*range(pointer-0x8000,pointer-0x8000+9)]]
  elif 13<=index<=20 or index in (26,27):
   offset=3*16384
   expected_reads=[e[1]-0x8000 for e in effects if e[0]=='resource']
   # Preflight reads are separate from original semantic reads.
   if index==27:expected_reads=[0x92e]+list(range(0x6bf,0x6c9))+expected_reads
   if index==15:
    command=before[1][2];table=0x483+2*command
    expected_reads=[table,table+1]+expected_reads
   if index==18:
    # The note helper repeats its octave read during pointer preflight.
    if expected_reads and expected_reads[0] in range(0x593,0x59b):expected_reads=[expected_reads[0]]+expected_reads
   assert native.reads==[offset+i for i in expected_reads],(index,native.reads,expected_reads)
  else:assert not native.reads
  if index in (21,22,23) or index==6 and nmis==3:
   new_boundaries.append(dict(helper=index,context=ctx.hex(),instructions=instructions-before_instructions))
  completed[str(index)]=completed.get(str(index),0)+1
  event=0;count+=1
  # Continue through fade, frame yield and the next real NMI prefix.
 assert count==292 and nmis==11 and ref.pc==0x83a0 and ref.a==3 and bus[0xc9]!=0
 terminal=native.snapshot()
 assert native.run(0,pads)==0xffffffff  # Music data command03 is not linked.
 assert native.snapshot()==terminal and not native.events and not native.reads
 final_context=context(ref).hex();final_mapper=bus.mapper.snapshot()[:4]
 # Independently follow the blocked command03 to its parser continuation.
 next_steps=0
 while ref.pc!=0x839d:
  ref.step();next_steps+=1
  assert next_steps<1000
 native.m.cleanup()
 rejections=0
 for saved,event in checkpoints:
  probe=Native(code,rom[16:16+131072]);probe.restore(saved)
  for addr,value in [(CTX,b'\x12\x34'),(RUNTIME,b'\0'),(RUNTIME+3,b'\x05'),(RUNTIME+10,b'\0\0'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01')]:
   probe.reject(addr,value,event=event);rejections+=1
  for e in (2,0xffffffff,0x100):probe.reject(event=e);rejections+=1
  if probe.mem.r16(CTX)!=0xfe8d:probe.reject(event=1);rejections+=1
  probe.m.cleanup()
 return dict(pads=pads,resume_pads=resume_pads,delayed_polls=delay,waits=waits,advanced_calls=count,logical_NMIs=nmis,
  original_instructions=instructions,APU_writes=apu_writes,inert_rejections=rejections,final_context=final_context,
  helper_completions=completed,new_boundaries=new_boundaries,final_mapper=final_mapper,next_original_boundary=hex(ref.pc),next_original_instructions=next_steps)

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--rom',type=Path,required=True)
 rom=parser.parse_args().rom.read_bytes()
 assert hashlib.sha256(rom).hexdigest()==SHA
 code=assemble();assert code==assemble()
 cases=[run_case(rom,code,p,d,r) for p,d,r in [((0,0),0,(0,0)),((0,0),13,(0,0)),((16,0),7,(0,0)),((1,0),2,(2,0)),((2,0),3,(2,0)),((4,8),1,(8,4)),((128,64),0,(64,128)),((255,255),4,(255,255))]]
 print(json.dumps(dict(status='PASS',scope='PRIVATE original-ROM, host M68EC020',code_bytes=len(code),
  code_sha256=hashlib.sha256(code).hexdigest(),cases=cases),indent=2))
if __name__=='__main__':main()
