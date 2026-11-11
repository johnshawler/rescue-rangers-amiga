"""PRIVATE original-state boundary selection; never reads native diagnostics."""
from recovery_state_dispatch_startup_oracle import ControllerBus,SHA,select_boundary as previous,log_resource as previous_log

def select_boundary(ref,bus,event):
 pc=ref.pc
 if pc==0x83a0 and ref.a in (14,1,18,19,15):return (-1,None,None) if event else (1,{14:51,1:52,18:53,19:54,15:55}[ref.a],(0x839d,))
 if pc==0xfe8d and bus.mapper.bank==2:
  if bus[0x80]==4:
   sp=bus[0x82];frame=bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8
   if frame in (0xa024,0xa06b,0xa088):return (-1,None,None) if event else (1,50,(frame+1,))
  elif bus[0x19]:return (1,48,(0xc0bf,)) if event==1 else (0,None,None)
 target=None
 if pc==0xc5d1:index,target=43,0xa000
 elif pc==0xa025:index,target=44,0xa0bb if (bus[0xbe]|bus[0xbf]<<8)==1 else 0xa000
 elif pc==0xa000:
  index=45;v=bus[0x14]
  target=(0xa0bb if bus[0x50] else 0xa05c) if v&16 else 0xf379 if v&35 else 0xff04
 elif pc==0xa0bb:
  index=46;target=((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535
 elif pc==0xa05c:index,target=47,0xff04
 elif pc==0xa06c:index,target=49,0xa0bb if bus[0x14]&16 else 0xa07b if bus[0x14]&3 else 0xff04
 elif pc==0xa089:index,target=49,0xa06c
 if target is not None:return (-1,None,None) if event else (1,index,(target,))
 return previous(ref,bus,event)

def log_resource(ref,bus,index):
 if index<43:return previous_log(ref,bus,index)
 pc=ref.pc;address=None
 if index==43 and pc in (0xc5d3,0xc5de,0xc5e4):
  address=0xd657+ref.x if pc==0xc5d3 else (0xc73f if pc==0xc5de else 0xc75d)+ref.y
 if index==47 and pc==0xa05e:address=0xa0c9+ref.x
 if index>=51 and pc in (0x802c,0x8030,0x857a):address=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
 if address is not None:bus.events.append(('resource',address,bus[address],0))
