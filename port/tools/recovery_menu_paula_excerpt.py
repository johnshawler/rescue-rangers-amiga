#!/usr/bin/env python3
"""Private lossless actual-callback excerpt, with 200ms lead/400ms silent tail."""
import argparse,hashlib,json,wave
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();b=a.output
raw=(b/'full-capture.s16le').read_bytes();pcm=np.frombuffer(raw,'<i2').reshape(-1,2)
active=np.flatnonzero(np.any(pcm!=0,axis=1));lo=int(active[0])-8820;hi=int(active[-1])+17641
assert lo>=0 and hi<len(pcm) and np.all(pcm[hi-17640:hi]==0)
out=b/'private-right-selection-preview.wav';assert not out.exists()
with wave.open(str(out),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(raw[lo*4:hi*4])
r=dict(source='full-capture.s16le',source_sha256=hashlib.sha256(raw).hexdigest(),first_sample_inclusive=lo,end_sample_exclusive=hi,frames=hi-lo,seconds=(hi-lo)/44100,format='44100Hz stereo signed16 little-endian, unchanged callback samples',wav_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),label='Bounded native menu/Paula diagnostic with right selection; not playable release or exact NES fidelity')
(b/'preview.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
