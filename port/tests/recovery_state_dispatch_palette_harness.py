"""ROM-free native harness. No original-ROM loading or oracle imports."""
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
RESOURCE = 0x30000
CODE, STOP, RAM, CTX, JOURNAL, RUNTIME, STACK = 0x1000,0x800,0x10000,0x12000,0x13000,0x16000,0x1f0000
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
  self.regions=((RAM,2048),(CTX,8),(JOURNAL,8754),(RUNTIME,12))
  for addr,size in self.regions:self.mem.w_block(addr-16,GUARD+bytes(size)+GUARD)
  self.mem.w_block(RAM,bytes([0xa5])*2048)
  self.mem.w_block(CTX,bytes.fromhex('fe2417330024fda7'))
  self.mem.w_block(RUNTIME,bytes.fromhex('0c0000030000ffff0000d501'))
  def trace(mode,width,addr,value):
   size=1<<width
   ranges=[(a,a+n) for a,n in self.regions]+[(STACK-512,STACK)]
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
    self.events.append((event_kind(a),a,v,k))
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
  cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  self.events.clear();self.reads.clear();cpu.w_pc(CODE);mem.set_trace_mode(True)
  for _ in range(1000):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('native dispatch timeout')
  mem.set_trace_mode(False)
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

def assemble():
 source=(PORT/'src/recovery_state_dispatch_palette.s').read_bytes()+b'\n'+(PORT/'src/recovery_state_dispatch_prefix.s').read_bytes()+b'\n'+b'\n'.join((PORT/'src'/f'{n}.s').read_bytes() for n in NAMES)
 with tempfile.TemporaryDirectory() as t:
  src,out=Path(t)/'dispatch.s',Path(t)/'dispatch.bin';src.write_bytes(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True)
  code=out.read_bytes()
 assert CODE+len(code)<RAM-16
 return code

