"""Private raw envelope comparison before canonical publication."""
from recovery_bank_loader_sfx_oracle import *
from recovery_bank_loader_sfx_oracle import raw_module_result as old_raw

def raw_module_result(before,rom,index):
 if index!=68:return old_raw(before,rom,index)
 from recovery_test_active_command0e_rom import Ricoh
 from recovery_test_sfx_envelope import run_original
 b=ControllerBus(rom);b.map_bank(3);b[:2048]=before[0];b.events.clear()
 c=before[1];m=Ricoh(memory=b);m.pc=int.from_bytes(c[:2],'big');m.a,m.x,m.y,m.p,m.sp=c[2:7]
 return run_original(b,m,c[7])
