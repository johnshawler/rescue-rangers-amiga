"""Private raw object evidence, independent of canonical live publication."""
from recovery_bank_loader_play_oracle import *
from recovery_bank_loader_play_oracle import raw_module_result as old_raw

def raw_module_result(before,rom,index):
 if index!=90:return old_raw(before,rom,index)
 from recovery_test_active_command0e_rom import Ricoh
 import struct
 b=ControllerBus(rom);b.map_bank(before[3][3]);b[:2048]=before[0];b.events.clear()
 c=before[1];m=Ricoh(memory=b);m.pc=int.from_bytes(c[:2],'big');m.a,m.x,m.y,m.p,m.sp=c[2:7]
 for _ in range(200000):
  log_resource(m,b,90);m.step()
  if not 0x8000<=m.pc<0x81e0:break
 else:raise AssertionError('raw object budget')
 return bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events
