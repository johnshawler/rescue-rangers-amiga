"""PRIVATE original-state selector, independent of native output/diagnostics."""
from recovery_state_dispatch_scheduler_oracle import ControllerBus,SHA,select_boundary as previous,log_resource as previous_log

def select_boundary(ref,bus,event):
 pc=ref.pc
 if pc==0x83a0 and ref.a in (2,3):return (-1,None,None) if event else (1,29 if ref.a==3 else 30,(0x839d,))
 if pc==0xfe8d and bus[0x80]==4:
  sp=bus[0x82];target=(bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8)+1
  if target in (0xc2a8,0xc597,0xc5ce):return (-1,None,None) if event else (1,31,(target,))
 if pc==0xfe8d and bus.mapper.bank==2:
  return (1,40,(0xc0bf,)) if event==1 else (0,None,None)
 if pc==0xc0bf and bus.mapper.bank==2:return (-1,None,None) if event else (1,41,(0xc0f6,))
 if pc==0xc0f9 and bus[0xf1]==2:return (-1,None,None) if event else (1,42,(0xfe8d,))
 if pc==0xc2a8:
  target=0xc2a5
  if bus[256+((ref.sp+1)&255)]==1:
   level=(bus[0xf]+bus[0xd])&255
   if level==0x50 or level>=128:target=(bus[256+((ref.sp+2)&255)]|bus[256+((ref.sp+3)&255)]<<8)+1
  return (-1,None,None) if event else (1,32,(target,))
 targets={0xc594:(32,0xff04),0xff04:(33,0xfe8d),0xc597:(34,0xc5bb),0xc5bb:(35,0xc5c0),0xc5c0:(36,0xc5c5),0xc5c5:(37,0xc5cb),0xc5cb:(38,0xff04),0xc5ce:(39,0xc2a5)}
 if pc==0xc2a5 and bus.mapper.bank==2:targets[pc]=(33,0xfe8d)
 if pc in targets:
  index,target=targets[pc];return (-1,None,None) if event else (1,index,(target,))
 return previous(ref,bus,event)

def log_resource(ref,bus,index):
 if index<29:
  if 13<=index<=20 or index in (26,27):previous_log(ref,bus)
  return
 pc=ref.pc;addr=None
 if index in (29,30):
  if pc in (0x802c,0x8030):addr=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
 elif index==36 and pc in (0x8000,0x8005,0x800f,0x8019,0x8021,0x8028):
  addr=0x803d+ref.x if pc==0x8000 else 0x8047+ref.x if pc==0x8005 else (bus[0]+256*bus[1]+ref.y)&65535
 elif index==37 and pc in (0x8822,0x8838,0x883e,0x8844,0x884a):
  addr=ref.y+{0x8822:0x8861,0x8838:0x8871,0x883e:0x8872,0x8844:0x8873,0x884a:0x8874}[pc]
 if addr is not None:bus.events.append(('resource',addr,bus[addr],0))
