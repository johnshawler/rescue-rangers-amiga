"""Private original-state stage completion boundaries."""
from recovery_bank_loader_map_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log

def select_boundary(ref,bus,event):
 pc=ref.pc;idx=targets=None
 if pc in (0x8040,0x8090) and bus.mapper.bank==4:
  idx=116;targets=(((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535,)
 elif pc in (0xe106,0xe10c,0xe10f,0xc262,0xc265,0xc703,0xc617):idx,targets=130,(0xc158,0xff04,0xff53,0x8000,0xc26e,0xc77b)
 elif pc==0xc26e:idx,targets=131,(0xc2a5,)
 elif pc==0xc2a5 and bus.mapper.bank==5:idx,targets=33,(0xfe8d,)
 elif pc==0xc2a8 and bus.mapper.bank==5:
  idx=132;v=(bus[15]+bus[13])&255
  targets=(0xc703 if bus[256+((ref.sp+1)&255)]==1 and (v==80 or v>=128) else 0xc2a5,)
 elif pc==0xfe8d and bus[128]==4:
  sp=bus[130];ret=(bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8)+1
  if bus.mapper.bank==4 and ret==0xe10f or bus.mapper.bank==5 and ret==0xc2a8:idx,targets=133,(ret,)
 if targets is not None:return (-1,None,None) if event else (1,idx,targets)
 return old(ref,bus,event)

def log_resource(ref,bus,index):
 if index not in (116,130):return old_log(ref,bus,index)
 op,mode=ref.disassemble[bus[ref.pc]]
 if op not in ('LDA','LDX','LDY','AND','ORA','EOR','ADC','SBC','CMP','CPX','CPY'):return
 pc=ref.pc;a=None
 if mode in ('abs','abx','aby'):a=((bus[pc+1]|bus[pc+2]<<8)+(ref.x if mode=='abx' else ref.y if mode=='aby' else 0))&65535
 elif mode=='iny':
  z=bus[pc+1];a=((bus[z]|bus[(z+1)&255]<<8)+ref.y)&65535
 if a is not None and a>=32768:bus.events.append(('resource',a,bus[a],0))
