#!/usr/bin/env python3
"""Read actual target CIA segmentation; does not equate logical RTIs with frames."""
from pathlib import Path
import argparse,hashlib,json,struct
ASM=('dispatch','capture','device','chr','background','sprites','empty')
AUDIO=('shadow','planner','wait','apply')
def report(out):
 chip=(out/'full-CHIP.bin').read_bytes();cfg=json.loads((out/'build.json').read_text());assert cfg['profiling']
 assert chip.count(b'CDRPRO01')==chip.count(b'CDRPROA1')==1
 p=chip.index(b'CDRPRO01');rows={}
 for i,name in enumerate(ASM):
  start,total,count,maximum=struct.unpack_from('>4I',chip,p+8+16*i)
  assert count>0 and total>=maximum>0
  rows[name]=dict(total_ticks=total,count=count,mean_ticks=total/count,max_ticks=maximum,total_ms=total*1000/709379)
 p=chip.index(b'CDRPROA1');v=struct.unpack_from('>12I',chip,p+8)
 for i,name in enumerate(AUDIO):
  total,count,maximum=v[i],v[i+4],v[i+8];assert count>0 and total>=maximum>0
  rows[name]=dict(total_ticks=total,count=count,mean_ticks=total/count,max_ticks=maximum,total_ms=total*1000/709379)
 assert rows['capture']['count']==rows['empty']['count']==rows['shadow']['count']
 assert rows['planner']['count']==rows['wait']['count']==rows['apply']['count']
 assert all(rows[n]['count']==1 for n in ('chr','background','sprites'))
 result=dict(display_dma=cfg['display_dma'],CIA_Hz=709379,segments=rows,chip_sha256=hashlib.sha256(chip).hexdigest(),limits='Instrumented inclusive intervals, not optimized performance. Empty segment measures timestamp/save/return overhead within brackets only; total perturbation also includes both calls and bookkeeping. Audio uses a separate C timing path. Segment sums do not include every runner instruction. Publication/wait feedback changes totals nonlinearly. No game FPS claim.')
 (out/'profile.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);v=a.parse_args();report(v.output)
