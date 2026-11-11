"""Private actual bank5 queued-NMI boundary; ordinary audio follows C0BF."""
from recovery_bank_loader_scroll_status_oracle import *
from recovery_bank_loader_scroll_status_oracle import select_boundary as old

def select_boundary(ref,bus,event):
 if ref.pc==0xfe8d and bus.mapper.bank==5 and bus[0x80]==1 and bus[0x19]:
  if event not in (0,1) or bus[0xf5] or bus[0xf6] or not bus[0xff]&128:return -1,None,None
  return (1,98,(0xc0bf,)) if event else (0,None,None)
 return old(ref,bus,event)
