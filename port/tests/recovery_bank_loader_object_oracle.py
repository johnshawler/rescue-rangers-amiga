"""Private original-first bank5 caller/interrupt selection and semantic reads."""
from recovery_bank_loader_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log

def select_boundary(ref,bus,event):
 pc=ref.pc;idx=target=None
 if pc==0xf392:idx,target=91,0xff53
 elif bus.mapper.bank==5:
  if pc==0xf39f:idx,target=92,0x8000
  elif pc==0x8000:
   idx=90;target=((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535
  elif pc==0xf3a2:idx,target=93,0xff04
  elif pc==0xf3a9:idx,target=95,0xff53
  elif pc==0xc0bf:idx,target=41,0xc0f6
  elif pc==0xfe8d:
   if bus[128]==4:idx,target=94,0xf3a9
   else:return (1,40,(0xc0bf,)) if event==1 else (0,None,None)
 if pc==0xc0f9 and bus[0xf1]==5:idx,target=42,0xfe8d
 if target is not None:return (-1,None,None) if event else (1,idx,(target,))
 return old(ref,bus,event)

def log_resource(ref,bus,index):
 if index!=90:return old_log(ref,bus,index)
 pc=ref.pc;op=bus[pc];a=None
 if op in (0xb9,0xbd):a=((bus[pc+1]|bus[pc+2]<<8)+(ref.y if op==0xb9 else ref.x))&65535
 elif op in (0xb1,0xd1,0x71):
  z=bus[pc+1];a=((bus[z]|bus[(z+1)&255]<<8)+ref.y)&65535
 if a is not None and a>=0x8000:bus.events.append(('resource',a,bus[a],0))
