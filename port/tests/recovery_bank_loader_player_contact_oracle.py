"""Private original player contact and original external collision boundaries."""
from recovery_bank_loader_candidate_scan_oracle import *
from recovery_bank_loader_candidate_scan_oracle import select_boundary as old,log_resource as old_log
REGIONS={**REGIONS,154:((0xf92b,0xf977),)}
RETURNS={**RETURNS,154:(0xf941,)}
def select_boundary(ref,bus,event):
 if ref.pc in (0xf92b,0xf95a,0xf96c):return (-1,None,None) if event else (1,154,())
 return old(ref,bus,event)
def log_resource(ref,bus,index):return old_log(ref,bus,135 if index==154 else index)
