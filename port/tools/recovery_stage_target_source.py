"""Additive stock stage integration. Existing live/menu sources stay unchanged."""
from pathlib import Path
import sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'tests'))
from recovery_live_source import transform as live_transform,once
from recovery_state_menu_sfx_harness import SOURCES as OLD
from recovery_bank_loader_music_harness import SOURCES,SIZES
from build_recovery_menu_sfx_target import DEVICE

def transform(s,stop_rti=0,full_redraw=True,scene=False):
 s=live_transform(s,stop_rti,False,False)
 old='\n'.join(f' include "{n}.s"' for n in OLD)+'\n'
 new='\n'.join(f' include "{n}.s"' for n in SOURCES)+'\n'
 s=once(s,old,new)
 s=once(s,' bne.l recovery_state_menu_sfx',' bne.l recovery_bank_loader_music_dispatch')
 s=s.replace(' cmpi.w #$c5f8,(a1)',' cmpi.w #$c77b,(a1)')
 s=once(s,' cmpi.w #72,d0',' cmpi.w #134,d0')
 # Output-only last completion journal includes both long-DMA producers.
 s=once(s,' cmpi.w #48,d0\n bne.s .length',' cmpi.w #98,d0\n beq.s .long_dma\n cmpi.w #48,d0\n bne.s .length\n.long_dma:')
 s=once(s,' include "recovery_state_menu_display_device.s"',' include "recovery_stage_target_device.s"')
 old_ids=','.join(str(DEVICE.get(i,255)) for i in range(72))+',255'
 ids=dict(DEVICE);ids.update({78:3,79:2,81:43,84:3,98:48,110:43,115:43})
 s=once(s,' dc.b '+old_ids+'\ninput_samples:', ' dc.b '+','.join(str(ids.get(i,255)) for i in range(135))+'\ninput_samples:')
 s=once(s,(P/'src/recovery_live_bridge.s').read_text(),(P/'src/recovery_stage_target_bridge.s').read_text())
 s=once(s,(P/'src/recovery_live_scanout.s').read_text(),(P/'src/recovery_stage_target_scanout.s').read_text())
 # Ensure terminal display reflects the final loaded boundary, not the prior RTI.
 s=once(s,' clr.l 8(a6)\n bsr.l paula_adapter+8\nstop:', ' clr.l 8(a6)\n bsr.l paula_render\nstop:')
 return s

# The release manifest is a flat, reviewed source allowlist. Historical manifests
# are evidence files, not permission to copy their transitive research inputs.
def source_files():
 import json
 manifest=P/'analysis/recovery_stage_target_manifest.json'
 data=json.loads(manifest.read_text())
 files={**data['public_allowlist'],**data['dependencies']}
 for name in files:
  path=Path(name)
  assert not path.is_absolute() and '..' not in path.parts,name
  assert 'original-disassembly' not in name,name
  assert not any(part in path.name for part in ('experimental_paula_', 'experimental_test_paula_', 'experimental_verify_paula_', 'experimental_build_paula_', 'experimental_run_paula_')),name
 return files
