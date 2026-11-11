#!/usr/bin/env python3
"""Private independent original replay for real keyboard capture. No target input."""
from pathlib import Path
import argparse,json,struct,hashlib,sys,re
import numpy as np
from recovery_play_target_oracle import oracle
from recovery_menu_paula_verify import plan as title_plan,spectral
def plan(r,en):
 if r[14]!=8:return title_plan(r,en)
 copy=list(r);copy[14]=7
 p=title_plan(copy,en);p[-1]=8;return p
from recovery_stage_target_scanout_check import verify_scanout

def check_retained_spectral(pcm,rows,audio_expected,active_first):
 rtis=len(audio_expected)
 spec=None
 if rtis<=256:
  timeline=[dict(ready=a,published=p,end=e) for a,p,e in rows]
  spec=spectral(pcm,timeline,[x[3] for x in audio_expected],active_first)[0]
  for kind in ('DC','swapped','wrong_tone'):
   bad=pcm.copy()
   if kind=='DC':bad[:]=1000
   elif kind=='swapped':bad=bad[:,::-1]
   else:
    origin=active_first-timeline[2]['published']*44100/709379
    lo=round(origin+timeline[17]['published']*44100/709379);hi=round(origin+timeline[19]['published']*44100/709379)
    bad[lo:hi,0]=2000*np.sin(np.arange(hi-lo)*2*np.pi*1000/44100)
   try:spectral(bad,timeline,[x[3] for x in audio_expected],active_first)
   except AssertionError:pass
   else:raise AssertionError('negative PCM accepted '+kind)
  spec['negative_PCM_checks']=['DC','swapped','wrong_tone']
 return spec

def verify(b,expected_unsupported=None):
 cfg=json.loads((b/"build.json").read_text())
 log=(b/'full.log').read_text()
 assert re.findall(r'^Model: "(.*)"\.$',log,re.M)==['A1200OG']
 for name,value in (('chipset','aga'),('chipset_compatible','A1200'),('cpu_model','68020'),('fpu_model','0'),('mmu_model','0'),('chipmem_size','4'),('bogomem_size','0'),('fastmem_size','0'),('ntsc','false'),('cpu_cycle_exact','true'),('cpu_memory_cycle_exact','true'),('blitter_cycle_exact','true')):
  matches=re.findall(r'^'+name+r'=(.*)$',log,re.M);assert matches and all(x.strip()==value for x in matches),(name,matches)
 assert re.findall(r'^CPU=.*$',log,re.M)==['CPU=68020, FPU=0, MMU=0, JIT=0. ~cycle-exact 24-bit']
 runs=re.findall(r'^PASS runs=(\d+) video_callbacks=(\d+) .*$',log,re.M)
 assert len(runs)==1 and runs[0][0]==runs[0][1] and int(runs[0][0])>0
 chip=(b/'full-CHIP.bin').read_bytes();rom=Path('input/rescue-rangers-europe.nes').read_bytes()
 f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8)
 live=struct.unpack_from('>9I',chip,chip.index(b'CDRCLIV1')+8)
 assert live[0]==65536 and live[1]==0 and 0<=live[2]<=4096 and live[5]<=128
 assert live[7]<=live[2] and live[8]<=live[2]
 symbols=json.loads((b/'target.symbols.json').read_text())
 payload=(b/'target.bin').read_bytes();immutable=payload[:payload.index(b'CDRDIS01')]
 assert chip.count(immutable)==1
 base=chip.index(immutable)
 assert len(chip)==2*1024*1024 and base+cfg['allocation_bytes']<=len(chip)
 assert cfg['allocation_bytes']==((len(payload)+16+511)//512)*512
 boot=(b/'boot.bin').read_bytes()
 assert bytes.fromhex('203c')+struct.pack('>I',cfg['allocation_bytes'])+bytes.fromhex('223c000100024eaeff3a') in boot

 # All appended executable ranges, excluding deliberately mutable telemetry.
 ranges=[(symbols['paula_consume'],symbols['recovery_live_report']),(symbols['startup_rgb12'],symbols['startup_rgb12']+128)]
 if 'recovery_redraw_invalidate_oam' in symbols:ranges.append((symbols['recovery_redraw_invalidate_oam'],symbols['recovery_live_banks']))
 start_code=symbols.get('recovery_live_diagnostic_stop',symbols.get('recovery_live_dispatch'))
 if start_code is not None:ranges.append((start_code,len(payload)))
 for lo,hi in ranges:assert chip[base+lo:base+hi]==payload[lo:hi], ('appended immutable code',lo,hi)
 assert chip.index(b'CDRSFX01')==base+symbols['report']
 assert chip.index(b'CDRCLIV1')==base+symbols['recovery_live_report']
 assert live[3]==base+symbols['recovery_live_state'] and live[4]==base+symbols['recovery_live_changes']
 assert live[6]&0xffffff==0 and live[6]>>24==chip[live[3]]
 assert struct.unpack_from('>I',chip,live[3]+8)[0]>=live[5]
 for i,key in [(4,'ram'),(5,'context'),(6,'journal'),(7,'runtime'),(8,'resource'),(9,'stack'),(10,'stack_end'),(16,'capture')]:assert f[i]==base+symbols[key]
 assert f[1]<=1000000 and f[17]<=135168
 pc=int.from_bytes(chip[f[5]:f[5]+2],'big')
 if expected_unsupported is not None:
  assert f[0]==0xffffffff and pc==int(expected_unsupported,16)
 elif cfg.get('diagnostic_stop_rti',0):
  assert f[0]==1 and live[2]==cfg['diagnostic_stop_rti']
 else:
  assert f[0]==0 and pc==0xc77b
  assert struct.unpack_from('>I',chip,base+symbols['recovery_play_arrivals'])[0]==6
 changes=[struct.unpack_from('>4I',chip,live[4]+i*16) for i in range(live[5])]
 ref=oracle(rom,changes,f[1],scene=cfg.get("scene",False));results,bus,_=ref
 # Independently count accepted render states at completed original RTIs.
 ctrl=mask=sx=sy=latch=eventpos=tick=rendercount=lastrender=0
 for i,result in enumerate(results):
  for e in bus.events[eventpos:bus.event_ends[i]]:
   if e[0]!='ppu':continue
   a,v=e[1:3]
   if a==0x2002:latch=0
   elif a==0x2000:ctrl=v
   elif a==0x2001:mask=v
   elif a==0x2005:
    if latch:sy=v
    else:sx=v
    latch^=1
   elif a==0x2006:latch^=1
  eventpos=bus.event_ends[i]
  if result[0] in (8,20,42):
   tick+=1
   if ctrl in (0x90,0x91) and mask==0x1e and sy==0 and bus.runtime_checks[i][0]==0x1e:rendercount+=1;lastrender=tick
 assert (live[7],live[8])==(rendercount,lastrender), 'render counters vs original supported snapshots'
 assert chip[f[4]:f[4]+2048]==results[-1][3],'RAM'
 assert chip[f[5]:f[5]+8]==results[-1][2],'context'
 assert chip[f[7]:f[7]+12]==bus.runtime_checks[-1],'runtime'
 assert chip[f[8]:f[8]+131072]==rom[16:131088]
 for a,n in [(f[4],2048),(f[5],8),(f[6],134638),(f[7],12),(f[8],131072),(f[9],4096),(f[16],135168)]:
  assert chip[a-16:a]==b'\x5a'*16 and chip[a+n:a+n+16]==b'\x5a'*16
 assert f[15]==f[10],'terminal stack'
 last=results[-1];j=last[4];count=int.from_bytes(j[:2],'big') if j else 0
 cap=struct.pack('>HH',last[0],count)+(j[2:2+count*4] if j else b'')
 if last[0] in (6,11,40,48,98):cap+=j[{6:42,11:198,40:238,48:134382,98:134382}[last[0]]:][:256]
 assert f[17]==len(cap) and chip[f[16]:f[16]+len(cap)]==cap,'last journal only'
 payload=(b/'target.bin').read_bytes();immutable=payload[:payload.index(b'CDRDIS01')]
 assert chip.count(immutable)==1
 syms={x.split()[-1]:int(x.split()[0],16) for x in (b/'adapter.symbols').read_text().splitlines() if len(x.split()) in(3,4)}
 assert chip.count((b/'adapter.bin').read_bytes()[:syms['mp']])==1,'immutable compiled adapter/planner/waves' 
 mp=struct.unpack_from('>15I',chip,chip.index(b'CDRPAU01')+8)
 stage,writes,rtis,rejects,late,maxinterval,maxwork,start,lasttime,stop,trace,shadow,enable,rs,render_end=mp
 assert trace==base+symbols['paula_adapter']+syms['records'] and shadow==base+symbols['paula_adapter']+syms['shadow']
 assert start<=lasttime<=stop and 0<=late<=rtis and 0<=maxinterval<=lasttime-start
 r=bytearray(16);r[14]=7;en=0;expected=[]
 for helper,_,ctx,ram,journal,*_ in results:
  if journal:
   for i in range(struct.unpack_from('>H',journal)[0]):
    a,v,k=struct.unpack_from('>HBB',journal,2+4*i)
    if 0x4000<=a<=0x400f:assert k==1;r[a-0x4000]=v
    elif a==0x4015:assert k==1;en=v
  if helper in (8,20,42):expected.append((helper,en,bytes(r),plan(r,en)))
 assert rtis==len(expected)==live[2] and writes==bus.summary['APU_writes'] and rejects==0
 assert chip[shadow:shadow+16]==r and enable==en
 rows=[]
 for i in range(max(0,rtis-256),rtis):
  q=trace+56*(i&255);ready,published,end,h,e=struct.unpack_from('>3I2H',chip,q)
  eh,ee,er,pl=expected[i]
  assert (h,e)==(eh,ee) and chip[q+16:q+32]==er and list(struct.unpack_from('>12H',chip,q+32))==pl
  assert stop>=end>=published>=ready>=start and end-published<=maxwork
  if rows:assert published-rows[-1][1]>=14188
  rows.append((ready,published,end))
 assert rows[-1][1]==lasttime and rs>=lasttime and render_end>=rs and stop-render_end>=14188
 if rtis<=256:
  intervals=[rows[0][1]-start]+[rows[i][1]-rows[i-1][1] for i in range(1,len(rows))]
  assert max(intervals)==maxinterval and late<=sum(v>14188 for v in intervals)
  assert max(row[2]-row[1] for row in rows)==maxwork
 from recovery_stage_target_pixels import expected as expected_pixels
 _,nt,pal,oam,chrdata,frame,opacity,state=expected_pixels(rom,ref)
 d=struct.unpack_from('>10I',chip,chip.index(b'CDRDIS01')+8)
 assert chip.index(b'CDRDIS01')==base+symbols['startup_display_report']
 assert d[0]==0
 for i,key in enumerate(('startup_device','startup_nt','startup_palette','startup_oam','startup_chr','startup_frame','startup_copper'),1):assert d[i]==base+symbols[key]
 assert rs<=d[8]<=d[9]<=render_end
 for name,addr,want in [('device',d[1],state),('NT',d[2],nt),('palette',d[3],pal),('OAM',d[4],oam),('CHR',d[5],chrdata),('frame',d[6],frame)]:
  assert chip[addr:addr+len(want)]==want,name
 screen=verify_scanout(chip,b/'full-screen.ppm',d[7],d[6],pal,frame)
 pcm=np.fromfile(b/'full-capture.s16le',dtype='<i2').reshape(-1,2).astype(float)
 active=np.flatnonzero(np.any(pcm!=0,axis=1));assert len(active)>4410 and np.max(np.abs(pcm))<32767
 ac=np.std(pcm[active[0]:active[-1]+1],axis=0);assert np.all(ac>100)
 assert len(pcm)-active[-1]>44100,'one second terminal silence'
 spec=check_retained_spectral(pcm,rows,expected,int(active[0]))
 assert stage==3
 mpline=next(x.split() for x in (b/'adapter.symbols').read_text().splitlines() if x.split()[-1]=='mp')
 if len(mpline)==4 and int(mpline[1],16)>=72:assert struct.unpack_from('>I',chip,chip.index(b'CDRPAU01')+68)[0]==0
 summary=dict(status='PASS',completed_game_frames=bus.summary['completed_game_frames'],arrival_helpers=bus.summary['arrival_helpers'],scheduler_returns=bus.summary['scheduler_returns'],spectral=spec,allocation_bytes=cfg['allocation_bytes'],Fast_bytes=0,payload_base=base,noise_extension=cfg.get('noise_extension'),stock_target='PAL A1200OG 68020 AGA 2MiB Chip zero Fast cycle-exact',callbacks=int(runs[0][0]),runner_error=f[0],endpoint=results[-1][2].hex(),helper_calls=f[1],rtis=rtis,render_count=live[7],input_changes=changes,selection=bus.summary['confirmations'],original_instructions=ref[2],last_journal_equal=True,retained_audio_records_equal=len(rows),overwritten_audio_records=max(0,rtis-256),target_exhaustive_journals=False,final_original_ram_context_runtime=True,frame_screen=screen,progression_ticks=lasttime-start,progression_seconds=(lasttime-start)/709379,late_updates=late,max_interval_ticks=maxinterval,final_render_ticks=render_end-rs,actual_pcm_AC_RMS=ac.tolist(),terminal_silence_seconds=float((len(pcm)-active[-1]-1)/44100))
 (b/'play-target-verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
 return ref
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);a.add_argument('--expected-unsupported');v=a.parse_args();verify(v.output,v.expected_unsupported)
