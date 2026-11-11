#!/usr/bin/env python3
"""One resident RAM/context pair, FE24 after hardware warmup through bounded SFX ticks.
Additive composition derived from frozen cursor/request test; originals unchanged.
Reference executes continuously; no captured-state injection or RAM/context reload.
"""
import sys
if __name__ == '__main__' and '--rom' not in sys.argv:
 import runpy
 from pathlib import Path
 runpy.run_path(str(Path(__file__).with_name('recovery_test_sfx_stream_control_isolated.py')),run_name='__main__')
 raise SystemExit(0)
import hashlib,random,os,struct,subprocess,tempfile
from pathlib import Path
import machine68k
from py65.devices.mpu6502 import MPU
from verify_recovery_runtime_probe import PREFIX,TARGETS,architectural_status_view
from recovery_test_active_nmi_runtime_chain import ControllerBus,SerialMapper,SHA
from recovery_test_repeated_command02_audio import reference as audio_reference
from recovery_test_active_command02_contract import command02
from recovery_test_active_control_contract import declarative as control_model
from recovery_test_music_duration_prepare_contract import contract as prepare_model
from recovery_test_music_duration_progress_contract import declarative as progress_model
from recovery_music_envelope_declarative import envelope
from recovery_test_active_command03_contract import command03
PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x40000,0x20000,0x1000,0x800,0x1f0000

NAMES=('recovery_audio_reset_command', 'recovery_reset_ram', 'recovery_reset_mapper', 'recovery_reset_video', 'recovery_reset_dispatch', 'recovery_first_yield', 'recovery_first_nmi_prefix', 'recovery_nmi_audio_entry', 'recovery_silent_tick_rti', 'recovery_scheduler_resume', 'recovery_resumed_task_setup', 'recovery_palette_nmi_prefix', 'recovery_music07_command', 'recovery_music_tick_fetch', 'recovery_music_command04', 'recovery_music_stream_fetch', 'recovery_music_command05', 'recovery_music_command06', 'recovery_music_stream_command07_volume', 'recovery_music_event_instrument08', 'recovery_music_event_command18', 'recovery_music_event_command09', 'recovery_music_event_rest', 'recovery_music_channel_iteration', 'recovery_music_indexed_fetch', 'recovery_music_indexed_commands', 'recovery_music_indexed_rest', 'recovery_music_pitched_gate', 'recovery_music_pitched_note', 'recovery_active_nmi_return', 'recovery_general_task_scheduler', 'recovery_idle_nmi_prefix', 'recovery_music_active_control', 'recovery_music_duration_prepare', 'recovery_music_active_envelope', 'recovery_music_duration_progress', 'recovery_music_active_command03', 'recovery_startup_fade_continue', 'recovery_gameplay_frame_yield', 'recovery_music_empty_queue_entry', 'recovery_startup_video_clear', 'recovery_startup_bank_select', 'recovery_startup_resource_load', 'recovery_startup_title_setup', 'recovery_title_yield_entry', 'recovery_chr_nmi_prefix', 'recovery_title_fade_entry', 'recovery_music_active_command02', 'recovery_title_engine_tables', 'recovery_title_engine_wait', 'recovery_title_menu_countdown', 'recovery_title_menu_dispatch', 'recovery_title_menu_exit', 'recovery_character_menu_setup', 'recovery_queued_video_nmi_prefix', 'recovery_character_selection_dispatch', 'recovery_character_cursor_sound_request', 'recovery_sfx27_table_dispatch', 'recovery_sfx_header_initialize', 'recovery_sfx_initialized_tail', 'recovery_sfx_stream_entry', 'recovery_sfx_duration_math', 'recovery_sfx_channel_reconfigure', 'recovery_sfx_phase_dispatch', 'recovery_sfx_tick_entry', 'recovery_sfx_command_mask', 'recovery_sfx_event_action', 'recovery_sfx_active_control', 'recovery_sfx_envelope', 'recovery_sfx_stream_control')
SIZES={0: 30, 1: 0, 2: 82, 3: 8754, 4: 0, 5: 6, 6: 298, 7: 22, 8: 22, 9: 74, 10: 0, 11: 454, 12: 30, 13: 6, 14: 14, 15: 6, 16: 18, 17: 14, 18: 14, 19: 22, 20: 14, 21: 14, 22: 10, 23: 0, 24: 6, 25: 22, 26: 10, 27: 10, 28: 18, 29: 22, 30: 74, 31: 454, 32: 0, 33: 10, 34: 514, 35: 0, 36: 10, 37: 512, 38: 512, 39: 22, 40: 4382, 41: 22, 42: 32770, 43: 566, 44: 8, 45: 494, 46: 512, 47: 10, 48: 362, 49: 8, 50: 16, 51: 16, 52: 256, 53:106,54:134638,55:196,56:6,57:14,58:6,59:2,60:18,61:6,62:30,63:30,64:30,65:78,66:14,67:2,68:514,69:30}

class CompleteBus(ControllerBus):
 def __setitem__(self,a,v):
  if isinstance(a,int) and (0x4000<=a<=0x4013 or a==0x4015):
   self.events.append(('apu',a,v,1));return
  super().__setitem__(a,v)
def view(ref):return architectural_status_view(struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7))
def kind(index):
 if index in (53,56,57,58,60,61,64,65):return 'resource'
 if index in (2,7,8,29,39,41):return 'mapper'
 if index in (0,12,62):return 'apu'
 if index in (9,30):return 'controller'
 if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28,33,36,47,48):return 'resource'
 return 'ppu'
RESOURCE2=0x28000
FIXED=0x30000
class Native:
 def __init__(self,resource,resource2,fixed):
  with tempfile.TemporaryDirectory() as tmp:
   source,out=Path(tmp)/'native.s',Path(tmp)/'native.bin'
   source.write_text(''.join(' bra.l '+n+'\n' for n in NAMES)+'\n'.join((PORT/'src'/(n+'.s')).read_text() for n in NAMES))
   subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True);self.code=out.read_bytes()
  assert CODE+len(self.code)<BASE-16
  self.m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);self.mem,self.cpu=self.m.mem,self.m.cpu
  self.guard=bytes(range(16));self.resource=resource;self.resource2=resource2;self.fixed=fixed;self.rng=random.Random(0xc597);self.mapper=SerialMapper();self.events=[];self.reads=[];self.index=0;self.calls=0;self.status=0;self.pads=(0,0)
  mem=self.mem;mem.w_block(CODE,self.code);mem.w16(STOP,0x60fe);mem.w_block(RESOURCE-16,self.guard+resource+self.guard);mem.w_block(RESOURCE2-16,self.guard+resource2+self.guard);mem.w_block(FIXED-16,self.guard+fixed+self.guard)
  def trace(mode,width,a,v):
   n=1<<width;size=SIZES[self.index]
   ranges=((CODE,CODE+len(self.code)),(STOP,STOP+4),(BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+size),(RESOURCE,RESOURCE+16384),(RESOURCE2,RESOURCE2+16384),(FIXED,FIXED+16384),(STACK-512,STACK+4)) if mode=='R' else ((BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+size),(STACK-512,STACK))
   assert mode in ('R','W') and any(lo<=a and a+n<=hi for lo,hi in ranges),(mode,width,hex(a),self.index)
   if mode=='R' and RESOURCE<=a<RESOURCE+16384:
    assert width==0 and self.mapper.bank==3 and self.mapper.control==0x1e and not self.mapper.bits
    self.reads.append(a-RESOURCE)
   if mode=='R' and RESOURCE2<=a<RESOURCE2+16384:
    assert width==0 and self.mapper.bank==2 and self.mapper.control==0x1e and not self.mapper.bits
    self.reads.append(a-RESOURCE2)
   if mode=='R' and FIXED<=a<FIXED+16384:
    assert width==0 and self.mapper.control==0x1e and not self.mapper.bits
    self.reads.append(a-FIXED)
   if mode=='W' and BASE<=a<BASE+2048:
    assert width==0;self.events.append(('ram',a-BASE,v))
   if mode=='W' and a==JOURNAL and width==1 and v and self.index not in (37,38,44,46,49,50,51,52,55):
    assert 1<=v<=(size-2)//4
    at=JOURNAL+2+4*(v-1);address,value,k=mem.r16(at),mem.r8(at+2),mem.r8(at+3)
    typ=('apu' if k else 'resource') if self.index in (34,66,68,69) else kind(self.index)
    if self.index in (42,43):typ='resource' if k==0 else 'ppu';k=0 if k in (0,2) else 1
    if self.index in (45,54):typ='mapper' if address>=0x8000 else 'ppu'
    self.events.append((typ,address,value,k))
    if typ=='mapper':self.mapper.write(address,value)
    if typ=='ppu' and address==0x4014:
     offset=42 if self.index==6 else 134382 if self.index==54 else 238 if self.index==45 else 198
     assert bytes(mem.r_block(JOURNAL+offset,256))==bytes(mem.r_block(BASE+0x200,256))
  mem.set_trace_func(trace)
  for mode in ('R','W'):
   for a in (0,0x25000,0x90000,BASE+2047):
    try:trace(mode,2,a,0)
    except AssertionError:pass
    else:raise AssertionError('global whitelist escape')
 def load(self,s,c):
  assert self.calls==0
  self.mem.set_trace_mode(False);self.mem.w_block(BASE-16,self.guard+s+self.guard);self.mem.w_block(CTX-16,self.guard+c+self.guard)
 def state(self):return bytes(self.mem.r_block(BASE,2048)),bytes(self.mem.r_block(CTX,8))
 def run(self,index,status=None,allow_rejection=False):
  self.index=index;mem,cpu=self.mem,self.cpu;size=SIZES[index];mem.set_trace_mode(False)
  self.journal_seed=self.rng.randbytes(size) if index in (63,64,65,66,68,69) else bytes(size)
  mem.w_block(JOURNAL-16,self.guard+self.journal_seed+self.guard)
  regs=[self.rng.getrandbits(32) for _ in range(15)];regs[8:12]=[BASE,CTX,JOURNAL,FIXED if index==48 else RESOURCE2 if index in (42,43,53,56) else RESOURCE]
  if index in (9,30):regs[0]=(regs[0]&0xffffff00)|self.pads[0];regs[1]=(regs[1]&0xffffff00)|self.pads[1]
  mem.w_block(STACK-528,bytes([105])*528)
  cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_pc(CODE+index*6);self.events.clear();self.reads.clear();mem.set_trace_mode(True)
  for _ in range(1500):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('native timeout')
  mem.set_trace_mode(False);self.status=cpu.r_reg(0);self.calls+=int(self.status!=0xffffffff)
  assert allow_rejection or self.status!=0xffffffff,('native rejection',index,self.state()[1].hex())
  if status is not None:assert self.status==status
  assert bytes(mem.r_block(STACK-528,16))==bytes([105])*16
  assert cpu.r_sp()==STACK+4 and [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,size),(RESOURCE,16384),(RESOURCE2,16384),(FIXED,16384)):
   assert bytes(mem.r_block(a-16,16))==self.guard and bytes(mem.r_block(a+n,16))==self.guard
  assert bytes(mem.r_block(CODE,len(self.code)))==self.code
  assert bytes(mem.r_block(RESOURCE,16384))==self.resource
  assert bytes(mem.r_block(RESOURCE2,16384))==self.resource2
  assert bytes(mem.r_block(FIXED,16384))==self.fixed
  return self.state()+(list(self.events),)

def bootstrap(rom,native):
    bus = CompleteBus(rom)
    bus.inputs = (0,0)
    bus.pos = [0,0]
    bus[:2048] = [0xa5]*2048
    bus.events.clear()
    ref = MPU(memory=bus)
    ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp = 0xfe24,0x17,0x33,0,0x24,0xfd
    native.load(bytes(bus[:2048]),bytes.fromhex("fe2417330024fda7"))
    results = []
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
        got=native.run(index,status)
        assert got==(bytes(bus[:2048]),context,list(events)),('bootstrap',call,index,got[1].hex(),context.hex())
        assert bytes(native.mem.r_block(JOURNAL,size))==journal
        assert native.mapper.snapshot()==bus.mapper.snapshot()
        results.append((index,status,context,bytes(bus[:2048]),journal,raw))
    assert ref.pc == 0xc2a8 and ref.sp == 0xbc
    assert bus[0x1bd:0x1c0] == [4,0x93,0xc5]
    assert bus[0x80] == 2 and bus[0x18] == 0
    assert bus.bank == 6 and bus.mapper.control == 0x1e and not bus.mapper.bits
    assert len(frames) == 2
    return bus,ref,instructions

def main():
 path=PORT.parent/'input/rescue-rangers-europe.nes';rom=path.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 native=Native(rom[49168:65552],rom[16+2*16384:16+3*16384],rom[16+7*16384:16+8*16384]);bus,ref,instructions=bootstrap(rom,native)
 assert native.calls==68
 counts={k:sum(e[0]==k for e in bus.events) for k in ('ram','ppu','mapper','controller','resource','apu')}
 bootstrap_counts=dict(counts);nmis=0;fade_samples=0;frame=None;idle=False;audio_calls=0;fade_values=[];title_started=False;chr_consumed=False;title_entry_calls=0;command02_calls=0
 char_visits=0;choice=int(os.environ.get('CHARACTER_INPUT','16'),0)
 phase_records=[];phase_started=False;return_records=[];envelope_calls=0;envelope_apu=0;stream_control_records=[]
 menu_cycles=0;menu_input=int(os.environ.get("MENU_INPUT","16"),0)
 for boundary in range(100000):
  pc=ref.pc

  if audio_calls>=int(os.environ.get("AUDIO_RETURN_CAP","44")):break
  if nmis+2>=120 and pc==0xfe90:break
  if pc in (0x80fb,0x8249,0x8152):break
  if pc in (0xc5f8,) or (pc==0x83a0 and ref.a not in (2,3,4,5,6,7,8,9,24) and ref.a<32):break
  if pc==0xa06c:
   char_visits+=1
   if char_visits==1:
    assert native.calls==1128 and view(ref)==bytes.fromhex('a06cffffffa4bda7') and bus[0x19]==0
    assert bus[0x203]==0x28
   if choice==0 and char_visits==4:break
  if pc==0xa025:
   if menu_cycles==0:
    assert native.calls==1077 and view(ref)==bytes.fromhex('a025ffffffa4bda7')
    assert bus[0xbe:0xc0]==[0x84,3] and bus[0x1be:0x1c0]==[0xf7,0xc5]
    assert bus.mapper.snapshot()==(30,31,31,2,())
   menu_cycles+=1
   if menu_cycles==int(os.environ.get('MENU_CYCLES','901')):break
  before=native.state();assert before==(bytes(bus[:2048]),view(ref))
  start=len(bus.events);dma_start=len(bus.dma)
  if pc==0x8060:phase_started=True
  if pc==0x8235:
   from recovery_test_sfx_stream_control import run_original as stream_original
   from recovery_sfx_stream_control_model import model as stream_control_model
   index=69
   stream_original(bus,ref,0xa7)
  elif pc==0x86b2 and ref.x<4:
   from recovery_test_sfx_envelope import run_original,model as sfx_envelope,validation_reads as envelope_validation
   index=68
   assert sfx_envelope(*before,native.resource) is not None
   run_original(bus,ref,0xa7)
  elif pc==0x8052 or (pc==0xc0f6 and (bus[0xcf] or bus[0xd0] or bus[0xd1])):
   from recovery_test_sfx_active_control import model as active_model
   index=67
   for _ in range(100):
    at=ref.pc;ref.step();instructions+=1
    if at==0x80ba or ref.pc in (0x8224,0x8060):break
   else:raise AssertionError('active control timeout')
  elif pc in (0x830b,0x831b):
   from recovery_test_sfx_event_action import model as event_model
   index=66
   for _ in range(500):
    at=ref.pc
    if at in (0x8626,0x862b):
     a=(0x8934 if at==0x8626 else 0x8935)+ref.y;bus.events.append(('resource',a,bus[a],0))
    if at==0x8638:
     a=(bus[0xc5]+256*bus[0xc6]+ref.y)&65535;bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if at in (0x8643,0x8651,0x80ce):break
   else:raise AssertionError('SFX event timeout')
  elif pc==0x82dc:
   from recovery_test_sfx_command_mask import model as mask_model, validation_reads as mask_validation
   index=65
   for _ in range(400):
    at=ref.pc;a=None
    if at==0x835a:a=bus[0xd0]+256*bus[0xd1]
    elif at in (0x802c,0x8030):a=(bus[0xc1]+256*bus[0xc2]+ref.y)&65535
    elif at in (0x868c,0x8693):a=0x8a02 if at==0x868c else 0x8a01
    if a is not None:bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc in (0x830b,0x831b):break
   else:raise AssertionError('SFX command mask timeout')
  elif pc in (0x82b0,0x82c0):
   from recovery_test_sfx_tick_entry import model as tick_model
   index=64
   for _ in range(100):
    at=ref.pc
    if at in (0x868c,0x8693):
     a=0x8a02 if at==0x868c else 0x8a01;bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc in (0x82dc,0x86b2) or at in (0x82cc,0x85a5):break
   else:raise AssertionError('SFX tick entry timeout')
  elif pc in (0x8060,0x807a) or (pc==0x8085 and (bus[0xcf] or bus[0xd0] or bus[0xd1])):
   from recovery_test_sfx_phase_dispatch import model as phase_model
   index=63
   for _ in range(500):
    at=ref.pc;ref.step();instructions+=1
    if at==0x80ba or ref.pc in (0x82b0,0x8374,0x839d):break
   else:raise AssertionError('phase dispatch timeout')
  elif pc==0x81a3:
   from recovery_test_sfx_channel_reconfigure import model as channel_model
   index=62;assert channel_model(*before,native.resource) is not None
   for _ in range(200):
    ref.step();instructions+=1
    if ref.pc==0x8060:break
   else:raise AssertionError('channel timeout')
  elif pc in (0x8006,0x8298):
   from recovery_test_sfx_duration_math import model as duration_model
   index=61;target=int.from_bytes(duration_model(*before,native.resource)[1][:2],'big')
   assert bus.bank==3 and bus.mapper.control==0x1e and not bus.mapper.bits
   for _ in range(200):
    if ref.pc==0x835a:
     a=bus[0xd0]+256*bus[0xd1];bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('duration timeout')
  elif pc==0x8224:
   from recovery_test_sfx_stream_entry import model as stream_model
   index=60;target=int.from_bytes(stream_model(*before,native.resource)[1][:2],'big')
   for _ in range(200):
    if ref.pc==0x835a:
     a=bus[0xd0]+256*bus[0xd1];bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('stream timeout')
  elif pc==0x8151:
   from recovery_test_sfx_initialized_tail import model as tail_model
   index=59;assert tail_model(*before,native.resource) is not None
   for _ in range(100):
    ref.step();instructions+=1
    if ref.pc==0x8224:break
   else:raise AssertionError('SFX return tail timeout')
  elif pc==0x810d:
   from recovery_test_sfx_header_initialize import model as header_model
   index=58;target=int.from_bytes(header_model(*before,native.resource)[1][:2],'big')
   a=bus[0xc1]+256*bus[0xc2];bus.events.append(('resource',a,bus[a],0))
   for _ in range(250):
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('SFX header timeout')
  elif pc==0x8003 and ref.a==0x27:
   from recovery_test_pending_sfx27_dispatch import model as dispatch_model
   index=57;target=int.from_bytes(dispatch_model(*before,native.resource)[1][:2],'big')
   for _ in range(100):
    at=ref.pc
    if at in (0x80f0,0x80fd,0x8102):
     a={0x80f0:0x8a00,0x80fd:0x8a04+ref.x,0x8102:0x8a03+ref.x}[at];bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('SFX27 dispatch timeout')
  elif pc in (0xa07b,0xf379,0xa086):
   from recovery_test_character_cursor_sound_request import model as cursor_model
   index=56;target=int.from_bytes(cursor_model(*before,native.resource2)[1][:2],'big')
   for _ in range(50):
    at=ref.pc
    if at==0xa07b:
     a=0xa0e1+ref.y;bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if at in (0xa083,0xa086,0xf391):break
   else:raise AssertionError('cursor sound timeout')
   assert ref.pc==target
  elif pc in (0xa06c,0xa089):
   from recovery_test_character_selection_dispatch import model as character_model
   index=55;target=int.from_bytes(character_model(*before)[1][:2],'big')
   assert bus.bank==2 and not bus.mapper.bits
   for _ in range(1000):
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('character dispatch timeout')
  elif pc==0xa05c:
   assert native.calls==1104 and view(ref)==bytes.fromhex('a05c00ffff27bda7')
   index=53
   assert bus.bank==2 and not bus.mapper.bits
   for _ in range(200):
    if ref.pc==0xa05e:
     a=0xa0c9+ref.x;bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc==0xff04:break
   else:raise AssertionError('character setup timeout')
  elif pc in (0xa025,0xa000,0xa0bb):
   from recovery_test_title_menu_loop import model as menu_model
   index={0xa025:50,0xa000:51,0xa0bb:52}[pc]
   target=int.from_bytes(menu_model(*before)[1][:2],'big')
   assert bus.bank==2 and not bus.mapper.bits
   for _ in range(1000):
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('menu loop timeout')
  elif pc in (0xc5d1,):
   index=48 if pc==0xc5d1 else 49
   target=0xa000 if index==48 else 0xff04
   assert bus.bank==2 and not bus.mapper.bits
   if index==49:assert bus[0x14]&0x33==0
   for _ in range(2000):
    at=ref.pc
    if at in (0xc5d3,0xc5de,0xc5e4):
     a=0xd657+ref.x if at==0xc5d3 else (0xc73f if at==0xc5de else 0xc75d)+ref.y
     bus.events.append(('resource',a,bus[a],0))
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('title engine timeout')
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
   assert bus[0xf6]==0 and native.state()[0][0xf6]==0
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
   index=30;native.pads=((choice if char_visits>=2 else 0) if char_visits else menu_input if menu_cycles else 0,0);bus.inputs,bus.pos=native.pads,[0,0]
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
   from recovery_test_pending_sfx27_dispatch import dequeue
   index=39 if bus[0xdc+bus[0xdb]]==0x88 else 7
   assert bus[0xf5]==0 and bus[0xdb]<8
   target=0xc0f6 if index==39 else 0x8003
   for _ in range(40):
    ref.step();instructions+=1
    if ref.pc==target:break
   else:raise AssertionError('queue timeout')
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
  got=native.run(index)
  assert got==want,('resident mismatch',boundary,index,got[1].hex(),want[1].hex(),[(i,a,b) for i,(a,b) in enumerate(zip(got[0],want[0])) if a!=b],got[2],want[2])
  assert native.mapper.snapshot()==bus.mapper.snapshot()
  if index in (37,38,44,46,49,50,51,52,55):
   assert all(e[0]=='ram' for e in want[2])
   expected=b''.join(struct.pack('>HBB',e[1],e[2],0) for e in want[2]);assert native.status==len(want[2])
  else:
   assert native.status==(int(not idle) if index==30 else 1)
   je=[e for e in want[2] if e[0] in (('apu','resource') if index in (34,66,68,69) else (kind(index),))]
   expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',*e[1:]) for e in je) if SIZES[index] else b''
   if index in (42,43):
    je=[e for e in want[2] if e[0] in ('resource','ppu')]
    expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',e[1],e[2],0 if e[0]=='resource' else 1 if e[3] else 2) for e in je)
   if index in (45,54):
    je=[e for e in want[2] if e[0] in ('ppu','mapper')]
    expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',*e[1:]) for e in je)
   if index in (31,45,54):
    expected+=bytes((134382 if index==54 else 238 if index==45 else 198)-len(expected))+bus.dma[-1]
  assert bytes(native.mem.r_block(JOURNAL,SIZES[index]))==expected+native.journal_seed[len(expected):]
  semantic=[e[1]-0x8000 for e in want[2] if e[0]=='resource']
  if index==32:assert control_model(*before)==want;assert native.reads==[]
  elif index==33:
   model,reads=prepare_model(*before,native.resource);assert model[:3]==want;assert native.reads==reads
  elif index==34:
   assert envelope(*before,native.resource)==want;assert native.reads==[0x92e]+list(range(0x6bf,0x6c9))+semantic
  elif index==35:assert progress_model(*before)==want;assert native.reads==[]
  elif index==36:assert command03(*before,native.resource)==want;assert native.reads==[0x489,0x48a]+semantic
  if index==47:
   assert command02(*before,native.resource)==want;assert native.reads==[0x487,0x488]+semantic
  if index in (44,46):
   from recovery_test_title_fade_yield import model
   predicted=model(*before);assert predicted[:2]==want[:2] and [('ram',a,v) for a,v in predicted[2]]==want[2]
  if index==42:
   from recovery_test_startup_resource_load import model,validation_reads
   assert model(*before,native.resource2)==want
   assert native.reads==validation_reads(native.resource2)+semantic
  elif index==43:
   from recovery_test_startup_title_setup import model
   assert model(*before,native.resource2)==want and native.reads==semantic
  if index==7:
   assert dequeue(*before,native.resource)==want
   assert native.reads==[]
  if index==29 and audio_calls>=39:
   return_records.append((native.calls,nmis+2,audio_calls,view(ref).hex()))
  if index==69:
   assert stream_control_model(*before,native.resource)==want and native.reads==[]
   stream_control_records.append((native.calls,nmis+2,audio_calls,view(ref).hex(),bool(bus[0xcf]),sum(e[0]=='apu' for e in want[2])))
  if index==68:
   envelope_calls+=1;envelope_apu+=sum(e[0]=='apu' for e in want[2])
   assert sfx_envelope(*before,native.resource)==want
   assert native.reads==envelope_validation(*before,native.resource)+semantic
  if index==67:
   assert active_model(*before,native.resource)==want and native.reads==[]
  if index==66:
   assert event_model(*before,native.resource)==want and native.reads==semantic
  if index==65:
   assert mask_model(*before,native.resource)==want and native.reads==mask_validation(*before,native.resource)+semantic
  if index==64:
   assert tick_model(*before,native.resource)==want and native.reads==semantic
  if index==63:
   assert phase_model(*before,native.resource)==want and native.reads==[]
  if index==62:
   assert channel_model(*before,native.resource)==want and native.reads==[]
  if index==61:
   assert duration_model(*before,native.resource)==want and native.reads==semantic
  if index==60:
   assert stream_model(*before,native.resource)==want and native.reads==semantic
  if index==59:
   assert tail_model(*before,native.resource)==want and native.reads==[]
  if index==58:
   assert header_model(*before,native.resource)==want and native.reads==semantic
  if index==57:
   assert dispatch_model(*before,native.resource)==want
   assert native.reads==[0xa00]+semantic
  if index==56:
   assert cursor_model(*before,native.resource2)==want
   assert native.reads==semantic
  if index==53:
   from recovery_test_character_menu_setup import model
   assert model(*before,native.resource2)==want
   assert native.reads==semantic
  if index==48:
   from recovery_test_title_engine_tables import model
   assert model(*before,native.fixed)==want
   assert native.reads==[e[1]-0xc000 for e in want[2] if e[0]=='resource']
  if index==49:
   from recovery_test_title_engine_wait import model
   predicted=model(*before);assert predicted[:2]==want[:2] and [('ram',a,v) for a,v in predicted[2]]==want[2]
  if index==55:
   predicted=character_model(*before)
   assert predicted[:2]==want[:2] and [('ram',a,v) for a,v in predicted[2]]==want[2]
   assert native.reads==[]
  if index in (50,51,52):
   predicted=menu_model(*before)
   assert predicted[:2]==want[:2] and [('ram',a,v) for a,v in predicted[2]]==want[2]
   assert native.reads==[]
  if index in (60,63,64,65,66,67,68,69) and os.environ.get('PRIVATE_TRACE_DIR'):
   import json
   private_dir=Path(os.environ['PRIVATE_TRACE_DIR']).resolve()
   assert not private_dir.is_relative_to(PORT.parent.resolve()), 'Keep captured state outside the public project'
   private_dir.mkdir(parents=True,exist_ok=True)
   record={'helper':index,'before_ram':before[0].hex(),'before_context':before[1].hex(),
           'after_ram':want[0].hex(),'after_context':want[1].hex(),
           'reference_raw_context':struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7).hex(),
           'effects':want[2],'resource_reads':native.reads,
           'journal':bytes(native.mem.r_block(JOURNAL,SIZES[index])).hex()}
   (private_dir/('input_%d_call_%d_helper_%d.json'%(choice,native.calls,index))).write_text(json.dumps(record,indent=2)+'\n')
  if phase_started:
   phase_records.append((index,len(want[2]),hashlib.sha256(repr((want,native.reads)).encode()).hexdigest()))
  for e in want[2]:counts[e[0]]+=1
 else:raise AssertionError('boundary bound')
 assert menu_input==16 and choice in (0,1,2,16)
 assert native.state()==(bytes(bus[:2048]),view(ref))
 expected={0:(1219,41,39,'a06cffffffa4bda7'),16:(1196,40,38,'c5f8f800ff27bfa7')}
 if choice in (0,16):assert (native.calls,nmis+2,audio_calls,view(ref).hex())==expected[choice]
 elif os.environ.get("AUDIO_RETURN_CAP","44")=="44":
  assert (native.calls,nmis+2,audio_calls,view(ref).hex())==(1429,46,44,'fe9000100026ffa7')
  assert native.mapper.snapshot()==(30,31,31,2,())
  assert [item[2] for item in return_records]==list(range(39,45))
  assert envelope_calls==5 and envelope_apu==12
 else:
  assert os.environ['AUDIO_RETURN_CAP']=='118'
  assert (native.calls,nmis+2,audio_calls,view(ref).hex())==(2442,78,75,'83a00e2a00a4f2a7')
  assert native.mapper.snapshot()==(30,31,31,3,())
  assert stream_control_records==[(1766,56,53,'806000ff0427f4a7',False,4)]
  assert envelope_calls==16 and envelope_apu==34
  assert not any(bus[a] for a in (0xce,0xcf,0xd0,0xd1,0xd7,0xd8))
  assert [item[2] for item in return_records]==list(range(39,76))
  # Existing indexed command0E is deliberately not newly composed here.
  from recovery_test_active_command0e_contract import command0e
  assert command0e(*native.state(),native.resource) is not None
  print('Boundary: existing command0E contract accepts this terminal state; not executed here.')
 if os.environ.get('PRIVATE_TRACE_DIR'):
  import json
  private_dir=Path(os.environ['PRIVATE_TRACE_DIR']).resolve()
  assert not private_dir.is_relative_to(PORT.parent.resolve())
  private_dir.mkdir(parents=True,exist_ok=True)
  terminal={'native_ram':native.state()[0].hex(),'native_context':native.state()[1].hex(),
            'original_raw_context':struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7).hex(),
            'mapper':native.mapper.snapshot(),'helpers':native.calls,'nmis':nmis+2,'returns':audio_calls,
            'return_milestones':return_records}
  (private_dir/('input_%d_terminal.json'%choice)).write_text(json.dumps(terminal,indent=2)+'\n')
 print('Stream shutdown milestones',stream_control_records)
 print('SFX still active' ,bool(bus[0xcf]))
 print('Mixed return milestones',return_records,'SFX envelopes',envelope_calls,'SFX APU writes',envelope_apu)
 print('CHECKPOINT',native.calls,nmis+2,audio_calls,view(ref).hex(),native.mapper.snapshot(),counts)
 print('Phase records',len(phase_records),'SHA256',hashlib.sha256(repr(phase_records).encode()).hexdigest())
 assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 print('PASS continuous FE24 execution through SFX stream control and bounded subsequent ticks:',native.calls,'calls;',nmis+2,'NMIs;',audio_calls,'audio calls; external choice',choice,'visits',char_visits,'context',view(ref).hex(),'mapper',native.mapper.snapshot(),counts)
 print('Composite',len(native.code),hashlib.sha256(native.code).hexdigest())
 print('One initialization; full RAM/context/effects/journals/resources/ABI/guards/bounds. No state injection or skipped audio.')
 native.m.cleanup()
if __name__=='__main__':main()
