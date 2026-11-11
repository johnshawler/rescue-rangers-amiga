"""Scene wrapper test harness, derived from frozen SFX harness; user mode execution."""
import hashlib, json, os, random, struct, subprocess, tempfile
from pathlib import Path
import machine68k
PORT = Path(__file__).resolve().parents[1]
NAMES = ('recovery_audio_reset_command','recovery_reset_ram','recovery_reset_mapper',
 'recovery_reset_video','recovery_reset_dispatch','recovery_first_yield',
 'recovery_first_nmi_prefix','recovery_nmi_audio_entry','recovery_silent_tick_rti',
 'recovery_scheduler_resume','recovery_resumed_task_setup')
NAMES += ("recovery_palette_nmi_prefix", "recovery_music07_command")
SIZES = (30,0,82,8754,0,6,298,22,22,74,0,454,30)
NAMES += ('recovery_music_tick_fetch', 'recovery_music_indexed_fetch', 'recovery_music_indexed_commands', 'recovery_music_indexed_rest', 'recovery_music_pitched_gate', 'recovery_music_pitched_note', 'recovery_music_channel_iteration', 'recovery_active_nmi_return')
SIZES += (6,6,22,10,10,18,0,22)
RESOURCE = 0x80000
CODE, STOP, RAM, CTX, JOURNAL, RUNTIME, STACK = 0x1000,0x800,0x10000,0x12000,0x13000,0x60000,0x1f0000
GUARD = bytes(range(16))

def event_kind(address):
 if address >= 0x8000: return 'mapper'
 if address < 0x4000 or address == 0x4014: return 'ppu'
 if address in (0x4016,0x4017): return 'controller'
 return 'apu'

class Native:
 def __init__(self,code,resource):
  self.m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
  self.mem,self.cpu=self.m.mem,self.m.cpu
  self.resource=bytes(resource); assert len(resource)==131072
  self.mem.w_block(RESOURCE-16,GUARD+self.resource+GUARD)
  self.reads=[]
  self.code=code; self.rng=random.Random(0xd501); self.events=[]
  self.mem.w_block(CODE,code); self.mem.w16(STOP,0x60fe)
  self.regions=((RAM,2048),(CTX,8),(JOURNAL,134638),(RUNTIME,12))
  for addr,size in self.regions:self.mem.w_block(addr-16,GUARD+bytes(size)+GUARD)
  self.mem.w_block(RAM,bytes([0xa5])*2048)
  self.mem.w_block(CTX,bytes.fromhex('fe2417330024fda7'))
  self.mem.w_block(RUNTIME,bytes.fromhex('0c0000030000ffff0000d501'))
  def trace(mode,width,addr,value):
   size=1<<width
   ranges=[(a,a+n) for a,n in self.regions]+[(STACK-1024,STACK)]
   if mode=='R':ranges += [(RESOURCE,RESOURCE+len(self.resource))]
   if RESOURCE<=addr<RESOURCE+len(self.resource):
    assert mode=='R' and width==0
    self.reads.append(addr-RESOURCE)
   if mode=='R':ranges += [(CODE,CODE+len(code)),(STOP,STOP+4),(STACK,STACK+4)]
   assert mode in ('R','W') and any(a<=addr and addr+size<=b for a,b in ranges),(mode,width,hex(addr))
   if mode=='W' and RAM<=addr<RAM+2048:
    assert width==0; self.events.append(('ram',addr-RAM,value))
   if mode=='W' and addr==JOURNAL and width==1 and value:
    at=JOURNAL+2+4*(value-1)
    a,v,k=self.mem.r16(at),self.mem.r8(at+2),self.mem.r8(at+3)
    pc=self.mem.r16(CTX)
    typ=('resource' if k==0 else 'ppu') if pc==0x8000 else 'resource' if pc in (0x9003,0x9039,0x9041) else 'resource' if pc in (0xa07b,0x8003,0x810d,0x8224,0x8006,0x8298,0x82b0,0x82c0,0x82dc) and k==0 else 'apu' if pc in (0x81a3,0x8235) else ('resource' if k==0 else 'apu') if pc in (0x830b,0x831b) or pc==0x86b2 and self.mem.r8(CTX+3)<4 else 'resource' if pc==0xc5d1 or (pc==0xa05c and 0x8000<=a<0xc000) else 'resource' if pc in (0xc0f3,0x839d,0x83a0,0x83fd,0x8374,0x86b2,0xc5c0,0xc5c5) and 0x8000<=a<0xc000 else event_kind(a)
    self.events.append((typ,a,v,0 if pc in (0xc5c0,0xc5c5,0x8000) and k==2 else k))
  self.mem.set_trace_func(trace)
  self.trace=trace
 def snapshot(self):return tuple(bytes(self.mem.r_block(a,n)) for a,n in self.regions)
 def restore(self,snapshot):
  for (a,n),v in zip(self.regions,snapshot):self.mem.w_block(a,v)
 def run(self,event=0,pads=(0,0)):
  mem,cpu=self.mem,self.cpu
  regs=[self.rng.getrandbits(32) for _ in range(15)]
  regs[0]=(regs[0]&0xffffff00)|pads[0];regs[1]=(regs[1]&0xffffff00)|pads[1]
  regs[2]=event;regs[8]=RAM;regs[9]=CTX;regs[10]=JOURNAL;regs[12]=RUNTIME;regs[13]=RESOURCE
  cpu.w_sr(0x0000);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  self.events.clear();self.reads.clear();cpu.w_pc(CODE);mem.set_trace_mode(True)
  for _ in range(10000):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('native dispatch timeout')
  mem.set_trace_mode(False)
  assert cpu.r_sr() & 0x2000 == 0, "helper left user mode"
  assert cpu.r_sp()==STACK+4
  assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  for a,n in self.regions:
   assert bytes(mem.r_block(a-16,16))==GUARD and bytes(mem.r_block(a+n,16))==GUARD
  assert bytes(mem.r_block(CODE,len(self.code)))==self.code
  assert bytes(mem.r_block(RESOURCE,len(self.resource)))==self.resource
  assert bytes(mem.r_block(RESOURCE-16,16))==GUARD
  assert bytes(mem.r_block(RESOURCE+len(self.resource),16))==GUARD
  return cpu.r_reg(0)
 def reject(self,addr=None,value=None,event=0,pads=(0,0)):
  saved=self.snapshot()
  if addr is not None:self.mem.w_block(addr,value)
  before=self.snapshot()
  assert self.run(event,pads)==0xffffffff, ('admitted invalid state',hex(addr or 0),value,event)
  assert self.snapshot()==before and not self.events,'failed dispatch was not inert'
  self.restore(saved)

SIZES=SIZES+(74,0,0,22,0,10,514,0)+(10,10,74,0,0,4382,22,32770,566,0,0,494,22,22)+(362,0,0,0,106,134638,0,74)

EXTRA=("recovery_general_task_scheduler","recovery_startup_fade_continue","recovery_gameplay_frame_yield","recovery_music_empty_queue_entry","recovery_music_active_control","recovery_music_duration_prepare","recovery_music_active_envelope","recovery_music_duration_progress","recovery_music_active_command03","recovery_music_active_command02","recovery_startup_video_clear","recovery_startup_bank_select","recovery_startup_resource_load","recovery_startup_title_setup","recovery_title_yield_entry","recovery_chr_nmi_prefix","recovery_title_fade_entry")

SOURCES=("recovery_state_dispatch_startup","recovery_state_dispatch_scheduler","recovery_state_dispatch_active","recovery_state_dispatch_palette","recovery_state_dispatch_prefix")+NAMES+EXTRA

SOURCES=("recovery_state_dispatch_menu",)+SOURCES+("recovery_title_engine_tables","recovery_title_menu_countdown","recovery_title_menu_dispatch","recovery_title_menu_exit","recovery_character_menu_setup","recovery_queued_video_nmi_prefix","recovery_character_selection_dispatch")

SIZES += (22,10,22,22,22)
SOURCES += tuple("recovery_music_active_command"+c for c in ("0e","01","12","13","0f"))

SOURCES = ("recovery_state_menu_sfx",) + SOURCES + ('recovery_character_cursor_sound_request', 'recovery_sfx27_table_dispatch', 'recovery_sfx_header_initialize', 'recovery_sfx_initialized_tail', 'recovery_sfx_stream_entry', 'recovery_sfx_duration_math', 'recovery_sfx_channel_reconfigure', 'recovery_sfx_phase_dispatch', 'recovery_sfx_tick_entry', 'recovery_sfx_command_mask', 'recovery_sfx_event_action', 'recovery_sfx_active_control', 'recovery_sfx_envelope', 'recovery_sfx_stream_control')
SIZES += (6, 14, 6, 2, 18, 6, 30, 30, 30, 78, 14, 2, 514, 30)

SIZES += (22,2)
SOURCES += ("recovery_state_menu_sfx_tail",)

def assemble():
 source=b'\n'.join((PORT/'src'/f'{n}.s').read_bytes() for n in SOURCES)
 with tempfile.TemporaryDirectory() as t:
  src,out=Path(t)/'dispatch.s',Path(t)/'dispatch.bin';src.write_bytes(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True)
  code=out.read_bytes()
 assert CODE+len(code)<RAM-16
 return code

SOURCES=("recovery_scene_continue_dispatch",)+SOURCES+("recovery_post_confirmation_entry","recovery_scene_palette_entry","recovery_scene_sprite_hide","recovery_scene_continue_prepare")
SIZES += (0,0,0,0,0,74,4382)

SOURCES=("recovery_bank_loader_dispatch",)+SOURCES+tuple("recovery_bank_loader_"+n for n in ("restore","prefix","resource","second","assets","fade","fade_entry"))
SIZES+=(22,6,32770,0,154,6,0,0,74,0,0)
