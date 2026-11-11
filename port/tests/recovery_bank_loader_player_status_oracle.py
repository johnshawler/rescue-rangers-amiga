"""Private raw140 comparison, before explicit B-only boundary publication."""
from recovery_bank_loader_player_contact_oracle import *
from recovery_bank_loader_player_contact_oracle import raw_module_result as old_raw

def raw_module_result(before,rom,index):
 if index!=140:return old_raw(before,rom,index)
 from recovery_test_active_command0e_rom import Ricoh
 import struct
 b=ControllerBus(rom);b.map_bank(before[3][3]);b[:2048]=before[0];b.events.clear();c=before[1];m=Ricoh(memory=b);m.pc=int.from_bytes(c[:2],'big');m.a,m.x,m.y,m.p,m.sp=c[2:7]
 for _ in range(200000):
  op=b[m.pc];log_resource(m,b,140);m.step()
  if op==0x6c or op==0x60 and m.pc not in RETURNS[140] or not any(lo<=m.pc<hi for lo,hi in REGIONS[140]):break
 else:raise AssertionError('raw player budget')
 return bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events
