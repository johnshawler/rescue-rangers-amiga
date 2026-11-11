"""Private original-first full-frame region and scheduler bookkeeping."""
from recovery_bank_loader_carry_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log,REGIONS,RETURNS,raw_module_result
ENTRIES=(54947, 55007, 55056, 55429, 55441, 55467, 55479, 55497, 55511, 55556, 55570, 55732, 55756, 55766, 55798, 55844, 55888, 55924, 55981, 55983, 56007, 56061, 56084, 56144, 56175, 56208, 56602, 56653, 56659, 56698, 56775, 56909, 56929, 56970, 57000, 57011, 57016, 57017, 57034, 57037, 57070, 57089, 57092)
REGIONS={**REGIONS,135:((0xc21e,0xc235),(0xc2dc,0xc2f7),(0xc77b,0xc926),(0xf379,0xf392)),137:((0xe9c9,0xea0f),),160:((54947, 56173), (56175, 56300), (56602, 57186))}
RETURNS={**RETURNS,135:(0xc786,0xc795,0xc7f0,0xc837,0xc841,0xc8e0),137:(),160:(55007, 55056, 55429, 55441, 55467, 55479, 55497, 55511, 55556, 55570, 55844, 55924, 55981, 56007, 56084, 56653, 56659, 56698, 56775, 56909, 56929, 57011, 57016, 57034, 57037, 57089, 57092)}
def select_boundary(ref,bus,event):
 if ref.pc in ENTRIES or ref.pc==0xe9c9:return (-1,None,None) if event else (1,137 if ref.pc==0xe9c9 else 160,())
 if ref.pc==0xfe8d and bus.mapper.bank==5 and bus[0x80]==4:
  sp=bus[0x82];ret=(bus[256+((sp+3)&255)]|bus[256+((sp+4)&255)]<<8)+1
  if ret==0xc848:return (-1,None,None) if event else (1,138,(0xc848,))
 return old(ref,bus,event)
def log_resource(ref,bus,index):return old_log(ref,bus,135 if index in (137,160) else index)
