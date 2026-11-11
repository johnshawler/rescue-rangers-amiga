#!/usr/bin/env python3
"""Synthetic CPU checks of instrumentation register/CCR preservation and accounting."""
import argparse,json,struct
from pathlib import Path
import machine68k

def test(out):
 code=(out/'target.bin').read_bytes();syms=json.loads((out/'target.symbols.json').read_text());B=0x1000
 m=machine68k.Machine(machine68k.CPUType.M68EC020,16384);mem,cpu=m.mem,m.cpu;mem.w_block(B,code)
 clock=[0]
 def trace(mode,width,addr,value):
  if mode=='R' and addr==0xbfd700:
   clock[0]+=100;v=~clock[0]&0xffffffff
   for a,s in ((0xbfd700,24),(0xbfd600,16),(0xbfd500,8),(0xbfd400,0)):mem.w8(a,v>>s&255)
 mem.set_trace_func(trace);mem.set_trace_mode(True)
 for i in range(7):
  for kind in ('start','end'):
   vals=[0x13570000+17*k for k in range(15)]
   for k,v in enumerate(vals):cpu.w_reg(k,v)
   cpu.w_sr(0x001f);cpu.w_sp(0x180000);mem.w32(0x180000,0x900);mem.w16(0x900,0x60fe)
   cpu.w_pc(B+syms[f'recovery_profile_{kind}_{i}'])
   for _ in range(100):
    cpu.execute(100)
    if cpu.r_pc()==0x900:break
   else:raise AssertionError('probe did not return')
   assert [cpu.r_reg(k) for k in range(15)]==vals
   assert cpu.r_sr()==0x001f and cpu.r_sp()==0x180004
  p=B+syms['recovery_profile_data']+8+16*i
  assert mem.r32(p+8)==1 and mem.r32(p+4)==mem.r32(p+12)>0
 mem.set_trace_mode(False)
 print('PASS: 14 probes preserve D0-D7/A0-A6, user-mode CCR/SR and stack; seven accumulators count and bound correctly. Synthetic clock, not performance evidence.')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);v=a.parse_args();test(v.output)
