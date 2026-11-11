#!/usr/bin/env python3
"""Compare verified fresh candidates against identified uninstrumented controls.
Reads controls without modifying them. All capture/output paths are PRIVATE.
"""
from pathlib import Path
import argparse,hashlib,json,struct

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
def load(p):
 v=json.loads((p/'verification.json').read_text());assert v['status']=='PASS'
 assert v['audio']['status']=='PASS' and v['audio']['completed_RTI_plans']==43 and v['audio']['writes']==322
 assert v['negative_PCM_checks']==['DC','swapped','wrong_tone']
 b=(p/'target.bin').read_bytes();c=(p/'full-CHIP.bin').read_bytes();s=json.loads((p/'target.symbols.json').read_text())
 prefix=b[:b.index(b'CDRDIS01')];assert c.count(prefix)==1;base=c.index(prefix)
 q=c.index(b'CDRPAU01');f=struct.unpack_from('>15I',c,q+8)
 assert f[14]-f[13]==v['timing']['final_render_ticks']
 return v,b,c,s,base

def compare(candidate,control):
 v,b,c,s,base=load(candidate);w,d,e,t,oldbase=load(control)
 assert v['memory']['history']==w['memory']['history']=='default'
 assert v['memory']['display_dma']==w['memory']['display_dma']
 assert (candidate/'adapter.bin').read_bytes()==(control/'adapter.bin').read_bytes()
 assert b[s['nes_draw_sprites_8x8']:s['startup_display_report']]==d[t['nes_draw_sprites_8x8']:t['startup_display_report']]
 # Both final scenes, including every planar byte and opacity/cache, are identical.
 regions={'startup_nt':2048,'startup_palette':32,'startup_oam':256,'startup_chr':8192,'startup_frame':51200,'startup_opacity':7680,'startup_cache':1920,'startup_scratch':2196}
 for name,n in regions.items():assert c[base+s[name]:base+s[name]+n]==e[oldbase+t[name]:oldbase+t[name]+n],name
 assert (candidate/'full-screen.ppm').read_bytes()==(control/'full-screen.ppm').read_bytes()
 # Live timestamps/addresses vary, but every completed original audio state/plan agrees.
 for x,y in zip(v['private_records'],w['private_records']):assert (x['helper'],x['volumes'])==(y['helper'],y['volumes'])
 trace=struct.unpack_from('>I',c,c.index(b'CDRPAU01')+48)[0]
 oldtrace=struct.unpack_from('>I',e,e.index(b'CDRPAU01')+48)[0]
 for i in range(43):assert c[trace+56*i+12:trace+56*(i+1)]==e[oldtrace+56*i+12:oldtrace+56*(i+1)]
 old=w['timing']['final_render_ticks'];new=v['timing']['final_render_ticks']
 files=('build.json','target.adf','target.bin','full.log','full-CHIP.bin','full-capture.s16le','full-screen.ppm','verification.json')
 return dict(status='PASS',display=v['memory']['display_dma'],control_ticks=old,candidate_ticks=new,saved_ticks=old-new,saved_percent=100*(old-new)/old,candidate_ms=1000*new/709379,control_ms=1000*old/709379,regions_equal=list(regions),candidate=str(candidate),control=str(control),candidate_provenance={n:digest(candidate/n) for n in files},control_provenance={n:digest(control/n) for n in files})
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('candidate',type=Path);a.add_argument('control',type=Path);a.add_argument('--output',type=Path,required=True);v=a.parse_args()
 result=compare(v.candidate.resolve(),v.control.resolve())
 with v.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if 'provenance' not in k},indent=2))
