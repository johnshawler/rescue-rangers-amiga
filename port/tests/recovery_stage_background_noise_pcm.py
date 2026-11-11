#!/usr/bin/env python3
"""Additive phase-aware finite-loop discrimination. No NES fidelity claim.
Keeps the frozen verifier's windows, spectral bands, pulse-harmonic exclusion,
and thresholds. Each candidate gets the same 128 uniformly spaced loop phases.
Additional half/double-rate hypotheses reject gross playback-rate aliases.
The frozen phase-zero verifier and its rejected capture remain unchanged.
"""
from pathlib import Path
import json,struct,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from experimental_direct_paula_build import noise
PHASES=tuple(range(0,2048,16))
WAVES=tuple(np.array(noise(p,s),dtype=float) for p,s in ((148,0),(944,0),(8,1),(188,0)))
RATE=3546895/(160*44100)
RATE_FACTORS=(1.,.5,2.)

def admitted(s):
 assert len(s)==12
 return s[3]>.45 and s[3]>max([*s[:3],*s[4:]])+.08

class Classifier:
 def __init__(self,n,pulse_period):
  assert 2000<=n<=65536 and pulse_period>0
  self.n=n;self.sample=np.arange(n)*RATE;self.window=np.hanning(n)
  f=np.fft.rfftfreq(65536,1/44100);self.mask=(f>80)&(f<6000)
  fundamental=3546895/(8*pulse_period)
  for k in range(1,40):self.mask &= abs(f-k*fundamental)>20
  self.refs=np.stack([self.normalized(w[((self.sample*factor).astype(int)+p)%2048]) for factor in RATE_FACTORS for w in WAVES for p in PHASES])
 def normalized(self,v):
  assert len(v)==self.n
  a=np.log1p(np.abs(np.fft.rfft((v-np.mean(v))*self.window,n=65536))**2)[self.mask]
  a-=a.mean();norm=np.linalg.norm(a)
  return a/norm if norm else np.zeros_like(a)
 def scores(self,v):
  a=self.normalized(v)
  if not np.any(a):return [-1.0]*12
  return (self.refs@a).reshape(12,len(PHASES)).max(axis=1).tolist()
 def batch_scores(self,values):
  a=np.stack([self.normalized(v) for v in values]);s=(a@self.refs.T).reshape(len(a),12,len(PHASES)).max(axis=2)
  s[np.all(a==0,axis=1)]=-1
  return s

def check(b,report_path=None):
 chip=(b/'full-CHIP.bin').read_bytes();m=struct.unpack_from('>16I',chip,chip.index(b'CDRPAU01')+8)
 pcm=np.fromfile(b/'full-capture.s16le',dtype='<i2').reshape(-1,2).astype(float)
 active=np.flatnonzero(np.any(pcm!=0,axis=1));assert len(active)
 origin=active[-1]/44100-(m[9]-14188)/709379
 results=[];skipped=[]
 for i in range(max(0,m[2]-256),m[2]-1):
  q=m[10]+56*(i&255);row=struct.unpack_from('>3I2H',chip,q);p=struct.unpack_from('>12H',chip,q+32)
  nxt=struct.unpack_from('>3I2H',chip,m[10]+56*((i+1)&255))
  if p[-1]!=8 or not p[7]:continue
  assert p[3]==160
  lo=round((origin+row[1]/709379+.11)*44100);hi=round((origin+nxt[1]/709379-.02)*44100);n=hi-lo
  if n<2000:skipped.append(dict(RTI=i+1,samples=n,reason='Frozen minimum window'));continue
  assert 0<lo<hi<len(pcm)
  c=Classifier(n,p[0]);s=c.scores(pcm[lo:hi,0]);assert admitted(s),('phase-aware stage08',i+1,s)
  assert not admitted(c.scores(np.zeros(n))),'DC accepted'
  assert not admitted(c.scores(pcm[lo:hi,1])),'swapped channels accepted'
  # Every old candidate phase is an explicit adversarial alternative.
  negatives=[w[(c.sample.astype(int)+phase)%2048] for w in WAVES[:3] for phase in PHASES]
  ns=c.batch_scores(negatives);assert not any(admitted(x) for x in ns),'old phase accepted'
  results.append(dict(RTI=i+1,samples=n,noise_volume=p[7],correlation_by_wave5_6_7_8=s[:4],half_rate_correlations=s[4:8],double_rate_correlations=s[8:],negative_old_loop_phases=len(negatives)))
 assert results,'No captured audible08 interval available'
 result=dict(status='PASS',windows=results,skipped_audible_windows=skipped,phases_per_candidate=len(PHASES),phase_stride=16,rate_factors=RATE_FACTORS,threshold_correlation=.45,threshold_margin=.08,negative_checks=['DC','swapped channels','all 128 phases of each old loop'],alignment='Unchanged terminal DAC silence minus measured20ms mute drain;110ms leading and20ms trailing guards',frozen_phase_zero_verifier='Preserved separately; this additive classifier does not rewrite its result.',scope='Approximate PAL188 finite-loop discrimination only. No NES audio fidelity, exact phase, absolute latency, envelope, or mixing fidelity claim.')
 (report_path or b/'stage-background-noise-pcm.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':check(Path(sys.argv[1]))
