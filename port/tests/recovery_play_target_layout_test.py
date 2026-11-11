#!/usr/bin/env python3
"""Source-only actual linked capture ABI and size proof; no cartridge/oracle."""
from pathlib import Path
import json,sys,random,struct
import machine68k
from recovery_bank_loader_play_harness import SIZES
CAP=135168

def test(out):
 code=(out/'target.bin').read_bytes();s=json.loads((out/'target.symbols.json').read_text());base=0x1000
 ranges=[(n,s[n]-16,s[n]+z+16) for n,z in [('ram',2048),('context',8),('journal',134638),('runtime',12),('resource',131072),('stack',4096),('capture',CAP)]]
 for (a,lo,hi),(b,l,h) in zip(ranges,ranges[1:]):assert hi<=l,(a,b)
 assert all(lo%2==0 and 0<=lo<hi<=len(code) for _,lo,hi in ranges)
 assert s['stack_end']==s['stack']+4096 and s['capture']%4==0
 assert len(code)<=900096 and ((len(code)+16+511)//512)*512<1536*1024
 assert CAP%512==0 and 4+33595*4+256==134640<CAP
 m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
 mem.w16(0x800,0x60fe);rng=random.Random(732)
 cases=[]
 for helper,size in enumerate(SIZES):
  dma={6:42,11:198,40:238,48:134382,98:134382}.get(helper)
  count=0 if size==0 else ((dma if dma else size)-2)//4
  cases.append((helper,size,count,dma))
 # Consumer absolute admission bound, including maximal defined DMA record.
 cases += [(48,134638,33595,134382),(98,134638,33595,134382)]
 for helper,size,count,dma in cases:
  mem.w_block(base,code);addr=lambda n:base+s[n]
  data=struct.pack('>H',count)+bytes((i*7+13)%256 for i in range(134636))
  mem.w_block(addr('journal'),data)
  mem.w16(addr('runtime')+6,helper);mem.w16(addr('runtime')+8,65535 if helper in(48,98) else size)
  want=struct.pack('>HH',helper,count)+data[2:2+count*4]+(data[dma:dma+256] if dma else b'')
  assert len(want)<=134640
  mem.w32(addr('report')+72,addr('capture'));mem.w32(addr('report')+76,0)
  regs=[rng.getrandbits(32) for _ in range(15)];regs[10]=addr('journal');regs[12]=addr('runtime');regs[14]=addr('report')
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  mem.w32(addr('stack_end')-4,0x800);cpu.w_sr(0);cpu.w_sp(addr('stack_end')-4);cpu.w_pc(addr('capture_journal'))
  def trace(mode,width,a,v):
   n=1<<width
   read=[(base,base+len(code)),(0x800,0x804)]
   write=[(addr('capture'),addr('capture')+CAP),(addr('stack'),addr('stack_end')),(addr('report')+76,addr('report')+80)]
   assert any(lo<=a and a+n<=hi for lo,hi in (read if mode=='R' else write)),(mode,width,hex(a))
  mem.set_trace_func(trace);mem.set_trace_mode(True)
  for _ in range(1000):
   cpu.execute(10000)
   if cpu.r_pc()==0x800:break
  else:raise AssertionError(('capture timeout',helper))
  mem.set_trace_mode(False)
  assert cpu.r_sp()==addr('stack_end') and [cpu.r_reg(i) for i in range(15)]==regs
  assert cpu.r_sr()&0x2000==0
  assert mem.r32(addr('report')+76)==len(want)
  assert bytes(mem.r_block(addr('capture'),len(want)))==want
  for name,lo,hi in ranges:
   assert bytes(mem.r_block(base+lo,16))==b'\x5a'*16
   assert bytes(mem.r_block(base+hi-16,16))==b'\x5a'*16
  assert bytes(mem.r_block(base,s['startup_display_report']))==code[:s['startup_display_report']]
 m.cleanup()
 result=dict(status='PASS',cases=len(cases),capture_capacity=CAP,max_admitted_capture=134640,guarded_ranges=ranges,payload_bytes=len(code),allocation_bytes=((len(code)+16+511)//512)*512,all_registers_user_mode_stack_width_access_guards=True)
 (out/'play-target-layout.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':test(Path(sys.argv[1]))
