#!/usr/bin/env python3
"""PRIVATE release-then-press A edge comparison, derived from frozen SFX ROM harness.
Original reference executes first.
No reference state is reloaded into the native successful chain.
"""
from recovery_bank_loader_player_contact_harness import *
from recovery_bank_loader_player_contact_oracle import ControllerBus,SHA,select_boundary,log_resource
from recovery_bank_loader_player_contact_oracle import REGIONS,RETURNS,raw_module_result
from recovery_test_startup_resource_load import validation_reads
from recovery_test_active_command0e_rom import Ricoh as MPU
from collections import deque
from recovery_state_menu_sfx_models import MODELS,preflight
from recovery_test_active_command0e_contract import validation_reads as reads0e
from recovery_test_active_command12_contract import validation_reads as reads12
from recovery_test_active_command13_contract import validation_reads as reads13
from recovery_test_active_command0f_contract import validation_reads as reads0f

def context(ref):return struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,(ref.p&0xef)|0x20,ref.sp,0xa7)

def run_case(rom,code,history):
 dialogue=False;pads=resume_pads=(0,0);delay=2;menu_visits=char_visits=0;samples=[];startup_checkpoint=None;selection_checkpoint=None;music_checkpoint=None;last_checkpoints=deque(maxlen=8)
 native=Native(code,rom[16:16+131072])
 bus=ControllerBus(rom);bus.inputs=(0,0);bus.pos=[0,0]
 bus[:2048]=[0xa5]*2048;bus.events.clear()
 ref=MPU(memory=bus);ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 apu_state=bytearray(16);apu_enable=0;apu_frames=[]
 game_visits=0;goal=False;input_history=[]
 frames=[];confirmations=[];shutdowns=[];event=count=instructions=nmis=waits=0;checkpoints=[];completed={};new_boundaries=[];apu_writes=0
 while count<50000:
  assert native.mem.r16(CTX)==ref.pc
  native.mem.w_block(RUNTIME+6,bytes.fromhex('baddf00d'))
  native.mem.w_block(JOURNAL,bytes(134638))
  before=native.snapshot()
  if count%31==0:checkpoints.append((before,event))
  last_checkpoints.append((before,event))
  start=len(bus.events);dma_start=len(bus.dma)
  if ref.pc==0xa025:menu_visits+=1
  if ref.pc==0xa06c:char_visits+=1
  if char_visits:
   if history=='default':value=16 if char_visits<3 else 0 if char_visits<5 else 16
   elif history.endswith('_early'):value=0 if char_visits<2 else (1 if history.startswith('right') else 2) if char_visits<8 else 0 if char_visits<45 else 16
   elif history.endswith('_repeat'):
    direction=1 if history.startswith('right') else 2
    value=16 if char_visits<3 else 0 if char_visits<5 else direction if char_visits<8 else 0 if char_visits<10 else direction if char_visits<13 else 0 if char_visits<45 else direction if char_visits<48 else 0 if char_visits<80 else 16
   elif history in ('alternating','move_back'):
    value=16 if char_visits<3 else 0 if char_visits<5 else 1 if char_visits<8 else 0 if char_visits<10 else 2 if char_visits<13 else 0 if char_visits<45 else (2 if history=='move_back' else 1) if char_visits<48 else 0 if char_visits<80 else 16
   elif history=='rapid':
    value=16 if char_visits<3 else 0 if char_visits<5 else {5:1,7:1,9:2,11:1}.get(char_visits,0) if char_visits<45 else 16
   else:value=16 if char_visits<3 else 0 if char_visits<5 else (1 if history.startswith('right') else 2) if char_visits<8 else 0 if char_visits<40 else 16
  elif menu_visits:value={'neutral':0,'title_right':1,'title_left':2,'title_select':32}.get(history,16)
  else:value=0
  if ref.pc==0x911c:dialogue=True
  if dialogue:value=16 if nmis>300 and nmis%120<30 else 0
  if game_visits:value=129 if 6<=game_visits<=11 else 1
  pads=resume_pads=(value,0)
  status,index,target=select_boundary(ref,bus,event)
  before_instructions=instructions
  # Reference chooses AND completes its original instructions before native.
  if status==1:
   if event:
    frame_sp=ref.sp;frame_pc=ref.pc;frame_p=ref.p
    frame=bytes((frame_pc>>8,frame_pc&255,(frame_p&0xef)|0x20,frame_p|0x34,ref.a,ref.x,ref.y))
    ref.nmi();nmis+=1
   confirming=index==49 and ref.pc==0xa06c and bus[0x14]&16
   if confirming:choice=bus[0x203];old_table=bytes(bus[0x340:0x35e])
   if index in (9,21,31,50,77,87,94,97,114,133,138):bus.inputs=pads;bus.pos=[0,0];samples.append(list(pads));input_history.append(dict(call=count,nmi=nmis,game_frame=max(0,game_visits-1),helper=index,pads=list(pads)))
   for _ in range(50000):
    prior_pc=ref.pc;opcode=bus[ref.pc] if index in REGIONS else 0
    log_resource(ref,bus,index)
    ref.step();instructions+=1
    if index==135 and prior_pc==0xc85e:break
    if index in REGIONS:
     if opcode==0x6c or opcode==0x60 and ref.pc not in RETURNS[index] or not any(a<=ref.pc<b for a,b in REGIONS[index]):break
    elif ref.pc in target:break
   else:raise AssertionError(('original timeout',index,before[1].hex(),target,hex(ref.pc),before[0][0xc0],before[0][0x763]))
  if status==1 and event:
   assert bytes(bus[256+((frame_sp-i)&255)] for i in range(7))==frame
   frames.append(dict(sp=frame_sp,frame=frame.hex(),nmi=nmis))
  if status==1 and index in (8,20,42):
   saved=frames[-1];assert ref.sp==saved['sp']
   assert ref.p==int(saved['frame'][4:6],16)|0x30
   assert bytes(bus[256+((saved['sp']-i)&255)] for i in range(7)).hex()==saved['frame']
  if status==1 and confirming:
   swapped=b''.join(old_table[i:i+2][::-1] for i in range(0,30,2))
   expected_table=old_table if choice==40 else swapped
   assert bytes(bus[0x340:0x35e])==expected_table
   if choice!=40:assert [bus[a] for a in (0x5a2,0x5a4,0x5a6,0x5a8)]==[0x8d,0x8a,0x95,0x8e]
   confirmations.append(dict(cursor_x=choice,selection='original' if choice==40 else 'alternate',table_sha256=hashlib.sha256(expected_table).hexdigest(),swapped=choice!=40))
  raw_expected=raw_module_result(before,rom,index) if status==1 and index in (68,90,150,151,160) else None
  try:result=native.run(event,resume_pads if index in (21,31,50,77,87,94,97,114,133,138) else pads)
  except Exception:
   print('FAILED ENTRY',count,index,before[1].hex(),'nativePC',hex(native.cpu.r_pc()),'SP',hex(native.cpu.r_sp()),flush=True);raise
  if result!=status&0xffffffff:
   root=Path(os.environ['RECOVERY_PRIVATE_SNAPSHOT_DIR'])
   for suffix,blob in zip(('ram','context','journal','runtime'),before): (root/('before.'+suffix+'.bin')).write_bytes(blob)
   for suffix,blob in zip(('ram','context','journal','runtime'),native.snapshot()): (root/('after.'+suffix+'.bin')).write_bytes(blob)
   (root/'input_history.json').write_text(json.dumps(input_history))
   detail=dict(call=count,index=index,nmis=nmis,frames=max(0,game_visits-1),before=before[1].hex(),result=result,expected=status,event=event,pads=pads,inert=native.snapshot()==before and not native.events and not native.reads,APU_writes=apu_writes,helper_completions=completed)
   (root/'unsupported.json').write_text(json.dumps(detail,indent=2));print('UNSUPPORTED',json.dumps(detail),flush=True)
  assert result==status&0xffffffff,(count,index,before[1].hex(),result,status,before[0][0x80],before[0][0xf1],before[0][0x1b2:0x1b9].hex())
  if status!=1:
   assert native.snapshot()==before and not native.events and not native.reads
   if status<0:break
   for _ in range(delay):
    assert native.run(0,pads)==0 and native.snapshot()==before and not native.events
    waits+=1
   event=1;waits+=1;continue
  if raw_expected is not None:
   assert native.raw_adapter_context==raw_expected[1],('raw context before ABI adapter',native.raw_adapter_context.hex(),raw_expected[1].hex())
   assert native.snapshot()[0]==raw_expected[0] and native.events==raw_expected[2],('raw module effects before canonical publication',index)
  else:assert native.raw_adapter_context is None
  assert native.mem.r16(RUNTIME+6)==index,(count,index,native.mem.r16(RUNTIME+6),before[1].hex())
  assert native.mem.r16(RUNTIME+8)==(65535 if index in (48,98) else SIZES[index])
  ram,ctx,journal,runtime=native.snapshot()
  assert ram==bytes(bus[:2048]),('RAM',index,before[1].hex(),ctx.hex(),context(ref).hex(),[(i,a,b) for i,(a,b) in enumerate(zip(ram,bus[:2048])) if a!=b][:12])
  if ctx!=context(ref):
   root=Path(os.environ['RECOVERY_PRIVATE_SNAPSHOT_DIR'])
   for suffix,blob in zip(('ram','context','journal','runtime'),before): (root/('before.'+suffix+'.bin')).write_bytes(blob)
   for suffix,blob in zip(('ram','context','journal','runtime'),native.snapshot()): (root/('after.'+suffix+'.bin')).write_bytes(blob)
   (root/'input_history.json').write_text(json.dumps(input_history))
   print('RAW_BOUNDARY',json.dumps(dict(call=count,index=index,nmis=nmis,frames=max(0,game_visits-1),before=before[1].hex(),native=ctx.hex(),canonical=context(ref).hex(),raw_original=hex(ref.p),ram_equal=ram==bytes(bus[:2048]),events_equal=native.events==bus.events[start:])),flush=True)
  assert ctx==context(ref),('context',index,ctx.hex(),context(ref).hex())
  assert tuple(runtime[:4])==bus.mapper.snapshot()[:4] and runtime[4:6]==b'\0\0'
  assert not bus.mapper.bits
  assert native.events==bus.events[start:],('effects',index,native.events,bus.events[start:])
  effects=[e for e in bus.events[start:] if e[0]!='ram']
  apu_writes+=sum(e[0]=='apu' for e in effects)
  for e in effects:
   if e[0]=='apu' and 0x4000<=e[1]<=0x400f:apu_state[e[1]-0x4000]=e[2]
   elif e[0]=='apu' and e[1]==0x4015:apu_enable=e[2]
  if index in (8,20,42):apu_frames.append(dict(nmi=nmis,registers=apu_state.hex(),enable=apu_enable))
  expected=b''
  if SIZES[index]:
   expected=struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',e[1],e[2],2 if index in (36,81) and e[0]=='ppu' and e[3]==0 else e[3]) for e in effects)
   if index in (6,11,40,48,98):
    assert len(bus.dma)==dma_start+1
    offset={6:42,11:198,40:238,48:134382,98:134382}[index]
    expected+=bytes(offset-len(expected))+bus.dma[-1]
   expected+=bytes(SIZES[index]-len(expected))
  else:assert not effects
  assert journal==expected+bytes(134638-len(expected))
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
  elif index in (29,30,36,37):
   bankno=3 if index in (29,30) else 2
   reads=[e[1]-0x8000 for e in effects if e[0]=='resource']
   if index in (29,30):reads=[0x489,0x48a] + reads if index==29 else [0x487,0x488]+reads
   if index==36:reads=validation_reads(rom[16+32768:16+49152])+reads
   assert native.reads==[bankno*16384+i for i in reads],('resource reads',index,native.reads,reads)
  elif index in (43,47):
   base=7*16384-0xc000 if index==43 else 2*16384-0x8000
   assert native.reads==[base+e[1] for e in effects if e[0]=='resource']
  elif index==139:
   assert native.reads==[49152+0xa00]+[49152+e[1]-0x8000 for e in effects if e[0]=='resource']
  elif index in (136,137,140,150,151,160):
   bank=before[3][3];assert native.reads==[(bank*16384+e[1]-0x8000 if e[1]<0xc000 else e[1]+0x10000) for e in effects if e[0]=='resource']*2
  elif index==135:
   assert native.reads==[65536+e[1] for e in effects if e[0]=='resource']*2
  elif index==134:
   assert native.reads==[49152+e[1]-0x8000 for e in effects if e[0]=='resource']*2
  elif index in (116,130):
   bank=before[3][3];assert native.reads==[(bank*16384+e[1]-0x8000 if e[1]<0xc000 else e[1]+0x10000) for e in effects if e[0]=='resource']*2
  elif index==100:
   bank=before[3][3];assert native.reads==[(bank*16384+e[1]-0x8000 if e[1]<0xc000 else e[1]+0x10000) for e in effects if e[0]=='resource']*2
  elif index==110:
   assert native.reads==[65536+e[1]-0x8000 for e in effects if e[0]=='resource']
  elif index in (115,153,154):
   assert native.reads==[e[1]+0x10000 for e in effects if e[0]=='resource']*2
  elif index in (96,99):
   assert native.reads==[(e[1] if e[1]<0xc000 else 114688+e[1]-0xc000) for e in effects if e[0]=='resource']*2,('dialogue reads',index)
  elif index==90:
   assert native.reads==[(81920+e[1]-0x8000 if e[1]<0xc000 else 114688+e[1]-0xc000) for e in effects if e[0]=='resource']*2
  elif index in (80,81,83):
   from recovery_bank_loader_player_contact_oracle import validation_reads as bank_validation
   pre=bank_validation(rom[32784:49168],before[1][3]) if index==81 else []
   assert native.reads==[32768+i for i in pre]+[32768+e[1]-0x8000 for e in effects if e[0]=='resource'],('new resource',index,native.reads,pre)
  elif index>=73:
   assert not native.reads
  elif index>=56:
   bank=2 if index in (56,70) else 3;r=rom[16+bank*16384:16+(bank+1)*16384]
   want=MODELS[index](before[0],before[1],r)
   assert (ram,native.raw_adapter_context if index==68 else ctx,native.events)==want,('raw public model before publication',index)
   expected_reads=preflight(index,before[0],before[1],r)+[e[1]-0x8000 for e in effects if e[0]=='resource']
   assert native.reads==[bank*16384+i for i in expected_reads],('sfx reads',index,native.reads,expected_reads)
  elif index>=51:
   pre=([0x485,0x486] if index==52 else {51:reads0e,53:reads12,54:reads13,55:reads0f}[index](before[0],before[1],rom[49168:65552]))
   assert native.reads==[49152+i for i in pre]+[49152+e[1]-0x8000 for e in effects if e[0]=='resource']
  else:assert not native.reads
  if index==69:shutdowns.append(dict(call=count+1,nmis=nmis,context=ctx.hex(),active_state=[ram[a] for a in (0xce,0xcf,0xd0,0xd1,0xd7,0xd8)]))
  if index>=29 or index in (21,22,23) or index==6 and nmis==3:
   new_boundaries.append(dict(helper=index,context=ctx.hex(),instructions=instructions-before_instructions))
  completed[str(index)]=completed.get(str(index),0)+1
  event=0;count+=1
  if ref.pc==0xc77b:
   game_visits+=1
   if game_visits>=241:goal=True;break
  if count==67:assert ref.pc==0xc2a8
  if count==70:assert ref.pc==0xc0bf and nmis==3
  if count==292:assert context(ref).hex()=='83a0032b00a4aba7' and nmis==11
  if ref.pc==0xc5d1:
   assert count==990 and nmis==35 and ctx.hex()=='c5d1f0f0ffa5bfa7'
   startup_checkpoint=dict(calls=count,nmis=nmis,context=ctx.hex())
  if ref.pc==0xa06c and selection_checkpoint is None:selection_checkpoint=dict(calls=count,nmis=nmis,context=ctx.hex(),pending_video=ram[0x19])
  if ref.pc==0x83a0 and ref.a==14 and music_checkpoint is None:
   assert count>2000 and nmis>=78
   music_checkpoint=dict(calls=count,nmis=nmis,context=ctx.hex(),timer=ram[0xbe]+256*ram[0xbf])

  # Continue genuinely until the supported title boundary.
 assert count<50000,'single safety bound exhausted'
 assert startup_checkpoint is not None
 assert goal or status==-1,(history,count,nmis,hex(ref.pc),ref.a)
 if history=='neutral':assert menu_visits==900 and nmis==935
 if selection_checkpoint:assert selection_checkpoint['pending_video']==0
 terminal=native.snapshot()
 Path(os.environ['RECOVERY_PRIVATE_SNAPSHOT_DIR'],'input_history.json').write_text(json.dumps(input_history))
 if not goal and history!='char_idle':
  assert native.run(0,pads)==0xffffffff
  assert native.snapshot()==terminal and not native.events and not native.reads
 final_context=context(ref).hex();final_mapper=bus.mapper.snapshot()[:4]
 if os.environ.get('RECOVERY_PRIVATE_SNAPSHOT_DIR'):
  root=Path(os.environ['RECOVERY_PRIVATE_SNAPSHOT_DIR'])
  with (root/(history+'.apu_frames.json')).open('x') as output:json.dump(apu_frames,output)
  for suffix,blob in zip(('ram','context','journal','runtime'),terminal):
   with (root/(history+'.'+suffix+'.bin')).open('xb') as output:output.write(blob)
 next_steps=0
 native.m.cleanup()
 rejections=0
 for saved,event in checkpoints+list(last_checkpoints):
  probe=Native(code,rom[16:16+131072]);probe.restore(saved)
  for addr,value in [(CTX,b'\x12\x34'),(RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+10,b'\0\0'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01')]:
   probe.reject(addr,value,event=event);rejections+=1
  for e in (2,0xffffffff,0x100):probe.reject(event=e);rejections+=1
  if probe.mem.r16(CTX)!=0xfe8d:probe.reject(event=1);rejections+=1
  probe.m.cleanup()
 return dict(history=history,countdown_visits=menu_visits,music_checkpoint=music_checkpoint,samples=samples,startup_checkpoint=startup_checkpoint,selection_checkpoint=selection_checkpoint,pads=pads,resume_pads=resume_pads,delayed_polls=delay,waits=waits,advanced_calls=count,logical_NMIs=nmis,
  original_instructions=instructions,APU_writes=apu_writes,inert_rejections=rejections,final_context=final_context,
  confirmations=confirmations,shutdowns=shutdowns,nmi_frames=frames,helper_completions=completed,new_boundaries=new_boundaries,final_mapper=final_mapper,unsupported_boundary=None if goal else hex(ref.pc),goal_reached=goal,completed_game_frames=max(0,game_visits-1))

def main():
 import sys
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 code=assemble()
 histories=sys.argv[1:] or ['default','right','move_back']
 for history in histories:
  result=run_case(rom,code,history)
  print(json.dumps(result,sort_keys=True))
 print('PASS scene continuation composite',len(code),hashlib.sha256(code).hexdigest())
if __name__=='__main__':main()
