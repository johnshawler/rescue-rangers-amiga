#!/usr/bin/env python3
"""Verify private bounded captures against continuous unmodified original-ROM execution."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from recovery_resident_chr_fade_target_oracle import PORT,SHA,oracle,SerialMapper
from verify_recovery_resident_fade_probe import verify_amiga_log as prior_log
MARKER=b'CDRCHR01'
def layout(results,window):
 offsets=[];total=0
 for call,r in enumerate(results):
  offsets.append(total);total+=52+len(r[4])+(2048 if window*256<=call<(window+1)*256 else 0)
 return offsets,total

def verify_amiga_log(log):
 result=prior_log(log)
 for name,value in [('chipset','aga'),('chipset_compatible','A1200')]:
  matches=re.findall(r'^'+name+r'=(.*)$',log,re.MULTILINE)
  assert matches and all(v.strip()==value for v in matches),('AGA configuration',name,matches)
 result['chipset']='AGA'
 return result

def verify(chip,rom,window=None):
 assert len(chip)==2*1024*1024,'Expected stock 2 MiB Chip dump'
 assert hashlib.sha256(rom).hexdigest()==SHA,'Private cartridge hash mismatch'
 assert chip.count(MARKER)==1,'Wrong mode or corrupted marker'
 offset=chip.index(MARKER);assert offset+52<=len(chip)
 status,calls,ram,ctx,snapshots,resource,stack,stack_end,sp,actual_window,resource2=struct.unpack_from('>11I',chip,offset+8)
 assert (status,calls)==(0,1024),('Native ABI/status/call failure',status,calls)
 assert actual_window in range(4),'Invalid capture window'
 if window is not None:assert actual_window==window,'Wrong capture window'
 window=actual_window
 assert stack_end-stack==4096 and sp==stack_end,'Native stack imbalance'
 results,bus,instructions=oracle(rom);offsets,total=layout(results,window)
 ranges=[(ram,2048),(ctx,8),(snapshots,total),(resource,16384),(resource2,16384),(stack,4096)]
 guard=b'\x5a'*16
 for address,size in ranges:
  assert address%2==0,'Unaligned native buffer'
  assert 16<=address and address+size+16<=len(chip),'Buffer outside Chip'
  assert chip[address-16:address]==guard and chip[address+size:address+size+16]==guard,'Guard corruption'
  assert address-16>=offset+52 or address+size+16<=offset,'Report/guard alias'
 for i,(a,n) in enumerate(ranges):
  for b,m in ranges[i+1:]:assert a+n+16<=b-16 or b+m+16<=a-16,'Buffer alias'
 assert chip[resource:resource+16384]==rom[49168:65552],'Bank3 changed'
 assert chip[resource2:resource2+16384]==rom[32784:49168],'Bank2 changed'
 mapper=SerialMapper();dma=0
 for call,(index,status,context,state,journal,raw) in enumerate(results):
  start=snapshots+offsets[call];captured=window*256<=call<(window+1)*256
  end=20+(2048 if captured else 0);jo=end+16
  assert struct.unpack_from('>3I',chip,start)==(index,status,len(journal)),('Snapshot header',call)
  assert chip[start+12:start+20]==context,('Context',call,index)
  if captured:assert chip[start+20:start+2068]==state,('Full original RAM',call,index)
  actual=chip[start+jo:start+jo+len(journal)]
  assert actual==journal,('Ordered journal/DMA',call,index)
  assert chip[start+end:start+jo]==guard,('Journal lower guard',call)
  assert chip[start+jo+len(journal):start+jo+len(journal)+16]==guard,('Journal upper guard',call)
  if index in (2,7,8,29,39,41,45):
   for event in range(struct.unpack_from('>H',actual)[0]):
    address,value,metadata=struct.unpack_from('>HBB',actual,2+event*4)
    if address>=0x8000:mapper.write(address,value)
  if index in (6,11,31,45):dma+=256
  assert mapper.snapshot()==bus.mapper_checks[call],('Persistent mapper/latch',call)
 assert chip[ram:ram+2048]==results[-1][3],'Final RAM'
 assert chip[ctx:ctx+8]==results[-1][2],'Final context'
 counts={kind:sum(e[0]==kind for e in bus.events) for kind in ('ram','mapper','ppu','apu','controller','resource')}
 return dict(status='PASS',capture_window=window,executed_calls=1024,full_RAM_snapshots_equal=256,context_snapshots_equal=1024,journals_equal=1024,mapper_latch_checks=1024,DMA_bytes_equal=dma,immutable_resource_bytes=32768,logical_NMIs=35,continuous_original_instructions=instructions,ordered_reference_effects=counts,final_context=results[-1][2].hex(),final_mapper=list(bus.mapper.snapshot()[:4]),native_stack_balanced=True,target_access_trace=False,target_RAM_evidence='Full RAM in bounded capture window; ordered RAM journals only for fade/yield helpers',limit='Four independent full-reset runs collectively cover RAM at all boundaries. Diagnostic schedule only; no physical hardware, gameplay, display, speed or audio-output claim.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);args=p.parse_args();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();reports=[]
 for w in range(4):
  report=verify((args.directory/f'recovery-resident-chr-fade-w{w}-chip.bin').read_bytes(),rom,w)
  report['actual_target']=verify_amiga_log((args.directory/f'w{w}-amiga.log').read_text());reports.append(report)
 print(json.dumps(dict(status='PASS',full_RAM_boundaries_covered=1024,full_reset_runs=4,windows=reports),indent=2))
if __name__=='__main__':main()
