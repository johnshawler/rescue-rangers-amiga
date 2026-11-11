#!/usr/bin/env python3
"""PRIVATE captured finite-loop noise discrimination, not NES audio fidelity."""
from pathlib import Path
import sys,json,struct
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from experimental_direct_paula_build import noise

def check(b):
 chip=(b/'full-CHIP.bin').read_bytes();m=struct.unpack_from('>16I',chip,chip.index(b'CDRPAU01')+8)
 pcm=np.fromfile(b/'full-capture.s16le',dtype='<i2').reshape(-1,2).astype(float)
 active=np.flatnonzero(np.any(pcm!=0,axis=1))
 # Anchor from actual terminal DAC silence and measured20ms muted drain.
 # Filter tail is not sample-exact; guards exclude transitions and one2048 loop.
 origin=active[-1]/44100-(m[9]-14188)/709379
 waves=[np.array(noise(period,short)) for period,short in ((148,0),(944,0),(8,1),(188,0))]
 results=[]
 for i in range(max(0,m[2]-256),m[2]-1):
  q=m[10]+56*(i&255);row=struct.unpack_from('>3I2H',chip,q);p=struct.unpack_from('>12H',chip,q+32)
  nxt=struct.unpack_from('>3I2H',chip,m[10]+56*((i+1)&255))
  if p[-1]!=8 or not p[7]:continue
  lo=round((origin+row[1]/709379+.11)*44100);hi=round((origin+nxt[1]/709379-.02)*44100)
  n=hi-lo
  if n<2000:continue
  assert 0<lo<hi<len(pcm)
  f=np.fft.rfftfreq(65536,1/44100);mask=(f>80)&(f<6000)
  fundamental=3546895/(8*p[0])
  for k in range(1,40):mask &= abs(f-k*fundamental)>20
  sample=np.arange(n)*3546895/(160*44100)
  candidates=[w[sample.astype(int)%2048] for w in waves]
  def spectrum(v):return np.log1p(np.abs(np.fft.rfft((v-v.mean())*np.hanning(n),n=65536))**2)[mask]
  refs=[spectrum(v) for v in candidates]
  def scores(v):
   a=spectrum(v)
   if not np.std(a):return [-1]*4
   return [float(np.corrcoef(a,c)[0,1]) for c in refs]
  def admitted(s):return s[3]>.45 and s[3]>max(s[:3])+.08
  s=scores(pcm[lo:hi,0]);assert admitted(s),('stage08 spectrum',i+1,s)
  assert not admitted(scores(np.zeros(n))),'DC accepted'
  assert not admitted(scores(pcm[lo:hi,1])),'swapped channels accepted'
  for old in candidates[:3]:assert not admitted(scores(old)),'old noise loop accepted'
  results.append(dict(RTI=i+1,samples=n,noise_volume=p[7],correlation_by_wave5_6_7_8=s))
 assert results,'No captured audible08 interval available'
 report=dict(status='PASS',windows=results,negative_checks=['DC','swapped channels','each old finite loop'],alignment='terminal DAC silence minus measured20ms mute drain;110ms leading and20ms trailing guards',scope='Discriminates captured approximate PAL188 long-mode finite loop from old loops in mixed left channel after excluding pulse harmonics. Does not establish NES noise/envelope/mixing fidelity or absolute audio latency.')
 (b/'stage-target-noise-pcm.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report
if __name__=='__main__':check(Path(sys.argv[1]))
