#!/usr/bin/env python3
"""Diagnostic matched-history evidence; not an audio qualification bypass."""
from pathlib import Path
import argparse,json
from recovery_play_background_compare import history_digest

def check(b,control):
 for p in (b,control):
  for n in ('play-target-verification.json','play-target-replay.json','play-target-pcm.json'):
   assert json.loads((p/n).read_text())['status']=='PASS',(p,n)
 current=history_digest(b);old=history_digest(control);assert current==old,(current,old)
 result=dict(status='HISTORY_MATCH_ONLY',current=current,control=old,candidate_intervals=json.loads((b/'play-target-intervals.json').read_text()),control_intervals=json.loads((control/'play-target-intervals.json').read_text()),scope='Complete original helper/context/RAM/journal/runtime/pad/event/ordered-effect digest matches. This diagnostic does not qualify stage08 PCM, target release or sustainable FPS; measured timing is retained without a speedup claim.')
 (b/'play-background-history.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('capture',type=Path);a.add_argument('--control',type=Path,default=Path('port/build/recovery-play-target-v3'));v=a.parse_args();check(v.capture,v.control)
