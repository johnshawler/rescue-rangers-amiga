"""Original-only dialogue endpoints; controller pulses supplied by test history."""
from recovery_bank_loader_object_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log

def select_boundary(ref,bus,event):
 pc=ref.pc;idx=targets=None
 if bus.mapper.bank==2:
  if pc in (0x911c,0x911f,0xc60a):idx,targets=99,({0x911c:0x92ac,0x911f:0xc60a,0xc60a:0xc6b5}[pc],)
  elif pc in (0x92ac,0x9475,0x9478,0x947b,0x947e):idx,targets=96,(0xf379,0xff04,0x911f)
  elif pc==0xfe8d:
   if bus[128]==4:
    sp=bus[130];ret=(bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8)+1
    if ret in (0x9478,0x947b,0x947e):idx,targets=97,(ret,)
   elif bus[0x1c] or bus[0x1d]:return (1,98,(0xc0bf,)) if event==1 else (0,None,None)
 if targets is not None:return (-1,None,None) if event else (1,idx,targets)
 return old(ref,bus,event)

def log_resource(ref,bus,index):
 if index not in (96,99):return old_log(ref,bus,index)
 pc=ref.pc;op=bus[pc];a=None
 if op in (0xb9,0xbd,0xbc,0xbe):a=((bus[pc+1]|bus[pc+2]<<8)+(ref.y if op in (0xb9,0xbe) else ref.x))&65535
 elif op in (0xad,0xae,0xac):a=bus[pc+1]|bus[pc+2]<<8
 elif op in (0xb1,0xd1,0x71):
  z=bus[pc+1];a=((bus[z]|bus[(z+1)&255]<<8)+ref.y)&65535
 if a is not None and a>=0x8000:bus.events.append(('resource',a,bus[a],0))
