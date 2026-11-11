#!/usr/bin/env python3
"""One resident native RAM/context pair, reset through genuine title countdown/input loops.
Separate composition derived from frozen title menu loop test; original unchanged.
Reference executes continuously; no captured-state injection or RAM/context reload.
"""
import hashlib,random,os,struct,subprocess,tempfile
from pathlib import Path
import machine68k
from recovery_test_active_command0e_rom import Ricoh as MPU
from verify_recovery_runtime_probe import PREFIX,TARGETS,architectural_status_view
from recovery_test_active_nmi_runtime_chain import ControllerBus,SerialMapper,SHA
from recovery_test_repeated_command02_audio import reference as audio_reference
from recovery_test_active_command02_contract import command02
from recovery_test_active_control_contract import declarative as control_model
from recovery_test_music_duration_prepare_contract import contract as prepare_model
from recovery_test_music_duration_progress_contract import declarative as progress_model
from recovery_music_envelope_declarative import envelope
from recovery_test_active_command03_contract import command03
from recovery_test_active_command0e_contract import command0e,validation_reads as command0e_validation_reads
from recovery_test_active_command0e_rom import reference as command0e_reference
PORT=Path(__file__).resolve().parents[1]
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000

NAMES=('recovery_audio_reset_command', 'recovery_reset_ram', 'recovery_reset_mapper', 'recovery_reset_video', 'recovery_reset_dispatch', 'recovery_first_yield', 'recovery_first_nmi_prefix', 'recovery_nmi_audio_entry', 'recovery_silent_tick_rti', 'recovery_scheduler_resume', 'recovery_resumed_task_setup', 'recovery_palette_nmi_prefix', 'recovery_music07_command', 'recovery_music_tick_fetch', 'recovery_music_command04', 'recovery_music_stream_fetch', 'recovery_music_command05', 'recovery_music_command06', 'recovery_music_stream_command07_volume', 'recovery_music_event_instrument08', 'recovery_music_event_command18', 'recovery_music_event_command09', 'recovery_music_event_rest', 'recovery_music_channel_iteration', 'recovery_music_indexed_fetch', 'recovery_music_indexed_commands', 'recovery_music_indexed_rest', 'recovery_music_pitched_gate', 'recovery_music_pitched_note', 'recovery_active_nmi_return', 'recovery_general_task_scheduler', 'recovery_idle_nmi_prefix', 'recovery_music_active_control', 'recovery_music_duration_prepare', 'recovery_music_active_envelope', 'recovery_music_duration_progress', 'recovery_music_active_command03', 'recovery_startup_fade_continue', 'recovery_gameplay_frame_yield', 'recovery_music_empty_queue_entry', 'recovery_startup_video_clear', 'recovery_startup_bank_select', 'recovery_startup_resource_load', 'recovery_startup_title_setup', 'recovery_title_yield_entry', 'recovery_chr_nmi_prefix', 'recovery_title_fade_entry', 'recovery_music_active_command02', 'recovery_title_engine_tables', 'recovery_title_engine_wait', 'recovery_title_menu_countdown', 'recovery_title_menu_dispatch', 'recovery_title_menu_exit', 'recovery_music_active_command0e')
SIZES={0: 30, 1: 0, 2: 82, 3: 8754, 4: 0, 5: 6, 6: 298, 7: 22, 8: 22, 9: 74, 10: 0, 11: 454, 12: 30, 13: 6, 14: 14, 15: 6, 16: 18, 17: 14, 18: 14, 19: 22, 20: 14, 21: 14, 22: 10, 23: 0, 24: 6, 25: 22, 26: 10, 27: 10, 28: 18, 29: 22, 30: 74, 31: 454, 32: 0, 33: 10, 34: 514, 35: 0, 36: 10, 37: 512, 38: 512, 39: 22, 40: 4382, 41: 22, 42: 32770, 43: 566, 44: 8, 45: 494, 46: 512, 47: 10, 48: 362, 49: 8, 50: 16, 51: 16, 52: 256, 53: 22}

class CompleteBus(ControllerBus):
 def __setitem__(self,a,v):
  if isinstance(a,int) and (0x4000<=a<=0x4013 or a==0x4015):
   self.events.append(('apu',a,v,1));return
  super().__setitem__(a,v)
def view(ref):return architectural_status_view(struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7))
def kind(index):
 if index in (2,7,8,29,39,41):return 'mapper'
 if index in (0,12):return 'apu'
 if index in (9,30):return 'controller'
 if index in (13,14,15,16,17,18,19,20,21,22,24,25,26,27,28,33,36,47,48,53):return 'resource'
 return 'ppu'
RESOURCE2=0x28000
FIXED=0x30000
class Native:
 def __init__(self,resource,resource2,fixed):
  with tempfile.TemporaryDirectory() as tmp:
   source,out=Path(tmp)/'native.s',Path(tmp)/'native.bin'
   source.write_text(''.join(' bra.w '+n+'\n' for n in NAMES)+'\n'.join((PORT/'src'/(n+'.s')).read_text() for n in NAMES))
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
   if mode=='W' and a==JOURNAL and width==1 and v and self.index not in (37,38,44,46,49,50,51,52):
    assert 1<=v<=(size-2)//4
    at=JOURNAL+2+4*(v-1);address,value,k=mem.r16(at),mem.r8(at+2),mem.r8(at+3)
    typ=('apu' if k else 'resource') if self.index==34 else kind(self.index)
    if self.index in (42,43):typ='resource' if k==0 else 'ppu';k=0 if k in (0,2) else 1
    if self.index==45:typ='mapper' if address>=0x8000 else 'ppu'
    self.events.append((typ,address,value,k))
    if typ=='mapper':self.mapper.write(address,value)
    if typ=='ppu' and address==0x4014:
     offset=42 if self.index==6 else 238 if self.index==45 else 198
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
 def run(self,index,status=None):
  self.index=index;mem,cpu=self.mem,self.cpu;size=SIZES[index];mem.set_trace_mode(False)
  mem.w_block(JOURNAL-16,self.guard+bytes(size)+self.guard)
  regs=[self.rng.getrandbits(32) for _ in range(15)];regs[8:12]=[BASE,CTX,JOURNAL,FIXED if index==48 else RESOURCE2 if index in (42,43) else RESOURCE]
  if index in (9,30):regs[0]=(regs[0]&0xffffff00)|self.pads[0];regs[1]=(regs[1]&0xffffff00)|self.pads[1]
  cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_pc(CODE+index*4);self.events.clear();self.reads.clear();mem.set_trace_mode(True)
  for _ in range(1500):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('native timeout')
  mem.set_trace_mode(False);self.status=cpu.r_reg(0);self.calls+=1
  assert self.status!=0xffffffff,('native rejection',index,self.state()[1].hex())
  if status is not None:assert self.status==status
  assert cpu.r_sp()==STACK+4 and [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,size),(RESOURCE,16384),(RESOURCE2,16384),(FIXED,16384)):
   assert bytes(mem.r_block(a-16,16))==self.guard and bytes(mem.r_block(a+n,16))==self.guard
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
 bootstrap_counts=dict(counts);nmis=0;fade_samples=0;frame=None;idle=False;audio_calls=0;fade_values=[];title_started=False;chr_consumed=False;title_entry_calls=0;command02_calls=0;command0e_calls=0
 menu_cycles=0;menu_input=int(os.environ.get("MENU_INPUT","0"),0)
 for boundary in range(100000):
  pc=ref.pc
  if pc in (0xf379,0xa05c,0xc5f8) or (pc==0x83a0 and ref.a not in (2,3,4,5,6,7,8,9,14,24) and ref.a<32):break
  if native.calls==2318:
   assert view(ref)==bytes.fromhex('83a00e2a00a4f2a7') and menu_cycles==42
   assert counts=={'ram':31652,'ppu':4731,'mapper':810,'controller':1386,'resource':4410,'apu':601}
  if pc==0xa025:
   if menu_cycles==0:
    assert native.calls==1077 and view(ref)==bytes.fromhex('a025ffffffa4bda7')
    assert bus[0xbe:0xc0]==[0x84,3] and bus[0x1be:0x1c0]==[0xf7,0xc5]
    assert bus.mapper.snapshot()==(30,31,31,2,())
   menu_cycles+=1
   if menu_cycles==int(os.environ.get('MENU_CYCLES','901')):break
  before=native.state();assert before==(bytes(bus[:2048]),view(ref))
  start=len(bus.events);dma_start=len(bus.dma)
  if pc==0x83a0 and ref.a==14:
   index=53;command0e_calls+=1
   assert bus.bank==3 and not bus.mapper.bits
   command0e_reference(bus,ref)
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
   index=30;native.pads=(menu_input if menu_cycles else 0,0);bus.inputs,bus.pos=native.pads,[0,0]
   for _ in range(1000):
    at=ref.pc;ref.step();instructions+=1
    if (ref.pc==0xfe90 and at==0xfea3) or ref.pc in (0xc2a8,0xc597,0xc5ce,0xa025):break
   else:raise AssertionError('scheduler timeout')
   idle=ref.pc==0xfe90
  elif pc==0xfe90 and idle:
   index=45 if title_started else 31;idle=False;nmis+=1;saved_sp=ref.sp
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
  got=native.run(index)
  assert got==want,('resident mismatch',boundary,index,got[1].hex(),want[1].hex(),[(i,a,b) for i,(a,b) in enumerate(zip(got[0],want[0])) if a!=b],got[2],want[2])
  assert native.mapper.snapshot()==bus.mapper.snapshot()
  if index in (37,38,44,46,49,50,51,52):
   assert all(e[0]=='ram' for e in want[2])
   expected=b''.join(struct.pack('>HBB',e[1],e[2],0) for e in want[2]);assert native.status==len(want[2])
  else:
   assert native.status==(int(not idle) if index==30 else 1)
   je=[e for e in want[2] if e[0] in (('apu','resource') if index==34 else (kind(index),))]
   expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',*e[1:]) for e in je) if SIZES[index] else b''
   if index in (42,43):
    je=[e for e in want[2] if e[0] in ('resource','ppu')]
    expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',e[1],e[2],0 if e[0]=='resource' else 1 if e[3] else 2) for e in je)
   if index==45:
    je=[e for e in want[2] if e[0] in ('ppu','mapper')]
    expected=struct.pack('>H',len(je))+b''.join(struct.pack('>HBB',*e[1:]) for e in je)
   if index in (31,45):
    expected+=bytes((238 if index==45 else 198)-len(expected))+bus.dma[-1]
  assert bytes(native.mem.r_block(JOURNAL,SIZES[index]))==expected+bytes(SIZES[index]-len(expected))
  semantic=[e[1]-0x8000 for e in want[2] if e[0]=='resource']
  if index==32:assert control_model(*before)==want;assert native.reads==[]
  elif index==33:
   model,reads=prepare_model(*before,native.resource);assert model[:3]==want;assert native.reads==reads
  elif index==34:
   assert envelope(*before,native.resource)==want;assert native.reads==[0x92e]+list(range(0x6bf,0x6c9))+semantic
  elif index==35:assert progress_model(*before)==want;assert native.reads==[]
  elif index==36:assert command03(*before,native.resource)==want;assert native.reads==[0x489,0x48a]+semantic
  if index==53:
   assert command0e(*before,native.resource)==want
   assert native.reads==command0e_validation_reads(*before,native.resource)+semantic
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
  if index==48:
   from recovery_test_title_engine_tables import model
   assert model(*before,native.fixed)==want
   assert native.reads==[e[1]-0xc000 for e in want[2] if e[0]=='resource']
  if index==49:
   from recovery_test_title_engine_wait import model
   predicted=model(*before);assert predicted[:2]==want[:2] and [('ram',a,v) for a,v in predicted[2]]==want[2]
  if index in (50,51,52):
   predicted=menu_model(*before)
   assert predicted[:2]==want[:2] and [('ram',a,v) for a,v in predicted[2]]==want[2]
   assert native.reads==[]
  for e in want[2]:counts[e[0]]+=1
 else:raise AssertionError('boundary bound')
 if 'MENU_CYCLES' not in os.environ:
  if menu_input==0:
   assert (native.calls,menu_cycles,nmis+2,audio_calls,command02_calls,command0e_calls)==(7038,193,229,226,3,34)
   assert counts=={'ram':78580,'ppu':6241,'mapper':2320,'controller':4104,'resource':12714,'apu':1794}
   assert view(ref)==bytes.fromhex('83a0012b00a5f2a7')
  elif menu_input in (1,2,16,32):
   assert native.calls==1104 and menu_cycles==2 and nmis+2==37 and audio_calls==35 and command0e_calls==0
   assert counts=={'ram':17441 if menu_input==16 else 17445,'ppu':4321,'mapper':405,'controller':666,'resource':2342,'apu':266}
 assert native.state()==(bytes(bus[:2048]),view(ref))
 assert chr_consumed and title_entry_calls==2
 assert ref.pc in (0xa025,0x83a0,0xf379,0xa05c,0xc5f8)
 assert bus.bank==(3 if ref.pc==0x83a0 else 2) and bus.mapper.control==0x1e and not bus.mapper.bits
 assert bus[0x1a]==bus[0x1b]==0 and bus[0xf2]==bus[0xf3]==31
 assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 assert bus[0xbe]+256*bus[0xbf]==900-menu_cycles+(ref.pc==0xa025)
 assert bus[0x1be:0x1c0]==[0xf7,0xc5]
 print('PASS resident native reset→menu boundary:',native.calls,'helper calls;',nmis+2,'real reference NMIs;',audio_calls,'later active audio calls;',command02_calls,'command02 calls;',command0e_calls,'command0E calls;',counts,'ordered effects; final context',view(ref).hex(),'mapper',native.mapper.snapshot())
 print('One RAM/context load at reset; no state reload or patched readiness/status/return frame. Complete RAM/context/effects, ABI, journals/DMA, immutable resources, global bounds.')
 print('Assembled composite bytes/SHA256:',len(native.code),hashlib.sha256(native.code).hexdigest())
 print('Menu A025 visits:',menu_cycles,'timer:',bus[0xbe]+256*bus[0xbf],'matched external input:',menu_input,'next boundary:',hex(ref.pc),'A:',hex(ref.a));print('Host M68EC020 only; no target/speed claim.')
 native.m.cleanup()
if __name__=='__main__':main()
