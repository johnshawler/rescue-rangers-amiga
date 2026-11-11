"""Private original main-frame boundary selector."""
from recovery_bank_loader_music_oracle import ControllerBus,SHA,select_boundary as old,log_resource as old_log
from recovery_bank_loader_models import validation_reads
ENTRIES=(51067, 51078, 51093, 51111, 51114, 51140, 51149, 51152, 51167, 51175, 51184, 51189, 51192, 51210, 51230, 51233, 51240, 51243, 51248, 51255, 51258, 51265, 51272, 51291, 51294, 51321, 51371, 51376, 51379, 51416, 51424, 49694, 49884, 62329, 51438)
def select_boundary(ref,bus,event):
 if ref.pc in ENTRIES:
  ret=((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535
  extra=() if any(a<=ret<b for a,b in ((0xc21e,0xc235),(0xc2dc,0xc2f7),(0xc77b,0xc926),(0xf379,0xf392))) else (ret,)
  return (-1,None,None) if event else (1,135,(0xc940,0xff53,0xd1dc,0xc235,0x9000,0xe096,0x8b00,0xc60e,0x8000,0xd6a3,0x8090,0xe576,0xe9c9,0xff04,0xc588,0xc6b5,0xa410,0xf377)+extra)
 return old(ref,bus,event)
def log_resource(ref,bus,index):return old_log(ref,bus,134 if index==135 else index)
