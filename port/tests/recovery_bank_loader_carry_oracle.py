"""Private carry-region composition; unknown legacy PC lookup remains explicit rejection."""
from recovery_bank_loader_collision_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log,REGIONS,RETURNS,raw_module_result
REGIONS={**REGIONS,136:((0xd3e7,0xd4a1),)}
RETURNS={**RETURNS,136:(0xd40a,0xd434)}
def select_boundary(ref,bus,event):
 if ref.pc in (0xd3e7,0xd40b,0xd435,0xd460):return (-1,None,None) if event else (1,136,())
 try:return old(ref,bus,event)
 except KeyError as error:
  if error.args!=(ref.pc,):raise
  return (-1,None,None)
def log_resource(ref,bus,index):return old_log(ref,bus,135 if index==136 else index)
