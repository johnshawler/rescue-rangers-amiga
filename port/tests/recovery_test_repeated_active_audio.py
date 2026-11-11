#!/usr/bin/env python3
"""Resident-buffer standalone repeated audio calls from independently booted ROM state.
Not a full native reset/frame-continuity proof: C2A8 game task is not run here.
"""
import argparse,hashlib,random,os,subprocess,tempfile
from pathlib import Path
import machine68k
from py65.devices.mpu6502 import MPU
from recovery_test_music_pitched_event_chain import ControllerBus
from recovery_test_active_control_rom import run_control
from recovery_test_active_control_contract import declarative as control_model
from recovery_test_music_duration_prepare_contract import contract as prepare_model
from recovery_test_music_duration_progress_contract import declarative as progress_model
from recovery_test_active_envelope_rom import run_original as run_envelope
from recovery_test_music_indexed_rom import run_original as run_parser
from recovery_test_music_indexed_contract import contract as parser_model,COMMANDS
from recovery_test_music_pitched_gate_rom import run_gate
from recovery_test_music_pitched_note_rom import run_note
from recovery_test_music_pitched_gate_contract import contract as gate_model
from recovery_test_music_pitched_note_contract import contract as note_model
from recovery_test_active_command03_contract import command03
from recovery_music_envelope_declarative import envelope
PORT=Path(__file__).resolve().parents[1]
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
NAMES=('recovery_music_active_control','recovery_music_duration_prepare','recovery_music_active_envelope','recovery_music_duration_progress','recovery_music_indexed_fetch','recovery_music_indexed_commands','recovery_music_indexed_rest','recovery_music_pitched_gate','recovery_music_pitched_note','recovery_music_active_command03')
SIZES=(0,10,514,0,6,22,10,10,18,10)
class Bus(ControllerBus):
 def __setitem__(self,a,v):
  if isinstance(a,int) and 0x4000<=a<=0x4015:
   self.events.append(('apu',a,v,1));return
  super().__setitem__(a,v)
def context(ref,r=0):return ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,(ref.p&0xef)|32,ref.sp,r))
def boot(rom,seed):
 rng=random.Random(seed);bus=Bus(rom);ref=MPU(memory=bus);bus[:2048]=rng.randbytes(2048)
 ref.pc=0xfe24;ref.a,ref.x,ref.y,ref.p,ref.sp=0,0,0,0x20,seed&255
 def until(pc):
  for _ in range(100000):
   if ref.pc==pc:return
   ref.step()
  raise AssertionError(('bootstrap timeout',hex(pc),hex(ref.pc)))
 until(0xc574);until(0xfe8d);ref.nmi();until(0xc0f3);until(0xfe8d)
 bus.inputs=(seed&255,seed^255);until(0xc584);until(0xfe8d);ref.nmi();until(0xc0f9)
 assert bus.bank==3 and bus[0xcf]==0
 return bus,ref

def reference(bus,ref,index):
 if index==9:
  start=len(bus.events)
  for _ in range(60):
   pc=ref.pc
   if pc==0x839d:break
   assert 0x83a0<=pc<=0x83a7 or 0x8473<=pc<=0x8480 or 0x8023<=pc<=0x8037 or 0x84c4<=pc<=0x84cc,hex(pc)
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

class Native:
 def __init__(self,resource):
  with tempfile.TemporaryDirectory() as tmp:
   src,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
   src.write_text(''.join(' bra.w '+n+'\n' for n in NAMES)+'\n'.join((PORT/'src'/(n+'.s')).read_text() for n in NAMES))
   subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);self.code=out.read_bytes()
  self.m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);self.mem,self.cpu=self.m.mem,self.m.cpu;mem=self.mem
  mem.w_block(CODE,self.code);mem.w16(STOP,0x60fe);self.resource=resource;self.guard=bytes(range(16));self.rng=random.Random(0x86b2);self.index=0;self.events=[];self.reads=[]
  mem.w_block(RESOURCE-16,self.guard+resource+self.guard)
  def trace(mode,width,addr,v):
   n=1<<width;size=SIZES[self.index]
   ranges=((CODE,CODE+len(self.code)),(STOP,STOP+4),(BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+size),(RESOURCE,RESOURCE+16384),(STACK-512,STACK+4)) if mode=='R' else ((BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+size),(STACK-512,STACK))
   assert mode in ('R','W') and any(lo<=addr and addr+n<=hi for lo,hi in ranges),(mode,width,hex(addr),self.index)
   if mode=='R' and RESOURCE<=addr<RESOURCE+16384:
    assert width==0;self.reads.append(addr-RESOURCE)
   if mode=='W' and BASE<=addr<BASE+2048:
    assert width==0;self.events.append(('ram',addr-BASE,v))
   if mode=='W' and addr==JOURNAL and width==1 and v:
    assert v<=(size-2)//4
    at=JOURNAL+2+4*(v-1);kind=mem.r8(at+3)
    self.events.append(('apu' if kind else 'resource',mem.r16(at),mem.r8(at+2),kind))
  mem.set_trace_func(trace)
  for mode in ('R','W'):
   for a in (0,0x25000,0x90000,BASE+2047):
    try:trace(mode,2,a,0)
    except AssertionError:pass
    else:raise AssertionError('global bound failure')
 def load(self,s,c):
  self.mem.set_trace_mode(False)
  self.mem.w_block(BASE-16,self.guard+s+self.guard);self.mem.w_block(CTX-16,self.guard+c+self.guard)
 def call_entry(self):
  # Caller starts a fresh standalone audio invocation. RAM and other CPU fields persist.
  self.mem.set_trace_mode(False);self.mem.w16(CTX,0xc0f6)
 def state(self):return bytes(self.mem.r_block(BASE,2048)),bytes(self.mem.r_block(CTX,8))
 def run(self,index):
  self.index=index;mem,cpu=self.mem,self.cpu;size=SIZES[index]
  mem.set_trace_mode(False);mem.w_block(JOURNAL-16,self.guard+self.rng.randbytes(size)+self.guard)
  regs=[self.rng.getrandbits(32) for _ in range(15)];regs[8:12]=[BASE,CTX,JOURNAL,RESOURCE]
  cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_pc(CODE+index*4);self.events.clear();self.reads.clear();mem.set_trace_mode(True)
  for _ in range(400):
   cpu.execute(1000)
   if cpu.r_pc()==STOP:break
  else:raise AssertionError('native timeout')
  mem.set_trace_mode(False)
  assert cpu.r_reg(0)==1,('native reject',index,self.state()[1].hex())
  assert cpu.r_sp()==STACK+4 and [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
  for a,n in ((BASE,2048),(CTX,8),(JOURNAL,size),(RESOURCE,16384)):
   assert bytes(mem.r_block(a-16,16))==self.guard and bytes(mem.r_block(a+n,16))==self.guard
  assert bytes(mem.r_block(RESOURCE,16384))==self.resource
  return self.state()+ (list(self.events),)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ticks',type=int,default=16);parser.add_argument('--sequences',type=int,default=16);args=parser.parse_args()
 assert 1<=args.ticks<=41 and 1<=args.sequences<=256
 path=PORT.parent/'input/rescue-rangers-europe.nes';rom=path.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 resource=rom[49168:65552];n=Native(resource);total=apu=0
 for seed in range(args.sequences):
  bus,ref=boot(rom,seed);n.load(bytes(bus[:2048]),context(ref));tick_apu=[]
  for tick in range(1,args.ticks+1):
   ref.pc=0xc0f6;n.call_entry();this_apu=0
   for call in range(500):
    pc=ref.pc
    if pc==0xc0f9:break
    if pc in (0xc0f6,0x8085):index=0
    elif pc==0x8374:index=1
    elif pc==0x86b2:index=2
    elif pc==0x837f:index=3
    elif pc==0x839d:index=4
    elif pc==0x83fd:index=8
    elif pc==0x83a0:
     index=9 if ref.a==3 else 5 if ref.a in COMMANDS else 6 if ref.a in range(32,256,32) else 7 if ref.a>=32 else None
     assert index is not None,('unknown command',tick,ref.a)
    else:raise AssertionError(('untranslated boundary',tick,hex(pc)))
    before=n.state();assert before==(bytes(bus[:2048]),context(ref))
    want=reference(bus,ref,index);got=n.run(index)
    assert got==want,('repeat mismatch',seed,tick,index,got[1].hex(),want[1].hex(),got[2],want[2])
    semantic=[e[1]-0x8000 for e in want[2] if e[0]=='resource']
    # Existing parser helpers may preflight resource data; their declarative model gives exact reads.
    if index==0:expected=[];assert control_model(*before)==want
    elif index==1:model,expected=prepare_model(*before,resource);assert model[:3]==want
    elif index==2:expected=[0x92e]+list(range(0x6bf,0x6c9))+semantic;assert envelope(*before,resource)==want
    elif index==9:expected=[0x489,0x48a]+semantic;assert command03(*before,resource)==want
    elif index==3:expected=[];assert progress_model(*before)==want
    elif index in (4,5,6):
     pi=8 if index==4 else 3 if index==6 else COMMANDS.index(before[1][2]);model,expected=parser_model(*before,resource,pi);assert model[:3]==want
    else:model,expected=(gate_model if index==7 else note_model)(*before,resource);assert model[:3]==want
    assert n.reads==expected,(index,n.reads,expected)
    total+=1;this_apu+=sum(e[0]=='apu' for e in want[2])
   else:raise AssertionError('tick call bound')
   tick_apu.append(this_apu);apu+=this_apu
  if seed==0:print('Standalone tick APU event counts:',tick_apu,'final PC',hex(ref.pc),'durations',list(bus[0x760:0x764]))
 n.m.cleanup();assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 print(f'PASS {args.sequences} independently bootstrapped resident-buffer sequences of{args.ticks} repeated calls; {total} native helper calls; {apu} ordered APU events. Not native game-frame continuity.')
if __name__=='__main__':main()
