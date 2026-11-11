#!/usr/bin/env python3
"""Read existing qualified CIA records; does not change/instrument the target."""
from pathlib import Path
import json,struct,sys

def check(b):
 c=(b/'full-CHIP.bin').read_bytes();m=struct.unpack_from('>16I',c,c.index(b'CDRPAU01')+8)
 pcm=json.loads((b/'play-target-pcm.json').read_text());assert pcm['status']=='PASS'
 ids=[v['RTI']-1 for v in pcm['gameplay_windows']];assert ids==list(range(m[2]-5,m[2]))
 rows=[]
 for i in ids:
  prev=struct.unpack_from('>3I',c,m[10]+56*((i-1)&255));v=struct.unpack_from('>3I',c,m[10]+56*(i&255))
  assert prev[2]<v[0]<=v[1]<=v[2]
  rows.append(dict(completed_game_frame=i-ids[0]+1,previous_RTI=i,RTI=i+1,previous_published=prev[1],ready=v[0],published=v[1],hardware_apply_end=v[2],publication_interval_ticks=v[1]-prev[1],publication_interval_ms=(v[1]-prev[1])*1000/709379))
 r=dict(status='MEASURED',boundary='Consecutive completed original NMI audio-plan publication timestamps. Includes prior render, native engine/scheduler/NMI and adapter work occurring between publications; excludes the renderer after the final publication and does not separately attribute costs. Five diagnostic intervals, not sustained FPS.',rows=rows,total_interval_ms=sum(x['publication_interval_ms'] for x in rows),final_redraw_ticks=m[14]-m[13],final_redraw_ms=(m[14]-m[13])*1000/709379,all_completed_updates=m[2],late_updates=m[4])
 (b/'play-target-intervals.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));return r
if __name__=='__main__':check(Path(sys.argv[1]))
