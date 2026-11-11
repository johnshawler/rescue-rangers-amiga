#!/usr/bin/env python3
"""Validate private replay capture, independent synthetic tones and Chip waves."""
import argparse,hashlib,json,re,struct,wave
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();b=a.directory
ram=(b/'stock-CHIP.bin').read_bytes();assert len(ram)==2*1024*1024
pos=ram.index(b'DIRPAU01');stage,frame,total,maximum,summed,rejects,updates,start,end=struct.unpack_from('>9I',ram,pos+8)
assert stage==3 and frame==total==935 and rejects==0 and updates==944,(stage,frame,total,rejects,updates)
assert maximum<1000,maximum
log=(b/'stock.log').read_text()
for text in ('cpu_model=68020','chipset=aga','PAL mode V=50.0000Hz','chipmem_size=4','fastmem_size=0','cpu_cycle_exact=true','cpu_memory_cycle_exact=true','floppy_volume=100','sample_rate=44100.000'):assert text in log,text
symbols={s[2]:int(s[0],16) for line in (b/'symbols.txt').read_text().splitlines() if len(s:=line.split())==3};base=pos-symbols['dp_report']
# Compare deployed immutable waves and snapshots to the ELF image actually built.
payload=(b/'probe.bin').read_bytes()
for name,size in [('pulse',32),('tri',32),('dp_noise',6144),('dp_frames',935*16)]:
 off=symbols[name];assert ram[base+off:base+off+size]==payload[off:off+size]
s=np.fromfile(b/'capture.s16le',dtype='<i2').reshape(-1,2);onset=int(np.flatnonzero(abs(s[:,0].astype(float))>100)[0]);fs=44100
blocks=[]
chunks=[]
# Pinned PUAE callback conversion gain4/3, with unmodified volume registers:
# pulse/noise64*30*4/3=2560; triangle60*24*4/3=1920.
# These bounds describe this core/capture configuration, not a universal DAC.
amplitude_bounds=[[-2560,2560],[-2560,2560],[-1920,1920],
                  [-2560,2560],[-2560,2560],[720,2560]]
assert not np.any((s==-32768)|(s==32767)), 'Clipping anywhere in capture'

for i,name in enumerate(['pulse1','pulse2','triangle','noise07','noise0D','noise81','all','silence']):
 chunk=s[onset+int((i+.25)*fs):onset+int((i+.75)*fs)].astype(float);rms=np.sqrt(np.mean(chunk*chunk,axis=0));peaks=[]
 for ch in range(2):
  x=chunk[:,ch];spec=abs(np.fft.rfft((x-x.mean())*np.hanning(len(x))));peaks.append(float(np.argmax(spec[1:])+1)*fs/len(x))
 chunks.append(chunk)
 dc=chunk.mean(axis=0);ac=np.sqrt(np.mean((chunk-dc)**2,axis=0))
 mn=chunk.min(axis=0);mx=chunk.max(axis=0)
 expected=0 if i in (0,3,4,5) else 1
 if i<6:
  assert ac[expected]>100, ('Missing meaningful AC',name,ac)
  assert np.all(chunk[:,1-expected]==0), ('Channel isolation',name)
  low,high=amplitude_bounds[i]
  assert mn[expected]>=low-2 and mx[expected]<=high+2, ('Amplitude bounds',name,mn,mx)
  if i<5:
   assert mn[expected]<low*.9 and mx[expected]>high*.9, ('Unexpected attenuation',name)
 if i==6:
  assert min(ac)>100 and max(abs(chunk[:,0]))<=5122 and max(abs(chunk[:,1]))<=4482
 if i==7:assert np.all(chunk==0), 'Silence must be exactly zero'

 if i<6:assert rms[expected]>100 and rms[1-expected]<2,(name,rms)
 if i<2:assert abs(peaks[expected]-1662607/(16*236))<3
 if i==2:assert abs(peaks[expected]-1662607/(32*236))<3
 if i==6:assert min(rms)>100
 if i==7:assert max(rms)<2
 blocks.append({'name':name,'total_stereo_RMS':rms.tolist(),'DC':dc.tolist(),
                'AC_RMS':ac.tolist(),'min':mn.tolist(),'max':mx.tolist(),
                'clip_samples':0,'spectral_peak_Hz':peaks})
# Explicit finite-loop harmonic validation, not a NES-noise fidelity test.
# Half-second windows have2Hz native resolution. Zero-padding refines line
# location reporting to44100/262144Hz bins, not true frequency resolution.
N=262144
def spectrum(x):return abs(np.fft.rfft((x-x.mean())*np.hanning(len(x)),n=N))
sp=spectrum(chunks[0][:,0]);lo=round(430*N/fs);hi=round(450*N/fs)
pulse_bin=int(lo+np.argmax(sp[lo:hi+1]));pulse_hz=pulse_bin*fs/N
assert 438<pulse_hz<443
# Same normalization for all noise lines, inferred ONLY from independent pulse.
# Pulse timer235 maps to Paula period1007, with8 samples per loop.
clock=pulse_hz*8*1007
waves=np.frombuffer(payload,dtype='i1',offset=symbols['dp_noise'],count=6144).reshape(3,2048)
errors=[]
for i,w in enumerate(waves):
 sp=spectrum(chunks[3+i][:,0]);wp=abs(np.fft.rfft(w-w.mean()))
 lines=[]
 for harmonic in np.argsort(wp[1:])[-6:][::-1]+1:
  expected_hz=float(harmonic*clock/(160*2048))
  lo=round((expected_hz-3)*N/fs);hi=round((expected_hz+3)*N/fs)
  peak_bin=int(lo+np.argmax(sp[lo:hi+1]));captured_hz=peak_bin*fs/N
  error=abs(captured_hz-expected_hz)
  assert lo<peak_bin<hi and error<2, ('Finite-loop line mismatch',i,harmonic,error)
  assert sp[peak_bin]>.01*sp.max(), ('Finite-loop line missing',i,harmonic)
  errors.append(error)
  lines.append({'harmonic_index':int(harmonic),'expected_normalized_Hz':expected_hz,
                'capture_fft_bin':peak_bin,'captured_Hz':captured_hz,
                'absolute_error_Hz':error,'relative_peak_magnitude':float(sp[peak_bin]/sp.max())})
 blocks[3+i]['expected_unfiltered_amplitude_bounds']=amplitude_bounds[3+i]
 blocks[3+i]['finite_loop_harmonics']=lines
# Emit exactly the same slices as the earlier verifier; reuse original capture.
for first,name,length in [(0,'synthetic-blocks.wav',8),(8,'private-title-replay.wav',935/50)]:
 chunk=s[onset+int(first*fs):onset+int((first+length)*fs)]
 with wave.open(str(b/name),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(fs);f.writeframes(chunk.tobytes())
r={'status':'PASS','target':'stock PAL A1200OG, 68020 CPU/memory cycle exact, 2MiB Chip, zero Fast','replay_frames':frame,'planner_updates':updates,'rejections':rejects,'CIA_Eclock_Hz':709379,'max_update_Eticks':maximum,'max_update_us':maximum/709379*1e6,'mean_update_us':summed/updates/709379*1e6,'max_fraction_of_20ms_frame':maximum/709379/.02,'elapsed_TOD_ticks':(end-start)&0xffffff,'synthetic_blocks':blocks,'spectral_validation':{'pulse_capture_fft_bin':pulse_bin,'pulse_measured_Hz':pulse_hz,'clock_inferred_for_spectrum_only_Hz':clock,'zero_padded_bin_spacing_Hz':fs/N,'native_window_resolution_Hz':2,'max_harmonic_error_Hz':max(errors),'harmonics_checked':len(errors),'tolerance_Hz':2},'onset_sample':onset,'limitations':'Polling diagnostic has no spare CPU scheduling; measured update work excludes busy-wait, has no game/display workload, includes timer instrumentation. Not integrated native audio or exact APU reconstruction.'}
(b/'capture-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
