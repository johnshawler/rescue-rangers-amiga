"""Additive live integration, explicit bounded diagnostic; no original state edits."""
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b,1)
def transform(s,stop_rti=0,full_redraw=False,scene=False):
 if scene:
  extra=('recovery_scene_continue_dispatch','recovery_post_confirmation_entry','recovery_scene_palette_entry','recovery_scene_sprite_hide','recovery_scene_continue_prepare')
  block='\n'.join(' include "'+n+'.s"' for n in extra)+'\n cnop 0,4\n nop\n'
  s=once(s,' include "recovery_state_menu_sfx.s"',block+' include "recovery_state_menu_sfx.s"')
  s=once(s,' cmpi.w #$c5f8,(a1)',' cmpi.w #$ff53,(a1)')
 s=once(s,' bsr.l recovery_state_menu_sfx' ,' bsr.l recovery_live_dispatch')
 s=once(s,' cmpi.w #71,d0',' cmpi.w #'+str(78 if scene else 72)+',d0')
 s=once(s,'\ninput_samples:',(','+','.join(['255']*(6 if scene else 1))+(',3' if scene else ''))+'\ninput_samples:')
 s=once(s,' bsr.l paula_display_init',' bsr.l paula_display_init\n bsr.l recovery_live_init')
 s=once(s,' cmpi.l #12000,12(a6)',' bsr.l recovery_live_poll\n cmpi.l #1000000,12(a6)')
 a=s.index(' moveq #0,d0\n tst.l 80(a6)');b=s.index(' lea pad_value(pc),a3',a)
 s=s[:a]+' moveq #0,d0\n move.b recovery_live_state(pc),d0\n'+s[b:]
 s=once(s,' bsr.w capture_journal',' clr.l 76(a6)\n bsr.w capture_journal')
 endpoint='$ff53' if scene else '$c5f8'
 s=once(s,'.next:\n cmpi.w #'+endpoint+',((a1))'.replace('((a1))','(a1)'), '.next:\n bsr.l recovery_live_scanout\n bsr.l recovery_live_render\n cmpi.w #'+endpoint+',((a1))'.replace('((a1))','(a1)'))
 # End only at authentic existing dispatcher boundary. Live frames never mute.
 s=once(s,' bsr.l paula_render\nstop:', ' bsr.l paula_adapter+8\nstop:')
 s=once(s, '; Preserve the predecessor executable alignment and exact device bytes.\n nop', '; Preserve original device alignment.\n'+(' nop\n'*(4 if stop_rti else 3)).rstrip())
 s=once(s,' bsr.l recovery_live_render\n cmpi.w',f' bsr.l recovery_live_render\n ifne {stop_rti}\n bsr.l recovery_live_diagnostic_stop\n endif\n cmpi.w')
 s+='\nrecovery_live_stop_rti equ '+str(stop_rti)+'\n'+(P/'src/recovery_live_bridge.s').read_text()+'\n'+(P/'src/recovery_live_dispatch.s').read_text()+'\n'+(P/'src/recovery_live_scanout.s').read_text()
 if scene:s=once(s,' bne.l recovery_state_menu_sfx',' bne.l recovery_scene_continue_dispatch')
 if full_redraw:
  s=once(s,' cmp.w recovery_live_banks(pc),d0\n beq.s .cache_ready',' cmp.w recovery_live_banks(pc),d0\n nop\n nop')
 return s
