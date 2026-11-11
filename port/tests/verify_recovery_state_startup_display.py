#!/usr/bin/env python3
"""Actual stock-target dump and pixels against original-only replay."""
import hashlib,json,struct,sys
from pathlib import Path
from recovery_state_startup_display_oracle import oracle,SHA
import verify_recovery_startup_display as display
PORT=Path(__file__).resolve().parents[1]
OUT=PORT/'build/recovery_state_startup_display'

def verify(chip,rom,_window=None):
 assert len(chip)==2097152
 assert hashlib.sha256(rom).hexdigest()==SHA
 assert chip.count(b'CDRSTA01')==1
 p=chip.index(b'CDRSTA01');f=struct.unpack_from('>16I',chip,p+8)
 status,calls,nmis,event,ram,ctx,journal,runtime,resource,stack,stackend,captures,capend,cursor,laststatus,sp=f
 assert (status,calls,nmis,event,laststatus)==(0,990,35,0,0xffffffff),f
 assert stackend-stack==4096 and sp==stackend
 assert chip[stack:stack+3072]==bytes(3072),"Native stack exceeded upper 1KiB observational bound"
 assert capend-captures==786432 and captures<cursor<capend
 ranges=[(ram,2048),(ctx,8),(journal,32770),(runtime,12),(resource,131072),(stack,4096),(captures,786432)]
 for a,n in ranges:
  assert a%2==0 and a>=16 and a+n+16<=len(chip)
  assert chip[a-16:a]==b'\x5a'*16 and chip[a+n:a+n+16]==b'\x5a'*16,('guard',a,n)
 for i,(a,n) in enumerate(ranges):
  assert a+n<=p or a>=p+72
  for b,m in ranges[i+1:]:assert a+n+16<=b-16 or b+m+16<=a-16
 assert chip[resource:resource+131072]==rom[16:131088]
 assert chip[journal:journal+32770]==bytes(32770)
 results,bus,instructions=oracle(rom);at=captures
 for i,(idx,status,wctx,wram,wjournal,_) in enumerate(results):
  assert at+32<=cursor
  assert struct.unpack_from('>I',chip,at)[0]==1
  assert chip[at+4:at+12]==wctx,('context',i)
  assert chip[at+12:at+24]==bus.runtime_checks[i],('runtime',i)
  js,rs=struct.unpack_from('>II',chip,at+24)
  assert js==len(wjournal) and rs==(2048 if i<64 else 0)
  at+=32
  if rs:assert chip[at:at+rs]==wram,('RAM',i);at+=rs
  assert chip[at:at+js]==wjournal,('journal',i,idx);at+=js
 assert at==cursor
 assert chip[cursor:capend]==bytes(capend-cursor)
 assert chip[ram:ram+2048]==results[-1][3]
 assert chip[ctx:ctx+8]==results[-1][2]
 assert chip[runtime:runtime+12]==bus.runtime_checks[-1][:6]+bytes.fromhex('baddf00dd501')
 return dict(status='PASS',executed_calls=calls,logical_NMIs=nmis,full_RAM_snapshots_equal=64,context_snapshots_equal=calls,journals_equal=calls,mapper_latch_checks=calls,final_context=results[-1][2].hex(),final_mapper=list(bus.mapper.snapshot()[:4]),snapshot_bytes=cursor-captures,original_instructions=instructions,APU_writes=sum(e[0]=='apu' for e in bus.events),native_stack_balanced=True,target_access_trace=False)

def check(chip,rom,log):
 # Reuse the unchanged independently written device/pixel model with the new
 # original-only event stream, and the new capture ABI checker. No target input.
 old_verify,old_oracle=display.verify,display.oracle
 try:
  display.verify=verify;display.oracle=oracle
  result=display.check(chip,rom,log)
  record=chip.index(b'CDRDIS01')
  copper=struct.unpack_from('>10I',chip,record+8)[7]
  assert chip[copper+216:copper+220]==bytes.fromhex('fffffffe'),'Copper terminator'
  result['copper_terminator_verified']=True
  result['startup'].pop('limit',None)
  result['startup']['limit']='Every context/runtime/published journal; first 64 RAM boundaries and final RAM. No target memory access trace or all-boundary target RAM claim.'
  return result
 finally:display.verify,display.oracle=old_verify,old_oracle

def main():
 out=Path(sys.argv[1]) if len(sys.argv)>1 else OUT
 chip=(out/'chip.bin').read_bytes();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 result=check(chip,rom,(out/'amiga.log').read_text());result['actual_video']=display.verify_screen(chip,out/'screen.ppm')
 repeat=(out/'repeat-chip.bin').read_bytes()
 check(repeat,rom,(out/'repeat-amiga.log').read_text());display.verify_screen(repeat,out/'repeat-screen.ppm')
 assert repeat==chip and (out/'screen.ppm').read_bytes()==(out/'repeat-screen.ppm').read_bytes()
 result['repeat']={'fresh_executions':2,'full_Chip_dumps_equal':True,'raw_video_captures_equal':True}
 baseline=PORT/'build/startup-display-native'
 if (baseline/'chip.bin').exists() and (baseline/'screen.ppm').exists():
  old=(baseline/'chip.bin').read_bytes()
  frame=lambda c:struct.unpack_from('>10I',c,c.index(b'CDRDIS01')+8)[6]
  assert chip[frame(chip):frame(chip)+51200]==old[frame(old):frame(old)+51200]
  assert (out/'screen.ppm').read_bytes()==(baseline/'screen.ppm').read_bytes()
  result['optional_frozen_diagnostic_comparison']={'frame_bytes_equal':51200,'raw_video_equal':True,'used_as_target_input':False}

 (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
