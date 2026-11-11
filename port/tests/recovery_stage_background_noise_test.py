#!/usr/bin/env python3
"""ROM-free phase/window positives and adversarial finite-loop classification."""
import numpy as np
from recovery_stage_background_noise_pcm import Classifier,WAVES,admitted

def main():
 rng=np.random.default_rng(1882048);count=0
 # 17-byte spacing visits every residue modulo the16-byte classifier stride.
 # Fractional starts also test output/sample alignment absent from the template grid.
 phases=[(17*i)%2048+.375 for i in range(128)]
 for n in (2000,2001,2984,4096,4130,10415):
  c=Classifier(n,1135);samples=c.sample
  for label,w in enumerate(WAVES):
   signals=[w[np.floor(samples+p).astype(int)%2048]*1.7+350 for p in phases]
   scores=c.batch_scores(signals)
   for phase,s in zip(phases,scores):assert admitted(s)==(label==3),(n,label,phase,s)
   count+=len(signals)
  adversarial=[np.zeros(n),np.full(n,1000),rng.normal(size=n)*64,rng.choice([-64.,64.],n)]
  for freq in (100,392,1000,2000,5000):adversarial.append(64*np.sin(np.arange(n)*2*np.pi*freq/44100))
  for rate in (.5,2.):
   adversarial.append(WAVES[3][np.floor(samples*rate+123.375).astype(int)%2048])
  for s in c.batch_scores(adversarial):assert not admitted(s),(n,'unrelated',s)
  count+=len(adversarial)
  # Mixed-channel positive: moderate pulse contamination, gain, DC and a
  # simple low-pass filter, at phases independent of the template grid.
  mixed=[]
  pulse=32*np.where((np.arange(n)*3546895/(8*1135*44100))%1<.25,1.,-1.)
  for phase in (3.125,511.75,1027.5,2011.25):
   v=WAVES[3][np.floor(samples+phase).astype(int)%2048]+pulse
   out=np.empty(n);out[0]=v[0]
   for j in range(1,n):out[j]=.65*v[j]+.35*out[j-1]
   mixed.append(out*1.3+300)
  for s in c.batch_scores(mixed):assert admitted(s),(n,'filtered pulse mix',s)
  count+=len(mixed)
  print('PASS synthetic length',n,'all four loops,128 off-grid fractional phases, DC/white/random/tones',flush=True)
 print('PASS',count,'phase/window classifications; unchanged .45 correlation and .08 margin; no target timing.')
if __name__=='__main__':main()
