"""PRIVATE endpoint selector: original state only, no native metadata imports."""
from recovery_state_dispatch_active_oracle import ControllerBus as ActiveBus,SHA,log_resource as active_log_resource,select_boundary as active_boundary

def select_boundary(ref,bus,event):
 if ref.pc==0xc0bf and bus[0xdc+bus[0xdb]]==0x88:
  return (-1,None,None) if event else (1,24,(0xc0f6,))
 if ref.pc in (0xc0f6,0x8085):return (-1,None,None) if event else (1,25,(0x8374,0x839d,0xc0f9))
 if ref.pc==0x8374:return (-1,None,None) if event else (1,26,(0x837f,0x86b2))
 if ref.pc==0x86b2:return (-1,None,None) if event else (1,27,(0x837f,))
 if ref.pc==0x837f:return (-1,None,None) if event else (1,28,(0x839d,0x8085))
 if ref.pc in (0xc2a8,0xc2a5):
  if event:return -1,None,None
  if ref.pc==0xc2a8 and bus[256+((ref.sp+1)&255)]==1:
   level=(bus[0xf]+bus[0xd])&255
   if level==0x50 or level>=128:return -1,None,None
  return (1,22,(0xc2a5,)) if ref.pc==0xc2a8 else (1,23,(0xfe8d,))
 if ref.pc==0xc0f3 and bus[0xc9] and (bus[0xc0]>8 or bus[0x763]):return -1,None,None
 if ref.pc==0xfe8d and bus[0x80]==4:
  sp=bus[0x82]
  lo=bus[256+((sp+3)&255)];hi=bus[256+((sp+4)&255)]
  if (hi<<8|lo)==0xc2a7:
   return (-1,None,None) if event else (1,21,(0xc2a8,))
 return active_boundary(ref,bus,event)

class ControllerBus(ActiveBus):
 def __setitem__(self,address,value):
  if isinstance(address,int) and 0x4000<=address<=0x4013:
   self.events.append(('apu',address,value,1));return
  super().__setitem__(address,value)

def log_resource(ref,bus):
 active_log_resource(ref,bus)
 pc=ref.pc;address=None
 if pc in (0x86cb,0x86e0,0x86ef,0x86f5,0x8703,0x8766,0x87b3,0x8838,0x88f5):
  address=((bus[0xc5]|bus[0xc6]<<8)+ref.y)&65535
 elif pc in (0x86d1,0x86e8,0x870b,0x8846,0x88c8,0x88d0,0x88df,0x88e5):
  address=({0x86d1:0x890e,0x86e8:0x890e,0x870b:0x890e,0x8846:0x892e,0x88c8:0x8934,0x88d0:0x8935,0x88df:0x8934,0x88e5:0x8935}[pc]+ref.y)&65535
 if address is not None:bus.events.append(('resource',address,bus[address],0))
