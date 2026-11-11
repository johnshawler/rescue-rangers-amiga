"""Public full-dispatch guards; optional genuine original-first F328 fixture."""
import sys,random,struct
from pathlib import Path
from recovery_bank_loader_target_choice_harness import *
from recovery_bank_loader_target_choice_test import model

def main():
 rng=random.Random(0x152);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if len(sys.argv)>1 else None;n=Native(assemble(),rom[16:131088] if rom else bytes(131072));cases=guards=0
 for k in range(256):
  s=bytearray(rng.randbytes(2048));s[0x80]=2;s[0x91]=0;s[256+((k+1)&255)]=0x4b;s[256+((k+2)&255)]=0x8f;c=bytes.fromhex('f328')+bytes((17,k,23,(k&207)|32,k,0xa7));rt=bytes((30,0,16,k%8,0,0,0xba,0xdd,0xf0,0x0d,0xd5,1));before=(bytes(s),c,b'\xb6'*134638,rt);want=model(s,c);n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==want[:2] and n.events==want[2] and not n.reads and n.raw_adapter_context is None;assert after[2]==b'\0\0'+b'\xb6'*134636 and after[3]==rt[:6]+bytes.fromhex('00980002d501');cases+=1
  for at,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0'),(CTX+5,b'\x34'),(RAM+0x80,b'\4'),(RAM+0x91,b'\1')):
   n.restore(before);n.mem.w_block(at,v);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  for event in (1,2,0xffffffff):
   n.restore(before);assert n.run(event)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
 if rom:
  from recovery_bank_loader_target_choice_oracle import ControllerBus,REGIONS,RETURNS
  from recovery_test_active_command0e_rom import Ricoh
  root=Path(sys.argv[1]);before=tuple((root/('default.'+suffix+'.bin')).read_bytes() for suffix in ('ram','context','journal','runtime'));b=ControllerBus(rom);b.map_bank(before[3][3]);b[:2048]=before[0];b.events.clear();c=before[1];m=Ricoh(memory=b);m.pc=0xf328;m.a,m.x,m.y,m.p,m.sp=c[2:7]
  for steps in range(512):
   op=b[m.pc];m.step()
   if op==0x60 and m.pc not in RETURNS[152] or not any(lo<=m.pc<hi for lo,hi in REGIONS[152]):break
  else:raise AssertionError('original bound')
  raw=struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]);n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==(bytes(b[:2048]),raw) and n.events==b.events and not n.reads and n.raw_adapter_context is None;assert after[2]==b'\0\0'+before[2][2:] and after[3]==before[3][:6]+bytes.fromhex('00980002d501');print('PASS genuine F328',c.hex(),'->',raw.hex(),steps+1,'original instructions',len(b.events),'ordered RAM writes')
 n.m.cleanup();print('PASS F328 full dispatcher',cases,'cases;',guards,'inert guards')
if __name__=='__main__':main()
