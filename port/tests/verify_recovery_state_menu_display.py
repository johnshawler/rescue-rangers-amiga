#!/usr/bin/env python3
"""Actual stock-target dump and pixels against original-only replay."""
import hashlib,json,struct,sys
from pathlib import Path
from recovery_state_menu_display_oracle import oracle,SHA
import recovery_state_menu_display_pixels as display
PORT=Path(__file__).resolve().parents[1]
OUT=PORT/'build/recovery_state_menu_display'

def verify(chip,rom,_window=None):
 assert len(chip)==2097152
 assert hashlib.sha256(rom).hexdigest()==SHA
 assert chip.count(b'CDRMEN01')==1
 p=chip.index(b'CDRMEN01');f=struct.unpack_from('>16I',chip,p+8)
 status,calls,nmis,event,ram,ctx,journal,runtime,resource,stack,stackend,captures,capend,cursor,laststatus,sp=f
 assert (status,calls,nmis,event,laststatus)==(0,1091,38,0,1),f
 assert stackend-stack==4096 and sp==stackend
 assert chip[stack:stack+3072]==bytes(3072),"Native stack exceeded upper 1KiB observational bound"
 assert capend-captures==786432 and captures<cursor<capend
 ranges=[(ram,2048),(ctx,8),(journal,134638),(runtime,12),(resource,131072),(stack,4096),(captures,786432)]
 for a,n in ranges:
  assert a%2==0 and a>=16 and a+n+16<=len(chip)
  assert chip[a-16:a]==b'\x5a'*16 and chip[a+n:a+n+16]==b'\x5a'*16,('guard',a,n)
 for i,(a,n) in enumerate(ranges):
  assert a+n<=p or a>=p+72
  for b,m in ranges[i+1:]:assert a+n+16<=b-16 or b+m+16<=a-16
 assert chip[resource:resource+131072]==rom[16:131088]

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
 assert chip[runtime:runtime+12]==bus.runtime_checks[-1]
 assert chip[journal:journal+134638]==results[-1][4]+bytes(134638-len(results[-1][4]))
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
  # Enforce cross-component disjointness, not just each component alone.
  f=struct.unpack_from('>16I',chip,chip.index(b'CDRMEN01')+8)
  d=struct.unpack_from('>10I',chip,record+8)
  core=list(zip((f[4],f[5],f[6],f[7],f[8],f[9],f[11]),(2048,8,134638,12,131072,4096,786432)))
  shown=list(zip(d[1:8],(28,2048,32,256,8192,51200,220)))
  for a,n in core:
   for b,m in shown:assert a+n<=b or b+m<=a,'Cross-component buffer alias'
  result['copper_terminator_verified']=True
  _,bus,_=oracle(rom)
  result['ppu_events']=sum(e[0]=='ppu' for e in bus.events)
  result['mapper_writes']=sum(e[0]=='mapper' for e in bus.events)
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

 (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
