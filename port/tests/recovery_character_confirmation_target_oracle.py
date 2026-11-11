#!/usr/bin/env python3
"""Reference-only cartridge execution oracle, reset through default character confirmation C5F8.

The 6502 CPU runs the unmodified approved ROM continuously. This standalone
oracle neither imports a native executor nor reads native output. Bus and
boundary observers record effects of the ROM instructions; they do not produce
game state. The only state initialization is the declared original reset input.
Logical interrupt scheduling is diagnostic, not a real-time timing claim.
"""
import hashlib, struct
from functools import lru_cache
from pathlib import Path
from py65.devices.mpu6502 import MPU as OriginalCPU
PORT=Path(__file__).resolve().parents[1]
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
class MPU(OriginalCPU):
 def step(self):
  self.step_count=getattr(self,'step_count',0)+1
  return super().step()

NAMES=('recovery_audio_reset_command', 'recovery_reset_ram', 'recovery_reset_mapper', 'recovery_reset_video', 'recovery_reset_dispatch', 'recovery_first_yield', 'recovery_first_nmi_prefix', 'recovery_nmi_audio_entry', 'recovery_silent_tick_rti', 'recovery_scheduler_resume', 'recovery_resumed_task_setup', 'recovery_palette_nmi_prefix', 'recovery_music07_command', 'recovery_music_tick_fetch', 'recovery_music_command04', 'recovery_music_stream_fetch', 'recovery_music_command05', 'recovery_music_command06', 'recovery_music_stream_command07_volume', 'recovery_music_event_instrument08', 'recovery_music_event_command18', 'recovery_music_event_command09', 'recovery_music_event_rest', 'recovery_music_channel_iteration', 'recovery_music_indexed_fetch', 'recovery_music_indexed_commands', 'recovery_music_indexed_rest', 'recovery_music_pitched_gate', 'recovery_music_pitched_note', 'recovery_active_nmi_return', 'recovery_general_task_scheduler', 'recovery_idle_nmi_prefix', 'recovery_music_active_control', 'recovery_music_duration_prepare', 'recovery_music_active_envelope', 'recovery_music_duration_progress', 'recovery_music_active_command03', 'recovery_startup_fade_continue', 'recovery_gameplay_frame_yield', 'recovery_music_empty_queue_entry', 'recovery_startup_video_clear', 'recovery_startup_bank_select', 'recovery_startup_resource_load', 'recovery_startup_title_setup', 'recovery_title_yield_entry', 'recovery_chr_nmi_prefix', 'recovery_title_fade_entry', 'recovery_music_active_command02', 'recovery_title_engine_tables', 'recovery_title_engine_wait', 'recovery_title_menu_countdown', 'recovery_title_menu_dispatch', 'recovery_title_menu_exit', 'recovery_character_menu_setup', 'recovery_queued_video_nmi_prefix', 'recovery_character_selection_dispatch')
SIZES={0: 30, 1: 0, 2: 82, 3: 8754, 4: 0, 5: 6, 6: 298, 7: 22, 8: 22, 9: 74, 10: 0, 11: 454, 12: 30, 13: 6, 14: 14, 15: 6, 16: 18, 17: 14, 18: 14, 19: 22, 20: 14, 21: 14, 22: 10, 23: 0, 24: 6, 25: 22, 26: 10, 27: 10, 28: 18, 29: 22, 30: 74, 31: 454, 32: 0, 33: 10, 34: 514, 35: 0, 36: 10, 37: 512, 38: 512, 39: 22, 40: 4382, 41: 22, 42: 32770, 43: 566, 44: 8, 45: 494, 46: 512, 47: 10, 48: 362, 49: 8, 50: 16, 51: 16, 52: 256, 53:106,54:134638,55:196}

PREFIX = (1,2,3,4,5,6,7,0,8,9,10,30,31,7,12,13,14,15,16,15,17,15,18,
          15,19,15,20,15,21,15,22)

TARGETS = {0:0xc0f3,1:0xfe43,2:0xfe67,3:0xfe7c,4:0xc574,5:0xfe8d,
           6:0xc0bf,7:0x8003,8:0xfe8d,9:0xc584,10:0xfe8d,12:0xc0f3,
           13:0x83a0,14:0x839d,15:0x83a0,16:0x839d,17:0x839d,
           18:0x839d,19:0x839d,20:0x839d,21:0x839d,22:0x8085,
           24:0x83a0,25:0x839d,26:0x8085,27:0x83fd,28:0x8085,
           29:0xfe90,31:0xc0bf}

def architectural_status_view(raw):
    """Comparison view ONLY. Raw reference P and original frame RAM stay untouched."""
    return raw[:5] + bytes(((raw[5] & 0xef) | 0x20,)) + raw[6:]

class OriginalBus(list):
    def __init__(self, rom):
        super().__init__([0]*65536)
        self[0xc000:] = rom[16+7*16384:16+8*16384]
        self.events = []
        self.status = 0
    def __getitem__(self, address):
        if address == 0x2002:
            self.events.append(('ppu', 0x2002, 0, 0))
            return self.status  # Value unused; read still resets the PPU address latch.
        return super().__getitem__(address)
    def __setitem__(self, address, value):
        if isinstance(address, int):
            if address in (0xfff0, 0x9fff, 0xbfff, 0xdfff):
                self.events.append(('mapper', address, value, self[0xf5]))
                return
            if address in (0x2000,0x2006,0x2007):
                self.events.append(('ppu', address, value, 1))
                return
            assert 0 <= address < 2048, ('unsupported write', hex(address))
            self.events.append(('ram', address, value))
        super().__setitem__(address, value)

class SerialMapper:
    """Independent MMC1 logical write model, not a 6502 instruction interpreter.
    Explicit initial obligation: empty latch, 16KiB switch-low/fixed-last mode.
    """
    def __init__(self):
        self.bits=[]; self.control=0x0c; self.chr0=0; self.chr1=0; self.prg=3
    def write(self,address,value):
        if value&128:
            self.bits.clear(); self.control|=12; return
        self.bits.append(value&1)
        if len(self.bits)==5:
            data=sum(bit<<i for i,bit in enumerate(self.bits))
            field=('control','chr0','chr1','prg')[(address>>13)&3]
            setattr(self,field,data); self.bits.clear()
    def snapshot(self):
        return self.control,self.chr0,self.chr1,self.prg,tuple(self.bits)
    @property
    def bank(self):
        assert (self.control>>2)&3==3, ('unsupported mapper mapping mode',self.snapshot())
        return self.prg&7

class AudioBus(OriginalBus):
    def __init__(self,rom):
        super().__init__(rom)
        self.rom=rom
        self.dma=[]
        self.mapper=SerialMapper()
        self.bits=self.mapper.bits
        self.bank=3
        self.map_bank(3)
    def map_bank(self,bank):
        assert 0<=bank<8
        self.bank=bank
        list.__setitem__(self,slice(0x8000,0xc000),self.rom[16+bank*16384:16+(bank+1)*16384])
    def __setitem__(self,address,value):
        if address in (0x4000,0x4004,0x4008,0x400c,0x4001,0x4005,0x4015):
            self.events.append(('apu',address,value,1));return
        if address in (0x2001,0x2003,0x2005,0x4014):
            self.events.append(('ppu',address,value,1))
            if address==0x4014:
                assert value==2
                self.dma.append(bytes(self[0x200:0x300]))
            return
        super().__setitem__(address,value)
        if address in (0xfff0,0x9fff,0xbfff,0xdfff):
            self.mapper.write(address,value)
            self.map_bank(self.mapper.bank)

class ControllerBus(AudioBus):
    inputs=(0,0)
    pos=[0,0]
    def __getitem__(self,address):
        if isinstance(address,int) and address in (0x4016,0x4017):
            port=address-0x4016; bit=self.pos[port]
            assert bit<8
            value=(self.inputs[port]>>(7-bit))&1
            self.pos[port]+=1
            self.events.append(('controller',address,value,0))
            return value
        return super().__getitem__(address)
    def __setitem__(self,address,value):
        if address==0x4016:
            self.events.append(('controller',address,value,1))
            self.pos=[0,0]
            return
        return super().__setitem__(address,value)

class CompleteBus(ControllerBus):
 def __setitem__(self,a,v):
  if isinstance(a,int) and (0x4000<=a<=0x4013 or a==0x4015):
   self.events.append(('apu',a,v,1));return
  super().__setitem__(a,v)

def view(ref):return architectural_status_view(struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7))

def kind(index):
 if index==53:return 'resource'
 if index in (2,7,8,29,39,41):return 'mapper'
 if index in (0,12):return 'apu'
 if index in (9,30):return 'controller'
 if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28,33,36,47,48):return 'resource'
 return 'ppu'

def run_control(bus,ref,reserved):
 start=len(bus.events)
 continuation=ref.pc==0x8085 and bytes(bus[0x100+((ref.sp+i)&255)] for i in range(2,7))==bytes.fromhex('005180f8c0')
 for _ in range(1000):
  pc=ref.pc
  if pc in (0x8374,0x839d):break
  assert pc in (0xc0f6,0x8000,0x839c) or 0x803a<=pc<=0x80ba or 0x8363<=pc<=0x8372,hex(pc)
  if pc==0x804f:continuation=True
  ref.step()
  if pc==0x80ba:
   if continuation and ref.pc==0x8052:continuation=False
   else:break
  elif pc==0x839c:assert ref.pc==0x8085
 else:raise AssertionError('control timeout')
 return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,(ref.p&0xef)|32,ref.sp,reserved)),list(bus.events[start:])

def run_envelope(bus,ref,reserved):
 start=len(bus.events);depth=0
 for steps in range(20000):
  pc=ref.pc
  assert (0x86b2<=pc<=0x890d or 0x8006<=pc<=0x8037 or 0x80cf<=pc<=0x80e0),hex(pc)
  if pc in (0x802c,0x8030,0x86cb,0x86e0,0x86ef,0x86f5,0x8703,0x8766,0x87b3,0x8838,0x88f5):
   ptr=0xc1 if pc in (0x802c,0x8030) else 0xc5
   a=((bus[ptr]|bus[ptr+1]<<8)+ref.y)&65535
   bus.events.append(('resource',a,bus[a],0))
  elif pc in (0x86d1,0x86e8,0x870b,0x8846,0x88c8,0x88d0,0x88df,0x88e5):
   a=({0x86d1:0x890e,0x86e8:0x890e,0x870b:0x890e,0x8846:0x892e,0x88c8:0x8934,0x88d0:0x8935,0x88df:0x8934,0x88e5:0x8935}[pc]+ref.y)&65535
   bus.events.append(('resource',a,bus[a],0))
  if bus[pc]==0x20 and pc!=0x86bc:depth+=1
  final=bus[pc]==0x60 and depth==0
  if bus[pc]==0x60:depth-=1
  ref.step()
  if final:break
 else:raise AssertionError('original timeout')
 c=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,(ref.p&0xef)|0x20,ref.sp,reserved))
 return bytes(bus[:2048]),c,list(bus.events[start:])

def run_parser(bus,ref,reserved,index):
    start=len(bus.events)
    for steps in range(200):
        pc=ref.pc
        if steps and index!=3 and pc==(0x83a0 if index==8 else 0x839d):break
        assert (0x83a0<=pc<=0x83e6 or pc==0x839d or 0x8473<=pc<=0x8482 or
                0x856e<=pc<=0x8584 or 0x8023<=pc<=0x8037 or
                0x84cd<=pc<=0x84eb or 0x8551<=pc<=0x855b or
                0x8652<=pc<=0x8698 or 0x86a5<=pc<=0x86b1 or
                0x859b<=pc<=0x85a5 or 0x846d<=pc<=0x8472),hex(pc)
        addr=None
        if pc in (0x857a,0x802c,0x8030):addr=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
        elif pc in (0x868c,0x8693):addr=0x8a02 if pc==0x868c else 0x8a01
        elif pc in (0x83ba,0x83c1):addr=(0x8585 if pc==0x83ba else 0x858c)+ref.y
        if addr is not None:bus.events.append(('resource',addr,bus[addr],0))
        last=index==3 and pc==0x8472
        ref.step()
        if last:break
    else:raise AssertionError('original timeout')
    raw=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved))
    context=raw[:5]+bytes(((raw[5]&0xef)|0x20,))+raw[6:]
    return bytes(bus[:2048]),context,list(bus.events[start:])

def run_gate(bus,ref,reserved):
    start=len(bus.events)
    for steps in range(300):
        pc=ref.pc
        if pc==0x83fd:break
        assert 0x83a0<=pc<=0x83fa or 0x8006<=pc<=0x8022,hex(pc)
        if pc in (0x83ba,0x83c1):
            addr=(0x8585 if pc==0x83ba else 0x858c)+ref.y
            bus.events.append(('resource',addr,bus[addr],0))
        ref.step()
    else:raise AssertionError('gate reference timeout')
    return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved)),list(bus.events[start:])

def run_note(bus,ref,reserved):
    start=len(bus.events)
    for steps in range(300):
        pc=ref.pc
        assert 0x83fd<=pc<=0x8472 or 0x85a6<=pc<=0x8651,hex(pc)
        addr=None
        if pc==0x844d:addr=0x8593+ref.y
        if pc in (0x8626,0x862b):addr=(0x8934 if pc==0x8626 else 0x8935)+ref.y
        if pc==0x8638:addr=((bus[0xc5]|bus[0xc6]<<8)+ref.y)&65535
        if addr is not None:bus.events.append(('resource',addr,bus[addr],0))
        ref.step()
        if pc==0x8472:break
    else:raise AssertionError('note reference timeout')
    return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved)),list(bus.events[start:])

COMMANDS=(8,24,9,None,4,5,6,7,None)

def context(ref,r=0):return ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,(ref.p&0xef)|32,ref.sp,r))

def audio_reference(bus,ref,index):
 if index in (9,10):
  start=len(bus.events)
  for _ in range(60):
   pc=ref.pc
   if pc==0x839d:break
   assert 0x83a0<=pc<=0x83a7 or 0x8473<=pc<=0x8480 or 0x8023<=pc<=0x8037 or 0x84bd<=pc<=0x84cc,hex(pc)
   if pc in (0x802c,0x8030):
    a=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535;bus.events.append(('resource',a,bus[a],0))
   ref.step()
  else:raise AssertionError('command03 timeout')
  return bytes(bus[:2048]),context(ref),list(bus.events[start:])
 if index==0:return run_control(bus,ref,0)
 if index==2:return run_envelope(bus,ref,0)
 if index==4:return run_parser(bus,ref,0,8)
 if index==5:return run_parser(bus,ref,0,COMMANDS.index(ref.a))
 if index==6:return run_parser(bus,ref,0,3)
 if index==7:return run_gate(bus,ref,0)
 if index==8:return run_note(bus,ref,0)
 start=len(bus.events)
 for _ in range(100):
  pc=ref.pc
  if index==1:
   if pc in (0x837f,0x86b2):break
   assert 0x8374<=pc<=0x837c or 0x867c<=pc<=0x8698,hex(pc)
   if pc in (0x868c,0x8693):
    a=0x8a02 if pc==0x868c else 0x8a01;bus.events.append(('resource',a,bus[a],0))
  else:
   if pc==0x839d:break
   assert 0x837f<=pc<=0x839c or 0x859b<=pc<=0x85a5,hex(pc)
  ref.step()
  if index==3 and pc==0x839c:break
 else:raise AssertionError('duration timeout')
 return bytes(bus[:2048]),context(ref),list(bus.events[start:])

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
 assert hashlib.sha256(rom).hexdigest()==SHA, 'Private cartridge hash mismatch'
 bus,ref,instructions,results=bootstrap(rom)
 counts={k:sum(e[0]==k for e in bus.events) for k in ('ram','ppu','mapper','controller','resource','apu')}
 bootstrap_counts=dict(counts);nmis=0;fade_samples=0;frame=None;idle=False;audio_calls=0;fade_values=[];title_started=False;chr_consumed=False;title_entry_calls=0;command02_calls=0
 char_visits=0;menu_cycles=0
 bus.input_checks=[(0,0)]*68
 for boundary in range(2000):
  pc=ref.pc
  if pc==0xc5f8:break
  if pc==0xa06c:
   char_visits+=1
   if char_visits==1:assert len(results)==1128 and bus[0x203]==0x28,(len(results),hex(bus[0x203]))
  if pc==0xa025:menu_cycles+=1
  before=(bytes(bus[:2048]),view(ref))
  start=len(bus.events);dma_start=len(bus.dma)
  if pc in (0xa06c,0xa089,0xa025,0xa000,0xa0bb,0xa05c,0xc5d1):
   index={0xa06c:55,0xa089:55,0xa025:50,0xa000:51,0xa0bb:52,0xa05c:53,0xc5d1:48}[pc]
   assert bus.bank==2 and not bus.mapper.bits
   # Boundaries observed from genuine original instructions, no declarative/native model.
   targets={48:(0xa000,),50:(0xa000,0xa0bb),51:(0xff04,0xa05c,0xa0bb),52:(0xc5f8,),53:(0xff04,),55:((0xa06c,) if pc==0xa089 else (0xa0bb,0xff04,0xa07b))}
   for _ in range(2000):
    at=ref.pc
    if at in (0xc5d3,0xc5de,0xc5e4,0xa05e):
     a=0xd657+ref.x if at==0xc5d3 else 0xa0c9+ref.x if at==0xa05e else (0xc73f if at==0xc5de else 0xc75d)+ref.y
     bus.events.append(('resource',a,bus[a],0))
    ref.step()
    if ref.pc in targets[index]:break
   else:raise AssertionError(('menu timeout',index,hex(ref.pc)))
  elif pc in (0xc5cb,0xc5ce):
   index=44 if pc==0xc5cb else 46
   title_started=True;title_entry_calls+=1
   target=0xff04 if index==44 else 0xc2a5
   for _ in range(2000):
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('title entry timeout')
  elif pc in (0xc5c0,0xc5c5):
   index=42 if pc==0xc5c0 else 43
   target=0xc5c5 if index==42 else 0xc5cb
   assert bus.bank==2 and not bus.mapper.bits
   for _ in range(20000):
    at=ref.pc
    if at in (0x8000,0x8005,0x800f,0x8019,0x8021,0x8028):
     a=0x803d+ref.x if at==0x8000 else 0x8047+ref.x if at==0x8005 else (bus[0]+256*bus[1]+ref.y)&65535
     bus.events.append(('resource',a,bus[a],0))
    elif at in (0x8822,0x8838,0x883e,0x8844,0x884a):
     a=ref.y+{0x8822:0x8861,0x8838:0x8871,0x883e:0x8872,0x8844:0x8873,0x884a:0x8874}[at]
     bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('title resource timeout')
  elif pc==0xc5bb:
   index=41
   assert bus[0xf6]==0
   assert bus.mapper.snapshot()==(0x1e,0,0x10,6,())
   for _ in range(100):
    ref.step();instructions+=1
    if ref.pc==0xc5c0:break
   else:raise AssertionError('bank-selection timeout')
  elif pc==0xc597:
   index=40
   for _ in range(10000):
    ref.step();instructions+=1
    if ref.pc==0xc5bb:break
   else:raise AssertionError("video clear timeout")
  elif pc in (0xc2a8,0xc594):
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
   index=30;bus.inputs,bus.pos=((16 if char_visits>=2 else 0) if char_visits else 16 if menu_cycles else 0,0),[0,0]
   for _ in range(1000):
    at=ref.pc;ref.step();instructions+=1
    if (ref.pc==0xfe90 and at==0xfea3) or ref.pc in (0xc2a8,0xc597,0xc5ce,0xa025,0xa06c,0xa089):break
   else:raise AssertionError('scheduler timeout')
   idle=ref.pc==0xfe90
  elif pc==0xfe90 and idle:
   index=54 if bus[0x19] else 45 if title_started else 31;idle=False;nmis+=1;saved_sp=ref.sp
   frame=bytes((pc>>8,pc&255,(ref.p&0xef)|32,ref.p|0x34,ref.a,ref.x,ref.y))
   ref.nmi()
   for _ in range(2000):
    ref.step();instructions+=1
    if ref.pc==0xc0bf:break
   else:raise AssertionError('NMI timeout')
   assert bytes(bus[0x100+((saved_sp-i)&255)] for i in range(7))==frame
   assert len(bus.dma)==dma_start+1
   if index==45 and not chr_consumed:
    assert before[0][0x1a:0x1c]==bytes((0x9f,0x9f))
    assert bus[0x1a]==bus[0x1b]==0 and bus.mapper.chr0==31 and bus.mapper.chr1==31
    chr_consumed=True
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
   assert bus.bank==(2 if title_started else 6) and not bus.mapper.bits
   audio_calls+=1
  else:
   if pc in (0xc0f6,0x8085):index,ai=32,0
   elif pc==0x8374:index,ai=33,1
   elif pc==0x86b2:index,ai=34,2
   elif pc==0x837f:index,ai=35,3
   elif pc==0x839d:index,ai=24,4
   elif pc==0x83fd:index,ai=28,8
   elif pc==0x83a0:
    if ref.a==2:index,ai=47,10;command02_calls+=1
    elif ref.a==3:index,ai=36,9
    elif ref.a in (4,5,6,7,8,9,24):index,ai=25,5
    elif ref.a in range(32,256,32):index,ai=26,6
    elif ref.a>=32:index,ai=27,7
    else:raise AssertionError(('unsupported command',ref.a))
   else:raise AssertionError(('unsupported boundary',hex(pc)))
   audio_reference(bus,ref,ai)
  want=bytes(bus[:2048]),view(ref),list(bus.events[start:])
  if index in (37,38,44,46,49,50,51,52,55):
   assert all(e[0]=='ram' for e in want[2])
   expected=b''.join(struct.pack('>HBB',e[1],e[2],0) for e in want[2]);status=len(want[2])
  else:
   status=(int(not idle) if index==30 else 1)
   je=[e for e in want[2] if e[0] in (('apu','resource') if index==34 else (kind(index),))]
   expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',*e[1:]) for e in je) if SIZES[index] else b''
   if index in (42,43):
    je=[e for e in want[2] if e[0] in ('resource','ppu')]
    expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',e[1],e[2],0 if e[0]=='resource' else 1 if e[3] else 2) for e in je)
   if index in (45,54):
    je=[e for e in want[2] if e[0] in ('ppu','mapper')]
    expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',*e[1:]) for e in je)
   if index in (31,45,54):
    expected+=bytes((134382 if index==54 else 238 if index==45 else 198)-len(expected))+bus.dma[-1]
  journal=expected+bytes(SIZES[index]-len(expected))
  raw=struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
  results.append((index,status,want[1],want[0],journal,raw))
  bus.input_checks.append(bus.inputs)
  bus.mapper_checks.append(bus.mapper.snapshot())
  bus.interval_events.append(tuple(want[2]))
  for e in want[2]:counts[e[0]]+=1
 else:raise AssertionError('boundary bound')
 assert len(results)==1196 and nmis==38 and audio_calls==38
 assert view(ref)==bytes.fromhex('c5f8f800ff27bfa7')
 assert bus.mapper.snapshot()==(30,31,31,2,()) and bus[0x19]==0
 assert bus[0xbe]+256*bus[0xbf]==898 and len(bus.dma)==40
 return results,bus,ref.step_count

if __name__=='__main__':
 import json
 results,bus,instructions=oracle((PORT.parent/'input/rescue-rangers-europe.nes').read_bytes())
 print(json.dumps(dict(calls=len(results),logical_NMIs=len(bus.dma),original_instructions=instructions,final_context=results[-1][2].hex(),mapper=bus.mapper.snapshot(),effects={k:sum(e[0]==k for e in bus.events) for k in ('ram','ppu','mapper','controller','resource','apu')}),indent=2))
