"""Additive five-frame target; predecessor rendering/audio are unchanged."""
from recovery_stage_target_build import integrated_source as stage_source
from recovery_stage_target_source import SOURCES as OLD, source_files as stage_files
from recovery_bank_loader_play_harness import SOURCES,SIZES
from recovery_live_source import once
CAPACITY=135168

def integrated_source(history="default",display=1,stop_rti=0):
 assert stop_rti==0
 s=stage_source(history,display,0)
 s=once(s,'\n'.join(f' include "{n}.s"' for n in OLD)+'\n','\n'.join(f' include "{n}.s"' for n in SOURCES)+'\n')
 s=once(s,' bne.l recovery_bank_loader_music_dispatch',' bne.l recovery_bank_loader_play_dispatch')
 s=once(s,' cmpi.w #134,d0',' cmpi.w #160,d0')
 s=once(s,'\ninput_samples:',','+','.join(['255']*26)+'\ninput_samples:')
 s=once(s,' cmpi.l #262144,d4',f' cmpi.l #{CAPACITY},d4')
 s=once(s,' dcb.b 262144,0',f' dcb.b {CAPACITY},0')
 s=once(s,' dcb.b 16,$5a\ncapture:', ' cnop 0,4\n dcb.b 16,$5a\ncapture:')
 # Count authentic entry plus five subsequent whole-frame returns. This is
 # output-only diagnostic telemetry, never original RAM/context/task state.
 s=once(s,' cmpi.w #$c77b,(a1)\n beq.s .render',' cmpi.w #$c77b,(a1)\n bne.s .continue_play\n lea recovery_play_arrivals(pc),a3\n addq.l #1,(a3)\n cmpi.l #6,(a3)\n beq.s .render\n.continue_play:')
 s=once(s,'\npad_value:', '\nrecovery_play_arrivals: dc.l 0\npad_value:')
 return s

def source_files():
 import json
 from pathlib import Path
 p=Path(__file__).resolve().parents[1]/'analysis/recovery_play_target_manifest.json'
 data=json.loads(p.read_text())
 return {**data['public_allowlist'],**data['dependencies']}
