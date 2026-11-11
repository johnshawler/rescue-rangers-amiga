"""Private bank5 original pending queue boundary selection."""
from recovery_bank_loader_input_oracle import *
from recovery_bank_loader_input_oracle import select_boundary as old

def select_boundary(ref,bus,event):
 if ref.pc==0xc0bf and bus.mapper.bank==5:
  if event or bus[0xdb]>=8 or bus[0xf5] or bus[0xf6]:return -1,None,None
  return (1,41,(0xc0f6,)) if bus[0xdc+bus[0xdb]]==0x88 else (1,70,(0x8003,))
 return old(ref,bus,event)
