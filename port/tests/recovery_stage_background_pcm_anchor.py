#!/usr/bin/env python3
"""Private numeric audit of conservative terminal-anchor placement bound.
Structural premises and pinned core identities are in the accompanying report.
This does not select or alter the classifier's predeclared windows.
"""
from pathlib import Path
import argparse,json,struct,re
import numpy as np

def check(b):
 log=(b/'full.log').read_text()
 for name,value in (('floppy_volume','100'),('sound_interpol','anti')):
  values=re.findall(r'^'+name+r'=(.*)$',log,re.M);assert values and all(v.strip()==value for v in values),(name,values)
 assert 'sample_rate=44100.000' in log
 chip=(b/'full-CHIP.bin').read_bytes();m=struct.unpack_from('>16I',chip,chip.index(b'CDRPAU01')+8)
 overhead=m[9]-m[14]-14188;assert 0<=overhead<709
 q=m[10]+56*((m[2]-1)&255);p=struct.unpack_from('>12H',chip,q+32)
 # The final left channel is a nonzero pulse, with muted noise. No long natural
 # zero run can masquerade as the terminal mute. Exact plans separately verified.
 assert p[4]>0 and p[8]<4 and p[7]==0
 period=max(p[i] for i in range(4) if p[i+4])
 # All five hypothetical RC stages start at twice the maximum signed16 input.
 # a=.48 is slower than every configured fixed/LED cutoff. The relative
 # inflation comfortably exceeds float rounding; additive term bounds denormals.
 states=[65536.]*5
 for _ in range(32):
  value=0.
  for j in range(5):
   states[j]=(.48*value+.52*states[j])*1.000001+1e-8
   value=states[j]
 assert states[-1]<.25
 seconds=overhead/709379+2*period/3546895+33/44100
 assert seconds<100/44100 and seconds<.02
 pcm=np.fromfile(b/'full-capture.s16le',dtype='<i2').reshape(-1,2)
 active=np.flatnonzero(np.any(pcm,axis=1));assert len(active)
 assert len(pcm)-active[-1]>44100
 result=dict(status='PASS',render_end=m[14],stop=m[9],drain_ticks=14188,mute_overhead_upper_ticks=overhead,mute_overhead_ms=overhead*1000/709379,maximum_audible_final_period=period,two_period_ms=2*period*1000/3546895,filter_samples=32,filter_residual_bound=states[-1],anti_quantization_samples=1,conservative_anchor_bound_ms=seconds*1000,independently_tested_offset_samples=100,independently_tested_offset_ms=100000/44100,trailing_guard_ms=20,terminal_last_nonzero_sample=int(active[-1]),premises='Pinned core sample latch/filter/anti accumulation, callback copies without resampling, continuous final nonzero pulse, no other terminal audio source. See durable bound report.')
 (b/'stage-background-anchor.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('capture',type=Path);a=ap.parse_args();check(a.capture)
