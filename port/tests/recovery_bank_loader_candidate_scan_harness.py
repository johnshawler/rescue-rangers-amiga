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
RESOURCE = 0x90000
CODE, STOP, RAM, CTX, JOURNAL, RUNTIME, STACK = 0x1000,0x800,0x40000,0x42000,0x43000,0x70000,0x1f0000
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
  marker=bytes.fromhex("022900ef00054e75")
  self.adapter_address=CODE+code.index(marker) if code.count(marker)==1 else None
  self.context_shadow=bytearray(8);self.raw_adapter_context=None
  self.code=code; self.rng=random.Random(0xd501); self.events=[]
  self.mem.w_block(CODE,code); self.mem.w16(STOP,0x60fe)
  self.regions=((RAM,2048),(CTX,8),(JOURNAL,134638),(RUNTIME,12))
  for addr,size in self.regions:self.mem.w_block(addr-16,GUARD+bytes(size)+GUARD)
  self.mem.w_block(RAM,bytes([0xa5])*2048)
  self.mem.w_block(CTX,bytes.fromhex('fe2417330024fda7'))
  self.mem.w_block(RUNTIME,bytes.fromhex('0c0000030000ffff0000d501'))
  def trace(mode,width,addr,value):
   size=1<<width
   ranges=[(a,a+n) for a,n in self.regions]+[(STACK-4096,STACK)]
   if mode=='R':ranges += [(RESOURCE,RESOURCE+len(self.resource))]
   if RESOURCE<=addr<RESOURCE+len(self.resource):
    assert mode=='R' and width==0
    self.reads.append(addr-RESOURCE)
   if mode=='R':ranges += [(CODE,CODE+len(code)),(STOP,STOP+4),(STACK,STACK+4)]
   assert mode in ('R','W') and any(a<=addr and addr+size<=b for a,b in ranges),(mode,width,hex(addr))
   if mode=='W' and CTX<=addr and addr+size<=CTX+8:
    if self.adapter_address is not None and self.adapter_address<=self.cpu.r_pc()<=self.adapter_address+8:
     self.raw_adapter_context=bytes(self.context_shadow)
    self.context_shadow[addr-CTX:addr-CTX+size]=value.to_bytes(size,'big')
   if mode=='W' and RAM<=addr<RAM+2048:
    assert width==0; self.events.append(('ram',addr-RAM,value))
   if mode=='W' and addr==JOURNAL and width==1 and value:
    at=JOURNAL+2+4*(value-1)
    a,v,k=self.mem.r16(at),self.mem.r8(at+2),self.mem.r8(at+3)
    pc=self.mem.r16(CTX)
    typ='resource' if pc in (0xf977,0xf9d7,0xf9e4) else 'resource' if pc in (54947, 55007, 55056, 55429, 55441, 55467, 55479, 55497, 55511, 55556, 55570, 55732, 55756, 55766, 55798, 55844, 55888, 55924, 55981, 55983, 56007, 56061, 56084, 56144, 56175, 56208, 56602, 56653, 56659, 56698, 56775, 56909, 56929, 56970, 57000, 57011, 57016, 57017, 57034, 57037, 57070, 57089, 57092, 59849) else 'resource' if pc in (54247, 54283, 54325, 54368) else 'resource' if (pc in (60047, 60064, 60167, 60172, 60175, 60176, 60219, 60730, 60737, 60763, 60770, 60794, 60825, 60917, 60963, 61440, 61447, 61454, 61500, 61503, 61524, 61533, 61542, 61549, 61556, 61609, 61612, 61633, 61642, 61651, 61658, 61661, 61670, 61671, 61678, 61681, 61690, 61691, 61713, 61720, 61757, 61763, 61766, 61786, 61789, 61801, 61808, 61847, 61853, 61856, 61865, 61868, 61870, 61890, 61899, 61902, 61911, 61930, 61933, 61937, 61944, 61947, 61950, 61968, 61971, 61975, 61982, 62012, 62042, 62079, 62114, 62149, 62186, 62194, 62200, 62203, 62237, 62886, 62908, 62923, 63020, 63021, 63056, 63063, 63126, 63196, 63265, 63294, 63308, 63318, 63340, 63362, 63411, 63432, 63442, 63460) or self.mem.r8(RUNTIME+3)==6 and pc in (32768, 32799, 32809, 32819, 32848, 36373, 36376, 36378, 36402, 33212, 35784, 35798, 35874, 36664, 36684, 36732, 36739, 36754, 36762)) else 'resource' if pc in (51520, 51526, 51532, 51563, 51664, 51743, 51761, 51790, 51874, 51910, 51930, 51940, 52080, 52083, 52088, 52110, 52127, 52140, 52147, 52172, 52185, 52233, 52248, 52257, 52320, 52333, 54543, 54544, 54617, 54650, 54659, 54664, 54682, 54693, 54704, 54712, 54723, 54734, 54738, 54788, 54831) else 'resource' if pc in (51067, 51078, 51093, 51111, 51114, 51140, 51149, 51152, 51167, 51175, 51184, 51189, 51192, 51210, 51230, 51233, 51240, 51243, 51248, 51255, 51258, 51265, 51272, 51291, 51294, 51321, 51371, 51376, 51379, 51416, 51424, 49694, 49884, 62329, 51438) else 'resource' if pc in (0x8040,0x8090,0xe106,0xe10c,0xe10f,0xc262,0xc265,0xc703,0xc617) else 'resource' if pc in (0xe179,0xe17c,0xe1d3,0xe1e4,0xe1e7,0xe1ea,0xdbec,0xdc5c,0xdc5f,0xdf97,0xe028) else ('mapper' if a==0xfff0 else 'resource') if pc==0xc6b5 else ('resource' if k==0 else 'ppu') if pc in (0xc115,0xc14e,0xc158,0xc24a,0xe099) else 'resource' if pc in (0x911c,0x911f,0xc60a,0x92ac,0x9475,0x9478,0x947b,0x947e) else ('resource' if k==0 else 'ppu') if pc==0x8000 else 'resource' if pc in (0x9003,0x9039,0x9041) else 'resource' if pc in (0xa07b,0x8003,0x810d,0x8224,0x8006,0x8298,0x82b0,0x82c0,0x82dc) and k==0 else 'apu' if pc in (0x81a3,0x8235) else ('resource' if k==0 else 'apu') if pc in (0x830b,0x831b) or pc==0x86b2 and self.mem.r8(CTX+3)<4 else 'resource' if pc==0xc5d1 or (pc==0xa05c and 0x8000<=a<0xc000) else 'resource' if pc in (0xc0f3,0x839d,0x83a0,0x83fd,0x8374,0x86b2,0xc5c0,0xc5c5) and 0x8000<=a<0xc000 else event_kind(a)
    self.events.append((typ,a,v,0 if pc in (0xc5c0,0xc5c5,0x8000) and k==2 else k))
  self.mem.set_trace_func(trace)
  self.trace=trace
 def snapshot(self):return tuple(bytes(self.mem.r_block(a,n)) for a,n in self.regions)
 def restore(self,snapshot):
  for (a,n),v in zip(self.regions,snapshot):self.mem.w_block(a,v)
 def run(self,event=0,pads=(0,0)):
  mem,cpu=self.mem,self.cpu
  self.context_shadow=bytearray(mem.r_block(CTX,8));self.raw_adapter_context=None
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

SOURCES=("recovery_bank_loader_object_dispatch",)+SOURCES+("recovery_bank_loader_object_bridge","recovery_object_region")
SIZES+=(60002,0,0,0,74,0)

SOURCES=("recovery_bank_loader_dialogue_dispatch",)+SOURCES+tuple("recovery_bank_loader_dialogue_"+n for n in ("region","bridge","nmi"))
SIZES+=(60002,74,134638,60002)

SOURCES=("recovery_bank_loader_stage_dispatch",)+SOURCES+("recovery_bank_loader_stage_init","recovery_bank_loader_stage_fixed","recovery_gameplay_player_init","recovery_gameplay_fade_entry")
SIZES+=(0,)*10+(70,0,0,0,74,60002)

SOURCES=("recovery_bank_loader_map_dispatch",)+SOURCES+("recovery_stage_map_region",)
SIZES=SIZES[:100]+(60002,)+SIZES[101:]

SOURCES=("recovery_bank_loader_finish_dispatch",)+SOURCES+("recovery_stage_object_region","recovery_bank_loader_stage_finish","recovery_bank_loader_stage_fade_in")
SIZES+=(60002,)+(0,)*13+(60002,0,0,74)

SOURCES=("recovery_bank_loader_music_dispatch",)+SOURCES+("recovery_bank_loader_stage_music",)
SIZES+=(60002,)

SOURCES=("recovery_bank_loader_frame_dispatch",)+SOURCES+("recovery_bank_loader_frame_region",)
SIZES+=(60002,)

SOURCES=("recovery_bank_loader_action_dispatch",)+SOURCES+("recovery_player_action_region",)
SIZES+=(0,)*14+(60002,)

SOURCES=("recovery_bank_loader_collision_dispatch",)+SOURCES+("recovery_player_collision_region","recovery_player_frame_region")
SIZES=SIZES[:140]+(60002,)+SIZES[141:]+(60002,)

SOURCES+=("recovery_bank_loader_canonical_status",)

SOURCES=("recovery_bank_loader_carry_dispatch",)+SOURCES+("recovery_bank_loader_carry_region",)
SIZES=SIZES[:136]+(60002,)+SIZES[137:]

SOURCES=("recovery_bank_loader_play_dispatch",)+SOURCES+("recovery_bank_loader_palette_cycle","recovery_stage_scroll_region")
SIZES=SIZES[:137]+(60002,74)+SIZES[139:]+(0,)*8+(60002,)

SOURCES=("recovery_bank_loader_input_dispatch",)+SOURCES

SOURCES=("recovery_bank_loader_queue5_dispatch",)+SOURCES

SOURCES=("recovery_bank_loader_sfx_dispatch",)+SOURCES+("recovery_bank_loader_sfx_entry",)
SIZES=SIZES[:139]+(1926,)+SIZES[140:]

SOURCES=("recovery_bank_loader_envelope_dispatch",)+SOURCES

SOURCES=("recovery_bank_loader_scroll_status_dispatch",)+SOURCES

SOURCES=("recovery_bank_loader_video5_dispatch",)+SOURCES+("recovery_bank_loader_video5_preflight",)

SOURCES=("recovery_bank_loader_target_choice_dispatch",)+SOURCES+("recovery_bank_loader_target_choice_region",)
SIZES=SIZES[:152]+(2,)+SIZES[153:]

SOURCES=("recovery_bank_loader_candidate_scan_dispatch",)+SOURCES+("recovery_bank_loader_candidate_scan_region",)
SIZES=SIZES[:153]+(18,)+SIZES[154:]
