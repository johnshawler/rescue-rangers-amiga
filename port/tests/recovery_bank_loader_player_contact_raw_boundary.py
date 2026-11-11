"""Private raw140 boundary replay, never a publication adapter."""
import sys,json,struct
from pathlib import Path
from recovery_bank_loader_player_contact_harness import *
from recovery_bank_loader_player_contact_oracle import ControllerBus,REGIONS,RETURNS,log_resource
from recovery_test_active_command0e_rom import Ricoh

def main():
 root=Path(sys.argv[1]);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();before=tuple((root/('before.'+s+'.bin')).read_bytes() for s in ('ram','context','journal','runtime'));b=ControllerBus(rom);b.map_bank(before[3][3]);b[:2048]=before[0];b.events.clear();c=before[1];m=Ricoh(memory=b);m.pc=int.from_bytes(c[:2],'big');m.a,m.x,m.y,m.p,m.sp=c[2:7];pcs=[]
 for count in range(8192):
  pc=m.pc;pcs.append(pc);op=b[pc];log_resource(m,b,140);m.step()
  if op in (0x6c,) or op==0x60 and m.pc not in RETURNS[140] or not any(lo<=m.pc<hi for lo,hi in REGIONS[140]):break
 else:raise AssertionError('original bound')
 raw=struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]);n=Native(assemble(),rom[16:131088]);n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==(bytes(b[:2048]),raw) and n.events==b.events and n.raw_adapter_context is None
 es=[e for e in b.events if e[0]!='ram'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert after[2]==j+before[2][len(j):];assert after[3]==before[3][:6]+bytes.fromhex('008cea62d501');assert n.reads==[(6*16384+e[1]-0x8000 if e[1]<0xc000 else e[1]+65536) for e in es]*2
 result=dict(entry=c.hex(),raw=raw.hex(),canonical_status=hex(raw[5]&239),original_instructions=len(pcs),original_PLP_PCs=[hex(pc) for pc in pcs if b[pc]==0x28],ordered_effects=len(b.events),resource_records=len(es),native_status_adapter=False);n.m.cleanup();print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
