"""Clock-parameterized classifier, preserving frozen signal tests and gates."""
import numpy as np
from recovery_stage_background_noise_pcm import Classifier as FrozenClassifier,PHASES,WAVES,RATE_FACTORS,admitted
class Classifier(FrozenClassifier):
 def __init__(self,n,pulse_period,model):
  assert 2000<=n<=65536 and pulse_period>0
  self.n=n;self.sample=np.arange(n)*model.noise_rate();self.window=np.hanning(n)
  f=np.fft.rfftfreq(65536,1/model.sample_rate);self.mask=(f>80)&(f<6000)
  fundamental=model.pulse_hz(pulse_period)
  for k in range(1,40):self.mask &= abs(f-k*fundamental)>20
  self.refs=np.stack([self.normalized(w[((self.sample*factor).astype(int)+p)%2048]) for factor in RATE_FACTORS for w in WAVES for p in PHASES])
