"""Independent original map-resource read addresses and original external exits."""
from recovery_bank_loader_stage_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log
ENTRIES=(0xe179,0xe17c,0xe1d3,0xe1e4,0xe1e7,0xe1ea,0xdbec,0xdc5c,0xdc5f,0xdf97,0xe028)
def select_boundary(ref,bus,event):
 if ref.pc in ENTRIES:return (-1,None,None) if event else (1,100,(0xc14e,0xff53,0xc115,0x8040,0x8090,0xe106))
 return old(ref,bus,event)
def log_resource(ref,bus,index):
 if index!=100:return old_log(ref,bus,index)
 op,mode=ref.disassemble[bus[ref.pc]]
 if op not in ('LDA','LDX','LDY','AND','ORA','EOR','ADC','SBC','CMP','CPX','CPY'):return
 pc=ref.pc;a=None
 if mode in ('abs','abx','aby'):
  a=((bus[pc+1]|bus[pc+2]<<8)+(ref.x if mode=='abx' else ref.y if mode=='aby' else 0))&65535
 elif mode=='iny':
  z=bus[pc+1];a=((bus[z]|bus[(z+1)&255]<<8)+ref.y)&65535
 if a is not None and a>=32768:bus.events.append(('resource',a,bus[a],0))
