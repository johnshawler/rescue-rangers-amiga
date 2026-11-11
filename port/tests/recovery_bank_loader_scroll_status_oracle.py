"""Private original raw scroll output, before canonical publication."""
from recovery_bank_loader_envelope_oracle import *
from recovery_bank_loader_envelope_oracle import raw_module_result as old_raw

def raw_module_result(before,rom,index):
 if index!=160:return old_raw(before,rom,index)
 from recovery_test_active_command0e_rom import Ricoh
 from recovery_stage_scroll_test import RANGES,RETURN_SITES,log_read
 import struct
 b=ControllerBus(rom);b.map_bank(before[3][3]);b[:2048]=before[0];b.events.clear()
 c=before[1];m=Ricoh(memory=b);m.pc=int.from_bytes(c[:2],'big');m.a,m.x,m.y,m.p,m.sp=c[2:7]
 for _ in range(200000):
  op=b[m.pc];log_read(m,b);m.step()
  if op==0x6c or op==0x60 and m.pc not in RETURN_SITES or not any(a<=m.pc<z for a,z in RANGES):break
 else:raise AssertionError('raw scroll budget')
 return bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events

# Original map slices can now return to scroll caller DAAD, not only loaderE106.
# Stop on the actual static-region/external-return boundary; never run caller
# instructions merely to reach the historical loader-only target list.
REGIONS={**REGIONS,100:((0xc235,0xc247),(0xdbec,0xdd0a),(0xdf8a,0xe047),(0xe06b,0xe096),(0xe179,0xe1eb))}
RETURNS={**RETURNS,100:(0xdc5c,0xdc5f,0xdf92,0xdf97,0xe028,0xe17c,0xe17f,0xe1d3,0xe1e4,0xe1e7,0xe1ea)}
