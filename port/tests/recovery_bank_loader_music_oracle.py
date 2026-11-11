"""Private original-state stage music command0 and remainder selection."""
from recovery_bank_loader_finish_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log

def select_boundary(ref,bus,event):
 if ref.pc==0x8003 and ref.a==0 and bus.mapper.bank==3:return (-1,None,None) if event else (1,134,(0xc0f3,))
 return old(ref,bus,event)

def log_resource(ref,bus,index):
 if index!=134:return old_log(ref,bus,index)
 op,mode=ref.disassemble[bus[ref.pc]]
 if op not in ('LDA','LDX','LDY','AND','ORA','EOR','ADC','SBC','CMP','CPX','CPY'):return
 pc=ref.pc;a=None
 if mode in ('abs','abx','aby'):a=((bus[pc+1]|bus[pc+2]<<8)+(ref.x if mode=='abx' else ref.y if mode=='aby' else 0))&65535
 elif mode=='iny':
  z=bus[pc+1];a=((bus[z]|bus[(z+1)&255]<<8)+ref.y)&65535
 if a is not None and a>=32768:bus.events.append(('resource',a,bus[a],0))
