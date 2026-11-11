#!/usr/bin/env python3
"""Verify all additive target variants using the frozen independent oracle.
Requires actual stock-emulator dumps/logs/video, including repeat control/winner.
"""
import hashlib,json,struct
from pathlib import Path
from verify_recovery_startup_display import check,verify_screen,PORT
OUT=PORT/'build/startup-render-unrolled-experiment'

def fields(chip):
 assert chip.count(b'CDRDIS01')==1 and chip.count(b'RRUNROL1')==1
 f=struct.unpack_from('>10I',chip,chip.index(b'CDRDIS01')+8)
 t=struct.unpack_from('>2I',chip,chip.index(b'RRUNROL1')+8)
 start,end=f[-2:];chr_end,bg_end=t
 assert start<chr_end<bg_end<end
 return f,{'total':end-start,'admission_and_CHR':chr_end-start,'background':bg_end-chr_end,'sprites':end-bg_end}

def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 result={};reference_frame=reference_screen=None
 for variant in ('baseline','optimized','paired','compact'):
  out=OUT/variant;chip=(out/'chip.bin').read_bytes()
  report=check(chip,rom,(out/'amiga.log').read_text())
  report['video']=verify_screen(chip,out/'screen.ppm')
  f,timing=fields(chip);frame=chip[f[6]:f[6]+51200];screen=(out/'screen.ppm').read_bytes()
  if reference_frame is None:reference_frame,reference_screen=frame,screen
  assert frame==reference_frame and screen==reference_screen,variant
  report['split_CIA_E_ticks']=timing
  if variant in ('baseline','compact'):
   repeat=(out/'repeat-chip.bin').read_bytes()
   check(repeat,rom,(out/'repeat-amiga.log').read_text())
   verify_screen(repeat,out/'repeat-screen.ppm')
   assert repeat==chip and (out/'repeat-screen.ppm').read_bytes()==screen
   report['repeat_Chip_and_video_equal']=True
  result[variant]=report
 frozen=PORT/'build/startup-display-native'
 chip=(frozen/'chip.bin').read_bytes();f=struct.unpack_from('>10I',chip,chip.index(b'CDRDIS01')+8)
 assert chip[f[6]:f[6]+51200]==reference_frame
 assert (frozen/'screen.ppm').read_bytes()==reference_screen
 result['frozen_baseline_frame_and_full_video_equal']=True
 old=result['baseline']['split_CIA_E_ticks']['total'];new=result['compact']['split_CIA_E_ticks']['total']
 assert new<old
 result['improvement']={'ticks':old-new,'percent':100*(old-new)/old,'PAL_E_clock_ms':1000*(old-new)/709379,'DMA_during_measurement':False,'full_game_claim':False}
 (OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':'PASS','timing':{v:result[v]['split_CIA_E_ticks'] for v in ('baseline','optimized','paired','compact')},'improvement':result['improvement']},indent=2))
if __name__=='__main__':main()
