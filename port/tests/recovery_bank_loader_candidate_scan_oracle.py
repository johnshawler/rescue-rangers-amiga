"""Private original candidate scan; explicit existing collision-call exits."""
from recovery_bank_loader_target_choice_oracle import *
from recovery_bank_loader_target_choice_oracle import select_boundary as old
REGIONS={**REGIONS,153:((0xf977,0xf9f2),)}
RETURNS={**RETURNS,153:()}
def select_boundary(ref,bus,event):
 if ref.pc in (0xf977,0xf9d7,0xf9e4):return (-1,None,None) if event else (1,153,())
 return old(ref,bus,event)
from recovery_bank_loader_target_choice_oracle import log_resource as old_log
def log_resource(ref,bus,index):return old_log(ref,bus,135 if index==153 else index)
