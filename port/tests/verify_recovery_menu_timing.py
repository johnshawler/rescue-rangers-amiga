#!/usr/bin/env python3
"""Independent original final state and device/pixel checks outside measured path."""
import hashlib,json,struct,sys
from pathlib import Path
from recovery_state_menu_display_oracle import oracle,SHA
import recovery_state_menu_display_pixels as display
PORT=Path(__file__).resolve().parents[1]
OUT=PORT/'build/recovery_menu_timing'

def verify(chip,rom,_window=None):
 assert len(chip)==2097152
 assert hashlib.sha256(rom).hexdigest()==SHA
 assert chip.count(b'CDRTIM01')==1
 p=chip.index(b'CDRTIM01');f=struct.unpack_from('>16I',chip,p+8)
 status,calls,nmis,event,ram,ctx,journal,runtime,resource,stack,stackend,r0,r1,r2,laststatus,sp=f
 assert (status,calls,nmis,event,r0,r1,r2,laststatus)==(0,1091,38,0,0,0,0,1),f
 assert stackend-stack==4096 and sp==stackend
 assert chip[stack:stack+3072]==bytes(3072),'Stack upper 1KiB observational bound'
 ranges=[(ram,2048),(ctx,8),(journal,134638),(runtime,12),(resource,131072),(stack,4096)]
 for a,n in ranges:
  assert a%2==0 and a>=16 and a+n+16<=len(chip)
  assert chip[a-16:a]==b'\x5a'*16 and chip[a+n:a+n+16]==b'\x5a'*16,('guard',a,n)
 for i,(a,n) in enumerate(ranges):
  assert a+n<=p or a>=p+72
  for b,m in ranges[i+1:]:assert a+n+16<=b-16 or b+m+16<=a-16
 assert chip[resource:resource+131072]==rom[16:131088]
 results,bus,instructions=oracle(rom)
 assert chip[ram:ram+2048]==results[-1][3]
 assert chip[ctx:ctx+8]==results[-1][2]
 assert chip[runtime:runtime+12]==bus.runtime_checks[-1]
 want=results[-1][4];used=2+4*struct.unpack_from('>H',want)[0]
 assert used<=len(want)
 assert chip[journal:journal+used]==want[:used]
 return dict(status='PASS',executed_calls=calls,logical_NMIs=nmis,final_RAM_equal=True,final_context=results[-1][2].hex(),final_mapper=list(bus.mapper.snapshot()[:4]),original_instructions=instructions,APU_writes=sum(e[0]=='apu' for e in bus.events),native_stack_balanced=True,final_live_journal_bytes_equal=used,target_access_trace=False)

def check(chip,rom,log):
 old=display.verify
 try:
  display.verify=verify
  result=display.check(chip,rom,log)
 finally:display.verify=old
 record=chip.index(b'CDRDIS01');d=struct.unpack_from('>10I',chip,record+8)
 assert chip[d[7]+216:d[7]+220]==bytes.fromhex('fffffffe'),'Copper terminator'
 f=struct.unpack_from('>16I',chip,chip.index(b'CDRTIM01')+8)
 core=list(zip(f[4:10],(2048,8,134638,12,131072,4096)))
 shown=list(zip(d[1:8],(28,2048,32,256,8192,51200,220)))
 for a,n in core:
  for b,m in shown:assert a+n<=b or b+m<=a,'Cross-component buffer alias'
 result['startup']['limit']='Final RAM/context/runtime and last live journal only on stock target. Separate native-helper execution checks every boundary; no target per-boundary captures or access trace.'
 ticks=result.pop('CIA_E_ticks');progress=ticks['startup_with_diagnostics'];render=ticks['render_and_chr_mapping']
 assert 0<progress<709379*60 and 0<render<709379,'Invalid timer range'
 result['CIA_E_ticks']={'progression_including_runner_and_device':progress,'CHR_mapping_and_one_render':render}
 result['seconds_at_709379_Hz']={k:v/709379 for k,v in result['CIA_E_ticks'].items()}
 result['timing_limits']='CIA E-clock elapsed ticks, not CPU instruction clocks, display frames, NMI cadence or game FPS. DMA disabled; loading and final palette/Copper setup excluded.'
 return result

def main():
 out=Path(sys.argv[1]) if len(sys.argv)>1 else OUT
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 results=[]
 for prefix in ('','repeat-'):
  chip=(out/(prefix+'chip.bin')).read_bytes()
  result=check(chip,rom,(out/(prefix+'amiga.log')).read_text())
  result['actual_video']=display.verify_screen(chip,out/(prefix+'screen.ppm'))
  results.append(result)
 assert (out/'chip.bin').read_bytes()==(out/'repeat-chip.bin').read_bytes()
 assert (out/'screen.ppm').read_bytes()==(out/'repeat-screen.ppm').read_bytes()
 result=results[0];result['repeat']={'fresh_executions':2,'full_Chip_dumps_equal':True,'raw_video_captures_equal':True}
 (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
