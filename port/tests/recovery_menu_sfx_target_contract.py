#!/usr/bin/env python3
"""No-clear frozen-helper contract vs original at every boundary, unmeasured."""
import hashlib,json,struct
from recovery_state_menu_sfx_harness import Native,assemble,RAM,CTX,JOURNAL,RUNTIME
from recovery_menu_sfx_target_oracle import oracle,SHA
from verify_recovery_menu_sfx_target import OUT,PORT

import sys
sys.path.insert(0,str(PORT/'tools'))
from build_recovery_menu_sfx_target import sample

def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 code=assemble();reports=[]
 payload=(OUT/'move_back/recovery_menu_sfx_target.bin').read_bytes()
 assert payload.count(code)==1
 runner_size=payload.index(code)
 device_code=payload[runner_size+len(code):payload.index(b'CDRDIS01')]
 assert hashlib.sha256(device_code).hexdigest()=='85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad'
 identity=dict(runner_bytes=runner_size,static_helpers_bytes=len(code),device_renderer_clock_bytes=len(device_code),device_renderer_clock_sha256=hashlib.sha256(device_code).hexdigest(),unchanged_helper_bytes_present_in_target=True)
 for history in ('default','right_hold','move_back'):
  expected,bus,_=oracle(rom,history)
  for poison in (False,True):
   native=Native(code,rom[16:131088]);written=set();reads=0
   def trace(mode,width,address,value):
    nonlocal reads
    native.trace(mode,width,address,value)
    if JOURNAL<=address<JOURNAL+134638:
     offsets=set(range(address,address+(1<<width)))
     if mode=='W':written.update(offsets)
     else:
      assert offsets<=written,('Journal read before this call wrote it',hex(address))
      reads+=1
   native.mem.set_trace_func(trace)
   event=nmis=0;pads=(0,0);index=0;waiting=0;menu=character=0
   while index<len(expected):
    if native.mem.r16(CTX)==0xa025:menu=1
    if native.mem.r16(CTX)==0xa06c:character+=1
    pads=(sample(history,character) if character else 16 if menu else 0,0)
    if poison:native.mem.w_block(JOURNAL,bytes([0x69])*134638)
    written.clear()
    status=native.run(event,pads)
    if status==0:
     assert event==0;event=1;nmis+=1;waiting+=1;continue
    assert status==1
    idx,_,ctx,ram,journal,*_=expected[index]
    assert bytes(native.mem.r_block(CTX,8))==ctx,('context',index)
    assert bytes(native.mem.r_block(RAM,2048))==ram,('RAM',index)
    assert bytes(native.mem.r_block(RUNTIME,12))==bus.runtime_checks[index],('runtime',index)
    if journal:
     count=struct.unpack_from('>H',journal)[0];used=2+4*count
     assert bytes(native.mem.r_block(JOURNAL,used))==journal[:used],('journal',index)
     if idx in (6,11,40,48):
      off={6:42,11:198,40:238,48:134382}[idx]
      assert bytes(native.mem.r_block(JOURNAL+off,256))==journal[off:off+256],('DMA',index)
    index+=1;event=0
   assert native.mem.r16(CTX)==0xc5f8 and nmis==bus.summary['logical_NMIs']
   reports.append(dict(history=history,mode='poison_each_call' if poison else 'initialize_once_reuse',calls=index,logical_NMIs=nmis,waits=waiting,journal_reads_initialized_within_call=reads,full_RAM_boundaries_equal=index,context_runtime_live_journal_DMA_equal=True,registers_and_guards_verified=True))
 result=dict(status='PASS',code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest(),runs=reports,linked_code=identity,limit='Separate machine68k helper execution, not stock-target timing or target access trace. Unpublished journal padding is not a semantic output.')
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'contract.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
