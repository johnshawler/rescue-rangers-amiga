"""Private original/native event audit. Generated event streams must not be shared.
Run as a separate process before the compiled-planner audit.
"""
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',required=True,type=Path);p.add_argument('--output',required=True,type=Path);args=p.parse_args()
OUT=args.output.resolve()
if OUT.is_relative_to(ROOT) and not OUT.is_relative_to(ROOT/'port/build'):
 raise ValueError('Private outputs inside this repository must stay in ignored port/build')
OUT.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(ROOT/'port/tests'))
import recovery_state_menu_sfx_rom as t
BaseBus,BaseCPU=t.ControllerBus,t.MPU
class Bus(BaseBus):
 last=None
 def __init__(self,*args,**kwargs):
  self.audio_events=[];self.audio_reads=[];self.logical_nmi=0;self.instruction_index=0;self.current_pc=None;self.since_rti=False;self.rti=[];self.unclosed_entries=[]
  super().__init__(*args,**kwargs);Bus.last=self
 @staticmethod
 def audio(a):return isinstance(a,int) and (0x4000<=a<=0x4013 or a in (0x4015,0x4017))
 def __setitem__(self,a,v):
  super().__setitem__(a,v)
  if self.audio(a):self.audio_events.append(dict(nmi=self.logical_nmi,phase='before_first_entry' if not self.logical_nmi else 'entry_to_RTI' if self.since_rti else 'after_RTI',instruction=self.instruction_index,pc=self.current_pc,address=a,value=int(v)))
 def __getitem__(self,a):
  v=super().__getitem__(a)
  if self.audio(a):self.audio_reads.append(dict(nmi=self.logical_nmi,instruction=self.instruction_index,pc=self.current_pc,address=a,value=v))
  return v
class CPU(BaseCPU):
 def nmi(self):
  if self.memory.since_rti:self.memory.unclosed_entries.append(self.memory.logical_nmi)
  self.memory.logical_nmi+=1;self.memory.since_rti=True
  return super().nmi()
 def step(self):
  self.memory.current_pc=self.pc;self.memory.instruction_index+=1
  op=self.memory[self.pc]
  result=super().step()
  if op==0x40:
   self.memory.rti.append(dict(nmi=self.memory.logical_nmi,event_count=len(self.memory.audio_events),instruction=self.memory.instruction_index,return_pc=self.pc))
   self.memory.since_rti=False
  return result
t.ControllerBus,t.MPU=Bus,CPU
rom=args.rom.read_bytes();assert hashlib.sha256(rom).hexdigest()==t.SHA
code=t.assemble();assert hashlib.sha256(code).hexdigest()=='a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e'
histories=('right_hold','left_hold','right_early','left_early','right_repeat','left_repeat','alternating','move_back','rapid','default','neutral','title_right','title_left','title_select')
summary=[]
for history in histories:
 result=t.run_case(rom,code,history);bus=Bus.last
 writes=[e for e in bus.audio_events if e['address']!=0x4017]
 assert len(writes)==result['APU_writes']
 assert bus.logical_nmi==result['logical_NMIs']
 assert not bus.since_rti and not bus.unclosed_entries
 assert len(bus.rti)==bus.logical_nmi and all(r['nmi']==i+1 for i,r in enumerate(bus.rti))
 data={'history':history,'original_and_native_comparison':'PASS','logical_NMIs':bus.logical_nmi,'APU_writes':len(writes),'instructions':result['original_instructions'],'events':bus.audio_events,'reads':bus.audio_reads,'RTIs':bus.rti,'entries_without_previous_RTI':bus.unclosed_entries,'complete':not bus.since_rti,'source_test_sha256':hashlib.sha256(Path(t.__file__).read_bytes()).hexdigest(),'ROM_sha256':t.SHA,'boundary':result['final_context'],'timing':'Logical NMI groups and instruction ordinals only; no CPU-cycle timestamps.'}
 path=OUT/(history+'-private-events.json');path.write_text(json.dumps(data,indent=2)+'\n')
 row={k:data[k] for k in ('history','logical_NMIs','APU_writes','boundary','entries_without_previous_RTI')};row['RTIs']=len(bus.rti);row['read_count']=len(bus.audio_reads);row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();summary.append(row);print(json.dumps(row),flush=True)
 Bus.last=None
assert sum(x['APU_writes'] for x in summary)==15059
(OUT/'collection.json').write_text(json.dumps({'status':'PASS','cases':summary,'APU_writes':15059,'private':True,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'composition_sha256':hashlib.sha256(code).hexdigest(),'original_boundary':'FE24 after hardware warmup'},indent=2)+'\n')
