"""Private ordinary SFX dispatch, preserving known complete command helpers."""
from recovery_bank_loader_queue5_oracle import *
from recovery_bank_loader_queue5_oracle import select_boundary as old,log_resource as old_log

def select_boundary(ref,bus,event):
 if ref.pc==0x8003 and bus.mapper.bank==3 and ref.a<240 and ref.a not in (0,7,14,39):
  if event or not bus[0x8a00]:return -1,None,None
  x=((ref.a%bus[0x8a00])*2)&255
  return 1,139,(0x810d if bus[0x8a04+x]|bus[0x8a03+x] else 0x8151,)
 return old(ref,bus,event)

def log_resource(ref,bus,index):
 if index!=139:return old_log(ref,bus,index)
 if ref.pc in (0x80f0,0x80f6):a=0x8a00
 elif ref.pc==0x80fd:a=0x8a04+ref.x
 elif ref.pc==0x8102:a=0x8a03+ref.x
 else:return
 bus.events.append(('resource',a,bus[a],0))
