#!/usr/bin/env python3
"""Original-only device, pixel, final-state and ordered target journal verification."""
import hashlib,json,struct,sys
from pathlib import Path
from recovery_menu_sfx_target_oracle import oracle,SHA
import recovery_state_menu_display_pixels as display
PORT=Path(__file__).resolve().parents[1];OUT=PORT/'build/recovery_menu_sfx_target'
HISTORIES=('default','right_hold','move_back')
def verify(chip,rom,reference):
 assert len(chip)==2097152 and hashlib.sha256(rom).hexdigest()==SHA
 assert chip.count(b'CDRSFX01')==1
 p=chip.index(b'CDRSFX01');f=struct.unpack_from('>21I',chip,p+8)
 status,calls,nmis,event,ram,ctx,journal,runtime,resource,stack,stackend,r0,r1,r2,laststatus,sp,cap,used,menu,character,reserved=f
 results,bus,instructions=reference
 assert (status,calls,nmis,event,r0,r1,r2,laststatus,menu,character,reserved)==(0,len(results),bus.summary['logical_NMIs'],0,0,0,0,1,1,bus.summary['character_visits'],0),f
 assert stackend-stack==4096 and sp==stackend
 assert chip[stack:stack+3072]==bytes(3072)
 ranges=[(ram,2048),(ctx,8),(journal,134638),(runtime,12),(resource,131072),(stack,4096),(cap,262144)]
 for a,n in ranges:
  assert a%2==0 and a>=16 and a+n+16<=len(chip)
  assert chip[a-16:a]==b'\x5a'*16 and chip[a+n:a+n+16]==b'\x5a'*16,('guard',a,n)
 for i,(a,n) in enumerate(ranges):
  assert a+n<=p or a>=p+92
  for b,m in ranges[i+1:]:assert a+n+16<=b-16 or b+m+16<=a-16
 assert chip[resource:resource+131072]==rom[16:131088]
 assert chip[ram:ram+2048]==results[-1][3],'final RAM'
 assert chip[ctx:ctx+8]==results[-1][2],'final context'
 assert chip[runtime:runtime+12]==bus.runtime_checks[-1],'final runtime'
 want=results[-1][4]
 if want:
  n=2+4*struct.unpack_from('>H',want)[0];assert chip[journal:journal+n]==want[:n]
 assert used==len(bus.capture) and 0<used<=262144
 assert chip[cap:cap+used]==bus.capture,'ordered live journal and DMA stream'
 assert chip[cap+used:cap+262144]==bytes(262144-used),'capture overflow or unexpected tail'
 return dict(status='PASS',**bus.summary,final_context=results[-1][2].hex(),final_RAM_context_runtime_equal=True,native_stack_balanced=True,ordered_journal_and_DMA_equal=True,target_all_RAM_boundaries=False)

def check(chip,rom,log,history,reference=None):
 reference=reference or oracle(rom,history)
 payload=(OUT/history/'recovery_menu_sfx_target.bin').read_bytes()
 executable=payload[:payload.index(b'CDRDIS01')]
 assert chip.count(executable)==1,'Immutable runner/helpers/device code absent or altered'
 old_verify,old_oracle=display.verify,display.oracle
 try:
  display.verify=lambda c,r,_w:verify(c,r,reference)
  display.oracle=lambda _r:reference
  result=display.check(chip,rom,log)
 finally:display.verify,display.oracle=old_verify,old_oracle
 d=struct.unpack_from('>10I',chip,chip.index(b'CDRDIS01')+8)
 assert chip[d[7]+216:d[7]+220]==bytes.fromhex('fffffffe'),'Copper terminator'
 f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8)
 core=list(zip(f[4:10],(2048,8,134638,12,131072,4096)))+[(f[16],262144)]
 for a,n in core:
  for b,m in zip(d[1:8],(28,2048,32,256,8192,51200,220)):assert a+n<=b or b+m<=a
 result['startup']['limit']='Final RAM/context/runtime plus every completed live journal and DMA only. No target all-boundary RAM capture or target access trace.'
 ticks=result.pop('CIA_E_ticks');progress=ticks['startup_with_diagnostics'];render=ticks['render_and_chr_mapping']
 assert 0<progress<709379*60 and 0<render<709379
 result['CIA_E_ticks']={'progression_runner_device_capture':progress,'CHR_mapping_and_one_render':render}
 result['seconds_at_709379_Hz']={k:v/709379 for k,v in result['CIA_E_ticks'].items()}
 result['timing_limits']='Diagnostic CIA elapsed ticks with DMA disabled; loading and final palette/Copper excluded. Not game FPS, CPU instruction clocks, or live-input timing.'
 return result

def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();reports=[]
 for history in HISTORIES:
  out=OUT/history;reference=oracle(rom,history)
  for prefix in ('','repeat-'):
   chip=(out/(prefix+'chip.bin')).read_bytes();result=check(chip,rom,(out/(prefix+'amiga.log')).read_text(),history,reference)
   result['actual_video']=display.verify_screen(chip,out/(prefix+'screen.ppm'))
  assert (out/'chip.bin').read_bytes()==(out/'repeat-chip.bin').read_bytes()
  assert (out/'screen.ppm').read_bytes()==(out/'repeat-screen.ppm').read_bytes()
  result['repeat_fresh_boots_identical']=2;reports.append(result)
 (OUT/'verification.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(reports,indent=2))
if __name__=='__main__':main()
