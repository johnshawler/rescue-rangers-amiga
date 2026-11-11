"""PRIVATE reference control chosen exclusively from original PC/RAM/event.
No imports of native metadata, contract models or helper schedules.
"""
from recovery_state_dispatch_palette_oracle import ControllerBus,SHA,select_boundary as palette_boundary

def select_boundary(ref,bus,event):
 pc=ref.pc
 if pc==0xc0f3 and bus[0xc9]:result=(13,(0x83a0,))
 elif pc==0x839d:result=(14,(0x83a0,))
 elif pc==0x83a0:
  if ref.a in (4,5,6,7,8,9,24):result=(15,(0x839d,))
  elif ref.a>=32:result=(17,(0x83fd,)) if ref.a&31 else (16,(0x8085,))
  else:return -1,None,None
 elif pc==0x83fd:result=(18,(0x8085,))
 elif pc==0x8085:result=(19,(0x839d,0xc0f9))
 elif pc==0xc0f9:result=(20,(0xfe8d,))
 else:
  status,index,target=palette_boundary(ref,bus,event)
  return status,index,(target,)
 return (-1,None,None) if event else (1,*result)

def log_resource(ref,bus):
 """Record original semantic data loads, not instruction fetches/preflight."""
 pc=ref.pc;address=None
 if pc in (0x857a,0x802c,0x8030):address=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
 elif pc in (0x868c,0x8693):address=0x8a02 if pc==0x868c else 0x8a01
 elif pc in (0x83ba,0x83c1):address=(0x8585 if pc==0x83ba else 0x858c)+ref.y
 elif pc==0x844d:address=0x8593+ref.y
 elif pc in (0x8626,0x862b):address=(0x8934 if pc==0x8626 else 0x8935)+ref.y
 elif pc==0x8638:address=((bus[0xc5]|bus[0xc6]<<8)+ref.y)&65535
 if address is not None:bus.events.append(('resource',address,bus[address],0))
