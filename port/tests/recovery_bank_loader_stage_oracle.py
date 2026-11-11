"""Private original-state stage prefix boundaries, no native-state feedback."""
from recovery_bank_loader_dialogue_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log

def select_boundary(ref,bus,event):
 pc=ref.pc;idx=target=None
 if pc==0xc6b5:idx,target=110,0xc6bd
 elif pc==0xc6bd:idx,target=111,0xc700
 elif pc==0xc700:idx,target=112,0xc2a5
 elif pc==0xc24a:idx,target=115,0xff04
 elif pc==0xe099:idx,target=115,0xe179
 elif pc in (0xc115,0xc14e,0xc158):
  idx=115;target=((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535
 elif bus.mapper.bank==4:
  if pc==0xc2a5:idx,target=33,0xfe8d
  elif pc==0xc2a8:
   idx=113;v=(bus[15]+bus[13])&255
   target=0xc24a if bus[256+((ref.sp+1)&255)]==1 and (v==80 or v>=128) else 0xc2a5
  elif pc==0xc0bf:idx,target=(41,0xc0f6) if bus[0xdc+bus[0xdb]]==0x88 else (70,0x8003)
  elif pc==0xfe8d:
   if bus[128]==4:
    sp=bus[130];idx=114;target=(bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8)+1
   else:return (1,98,(0xc0bf,)) if event==1 else (0,None,None)
 if pc==0xc0f9 and bus[0xf1]==4:idx,target=42,0xfe8d
 if target is not None:return (-1,None,None) if event else (1,idx,(target,))
 return old(ref,bus,event)

def log_resource(ref,bus,index):
 if index not in (110,115):return old_log(ref,bus,index)
 pc=ref.pc;op=bus[pc];a=None
 if op in (0xb9,0xbd,0xbc,0xbe):a=((bus[pc+1]|bus[pc+2]<<8)+(ref.y if op in (0xb9,0xbe) else ref.x))&65535
 elif op in (0xad,0xae,0xac):a=bus[pc+1]|bus[pc+2]<<8
 elif op in (0xb1,0xd1,0x71):
  z=bus[pc+1];a=((bus[z]|bus[(z+1)&255]<<8)+ref.y)&65535
 if a is not None and a>=0x8000:bus.events.append(('resource',a,bus[a],0))
