#!/usr/bin/env python3
"""Private matched-history comparison, never inferred from final state alone."""
from pathlib import Path
import argparse,hashlib,json,struct
from recovery_stage_target_oracle import oracle

def history_digest(b):
 chip=(b/'full-CHIP.bin').read_bytes()
 f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8)
 live=struct.unpack_from('>9I',chip,chip.index(b'CDRCLIV1')+8)
 changes=[struct.unpack_from('>4I',chip,live[4]+16*i) for i in range(live[5])]
 results,bus,instructions=oracle(Path('input/rescue-rangers-europe.nes').read_bytes(),changes,f[1])
 h=hashlib.sha256()
 for i,(helper,status,ctx,ram,journal,pads,event) in enumerate(results):
  h.update(struct.pack('>HHBBBI',helper,status,*pads,event,len(journal)))
  h.update(ctx+ram+journal+bus.runtime_checks[i])
 h.update(json.dumps(bus.events,separators=(',',':')).encode())
 return dict(sha256=h.hexdigest(),helpers=len(results),instructions=instructions,changes=changes)

def compare(b,control):
 cur=json.loads((b/'stage-target-verification.json').read_text());old=json.loads((control/'stage-target-verification.json').read_text())
 for p in (b,control):
  for name in ('stage-target-verification.json','stage-target-replay.json', 'stage-background-noise-pcm.json' if p==b else 'stage-target-noise-pcm.json'):
   assert json.loads((p/name).read_text())['status']=='PASS',(p,name)
 assert json.loads((b/'stage-background-anchor.json').read_text())['status']=='PASS'
 cmeta=json.loads((b/'build.json').read_text());ometa=json.loads((control/'build.json').read_text())
 assert cmeta['display_dma']==ometa['display_dma']==1 and not cmeta['profiling']
 assert cmeta['native_sha256']==ometa['native_sha256']
 for result in (cur,old):assert result['Fast_bytes']==0
 current_history=history_digest(b);old_history=history_digest(control)
 matched=current_history==old_history and all(cur[n]==old[n] for n in ('input_changes','helper_calls','rtis','original_instructions'))
 cs=json.loads((control/'target.symbols.json').read_text());ss=json.loads((b/'target.symbols.json').read_text())
 cc=(control/'full-CHIP.bin').read_bytes();sc=(b/'full-CHIP.bin').read_bytes();equal={}
 for name,size in [('ram',2048),('context',8),('runtime',12),('startup_nt',2048),('startup_palette',32),('startup_oam',256),('startup_chr',8192),('startup_frame',51200),('startup_opacity',7680)]:
  a=old['payload_base']+cs[name];z=cur['payload_base']+ss[name];equal[name]=cc[a:a+size]==sc[z:z+size]
 if matched:assert all(equal.values())
 result=dict(status='PASS',audio_qualification_methods={'candidate':'additive phase-aware finite-loop + independently reviewed anchor bound','control':'unchanged frozen phase-zero finite-loop verifier'},frozen_candidate_PCM_failure_preserved=True,stronger_control_PCM_rejection_preserved=True,control=str(control),same_input_helper_history=matched,current_history=current_history,control_history=old_history,final_bytes_equal=equal,allocation_bytes=cur['allocation_bytes'],Fast_bytes=cur['Fast_bytes'],late_updates=cur['late_updates'],completed_updates=cur['rtis'],final_redraw_ticks=cur['final_render_ticks'],final_redraw_ms=cur['final_render_ticks']*1000/709379,control_final_redraw_ticks=old['final_render_ticks'],control_final_redraw_ms=old['final_render_ticks']*1000/709379,progression_ticks=cur['progression_ticks'],control_progression_ticks=old['progression_ticks'],PCM_byte_identical=(b/'full-capture.s16le').read_bytes()==(control/'full-capture.s16le').read_bytes(),scope='Uninstrumented final redraw with five-plane display DMA. Not full game FPS, individual segment timing, or physical-hardware evidence.')
 if matched:result['matched_final_redraw_reduction_percent']=(old['final_render_ticks']-cur['final_render_ticks'])*100/old['final_render_ticks']
 else:result['note']='Actual input/helper histories differ. No speedup calculated.'
 (b/'stage-background-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--control',type=Path,default=Path('port/build/recovery-stage-target-v3'));a=ap.parse_args();compare(a.output,a.control)
