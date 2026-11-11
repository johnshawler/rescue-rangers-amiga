#!/usr/bin/env python3
"""Reference-only continuous cartridge oracle for the private resident fade target.
No target memory, native executor or captured state is used for expectations.
"""
import hashlib,struct
from functools import lru_cache
from pathlib import Path
from py65.devices.mpu6502 import MPU as OriginalCPU

class MPU(OriginalCPU):
 def step(self):
  self.step_count=getattr(self,"step_count",0)+1
  return super().step()
from verify_recovery_runtime_probe import PREFIX,TARGETS,architectural_status_view
from recovery_test_active_nmi_runtime_chain import ControllerBus,SHA
from recovery_test_repeated_active_audio import reference as audio_reference
PORT=Path(__file__).resolve().parents[1]

NAMES=('recovery_audio_reset_command', 'recovery_reset_ram', 'recovery_reset_mapper', 'recovery_reset_video', 'recovery_reset_dispatch', 'recovery_first_yield', 'recovery_first_nmi_prefix', 'recovery_nmi_audio_entry', 'recovery_silent_tick_rti', 'recovery_scheduler_resume', 'recovery_resumed_task_setup', 'recovery_palette_nmi_prefix', 'recovery_music07_command', 'recovery_music_tick_fetch', 'recovery_music_command04', 'recovery_music_stream_fetch', 'recovery_music_command05', 'recovery_music_command06', 'recovery_music_stream_command07_volume', 'recovery_music_event_instrument08', 'recovery_music_event_command18', 'recovery_music_event_command09', 'recovery_music_event_rest', 'recovery_music_channel_iteration', 'recovery_music_indexed_fetch', 'recovery_music_indexed_commands', 'recovery_music_indexed_rest', 'recovery_music_pitched_gate', 'recovery_music_pitched_note', 'recovery_active_nmi_return', 'recovery_general_task_scheduler', 'recovery_idle_nmi_prefix', 'recovery_music_active_control', 'recovery_music_duration_prepare', 'recovery_music_active_envelope', 'recovery_music_duration_progress', 'recovery_music_active_command03', 'recovery_startup_fade_continue', 'recovery_gameplay_frame_yield', 'recovery_music_empty_queue_entry')
SIZES={0: 30, 1: 0, 2: 82, 3: 8754, 4: 0, 5: 6, 6: 298, 7: 22, 8: 22, 9: 74, 10: 0, 11: 454, 12: 30, 13: 6, 14: 14, 15: 6, 16: 18, 17: 14, 18: 14, 19: 22, 20: 14, 21: 14, 22: 10, 23: 0, 24: 6, 25: 22, 26: 10, 27: 10, 28: 18, 29: 22, 30: 74, 31: 454, 32: 0, 33: 10, 34: 514, 35: 0, 36: 10, 37: 512, 38: 512, 39: 22}

class CompleteBus(ControllerBus):
 def __setitem__(self,a,v):
  if isinstance(a,int) and (0x4000<=a<=0x4013 or a==0x4015):
   self.events.append(('apu',a,v,1));return
  super().__setitem__(a,v)
def view(ref):return architectural_status_view(struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7))
def kind(index):
 if index in (2,7,8,29,39):return 'mapper'
 if index in (0,12):return 'apu'
 if index in (9,30):return 'controller'
 if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28,33,36):return 'resource'
 return 'ppu'
def bootstrap(rom):
    bus = CompleteBus(rom)
    bus.inputs = (0,0)
    bus.pos = [0,0]
    bus[:2048] = [0xa5]*2048
    bus.events.clear()
    ref = MPU(memory=bus)
    ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp = 0xfe24,0x17,0x33,0,0x24,0xfd
    results = []
    bus.mapper_checks=[]
    bus.interval_events=[]
    frames = []
    instructions = 0
    for call in range(68):
        if call < len(PREFIX):
            index = PREFIX[call]
        elif ref.pc == 0x8085: index = 23
        elif ref.pc == 0x839d: index = 24
        elif ref.pc == 0x83a0:
            index = 25 if ref.a in (4,5,6,7,8,9,24) else 26 if ref.a in range(32,256,32) else 27
        elif ref.pc == 0x83fd: index = 28
        elif ref.pc == 0xc0f9: index = 29
        elif ref.pc == 0xfe90: index = 30
        else: raise AssertionError(('unsupported boundary',call,hex(ref.pc)))
        start = len(bus.events)
        dma_start = len(bus.dma)
        status = 0 if call == 11 else 1
        if index in (6,31):
            assert ref.pc == (0xfe8d if index == 6 else 0xfe90)
            saved_sp = ref.sp
            expected_frame = bytes((ref.pc>>8,ref.pc&255,(ref.p&0xef)|0x20,ref.p|0x34,ref.a,ref.x,ref.y))
            ref.nmi()
        if index in (9,30): bus.inputs,bus.pos = (0,0),[0,0]
        target = (0xfe90 if status == 0 else 0xc2a8) if index == 30 else TARGETS.get(index)
        for count in range(50000):
            pc = ref.pc
            # Semantic resource reads, observed at the original load instruction.
            addr = None
            if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28):
                assert bus.bank == 3 and bus.mapper.control == 0x1e and not bus.mapper.bits
                if pc in (0x857a,0x802c,0x8030): addr = ((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
                elif pc in (0x868c,0x8693): addr = 0x8a02 if pc == 0x868c else 0x8a01
                elif pc in (0x83ba,0x83c1): addr = (0x8585 if pc == 0x83ba else 0x858c)+ref.y
                elif pc == 0x844d: addr = 0x8593+ref.y
                elif pc in (0x8626,0x862b): addr = (0x8934 if pc == 0x8626 else 0x8935)+ref.y
                elif pc == 0x8638: addr = ((bus[0xc5]|bus[0xc6]<<8)+ref.y)&65535
            if addr is not None:
                assert 0x8000 <= addr < 0xc000
                bus.events.append(('resource',addr,bus[addr],0))
            ref.step()
            instructions += 1
            if index == 23:
                if ref.pc == 0x839d or pc == 0x80ba: break
                assert ref.pc not in (0x82b0,0x8374), 'Untranslated envelope/callback'
            elif ref.pc == target and (index != 30 or status != 0 or pc == 0xfea3): break
        else: raise AssertionError(('original timeout',call,index,hex(ref.pc)))
        if index in (6,31):
            frame = bytes(bus[0x100+((saved_sp-i)&255)] for i in range(7))
            assert frame == expected_frame
            frames.append((saved_sp,frame))
            assert len(bus.dma) == dma_start+1
        if index in (8,29):
            saved_sp,frame = frames[-1]
            assert ref.p == frame[2] | 0x30
            assert bytes(bus[0x100+((saved_sp-i)&255)] for i in range(7)) == frame
            assert bus.bank == 6 and not bus.mapper.bits
        raw = struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
        context = architectural_status_view(raw)
        events = bus.events[start:]
        kind = ('mapper' if index in (2,7,8,29) else 'apu' if index in (0,12) else
                'controller' if index in (9,30) else 'resource' if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28) else 'ppu')
        published = [e for e in events if e[0] == kind]
        size = SIZES[index]
        journal = b''
        if size:
            journal = struct.pack('>H',len(published))+b''.join(struct.pack('>HBB',*e[1:]) for e in published)
            if index in (6,31):
                offset = 42 if index == 6 else 198
                assert len(journal) <= offset
                journal += bytes(offset-len(journal))+bus.dma[-1]
            journal += bytes(size-len(journal))
            assert len(journal) == size
        else: assert not published
        results.append((index,status,context,bytes(bus[:2048]),journal,raw))
        bus.mapper_checks.append(bus.mapper.snapshot())
        bus.interval_events.append(tuple(events))
    assert ref.pc == 0xc2a8 and ref.sp == 0xbc
    assert bus[0x1bd:0x1c0] == [4,0x93,0xc5]
    assert bus[0x80] == 2 and bus[0x18] == 0
    assert bus.bank == 6 and bus.mapper.control == 0x1e and not bus.mapper.bits
    assert len(frames) == 2
    return bus,ref,instructions,results

@lru_cache(maxsize=1)
def oracle(rom):
 """Independent continuously executing cartridge CPU; no native execution/import."""
 assert hashlib.sha256(rom).hexdigest()==SHA, 'Private cartridge hash mismatch'
 bus,ref,instructions,results=bootstrap(rom)
 counts={k:sum(e[0]==k for e in bus.events) for k in ('ram','ppu','mapper','controller','resource','apu')}
 bootstrap_counts=dict(counts);nmis=0;fade_samples=0;frame=None;idle=False;audio_calls=0;fade_values=[]
 for boundary in range(2000):
  pc=ref.pc
  if pc==0xc597:break
  start=len(bus.events);dma_start=len(bus.dma)
  if pc in (0xc2a8,0xc594):
   index=37;fade_samples+=1
   for _ in range(1000):
    at=ref.pc;ref.step();instructions+=1
    if ref.pc==0xc2a5 or at in (0xc2bd,0xc594):break
   else:raise AssertionError('fade timeout')
   fade_values.append(bus[0xf])
  elif pc in (0xc2a5,0xff04):
   index=38
   for _ in range(1000):
    ref.step();instructions+=1
    if ref.pc==0xfe8d:break
   else:raise AssertionError('yield timeout')
  elif pc in (0xfe8d,0xfe90) and not idle:
   index=30;bus.inputs,bus.pos=(0,0),[0,0]
   for _ in range(1000):
    at=ref.pc;ref.step();instructions+=1
    if (ref.pc==0xfe90 and at==0xfea3) or ref.pc in (0xc2a8,0xc597):break
   else:raise AssertionError('scheduler timeout')
   idle=ref.pc==0xfe90
  elif pc==0xfe90 and idle:
   index=31;idle=False;nmis+=1;saved_sp=ref.sp
   frame=bytes((pc>>8,pc&255,(ref.p&0xef)|32,ref.p|0x34,ref.a,ref.x,ref.y))
   ref.nmi()
   for _ in range(2000):
    ref.step();instructions+=1
    if ref.pc==0xc0bf:break
   else:raise AssertionError('NMI timeout')
   assert bytes(bus[0x100+((saved_sp-i)&255)] for i in range(7))==frame
   assert len(bus.dma)==dma_start+1
  elif pc==0xc0bf:
   index=39
   assert bus[0xf5]==0 and bus[0xdb]<8 and bus[0xdc+bus[0xdb]]==0x88
   for _ in range(40):
    ref.step();instructions+=1
    if ref.pc==0xc0f6:break
   else:raise AssertionError('empty queue timeout')
  elif pc==0xc0f9:
   index=29
   for _ in range(40):
    ref.step();instructions+=1
    if ref.pc==0xfe90:break
   else:raise AssertionError('return timeout')
   assert ref.p==frame[2]|0x30
   assert bytes(bus[0x100+((saved_sp-i)&255)] for i in range(7))==frame
   assert bus.bank==6 and not bus.mapper.bits
   audio_calls+=1
  else:
   if pc in (0xc0f6,0x8085):index,ai=32,0
   elif pc==0x8374:index,ai=33,1
   elif pc==0x86b2:index,ai=34,2
   elif pc==0x837f:index,ai=35,3
   elif pc==0x839d:index,ai=24,4
   elif pc==0x83fd:index,ai=28,8
   elif pc==0x83a0:
    if ref.a==3:index,ai=36,9
    elif ref.a in (4,5,6,7,8,9,24):index,ai=25,5
    elif ref.a in range(32,256,32):index,ai=26,6
    elif ref.a>=32:index,ai=27,7
    else:raise AssertionError(('unsupported command',ref.a))
   else:raise AssertionError(('unsupported boundary',hex(pc)))
   audio_reference(bus,ref,ai)
  want=bytes(bus[:2048]),view(ref),list(bus.events[start:])
  if index in (37,38):
   assert all(e[0]=='ram' for e in want[2])
   expected=b''.join(struct.pack('>HBB',e[1],e[2],0) for e in want[2]);status=len(want[2])
  else:
   status=(int(not idle) if index==30 else 1)
   je=[e for e in want[2] if e[0] in (('apu','resource') if index==34 else (kind(index),))]
   expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',*e[1:]) for e in je) if SIZES[index] else b''
   if index==31:
    expected+=bytes(198-len(expected))+bus.dma[-1]
  journal=expected+bytes(SIZES[index]-len(expected))
  raw=struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
  results.append((index,status,want[1],want[0],journal,raw))
  bus.mapper_checks.append(bus.mapper.snapshot())
  bus.interval_events.append(tuple(want[2]))
  for e in want[2]:counts[e[0]]+=1
 else:raise AssertionError('boundary bound')
 assert ref.pc==0xc597 and ref.sp==0xbf and bus[0xf]==0x50
 assert nmis==16 and audio_calls==16 and fade_samples==17
 assert counts['apu']-bootstrap_counts['apu']==100
 assert bus.bank==6 and bus.mapper.control==0x1e and not bus.mapper.bits
 assert set(fade_values)=={0x10,0x20,0x30,0x40,0x50}
 assert len(results)==533
 return results,bus,ref.step_count
