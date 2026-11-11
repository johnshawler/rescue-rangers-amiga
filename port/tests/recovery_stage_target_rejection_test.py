#!/usr/bin/env python3
"""Additive complete live-target fault checks; synthetic bus, not PCM evidence."""
from pathlib import Path
import sys,json
cfg=json.loads((Path(sys.argv[1])/"build.json").read_text())
s=Path(__file__).with_name('recovery_menu_paula_target_rejection_test.py').read_text()
def once(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
once("('loop_guard', '0cae00002ee0000c'),('history_guard','0c830000007f'),('event_guard','4aae0014')", "('loop_guard', '0cae000f4240000c'),('event_guard','4aae0014')")
once("        ('input_history_guard','history_guard',0,9,0,0,-7),\n",'')
once("('helper_over_limit','capture_journal',0,72,0,0,-3)","('helper_over_limit','capture_journal',0,"+str(135)+",0,0,-3)")
once("if entry=='loop_guard':mem.w32(P+12,12000)","if entry=='loop_guard':mem.w32(P+12,1000000)")
once("('renderer_rejection_bridge','paula_render',0,9,0,0,-5)","('renderer_rejection_bridge','recovery_live_render',0,8,0,0,-5),\n        ('input_changes_exhausted','recovery_live_poll',0,9,0,0,-9),\n        ('audio_ring_limit','paula_consume',0,8,0,0,-4)")
once("  for i in range(4):mem.w16",'''  if entry=='recovery_live_render':mem.w32(BASE+symbols['startup_device']+16,1)
  if entry=='recovery_live_poll':
   mem.w8(BASE+symbols['recovery_live_state'],1);mem.w32(BASE+symbols['recovery_live_report']+28,128)
  if name=='audio_ring_limit':
   adapter_symbols={x.split()[-1]:int(x.split()[0],16) for x in (out/'adapter.symbols').read_text().splitlines() if len(x.split()) in(3,4)}
   mem.w32(BASE+symbols['paula_adapter']+adapter_symbols['mp']+16,4096)
  for i in range(4):mem.w16''')
once("if entry=='paula_render':assert", "if entry=='recovery_live_render':assert")
s=s.replace("'complete-target-rejections.json'","'live-complete-target-rejections.json'")
needle=" for name,entry,count,helper,size,used,error in cases:"
assert s.count(needle)==1
s=s.replace(needle," cases += [(name,'recovery_live_scanout',0,9,0,0,-5) for name in ('scanout_mask','scanout_ctrl','scanout_scrolly','scanout_mapper','scanout_latch','scanout_device_error')]\n"+needle)
needle="  if entry=='recovery_live_render':"
assert s.count(needle)==2
s=s.replace(needle,"  if entry=='recovery_live_scanout':\n   dev=BASE+symbols['startup_device'];mem.w8(dev,0x90);mem.w8(dev+1,0x1e);mem.w8(dev+10,0x1e);mem.w32(BASE+symbols['recovery_live_report']+36,1)\n   off,value={'scanout_mask':(1,0x1a),'scanout_ctrl':(0,0x80),'scanout_scrollx':(3,1),'scanout_scrolly':(4,1),'scanout_mapper':(10,0x0c),'scanout_latch':(15,1),'scanout_device_error':(19,1)}[name];mem.w8(dev+off,value)\n"+needle,1)
s=s.replace("if entry=='recovery_live_render':assert", "if entry in ('recovery_live_render','recovery_live_scanout'):assert")
s=s.replace("('helper48_missing_sentinel','capture_journal',0,48,12,0,-3),", "('helper48_missing_sentinel','capture_journal',0,48,12,0,-3),('helper98_missing_sentinel','capture_journal',0,98,12,0,-3),")
s=s.replace("live-complete-target-rejections.json","stage-target-rejections.json")
exec(compile(s,__file__,'exec'))
