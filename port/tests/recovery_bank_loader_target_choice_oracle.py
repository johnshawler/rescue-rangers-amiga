"""Private original F328 region and genuine external returns."""
from recovery_bank_loader_video5_oracle import *
from recovery_bank_loader_video5_oracle import select_boundary as old
REGIONS={**REGIONS,152:((0xf328,0xf36c),)}
RETURNS={**RETURNS,152:(0xf32d,0xf337)}
def select_boundary(ref,bus,event):
 if ref.pc==0xf328:return (-1,None,None) if event else (1,152,())
 return old(ref,bus,event)
