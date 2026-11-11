#!/usr/bin/env python3
"""Original-source and actual PCM validation. PRIVATE captures are output only."""
from pathlib import Path
import argparse,struct,json,re,sys
import numpy as np
import verify_recovery_menu_sfx_target as target
import recovery_state_menu_display_pixels as pixels

def plan(r,en):
 assert not en&~15 and r[1]==r[5]==8 and r[8] in (0,255) and all(r[i]&48==48 for i in (0,4,12)) and r[14] in(7,13,129)
 ps=[];vs=[]
 for i,b in enumerate((0,4,8)):
  t=r[b+2]+256*(r[b+3]&7);p=((64 if i<2 else 32)*(t+1)+7)//15
  v=(2*(r[b]&15) if i<2 else 24) if en&(1<<i) and t>=(8 if i<2 else 2) and (i<2 or r[8]) else 0
  if p<124:assert not v;p=124
  ps.append(p);vs.append(v)
 return ps+[160]+vs+[2*(r[12]&15) if en&8 else 0]+[r[0]>>6,r[4]>>6,4,{7:5,13:6,129:7}[r[14]]]

def spectral(pcm,rows,plans,first):
 # First audible original-derived completed plan is noise-only on AUD3/left.
 # Align onset once; no per-window fitted clocks or prerecorded reference audio.
 rate=44100;hz=709379
 first_index=next(i for i,p in enumerate(plans) if any(p[4:8]))
 assert first_index==2 and plans[2][4:8]==[0,0,0,26]
 origin=first-rows[first_index]['published']*rate/hz
 def window(a,z):
  lo=round(origin+rows[a]['published']*rate/hz)+round(.008*rate)
  hi=round(origin+rows[z]['published']*rate/hz)-round(.008*rate)
  assert hi-lo>1000
  return pcm[lo:hi]
 n=window(2,7);assert np.all(n[:,1]==0) and np.std(n[:,0])>100,'initial noise must be left-only AC'
 z=window(8,11);assert np.max(np.abs(z))==0,'native silent plans must produce silence'
 assert all(plans[i][6:8]==[0,0] for i in (17,18))
 tone=window(17,19);assert len(tone)>4000
 spectrum=np.abs(np.fft.rfft((tone-tone.mean(axis=0))*np.hanning(len(tone))[:,None],n=131072,axis=0));freq=np.fft.rfftfreq(131072,1/rate)
 peaks=[]
 for channel in range(2):
  expected=3546895/(plans[17][channel]*8)
  # The strongest non-DC component must be the correct voice fundamental.
  band=np.where((freq>80)&(freq<2000))[0];k=band[np.argmax(spectrum[band,channel])];found=float(freq[k]);assert abs(found-expected)<8,(channel,found,expected)
  peaks.append(dict(channel=['left pulse1','right pulse2'][channel],nominal_Hz=expected,observed_Hz=found,window_seconds=len(tone)/rate,native_resolution_Hz=rate/len(tone)))
 return dict(initial_noise_left_only=True,native_silence_verified=True,pulse_fundamentals=peaks),tone,freq,spectrum

def check(b):
 cfg=json.loads((b/'build.json').read_text());history=cfg['history'];rom=(target.PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 chip=(b/'full-CHIP.bin').read_bytes();log=(b/'full.log').read_text();ref=target.oracle(rom,history)
 oldv,oldo=pixels.verify,pixels.oracle
 try:
  pixels.verify=lambda c,r,_:target.verify(c,r,ref)
  pixels.oracle=lambda _:ref
  result=pixels.check(chip,rom,log)
 finally:pixels.verify,pixels.oracle=oldv,oldo
 result['video']=pixels.verify_screen(chip,b/'full-screen.ppm')
 symbols={x.split()[-1]:int(x.split()[0],16) for x in (b/'adapter.symbols').read_text().splitlines() if len(x.split()) in (3,4)}
 adapter=(b/'adapter.bin').read_bytes();immutable=adapter[:symbols['mp']]
 assert chip.count(immutable)==1,'compiled adapter/planner/wave data altered'
 payload=(b/'target.bin').read_bytes();code=payload[:payload.index(b'CDRDIS01')];assert chip.count(code)==1
 p=chip.index(b'CDRPAU01');f=struct.unpack_from('>15I',chip,p+8)
 stage,writes,rtis,rejects,late,max_interval,max_work,start,last,stop,trace,shadow,enable,render_start,render_end=f
 assert stage==3 and rejects==0 and rtis==ref[1].summary['logical_NMIs'] and writes==ref[1].summary['APU_writes']
 r=bytearray(16);r[14]=7;en=0;expected=[]
 for helper,_,ctx,ram,journal,*rest in ref[0]:
  if journal:
   n=struct.unpack_from('>H',journal)[0]
   for i in range(n):
    a,v,k=struct.unpack_from('>HBB',journal,2+4*i)
    if 0x4000<=a<=0x400f:assert k==1;r[a-0x4000]=v
    elif a==0x4015:assert k==1;en=v
    elif 0x4010<=a<=0x4013:raise AssertionError('DMC')
  if helper in(8,20,42):expected.append((helper,en,bytes(r),plan(r,en)))
 assert len(expected)==rtis and bytes(chip[shadow:shadow+16])==r and enable==en
 rows=[];prev=start
 for i,(helper,en,r,pl) in enumerate(expected):
  q=trace+56*i;ready,published,end,h,e=struct.unpack_from('>3I2H',chip,q)
  assert (h,e)==(helper,en) and chip[q+16:q+32]==r and list(struct.unpack_from('>12H',chip,q+32))==pl
  assert published-prev>=14188 and end>=published and published>=ready
  rows.append(dict(ready=ready,published=published,end=end,interval=published-prev,helper=h,volumes=pl[4:8]));prev=published
 assert all(v==0 for row in rows[:2] for v in row['volumes'])
 assert max(x['interval'] for x in rows)==max_interval
 assert chip[trace+56*rtis:trace+56*256]==bytes(56*(256-rtis))
 assert stop>=render_end>render_start>=last
 pcm=np.fromfile(b/'full-capture.s16le',dtype='<i2').reshape(-1,2).astype(float)
 assert np.max(np.abs(pcm))<32767,'clipping'
 # Locate sound in actual callbacks, not boot duration or successful register writes.
 active=np.flatnonzero(np.any(pcm!=0,axis=1));assert len(active)>4410
 first,last_sample=int(active[0]),int(active[-1]);assert np.all(pcm[last_sample+1:]==0) and len(pcm)-last_sample>44100
 segment=pcm[first:last_sample+1];ac=np.sqrt(np.mean((segment-segment.mean(axis=0))**2,axis=0));assert np.all(ac>100)
 assert (last_sample-first)/44100<((stop-start)/709379)+0.25
 spec,tone,freq,spectrum=spectral(pcm,rows,[x[3] for x in expected],first)
 result['spectral']=spec
 result['audio']=dict(status='PASS',writes=writes,completed_RTI_plans=rtis,first_two_plans_silent=True,first_sample=first,last_sample=last_sample,active_seconds=(last_sample-first)/44100,AC_RMS=ac.tolist(),DC=segment.mean(axis=0).tolist(),min=segment.min(axis=0).tolist(),max=segment.max(axis=0).tolist(),final_silence_seconds=(len(pcm)-last_sample-1)/44100)
 result['timing']=dict(CIA_Hz=709379,display_dma_during_progression=cfg['display_dma'],late_completed_updates=late,max_interval_ticks=max_interval,max_hardware_apply_ticks=max_work,progression_ticks=last-start,final_render_ticks=render_end-render_start,final_hold_before_mute_ticks=stop-last,interval_ticks=[x['interval'] for x in rows],limit='Minimum completed-update spacing, not NES or video frame cadence. Five blank planes scan during progression in DMA-on case; only one final native render. Old plan continues during long work. No live keyboard or full-rate rendering.')
 result['memory']=cfg;result['private_records']=rows
 # Actual capture plots, not synthesised target output.
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(2,1,figsize=(10,6));t=np.arange(len(tone))/44100
 ax[0].plot(t[:882],tone[:882,0],label='left');ax[0].plot(t[:882],tone[:882,1],label='right',alpha=.7);ax[0].legend();ax[0].set(xlabel='seconds',ylabel='actual PCM',title='Completed native RTIs 18–19: isolated pulse channels')
 for c in range(2):ax[1].plot(freq,spectrum[:,c],label=['left','right'][c])
 ax[1].set(xlim=(0,2000),xlabel='Hz',ylabel='Hann FFT magnitude');ax[1].legend();fig.tight_layout();fig.savefig(b/'actual-waveform-spectrum.png');plt.close(fig)
 # Negative checks operate on copies, preserving the captured source.
 for kind in ('DC','swapped','wrong_tone'):
  bad=pcm.copy()
  if kind=='DC':bad[:]=1000
  elif kind=='swapped':bad=bad[:,::-1]
  else:
   origin=first-rows[2]['published']*44100/709379
   lo=round(origin+rows[17]['published']*44100/709379);hi=round(origin+rows[19]['published']*44100/709379)
   bad[lo:hi,0]=2000*np.sin(np.arange(hi-lo)*2*np.pi*1000/44100)
  try:spectral(bad,rows,[x[3] for x in expected],first)
  except AssertionError:pass
  else:raise AssertionError('negative accepted '+kind)
 result['negative_PCM_checks']=['DC','swapped','wrong_tone']
 (b/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('audio','timing','memory')},indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();check(a.output)
