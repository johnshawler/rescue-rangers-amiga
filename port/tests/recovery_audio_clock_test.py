#!/usr/bin/env python3
"""ROM-free clock attestation, parity and phase/adversarial regressions."""
from fractions import Fraction
from pathlib import Path
import hashlib,tempfile,importlib.abc,sys
import numpy as np
from recovery_audio_clock_model import parse_log,ClockModel,verify_hashes
from recovery_audio_clock_classifier import Classifier,WAVES,admitted
from recovery_stage_background_noise_pcm import Classifier as FrozenClassifier

PREFIX='''Model: "A1200OG".
ntsc=false
cpu_model=68020
cpu_cycle_exact=true
cpu_memory_cycle_exact=true
sound_interpol=anti
sound_filter=emulated
floppy_volume=100
SNDRATE 312.0*227.0*50.000000=3541200.000000
SNDRATE 313.0*227.0*50.000000=3552550.000000
region=1 fps=50.000000000 sample_rate=44100.000
'''
class DenyPrivate(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if 'oracle' in fullname or fullname.startswith('py65'):raise ImportError('Private original oracle denied')
def guard(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)) and str(args[0]).lower().endswith('.nes'):raise PermissionError('ROM denied')

def main():
 sys.meta_path.insert(0,DenyPrivate());sys.addaudithook(guard)
 model,proof=parse_log(PREFIX)
 assert model.scheduler_step==41245.0234375
 assert model.cck==Fraction(5279363,128)*44100/512
 assert float(model.cck)==3552549.870300293 and float(model.cia)==710509.9740600586
 assert parse_log(PREFIX+'SNDRATE 313.0*227.0*50.000000=3552550.000000\n')[0]==model
 assert parse_log(PREFIX.replace('SNDRATE 312.0*227.0*50.000000=3541200.000000\n',''))[0]==model
 edits=[('SNDRATE 313.0*227.0*50.000000=3552550.000000','SNDRATE 313.0*227.0*50.000000=3552549.750000'),('313.0','312.5'),('sample_rate=44100.000','sample_rate=48000.000'),('fps=50.000000000','fps=60.000000000'),('ntsc=false','ntsc=true'),('cpu_model=68020','cpu_model=68000'),('sound_interpol=anti','sound_interpol=sinc'),('sound_filter=emulated','sound_filter=off'),('floppy_volume=100','floppy_volume=0'),('A1200OG','A500'),('SNDRATE 313.0*227.0*50.000000=3552550.000000','SNDRATE NaN*227.0*50.000000=NaN')]
 invalid=[PREFIX.replace(a,b) for a,b in edits]
 invalid += [PREFIX+'SNDRATE 312.0*227.0*50.000000=3541200.000000\n',PREFIX+'region=1 fps=50.000000000 sample_rate=44100.000\n',PREFIX+'sound_interpol=sinc\n','KEY logical_tick=1\n'+PREFIX,PREFIX.replace('SNDRATE 313.0*227.0*50.000000=3552550.000000\n',''),PREFIX.replace('region=1 fps=50.000000000 sample_rate=44100.000\n',''),PREFIX.replace('cpu_memory_cycle_exact=true\n',''),PREFIX.replace('SNDRATE 313.0*227.0*50.000000=3552550.000000\n','')+'SNDRATE 313.0*227.0*50.000000=3552550.000000\n']
 for log in invalid:
  try:parse_log(log)
  except AssertionError:pass
  else:raise AssertionError(('Unsupported timing admitted',log))
 with tempfile.TemporaryDirectory() as t:
  root=Path(t);(root/'source').write_bytes(b'pinned');h=hashlib.sha256(b'pinned').hexdigest();verify_hashes(root,{'source':h});(root/'source').write_bytes(b'changed')
  try:verify_hashes(root,{'source':h})
  except AssertionError:pass
  else:raise AssertionError('Changed source identity admitted')
 # At an identical nominal rate, the new layer is bit-exact with the frozen
 # classifier. Corrected production parsing cannot select this synthetic model.
 nominal=ClockModel(Fraction(3546895));n=2984
 old=FrozenClassifier(n,1135);same=Classifier(n,1135,nominal)
 assert np.array_equal(old.sample,same.sample) and np.array_equal(old.mask,same.mask) and np.array_equal(old.refs,same.refs)
 assert old.scores(WAVES[3][old.sample.astype(int)%2048])==same.scores(WAVES[3][same.sample.astype(int)%2048])
 for tick in (100,100000,50000000):
  legacy=round((1234.5-60000000/709379+tick/709379+.11)*44100)
  assert nominal.index(round(1234.5*44100),60000000,tick,.11)==legacy
 assert abs(model.seconds(4000000)-4000000/709379)>.008
 assert model.noise_rate()==float(model.cck)/(160*44100)
 assert model.pulse_hz(1135)==float(model.cck)/(8*1135)
 print('PASS clock/model identity, malformed/ambiguous/unsupported negatives:',len(invalid),'and exact old/new same-rate parity',flush=True)
 rng=np.random.default_rng(1882048);count=0;phases=[(17*i)%2048+.375 for i in range(128)]
 for n in (2000,2001,2984,4096,4130,10415):
  c=Classifier(n,1135,model);sample=c.sample
  for label,w in enumerate(WAVES):
   signals=[w[np.floor(sample+p).astype(int)%2048]*1.7+350 for p in phases]
   for phase,s in zip(phases,c.batch_scores(signals)):assert admitted(s)==(label==3),(n,label,phase,s)
   count+=len(signals)
  bad=[np.zeros(n),np.full(n,1000),rng.normal(size=n)*64,rng.choice([-64.,64.],n)]
  for freq in (100,392,1000,2000,5000):bad.append(64*np.sin(np.arange(n)*2*np.pi*freq/44100))
  for rate in (.5,2.):bad.append(WAVES[3][np.floor(sample*rate+123.375).astype(int)%2048])
  assert not any(admitted(s) for s in c.batch_scores(bad));count+=len(bad)
  mixed=[];pulse=32*np.where((np.arange(n)*model.pulse_hz(1135)/44100)%1<.25,1.,-1.)
  for phase in (3.125,511.75,1027.5,2011.25):
   v=WAVES[3][np.floor(sample+phase).astype(int)%2048]+pulse;out=np.empty(n);out[0]=v[0]
   for j in range(1,n):out[j]=.65*v[j]+.35*out[j-1]
   mixed.append(out*1.3+300)
  assert all(admitted(s) for s in c.batch_scores(mixed));count+=len(mixed)
  print('PASS corrected-clock synthetic length',n,flush=True)
 print('PASS',count,'corrected-rate phase/window classifications; original gates and selection unchanged.')
if __name__=='__main__':main()
