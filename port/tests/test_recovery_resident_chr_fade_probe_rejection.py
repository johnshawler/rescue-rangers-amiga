#!/usr/bin/env python3
"""Negative controls on real four-window Chip captures, never synthetic positive dumps."""
import argparse,json,struct
from pathlib import Path
from verify_recovery_resident_chr_fade_probe import MARKER,PORT,oracle,layout,verify,verify_amiga_log

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);args=p.parse_args()
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();results,_,_=oracle(rom)
 total_tests=0;log_cases=0;cross_modes=0
 for w in range(4):
  original=(args.directory/f'recovery-resident-chr-fade-w{w}-chip.bin').read_bytes();baseline=verify(original,rom,w);o=original.index(MARKER)
  status,calls,ram,ctx,snaps,res,stack,stackend,sp,window,res2=struct.unpack_from('>11I',original,o+8)
  offsets,total=layout(results,w);tests=[]
  def patch(label,a,b):tests.append((label,a,b))
  def u32(label,a,v):patch(label,a,struct.pack('>I',v))
  def flip(label,a):patch(label,a,bytes((original[a]^1,)))
  for i in range(8):flip('marker',o+i)
  for off in (8,12,36,40,44):u32('report',o+off,struct.unpack_from('>I',original,o+off)[0]^1)
  fields=[(16,ram,2048),(20,ctx,8),(24,snaps,total),(28,res,16384),(32,stack,4096),(48,res2,16384)]
  for off,a,n in fields:
   for bad in (0,1,15,len(original)-1,len(original),0xffffffff,o,o+2,o+52,a+1,16,len(original)-n-16,len(original)-n-14):u32('pointer bounds/alignment',o+off,bad)
   for off2,b,m in fields:
    if off2!=off:
     for bad in (b,b+2,b+m-2,b+m+14):u32('pointer alias/guard overlap',o+off,bad)
   for at in (a-16,a-1,a+n,a+n+15):flip('buffer guard',at)
  for call,r in enumerate(results):
   start=snaps+offsets[call];captured=w*256<=call<(w+1)*256;end=20+(2048 if captured else 0);jo=end+16;size=len(r[4])
   for off in (0,4,8):flip('snapshot header',start+off+3)
   for off in range(12,20):flip('every context byte',start+off)
   if captured:
    for off in (20,20+0xf,20+0x1a,20+0x1b,20+0xf2,20+0xf3,20+0xf6,20+0x1bd,2067):flip('RAM and CHR state',start+off)
   for off in (end,jo-1,jo+size,jo+size+15):flip('journal guards',start+off)
   if size:
    for off in (jo,jo+size-1):flip('journal',start+off)
   if r[0] in (6,11,31,45):
    dma=42 if r[0]==6 else 238 if r[0]==45 else 198
    for i in range(256):flip('DMA every byte',start+jo+dma+i)
   if r[0] in (2,7,8,29,39,41,45):
    count=struct.unpack_from('>H',original,start+jo)[0]
    for e in range(count):
     addr=struct.unpack_from('>H',original,start+jo+2+e*4)[0]
     if addr>=0x8000:flip('mapper serial write',start+jo+4+e*4)
  for a,n in ((ram,2048),(ctx,8),(res,16384),(res2,16384)):
   for at in (a,a+n-1):flip('final RAM/context/resource',at)
  for label,a,b in tests:
   damaged=bytearray(original);damaged[a:a+len(b)]=b
   try:verify(bytes(damaged),rom,w)
   except (AssertionError,struct.error):pass
   else:raise AssertionError(('Mutation accepted',w,label,a))
  total_tests+=len(tests)
  for damaged in (original[:-1],original+b'\0',original[:-8]+MARKER):
   try:verify(damaged,rom,w)
   except (AssertionError,struct.error):pass
   else:raise AssertionError('Malformed dump accepted')
   total_tests+=1
  for wrong in (rom[:-1],bytes(len(rom))):
   try:verify(original,wrong,w)
   except AssertionError:pass
   else:raise AssertionError('Wrong ROM accepted')
   total_tests+=1
  for wrong_window in set(range(4))-{w}:
   try:verify(original,rom,wrong_window)
   except AssertionError:pass
   else:raise AssertionError('Wrong window accepted')
   total_tests+=1
  assert verify(original,rom,w)==baseline
  log=(args.directory/f'w{w}-amiga.log').read_text();verify_amiga_log(log)
  replacements=[('Model: "A1200OG".','Model: "A1200".'),('cpu_model=68020','cpu_model=68030'),('fpu_model=0','fpu_model=68881'),('mmu_model=0','mmu_model=68030'),('chipmem_size=4','chipmem_size=2'),('bogomem_size=0','bogomem_size=1'),('fastmem_size=0','fastmem_size=4'),('ntsc=false','ntsc=true'),('cpu_cycle_exact=true','cpu_cycle_exact=false'),('cpu_memory_cycle_exact=true','cpu_memory_cycle_exact=false'),('blitter_cycle_exact=true','blitter_cycle_exact=false'),('CPU=68020, FPU=0, MMU=0, JIT=0.','CPU=68030, FPU=0, MMU=0, JIT=0.'),('PAL mode V=50.0000Hz','NTSC mode V=59.9400Hz'),('PASS runs=1800','PASS runs=1799'),('video_callbacks=1800','video_callbacks=1799'),('chipset=aga','chipset=ecs'),('chipset_compatible=A1200','chipset_compatible=A500')]
  for old,new in replacements:
   assert old in log
   for damaged in (log.replace(old,new),log.replace(old,'')):
    try:verify_amiga_log(damaged)
    except AssertionError:log_cases+=1
    else:raise AssertionError(('Invalid configuration accepted',old))
  for extra in ('cpu_model=68030','CPU=68030, FPU=0, MMU=0, JIT=0. ~cycle-exact 24-bit','NTSC mode V=59.9400Hz (NTSC)','fastmem_size=4','Model: "A1200OG".','chipset=ecs','chipset_compatible=A500'):
   try:verify_amiga_log(log+'\n'+extra+'\n')
   except AssertionError:log_cases+=1
   else:raise AssertionError(('Conflict accepted',extra))
 for old in sorted((PORT/'build').glob('*-chip.bin')):
  try:verify(old.read_bytes(),rom)
  except (AssertionError,struct.error):cross_modes+=1
  else:raise AssertionError(('Historical mode accepted',str(old)))
 print(json.dumps(dict(status='PASS',positive_real_baselines=8,dump_negative_cases=total_tests,configuration_negative_cases=log_cases,historical_cross_mode_cases=cross_modes),indent=2))
if __name__=='__main__':main()
