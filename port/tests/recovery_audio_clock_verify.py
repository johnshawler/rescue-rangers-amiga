#!/usr/bin/env python3
"""Read-only requalification of existing PCM with source-attested callback time.
Writes only to a fresh separate output directory, never a capture/checkpoint.
"""
from pathlib import Path
import argparse,json,struct
import numpy as np
from recovery_audio_clock_model import attest,parse_log,sha
from recovery_audio_clock_classifier import Classifier,PHASES,WAVES,admitted
ROOT=Path(__file__).resolve().parents[2]

def endpoint(chip,pcm,model):
 m=struct.unpack_from('>16I',chip,chip.index(b'CDRPAU01')+8)
 overhead=m[9]-m[14]-14188;assert 0<=overhead<710
 p=struct.unpack_from('>12H',chip,m[10]+56*((m[2]-1)&255)+32)
 assert p[4]>0 and p[8]<4 and p[7]==0
 period=max(p[i] for i in range(4) if p[i+4])
 states=[65536.]*5
 for _ in range(32):
  value=0.
  for j in range(5):
   states[j]=(.48*value+.52*states[j])*1.000001+1e-8;value=states[j]
 assert states[-1]<.25
 local=model.seconds(overhead)+2*period/float(model.cck)+33/model.sample_rate
 # Additional conservative edge mapping allowance: two CIA quantization ticks,
 # one PCM sample for endpoint/edge rounding and one internal scheduler unit.
 mapping=2/float(model.cia)+1/model.sample_rate+1/(float(model.cck)*512)
 active=np.flatnonzero(np.any(pcm!=0,axis=1));assert len(active)
 assert len(pcm)-active[-1]>model.sample_rate
 total=local+mapping;assert total<100/model.sample_rate and total<.02
 return m,int(active[-1]),dict(status='PASS',render_end=m[14],stop=m[9],fixed_drain_ticks=14188,mute_overhead_ticks=overhead,maximum_audible_final_period=period,filter_residual_bound=states[-1],local_endpoint_bound_ms=1000*local,additional_mapping_quantization_ms=1000*mapping,total_corrected_placement_uncertainty_ms=1000*total,legacy_nominal_clock_scale_error_remaining=False,scale_model='Exact rational derived from attested float32 scheduler step; nominal-to-callback accumulated error corrected explicitly, not treated as endpoint noise.',tested_offset_samples=100,tested_offset_ms=100000/model.sample_rate,trailing_guard_ms=20,last_active_sample=int(active[-1]),terminal_silence_seconds=(len(pcm)-int(active[-1])-1)/model.sample_rate,final_plan=list(p))

def noise_windows(chip,pcm,model,m,last):
 anchor=m[9]-14188;rows=[];skipped=[];shifts=list(range(-100,101))
 for i in range(max(0,m[2]-256),m[2]-1):
  q=m[10]+56*(i&255);row=struct.unpack_from('>3I2H',chip,q);p=struct.unpack_from('>12H',chip,q+32)
  nxt=struct.unpack_from('>3I2H',chip,m[10]+56*((i+1)&255))
  if p[-1]!=8 or not p[7]:continue
  assert p[3]==160
  lo=model.index(last,anchor,row[1],.11);hi=model.index(last,anchor,nxt[1],-.02);n=hi-lo
  if n<2000:skipped.append(dict(RTI=i+1,samples=n,reason='Unchanged minimum window length'));continue
  assert 100<lo<hi<len(pcm)-100
  c=Classifier(n,p[0],model);s=c.scores(pcm[lo:hi,0]);assert admitted(s),('corrected noise',i+1,s)
  assert not admitted(c.scores(np.zeros(n))) and not admitted(c.scores(pcm[lo:hi,1])),'DC/channel negative'
  negatives=[w[(c.sample.astype(int)+phase)%2048] for w in WAVES[:3] for phase in PHASES]
  assert not any(admitted(x) for x in c.batch_scores(negatives)),'Old-loop phase admitted'
  shifted=[]
  for start in range(0,len(shifts),32):shifted.extend(c.batch_scores([pcm[lo+k:hi+k,0] for k in shifts[start:start+32]]))
  assert all(admitted(x) for x in shifted),('Corrected anchor robustness',i+1)
  scale=[((anchor-t)/709379-model.seconds(anchor-t))*1000 for t in (row[1],nxt[1])]
  rows.append(dict(RTI=i+1,samples=n,first_sample=lo,end_sample_exclusive=hi,noise_volume=p[7],scores=s,margin=s[3]-max(*s[:3],*s[4:]),legacy_omitted_scale_error_start_end_ms=scale,corrected_scale_uncertainty='No cumulative nominal-clock error under attested stable scheduler; edge quantization is separately bounded.',shift_checks=len(shifts),minimum_shift_margin=min(float(x[3]-max(*x[:3],*x[4:])) for x in shifted),minimum_shift_correlation=min(float(x[3]) for x in shifted),negative_old_loop_phases=len(negatives)))
 assert len(rows)==4 and not skipped,('Expected all four retained eligible windows',len(rows),skipped)
 return dict(status='PASS',windows=rows,skipped_windows=skipped,phase_count_each_hypothesis=128,rate_factors=[1,.5,2],threshold_correlation=.45,threshold_margin=.08,physical_guards_seconds=[.11,.02],shift_checks=201*len(rows),negative_checks=['DC','actual swapped channel','all 128 phases of all three old finite loops'])

def tonal_windows(capture,chip,pcm,model,m,last,rom_path):
 # Re-derive the same five original gameplay windows, not a selection from PCM.
 from recovery_play_target_oracle import oracle
 from recovery_play_target_verify import plan
 f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8);live=struct.unpack_from('>9I',chip,chip.index(b'CDRCLIV1')+8)
 changes=[struct.unpack_from('>4I',chip,live[4]+i*16) for i in range(live[5])]
 ref=oracle(rom_path.read_bytes(),changes,f[1])
 expected=[];game=[];r=bytearray(16);r[14]=7;en=0;arrivals=0
 for helper,_,ctx,ram,j,*_ in ref[0]:
  if j:
   for i in range(struct.unpack_from('>H',j)[0]):
    a,v,k=struct.unpack_from('>HBB',j,2+4*i)
    if 0x4000<=a<=0x400f:r[a-0x4000]=v
    elif a==0x4015:en=v
  if helper in (8,20,42):
   expected.append(plan(r,en))
   if arrivals:game.append(len(expected)-1)
  if ctx[:2]==b'\xc7\x7b':arrivals+=1
 assert len(game)==5 and arrivals==6 and len(expected)==m[2]
 rows=[];anchor=m[9]-14188
 for i in game:
  q=m[10]+56*(i&255);times=struct.unpack_from('>3I',chip,q);p=expected[i]
  assert list(struct.unpack_from('>12H',chip,q+32))==p and p[4]>0 and p[5]>0 and p[7]==0
  end=struct.unpack_from('>I',chip,m[10]+56*((i+1)&255)+4)[0] if i+1<m[2] else anchor
  lo=model.index(last,anchor,times[1],.11);hi=model.index(last,anchor,end,-.03)
  assert 0<lo<hi<len(pcm) and hi-lo>4000
  sample=pcm[lo:hi];expected_hz=[model.pulse_hz(p[c]) for c in range(2)]
  def measure(v):
   assert np.all(np.std(v,axis=0)>100),'DC/silence'
   freq=np.fft.rfftfreq(131072,1/model.sample_rate);fft=np.abs(np.fft.rfft((v-v.mean(axis=0))*np.hanning(len(v))[:,None],n=131072,axis=0));band=np.where((freq>80)&(freq<2000))[0]
   peaks=[float(freq[band[np.argmax(fft[band,c])]]) for c in range(2)]
   assert all(abs(peaks[c]-expected_hz[c])<8 for c in range(2)),(i+1,peaks,expected_hz)
   return peaks
  peaks=measure(sample);negative=[np.full_like(sample,1000),sample[:,::-1],sample.copy()]
  negative[-1][:,0]=2000*np.sin(np.arange(len(sample))*2*np.pi*1000/model.sample_rate)
  for bad in negative:
   try:measure(bad)
   except AssertionError:pass
   else:raise AssertionError(('Negative tonal window admitted',i+1))
  rows.append(dict(RTI=i+1,samples=hi-lo,first_sample=lo,end_sample_exclusive=hi,callback_expected_pulse_hz=expected_hz,observed_peak_hz=peaks,triangle_volume=p[6],noise_volume=p[7],legacy_omitted_scale_error_start_end_ms=[((anchor-t)/709379-model.seconds(anchor-t))*1000 for t in (times[1],end)]))
 return dict(status='PASS',windows=rows,physical_guards_seconds=[.11,.03],frequency_tolerance_hz=8,negative_checks=15,scope='Original-derived five gameplay windows. No independent triangle amplitude, envelope/mixing, phase-continuity or NES-fidelity claim.')

def verify(capture,identities,tool_attestation,rom_path):
 verify_input={name:sha(capture/name) for name in identities}
 assert verify_input==identities,'Capture changed or not approved'
 model,runtime=parse_log((capture/'full.log').read_text());chip=(capture/'full-CHIP.bin').read_bytes()
 pcm=np.fromfile(capture/'full-capture.s16le',dtype='<i2').reshape(-1,2).astype(float)
 # Callback format and count are attested independently of the FFT data.
 import re
 count=re.findall(r'^PASS runs=(\d+) video_callbacks=(\d+) .* audio_frames=(\d+) .*$',(capture/'full.log').read_text(),re.M)
 assert len(count)==1 and count[0][0]==count[0][1] and int(count[0][2])==len(pcm)
 m,last,bound=endpoint(chip,pcm,model);assert m[2] in (395,400)
 noise=noise_windows(chip,pcm,model,m,last)
 tonal=tonal_windows(capture,chip,pcm,model,m,last,rom_path) if m[2]==400 else None
 assert {name:sha(capture/name) for name in identities}==verify_input,'Read-only verification mutated capture'
 return dict(status='PASS',capture=capture.name,immutable_capture_hashes=verify_input,source_attestation=tool_attestation,clock=model.describe(),runtime_clock_attestation=runtime,endpoint_and_mapping_bound=bound,noise=noise,gameplay_tonal=tonal,supersedes='Prior nominal-clock PCM qualification/total-placement claims for this capture. Frozen files and earlier failures remain historical evidence, not current conclusions.',scope='Callback-clock audio discrimination only. No target binary change, recapture, hardware-equivalent timing redefinition, full-gameplay qualification or NES audio fidelity claim.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--capture-root',type=Path,default=ROOT/'port/build');ap.add_argument('--rom',type=Path,default=ROOT/'input/rescue-rangers-europe.nes');ap.add_argument('--core-root',type=Path,default=ROOT.parent/'amiga-recovery-tools/libretro-uae');ap.add_argument('--frontend',type=Path,default=ROOT/'port/build/experimental-direct-paula/headless');args=ap.parse_args()
 identities=json.loads((ROOT/'port/analysis/recovery_audio_clock_capture_manifest.json').read_text())['captures']
 out=args.output.resolve();assert not any(out.is_relative_to((args.capture_root/n).resolve()) for n in identities),'Output must be separate from every frozen capture'
 tools=attest(args.core_root,args.frontend);out.mkdir(parents=True,exist_ok=False);summary=[]
 for name,files in identities.items():
  result=verify(args.capture_root/name,files,tools,args.rom);(out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');summary.append(dict(capture=name,status='PASS',noise_windows=len(result['noise']['windows']),minimum_noise_margin=min(w['margin'] for w in result['noise']['windows']),minimum_shift_margin=min(w['minimum_shift_margin'] for w in result['noise']['windows']),tonal_windows=len(result['gameplay_tonal']['windows']) if result['gameplay_tonal'] else 0));print(json.dumps(summary[-1]),flush=True)
 (out/'summary.json').write_text(json.dumps(dict(status='PASS',captures=summary),indent=2)+'\n')
if __name__=='__main__':main()
