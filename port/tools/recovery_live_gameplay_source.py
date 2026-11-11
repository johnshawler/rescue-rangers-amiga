"""Additive240-frame integrated target; actual CIA input, no synthetic game state."""
from recovery_play_target_source import integrated_source as old_source
from recovery_bank_loader_play_harness import SOURCES as OLD
from recovery_bank_loader_player_status_harness import SOURCES,SIZES
from recovery_live_source import once
from recovery_play_background_build import prepare

def integrated_source(history='default',display=1,stop_rti=0):
 s=old_source(history,display,stop_rti)
 s=once(s,'\n'.join(f' include "{n}.s"' for n in OLD)+'\n','\n'.join(f' include "{n}.s"' for n in SOURCES)+'\n')
 s=once(s,' bne.l recovery_bank_loader_play_dispatch',' bne.l recovery_bank_loader_player_status_dispatch')
 s=once(s,' cmpi.l #6,(a3)',' cmpi.l #241,(a3)')
 return s
