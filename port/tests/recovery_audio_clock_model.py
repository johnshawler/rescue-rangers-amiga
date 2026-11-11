#!/usr/bin/env python3
"""Pinned PUAE callback-clock attestation; never a hardware-speed conversion."""
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import hashlib,re,struct

CORE_SHA='84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456'
FRONTEND_SHA='5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1'
SOURCE_HASHES={
 'sources/src/custom.c':'31654d92277bbd1dd469d64244e3500c9097d9d992fb1bed358cf2c8fbc25f16',
 'sources/src/devices.c':'b6fc3f99d30aa7e2582bcd20770add86a4c5ae6b6af8fbe8521f30ff080a41a4',
 'sources/src/cia.c':'d9516d56e44c5e1ce2680ea3d00574bda8c5e6a73770433bd0d41d44cb521e42',
 'sources/src/include/sysdeps.h':'3acb3495ad3fbbd349b3cb4f90e0a033376a6dadbd5974e6e568941f6e613455',
 'retrodep/sounddep/sound.c':'e1e6173b2ca91d1d5cd40beda3677362a5916d8cda8c7beb2357ea986234623e',
 'sources/src/audio.c':'4f010577a1a3d8338da94aa26681ac95a813164331874b2b9f2a20661199aeb0',
 'libretro/libretro-core.c':'ba1024fdd269b6609283f719054bcaa50a33cb6425eff0be6a5d463863a74171',
 'sources/src/driveclick.c':'c265db935b3dc1f1fae49607fe99c3e8733cc56f4ac1a9955992f6e29e81c33e'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def f32(value):return struct.unpack('>f',struct.pack('>f',value))[0]

def verify_hashes(root,expected):
 for name,digest in expected.items():assert sha(root/name)==digest,('Unsupported tool/source identity',name)
 return dict(expected)
def attest(core_root,frontend):
 result=verify_hashes(core_root,{**SOURCE_HASHES,'puae_libretro.so':CORE_SHA})
 assert sha(frontend)==FRONTEND_SHA,'Unsupported callback frontend'
 return dict(core_sources=result,frontend_sha256=FRONTEND_SHA,reference_source_commit='d366f77c60e5a5f059f129cc3773d3048306083b')

@dataclass(frozen=True)
class ClockModel:
 cck:Fraction
 sample_rate:int=44100
 scheduler_step:float|None=None
 @property
 def cia(self):return self.cck/5
 def seconds(self,ticks):return float(Fraction(ticks)/self.cia)
 def noise_rate(self):return float(self.cck)/(160*self.sample_rate)
 def pulse_hz(self,period):return float(self.cck)/(8*period)
 def index(self,last_active,anchor_tick,tick,guard):
  # Relative timestamps avoid cancellation of large absolute clock values.
  return round(last_active+(self.seconds(tick-anchor_tick)+guard)*self.sample_rate)
 def describe(self):
  return dict(runtime_logged_cck_hz=3552550,scheduler_step_internal_units=self.scheduler_step,cycle_unit=512,sound_sync_multiplier=1,callback_cck_fraction=[self.cck.numerator,self.cck.denominator],callback_cck_hz=float(self.cck),callback_cia_fraction=[self.cia.numerator,self.cia.denominator],callback_cia_hz=float(self.cia),sample_rate=self.sample_rate,hardware_equivalent_cia_hz=709379,scope='Callback PCM time/frequency only. Hardware-equivalent performance conversions remain separate.')

SND=re.compile(r'^SNDRATE ([0-9]+\.[0-9]+)\*([0-9]+\.[0-9]+)\*([0-9]+\.[0-9]+)=([0-9]+\.[0-9]+)$')
REGION=re.compile(r'^region=(\d+) fps=([0-9]+\.[0-9]+) sample_rate=([0-9]+\.[0-9]+)$')
def parse_log(log):
 lines=log.splitlines();rates=[];regions=[]
 for i,line in enumerate(lines):
  if line.startswith('SNDRATE'):
   match=SND.fullmatch(line);assert match,('Malformed SNDRATE',line)
   v,h,f,rate=map(Decimal,match.groups());assert v*h*f==rate,('Inconsistent SNDRATE',line)
   assert (v,h,f,rate) in ((Decimal(312),Decimal(227),Decimal(50),Decimal(3541200)),(Decimal(313),Decimal(227),Decimal(50),Decimal(3552550))),('Unsupported runtime clock',line)
   rates.append((i,int(rate)))
  if line.startswith('region='):
   match=REGION.fullmatch(line);assert match,('Malformed callback rate',line)
   region,fps,sample=match.groups();assert (int(region),Decimal(fps),Decimal(sample))==(1,Decimal(50),Decimal(44100)),'Unsupported callback format'
   regions.append(i)
 assert rates and len(regions)==1,'Missing/ambiguous timing attestation'
 final_start=next((i for i,r in rates if r==3552550),None)
 assert final_start is not None and final_start<regions[0],'Clock not established before callbacks'
 assert all(r==3552550 for i,r in rates if i>=final_start),'Clock changed after stable model'
 assert not any(line.startswith(('OBS ','KEY ','PASS runs=')) for line in lines[:regions[0]]),'Runtime observations precede callback attestation'
 for name,value in (('ntsc','false'),('cpu_model','68020'),('cpu_cycle_exact','true'),('cpu_memory_cycle_exact','true'),('sound_interpol','anti'),('sound_filter','emulated'),('floppy_volume','100')):
  values=re.findall(r'^'+name+r'=(.*)$',log,re.M)
  assert values and all(v.strip()==value for v in values),('Missing/ambiguous runtime setting',name,values)
 assert re.findall(r'^Model: "(.*)"\.$',log,re.M)==['A1200OG']
 # Reproduce each C float32 operation. Do not round the result through a second
 # float32 clock conversion: the stored scheduler step is the rate evidence.
 clk=f32(f32(f32(313)*f32(227))*f32(50))
 step=f32(f32(f32(clk*f32(512))*f32(1))/f32(44100))
 assert step==41245.0234375
 model=ClockModel(Fraction.from_float(step)*44100/512,44100,step)
 return model,dict(sndrate_lines=[lines[i] for i,_ in rates],stable_before_region=True,no_later_rate_change=True,region_line=lines[regions[0]])
