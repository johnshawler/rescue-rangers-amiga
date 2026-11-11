#!/usr/bin/env python3
"""Actual five neutral-gameplay PCM windows; approximate Paula tonal output only."""
from pathlib import Path
import json,struct,sys
import numpy as np
from recovery_play_target_oracle import oracle
from recovery_play_target_verify import plan

def check(b):
 chip=(b/'full-CHIP.bin').read_bytes();m=struct.unpack_from('>16I',chip,chip.index(b'CDRPAU01')+8)
 f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8);live=struct.unpack_from('>9I',chip,chip.index(b'CDRCLIV1')+8)
 changes=[struct.unpack_from('>4I',chip,live[4]+i*16) for i in range(live[5])]
 ref=oracle(Path('input/rescue-rangers-europe.nes').read_bytes(),changes,f[1])
 expected=[];game_rtis=[];r=bytearray(16);r[14]=7;en=0;arrivals=0
 for helper,_,ctx,ram,j,*_ in ref[0]:
  if j:
   for i in range(struct.unpack_from('>H',j)[0]):
    a,v,k=struct.unpack_from('>HBB',j,2+4*i)
    if 0x4000<=a<=0x400f:r[a-0x4000]=v
    elif a==0x4015:en=v
  if helper in (8,20,42):
   expected.append(plan(r,en))
   if arrivals:game_rtis.append(len(expected)-1)
  if ctx[:2]==b'\xc7\x7b':arrivals+=1
 assert len(game_rtis)==5 and arrivals==6 and len(expected)==m[2]
 pcm=np.fromfile(b/'full-capture.s16le',dtype='<i2').reshape(-1,2).astype(float)
 active=np.flatnonzero(np.any(pcm!=0,axis=1));origin=active[-1]/44100-(m[9]-14188)/709379
 rows=[]
 for i in game_rtis:
  q=m[10]+56*(i&255);times=struct.unpack_from('>3I',chip,q);actual=list(struct.unpack_from('>12H',chip,q+32));p=expected[i]
  assert actual==p and p[4]>0 and p[5]>0 and p[7]==0
  end=struct.unpack_from('>I',chip,m[10]+56*((i+1)&255)+4)[0] if i+1<m[2] else m[9]-14188
  lo=round((origin+times[1]/709379+.11)*44100);hi=round((origin+end/709379-.03)*44100)
  assert 0<lo<hi<len(pcm) and hi-lo>4000
  sample=pcm[lo:hi];nominal=[3546895/(p[c]*8) for c in range(2)]
  def measure(v):
   assert np.all(np.std(v,axis=0)>100),'DC or silence'
   freq=np.fft.rfftfreq(131072,1/44100);fft=np.abs(np.fft.rfft((v-v.mean(axis=0))*np.hanning(len(v))[:,None],n=131072,axis=0))
   band=np.where((freq>80)&(freq<2000))[0];peaks=[float(freq[band[np.argmax(fft[band,c])]]) for c in range(2)]
   assert all(abs(peaks[c]-nominal[c])<8 for c in range(2)),(i+1,peaks,nominal)
   return peaks
  peaks=measure(sample)
  negatives={'DC':np.full_like(sample,1000),'swapped':sample[:,::-1],'wrong_left_tone':sample.copy()}
  negatives['wrong_left_tone'][:,0]=2000*np.sin(np.arange(len(sample))*2*np.pi*1000/44100)
  for name,bad in negatives.items():
   try:measure(bad)
   except AssertionError:pass
   else:raise AssertionError(('negative PCM admitted',name,i+1))
  rows.append(dict(RTI=i+1,samples=len(sample),nominal_pulse_Hz=nominal,observed_peak_Hz=peaks,triangle_volume=p[6],noise_volume=p[7]))
 result=dict(status='PASS',gameplay_windows=rows,negative_checks=['DC','channel_swap','wrong_left_tone'],scope='Five actual original-derived gameplay plan windows have correct stereo tonal peaks. Right pulse and triangle frequencies coincide closely in these frames; this does not separately establish triangle amplitude, envelope/mixing fidelity, phase continuity or original NES audio fidelity. Full record-ring comparison and stage08 noise discrimination remain separate required checks.')
 (b/'play-target-pcm.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':check(Path(sys.argv[1]))
