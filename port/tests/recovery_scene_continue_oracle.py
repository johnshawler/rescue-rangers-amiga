"""Private original-state selection for scene composition; no native feedback."""
from recovery_state_menu_sfx_oracle import ControllerBus,SHA,select_boundary as old,log_resource

def select_boundary(ref,bus,event):
 pc=ref.pc;target=None
 if pc==0xc5f8:idx,target=73,0xc63b if bus[0xb8] else 0x9000
 elif pc==0x9000:idx,target=73,0xf3c9
 elif pc==0xf3c9:idx,target=73,0xc274
 elif pc==0xc274:idx,target=74,0xc2a5
 elif pc==0xf3cf:idx,target=75,0xf3d2
 elif pc==0xf3d2:idx,target=75,0xff04
 elif pc==0xf3d5:idx,target=78,0xff53
 elif pc==0xc2a8 and bus.mapper.bank==2 and bus[256+((ref.sp+2)&255)]==0xce and bus[256+((ref.sp+3)&255)]==0xf3:
  idx=76;v=(bus[15]+bus[13])&255
  target=0xf3cf if bus[256+((ref.sp+1)&255)]==1 and (v==80 or v>=128) else 0xc2a5
 elif pc==0xfe8d and bus.mapper.bank==2 and bus[128]==4:
  sp=bus[130];frame=bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8
  if frame==0xf3d4:idx,target=77,0xf3d5
 if target is not None:return (-1,None,None) if event else (1,idx,(target,))
 return old(ref,bus,event)
