#!/usr/bin/env python3
"""Additive identity-bound comparison. Never writes to a capture directory."""
import argparse,hashlib,json,struct
from pathlib import Path
from recovery_audio_clock_model import parse_log,attest,verify_hashes,sha

ROOT=Path(__file__).resolve().parents[2]
NAMES=('recovery-play-background-v1','recovery-play-target-v3')
def require(ok,why):
 if not ok:raise ValueError(why)
def read(p):return json.loads(p.read_text())
def history(b,rom):
 from recovery_play_target_oracle import oracle
 c=(b/'full-CHIP.bin').read_bytes();f=struct.unpack_from('>21I',c,c.index(b'CDRSFX01')+8);live=struct.unpack_from('>9I',c,c.index(b'CDRCLIV1')+8)
 changes=[struct.unpack_from('>4I',c,live[4]+16*i) for i in range(live[5])]
 results,bus,instructions=oracle(rom,changes,f[1]);h=hashlib.sha256()
 for i,(helper,status,ctx,ram,journal,pads,event) in enumerate(results):
  h.update(struct.pack('>HHBBBI',helper,status,*pads,event,len(journal)));h.update(ctx+ram+journal+bus.runtime_checks[i])
 h.update(json.dumps(bus.events,separators=(',',':')).encode())
 return dict(sha256=h.hexdigest(),helpers=len(results),instructions=instructions,changes=[list(x) for x in changes])
def qualify(report,model,runtime,source,identity,v,replay,build):
 require(report['status']=='PASS' and report['immutable_capture_hashes']==identity,'Audio identity/status')
 require(report['clock']==model.describe() and report['runtime_clock_attestation']==runtime and report['source_attestation']==source,'Clock/source/config mismatch')
 n=report['noise'];t=report['gameplay_tonal'];bound=report['endpoint_and_mapping_bound']
 require(n['status']==t['status']==bound['status']=='PASS','Audio component failed')
 require([x['RTI'] for x in n['windows']]==list(range(380,384)) and not n['skipped_windows'],'Noise coverage')
 require(n['threshold_correlation']==.45 and n['threshold_margin']==.08 and n['physical_guards_seconds']==[.11,.02] and n['phase_count_each_hypothesis']==128 and n['rate_factors']==[1,.5,2] and n['shift_checks']==804,'Noise criteria')
 require(all(x['margin']>.08 and x['minimum_shift_margin']>.08 and x['minimum_shift_correlation']>.45 for x in n['windows']),'Noise scores')
 require([x['RTI'] for x in t['windows']]==list(range(396,401)) and t['physical_guards_seconds']==[.11,.03] and t['frequency_tolerance_hz']==8 and t['negative_checks']==15,'Tonal coverage')
 require(not bound['legacy_nominal_clock_scale_error_remaining'] and bound['total_corrected_placement_uncertainty_ms']<=100/44100*1000,'Placement bound')
 require(v['status']==replay['status']=='PASS' and v['frame_screen']['status']=='PASS','Runtime/replay/pixels')
 require(v['runner_error']==0 and v['rtis']==v['render_count']==400 and v['completed_game_frames']==5 and v['Fast_bytes']==0,'Runtime scope')
 require(all(replay[k] for k in ('ordered_effects_all_boundaries','all_RAM_context_runtime_boundaries','terminal_target_equal')),'Incomplete replay')
 require(v['final_original_ram_context_runtime'] and v['last_journal_equal'] and v['retained_audio_records_equal']==256,'State/device evidence')
 require(build['display_dma']==1 and not build.get('profiling',False) and build['goal_game_frames']==5,'Build scope')
def reductions(a,b,ha,hb,final_equal):
 matched=ha==hb
 if matched:require(final_equal,'Matched histories disagree in final state')
 out={'same_input_helper_history':matched}
 if matched:
  for k in ('final_redraw_ticks','five_interval_ticks','progression_ticks'):
   require(b[k]>0 and a[k]>0,'Invalid timing')
   out[k+'_reduction_percent']=(b[k]-a[k])*100/b[k]
 else:out['suppression']='Actual full input/helper histories differ; no timing percentage calculated.'
 return out

def run(capture_root,audio_root,rom,core,frontend):
 pin=read(ROOT/'port/analysis/recovery_play_clock_evidence.json');source=attest(core,frontend);records=[];chips=[];symbols=[]
 require(sha(rom)=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411','ROM identity')
 for name in NAMES:
  b=capture_root/name;p=pin[name];verify_hashes(b,p['capture_and_evidence']);require(sha(audio_root/(name+'.json'))==p['corrected_report_sha256'],'Corrected report identity')
  r=read(audio_root/(name+'.json'));require(r['capture']==name,'Capture name');v=read(b/'play-target-verification.json');replay=read(b/'play-target-replay.json');build=read(b/'build.json')
  model,runtime=parse_log((b/'full.log').read_text());qualify(r,model,runtime,source,p['capture_identity'],v,replay,build)
  h=history(b,rom.read_bytes());require(h['helpers']==v['helper_calls']==replay['calls'] and h['instructions']==v['original_instructions']==replay['original_instructions'] and h['changes']==v['input_changes']==replay['actual_input_changes'],'History evidence mismatch')
  c=(b/'full-CHIP.bin').read_bytes();m=struct.unpack_from('>16I',c,c.index(b'CDRPAU01')+8);intervals=[]
  for i in range(395,400):
   prev=struct.unpack_from('>3I',c,m[10]+56*((i-1)&255));now=struct.unpack_from('>3I',c,m[10]+56*(i&255));require(prev[2]<now[0]<=now[1]<=now[2],'Publication ordering');intervals.append(now[1]-prev[1])
  require(m[2]==400 and m[4]==v['late_updates'] and m[14]-m[13]==v['final_render_ticks'],'Raw timing evidence mismatch')
  timing=dict(final_redraw_ticks=m[14]-m[13],five_interval_ticks=sum(intervals),progression_ticks=v['progression_ticks'])
  records.append(dict(capture=name,history=h,timing=timing,interval_ticks=intervals,nominal_hardware_equivalent_ms={k:x*1000/709379 for k,x in timing.items()},callback_domain_ms={k:model.seconds(x)*1000 for k,x in timing.items()},clock=model.describe(),late_updates=v['late_updates'],completed_updates=400,Chip_allocation_bytes=v['allocation_bytes'],Fast_bytes=v['Fast_bytes'],native_sha256=build['native_sha256'],payload_base=v['payload_base']))
  chips.append(c);symbols.append(read(b/'target.symbols.json'))
 require(records[0]['native_sha256']==records[1]['native_sha256'],'Native identity differs')
 equal={}
 for name,size in [('ram',2048),('context',8),('runtime',12),('startup_nt',2048),('startup_palette',32),('startup_oam',256),('startup_chr',8192),('startup_frame',51200),('startup_opacity',7680)]:
  values=[]
  for r,c,s in zip(records,chips,symbols):
   start=r['payload_base']+s[name];require(0<=start and start+size<=len(c),'Final slice bounds');values.append(c[start:start+size])
  equal[name]=values[0]==values[1]
 result=dict(status='PASS',independent_review='PENDING for this new comparison layer',records=records,final_bytes_equal=equal,comparison=reductions(records[0]['timing'],records[1]['timing'],records[0]['history'],records[1]['history'],all(equal.values())),audio_method='Both captures: corrected callback-clock phase-aware finite-loop and five tonal windows; identity-pinned reports. Historical nominal reports/failures preserved, not used as qualification gates.',scope='Five diagnostic publication intervals, final redraw and bounded progression only. All updates late. No sustained game FPS, NES audio fidelity, host-time or physical hardware speed claim.')
 for name in NAMES:verify_hashes(capture_root/name,pin[name]['capture_and_evidence'])
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--capture-root',type=Path,default=ROOT/'port/build');p.add_argument('--audio-root',type=Path,default=ROOT/'port/build/recovery-audio-clock-v2');p.add_argument('--rom',type=Path,default=ROOT/'input/rescue-rangers-europe.nes');p.add_argument('--core',type=Path,default=ROOT.parent/'amiga-recovery-tools/libretro-uae');p.add_argument('--frontend',type=Path,default=ROOT/'port/build/experimental-direct-paula/headless');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 require(not a.output.exists(),'Output must be new')
 require(not any((a.capture_root/n).resolve() in a.output.resolve().parents for n in NAMES),'Cannot write into frozen capture')
 result=run(a.capture_root,a.audio_root,a.rom,a.core,a.frontend);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['comparison']))
