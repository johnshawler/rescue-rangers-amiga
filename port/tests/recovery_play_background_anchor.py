#!/usr/bin/env python3
"""Re-establish the endpoint/phase-window bound for this new gameplay capture.
No window fitting: same 110ms/20ms guards, .45/.08 gates, and +/-100 samples.
Pinned source structural premises are documented separately; no target changes.
"""
from pathlib import Path
import argparse,hashlib,json,struct
import numpy as np
from recovery_stage_background_pcm_anchor import check as numeric_bound
from recovery_stage_background_noise_pcm import Classifier,admitted
ROOT=Path(__file__).resolve().parents[2]

def check(b,tool_root,frontend):
 expected={
  'sources/src/audio.c':'4f010577a1a3d8338da94aa26681ac95a813164331874b2b9f2a20661199aeb0',
  'libretro/libretro-core.c':'ba1024fdd269b6609283f719054bcaa50a33cb6425eff0be6a5d463863a74171',
  'sources/src/driveclick.c':'c265db935b3dc1f1fae49607fe99c3e8733cc56f4ac1a9955992f6e29e81c33e',
  'puae_libretro.so':'84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456'}
 for n,h in expected.items():assert hashlib.sha256((tool_root/n).read_bytes()).hexdigest()==h,n
 for path,h in ((frontend,'5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1'),(ROOT/'port/tools/experimental_paula_headless.c','58ce7adb87e69c584cbe6cbb081d1c66632abeb7d76f9f6d312a2722ce250939'),(b/'adapter.bin','cb0ee1dbef484f0a54ad764408d1d20112af87c4f35396d33a513b3d915bce12')):
  assert hashlib.sha256(path.read_bytes()).hexdigest()==h,str(path)
 for n in ('play-target-verification.json','play-target-pcm.json'):
  assert json.loads((b/n).read_text())['status']=='PASS',n
 bound=numeric_bound(b)
 chip=(b/'full-CHIP.bin').read_bytes();m=struct.unpack_from('>16I',chip,chip.index(b'CDRPAU01')+8)
 final=struct.unpack_from('>12H',chip,m[10]+56*((m[2]-1)&255)+32)
 assert final[:4]==(1011,2266,567,160) and final[4:8]==(4,16,0,0),final
 assert m[2]==400 and m[1]==2931
 pcm=np.fromfile(b/'full-capture.s16le',dtype='<i2').reshape(-1,2).astype(float)
 active=np.flatnonzero(np.any(pcm!=0,axis=1));origin=active[-1]/44100-(m[9]-14188)/709379
 windows=json.loads((b/'play-background-noise-audit.json').read_text())['windows'];rows=[];all_good=True
 for w in windows:
  i=w['RTI']-1;q=m[10]+56*(i&255);times=struct.unpack_from('>3I',chip,q);p=struct.unpack_from('>12H',chip,q+32)
  nxt=struct.unpack_from('>3I',chip,m[10]+56*((i+1)&255))
  lo=round((origin+times[1]/709379+.11)*44100);hi=round((origin+nxt[1]/709379-.02)*44100)
  assert hi-lo==w['samples'] and lo>100 and hi+100<len(pcm)
  c=Classifier(hi-lo,p[0]);offsets=list(range(-100,101));scores=[]
  for start in range(0,len(offsets),32):scores.extend(c.batch_scores([pcm[lo+k:hi+k,0] for k in offsets[start:start+32]]))
  margins=[float(s[3]-max(*s[:3],*s[4:])) for s in scores];failed=[k for k,s in zip(offsets,scores) if not admitted(s)]
  all_good &= not failed
  rows.append(dict(RTI=i+1,samples=hi-lo,tested_offsets=offsets,failed_offsets=failed,minimum_margin=min(margins),minimum_correlation=min(float(s[3]) for s in scores)))
 result=dict(status='PASS' if all_good else 'FAIL',endpoint_bound_status='PASS',numeric_bound=bound,final_plan=list(final),source_sha256=expected,offset_windows=rows,total_shift_checks=201*len(rows),threshold_correlation=.45,threshold_margin=.08,scope='New-capture endpoint bound and all integer offsets within +/-100 samples for unchanged eligible noise windows. Does not prove arbitrary shifts, exact phase, physical-hardware latency, or NES waveform/envelope/mixing fidelity.')
 (b/'play-background-anchor.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert all_good,'Capture-specific anchor robustness failed'
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('capture',type=Path);a.add_argument('--tool-root',type=Path,default=ROOT.parent/'amiga-recovery-tools/libretro-uae');a.add_argument('--frontend',type=Path,default=ROOT/'port/build/experimental-direct-paula/headless');v=a.parse_args();check(v.capture,v.tool_root,v.frontend)
