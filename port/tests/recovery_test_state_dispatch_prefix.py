#!/usr/bin/env python3
"""Dynamic native dispatcher versus continuous unmodified cartridge execution.
The cartridge oracle is test-only. It never supplies state or dispatch choices.
"""
import hashlib, json, os, random, struct, subprocess, tempfile
from pathlib import Path
import machine68k
from recovery_state_dispatch_prefix_oracle import ControllerBus, SHA, select_boundary
from py65.devices.mpu6502 import MPU

PORT = Path(__file__).resolve().parents[1]
NAMES = ('recovery_audio_reset_command','recovery_reset_ram','recovery_reset_mapper',
 'recovery_reset_video','recovery_reset_dispatch','recovery_first_yield',
 'recovery_first_nmi_prefix','recovery_nmi_audio_entry','recovery_silent_tick_rti',
 'recovery_scheduler_resume','recovery_resumed_task_setup')
SIZES = (30,0,82,8754,0,6,298,22,22,74,0)
CODE, STOP, RAM, CTX, JOURNAL, RUNTIME, STACK = 0x1000,0x800,0x10000,0x12000,0x13000,0x16000,0x1f0000
GUARD = bytes(range(16))

def context(ref):
 return struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,(ref.p & 0xef)|0x20,ref.sp,0xa7)

def event_kind(address):
 if address >= 0x8000: return 'mapper'
 if address < 0x4000 or address == 0x4014: return 'ppu'
 if address in (0x4016,0x4017): return 'controller'
 return 'apu'

class Native:
 def __init__(self,code):
  self.m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
  self.mem,self.cpu=self.m.mem,self.m.cpu
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
  regs[2]=event;regs[8]=RAM;regs[9]=CTX;regs[10]=JOURNAL;regs[12]=RUNTIME
  cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  self.events.clear();cpu.w_pc(CODE);mem.set_trace_mode(True)
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
  return cpu.r_reg(0)
 def reject(self,addr=None,value=None,event=0,pads=(0,0)):
  saved=self.snapshot()
  if addr is not None:self.mem.w_block(addr,value)
  before=self.snapshot()
  assert self.run(event,pads)==0xffffffff, ('admitted invalid state',hex(addr or 0),value,event)
  assert self.snapshot()==before and not self.events,'failed dispatch was not inert'
  self.restore(saved)

def assemble():
 source=(PORT/'src/recovery_state_dispatch_prefix.s').read_bytes()+b'\n'+b'\n'.join((PORT/'src'/f'{n}.s').read_bytes() for n in NAMES)
 with tempfile.TemporaryDirectory() as t:
  src,out=Path(t)/'dispatch.s',Path(t)/'dispatch.bin';src.write_bytes(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True)
  code=out.read_bytes()
 assert CODE+len(code)<RAM-16
 return code

def run_case(rom,code,pads,delay):
 native=Native(code)
 bus=ControllerBus(rom);bus.inputs=(0,0);bus.pos=[0,0]
 bus[:2048]=[0xa5]*2048;bus.events.clear()
 ref=MPU(memory=bus);ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 count=instructions=nmis=rejections=waits=0
 event=0
 checkpoints=[]
 # Additional per-helper failed guards are selected only by current native PC.
 guards={0xfe24:(CTX+4,b'\x01'),0xfe43:(RAM+0xf6,b'\x01'),
  0xfe67:(RAM+0x97,b'\x01'),0xc574:(RAM+0x91,b'\x01'),
  0xc0bf:(RAM+0xf5,b'\x01'),0x8003:(CTX+2,b'\x00'),
  0xc0f3:(RAM+0xcf,b'\x01'),0xc584:(RAM+0x91,b'\x01')}
 while count<32:
  pc=native.mem.r16(CTX)
  assert pc==ref.pc
  checkpoints.append((native.snapshot(),event))
  # Journal scratch clearing is explicit host output-buffer preparation only.
  # No RAM, context or mapper is ever reloaded along the successful chain.
  native.mem.w_block(RUNTIME+6,bytes.fromhex("baddf00d"))
  native.mem.w_block(JOURNAL,bytes(8754))
  before=native.snapshot()
  start=len(bus.events);dma_start=len(bus.dma)
  expected_status,index,target=select_boundary(ref,bus,event)
  result=native.run(event,pads)
  assert result==(expected_status & 0xffffffff)
  if result==0xffffffff:
   assert native.snapshot()==before and not native.events, 'terminal rejection changed state'
   assert pc==0xfe8d and native.mem.r8(RAM+0x18)==0xff
   break
  if result==0:
   assert native.snapshot()==before
   for _ in range(delay):
    assert native.run(0,pads)==0 and native.snapshot()==before
    waits+=1
   event=1;waits+=1;continue
  assert result==1
  assert native.mem.r16(RUNTIME+6)==index
  size=native.mem.r16(RUNTIME+8)
  assert size==SIZES[index]
  if event:
   assert index==6 and ref.pc==0xfe8d
   ref.nmi();nmis+=1
  if index==9:bus.inputs=pads;bus.pos=[0,0]
  for _ in range(50000):
   ref.step();instructions+=1
   if ref.pc==target:break
  else:raise AssertionError(('original timeout',index,hex(ref.pc)))
  event=0;count+=1
  ram,ctx,journal,runtime=native.snapshot()
  assert ram==bytes(bus[:2048]),('RAM',index)
  assert ctx==context(ref),('context',index,ctx.hex(),context(ref).hex())
  assert tuple(runtime[:4])==bus.mapper.snapshot()[:4] and runtime[4:6]==b'\0\0'
  assert not bus.mapper.bits
  assert native.events==bus.events[start:],('ordered effects',index,native.events[:4],bus.events[start:start+4])
  kind='mapper' if index in (2,7,8) else 'apu' if index==0 else 'controller' if index==9 else 'ppu'
  effects=[e for e in bus.events[start:] if e[0]==kind]
  expected=b''
  if size:
   expected=struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',*e[1:]) for e in effects)
   if index==6:
    assert len(bus.dma)==dma_start+1
    expected+=bus.dma[-1]
   expected+=bytes(size-len(expected))
  else:assert not effects
  assert journal[:size]==expected and journal[size:]==bytes(8754-size)
 else:raise AssertionError('did not reach safe unsupported boundary')
 assert count==11 and nmis==1 and ref.pc==0xfe8d and bus[0x18]==0xff
 final=native.snapshot()
 native.m.cleanup()
 # machine68k is process-global: run isolated adversarial machines only after
 # finishing the uninterrupted resident chain, never simultaneously.
 for saved,event in checkpoints:
  probe=Native(code);probe.restore(saved)
  pc=probe.mem.r16(CTX)
  probe.reject(CTX,b'\x12\x34',event);rejections+=1
  probe.reject(RUNTIME+3,b'\x05',event);rejections+=1
  probe.reject(RUNTIME+10,b'\x00\x00',event);rejections+=1
  probe.reject(RUNTIME+4,b'\x01',event);rejections+=1
  probe.reject(RUNTIME+5,b'\x01',event);rejections+=1
  probe.reject(event=2);rejections+=1
  probe.reject(RUNTIME,b"\x00",event=event);rejections+=1
  if pc!=0xfe8d:
   probe.reject(event=1);rejections+=1
  if pc in guards:
   probe.reject(*guards[pc],event=event);rejections+=1
  if event:
   probe.reject(CTX+5,b'\x30',event=event);rejections+=1
  probe.m.cleanup()
 probe=Native(code);probe.restore(final)
 probe.reject(event=1,pads=pads);rejections+=1
 probe.m.cleanup()
 result=dict(pads=list(pads),delayed_NMI_polls=delay,advanced_calls=count,
  logical_NMIs=nmis,waits=waits,inert_rejections=rejections,
  original_instructions=instructions,final_context=context(ref).hex(),
  final_mapper=list(bus.mapper.snapshot()[:4]),code_sha256=hashlib.sha256(code).hexdigest())
 return result

def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 assert hashlib.sha256(rom).hexdigest()==SHA
 code=assemble();assert code==assemble()
 cases=[run_case(rom,code,pads,delay) for pads,delay in
  [((0,0),0),((0,0),7),((0x10,0),2),((1,0),1),((2,0),3),((4,8),0),((0xff,0xff),1)]]
 report=dict(status='PASS',scope='host M68EC020 state-driven first-NMI prefix',
  code_bytes=len(code),cases=cases,
  limits=['No title or character-menu reachability','No release/repress edge across repeated controller polls',
  'No timeout path','No resource-reading helper admitted','No physical target, display, audio or timing claim'])
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
