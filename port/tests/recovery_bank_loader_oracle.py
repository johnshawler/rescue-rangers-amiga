"""Private original-only endpoint/resource selection, independent of native output."""
from recovery_scene_continue_oracle import ControllerBus,SHA,select_boundary as old,log_resource as old_log

def select_boundary(ref,bus,event):
 pc=ref.pc;idx=target=None
 if pc==0xff53:
  if bus[0xf6]:return -1,None,None
  idx=79;target=((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535
 elif bus.mapper.bank==2:
  if pc==0x9003:idx,target=80,0x8000
  elif pc==0x8000:
   idx=81;target=((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535
  elif pc==0x9034:idx,target=82,0x8000
  elif pc in (0x9039,0x9041):idx,target=83,0xf3e5
  elif pc==0xf3e5:idx,target=84,0xff04
  elif pc==0xf3ee:idx,target=85,0xc2a5
  elif pc==0xf3f1:idx,target=88,0xff53
  elif pc==0x910c:idx,target=89,0xf392
  elif pc==0xc2a8 and bus[256+((ref.sp+2)&255)]==0xf0 and bus[256+((ref.sp+3)&255)]==0xf3:
   idx=86;v=(bus[15]+bus[13])&255
   target=0xf3f1 if bus[256+((ref.sp+1)&255)]==1 and (v==80 or v>=128) else 0xc2a5
  elif pc==0xfe8d and bus[128]==4:
   sp=bus[130];frame=bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8
   if frame==0xf3ed:idx,target=87,0xf3ee
 if target is not None:return (-1,None,None) if event else (1,idx,(target,))
 return old(ref,bus,event)

def log_resource(ref,bus,index):
 if index<79:return old_log(ref,bus,index)
 pc=ref.pc;a=None
 if index==80 and pc==0x902c:a=0x91f3+ref.y
 if index==81 and pc in (0x8000,0x8005,0x800f,0x8019,0x8021,0x8028):
  a=0x803d+ref.x if pc==0x8000 else 0x8047+ref.x if pc==0x8005 else (bus[0]+256*bus[1]+ref.y)&65535
 if index==83 and pc in (0x9043,0x904a,0x9059,0x9075,0x908c):
  a={0x9043:0x91f4+ref.y,0x904a:0x91f3+ref.y,0x9059:0x922f+ref.y,0x9075:0x922b+ref.x,0x908c:0x922f+ref.y}[pc]
 if a is not None:bus.events.append(('resource',a,bus[a],0))

from recovery_bank_loader_models import validation_reads
