#!/usr/bin/env python3
"""Execute compiled adapter in machine68k; synthetic clock is test-only.
Tests stale-count isolation, ordered writes, enable gating, RTI-only publication,
unsupported-plan fail/mute and journal bounds. Not target timing evidence.
"""
from pathlib import Path
import argparse,struct
import machine68k

def test(b):
 code=(b/'adapter.bin').read_bytes();symbols={x.split()[-1]:int(x.split()[0],16) for x in (b/'adapter.symbols').read_text().splitlines() if len(x.split()) in(3,4)}
 def unit():
  m=machine68k.Machine(machine68k.CPUType.M68EC020,16384);mem,cpu=m.mem,m.cpu;mem.w_block(0x1000,code);mem.w16(0x800,0x60fe);clock=[0];writes=[]
  def trace(mode,width,addr,value):
   if mode=='R' and addr==0xbfd700:
    clock[0]+=100;v=(~clock[0])&0xffffffff
    for a,shift in ((0xbfd700,24),(0xbfd600,16),(0xbfd500,8),(0xbfd400,0)):mem.w8(a,(v>>shift)&255)
   if mode=='W' and 0xdff000<=addr<0xdff200:writes.append((addr,width,value))
  mem.set_trace_func(trace)
  def call(entry,*args):
   sp=0x100000;cpu.w_sr(0x2700);cpu.w_sp(sp);mem.w32(sp,0x800)
   for i,x in enumerate(args):mem.w32(sp+4+i*4,x)
   saved={r:0x51000000+r for r in list(range(2,8))+list(range(10,15))}
   for r,v in saved.items():cpu.w_reg(r,v)
   cpu.w_pc(0x1000+entry);mem.set_trace_mode(True)
   for _ in range(1000):
    cpu.execute(1000)
    if cpu.r_pc()==0x800:break
   else:raise AssertionError('timeout')
   mem.set_trace_mode(False);assert cpu.r_sp()==sp+4 and all(cpu.r_reg(r)==v for r,v in saved.items());return cpu.r_reg(0)
  call(0);return mem,call,writes
 def journal(mem,events):mem.w_block(0x80000,struct.pack('>H',len(events))+b''.join(struct.pack('>HBB',a,v,1) for a,v in events))
 mp=0x1000+symbols['mp'];shadow=0x1000+symbols['shadow']
 mem,call,writes=unit();assert bytes(mem.r_block(shadow,16))==bytes(14)+b'\x07\0'
 journal(mem,[(0x4000,255)]);before=bytes(mem.r_block(shadow,16));writes.clear();assert call(4,0x80000,0,9)==1 and bytes(mem.r_block(shadow,16))==before and not writes
 ev=[(0x4000,0x3f),(0x4000,0x30),(0x4001,8),(0x4004,0x30),(0x4005,8),(0x400c,0x30),(0x4015,0)]
 journal(mem,ev);assert call(4,0x80000,2+4*len(ev),9)==1 and mem.r8(shadow)==0x30 and mem.r32(mp+16)==0 and not writes
 journal(mem,[]);assert call(4,0x80000,2,8)==1 and mem.r32(mp+16)==1
 tr=mem.r32(mp+48);assert bytes(mem.r_block(tr+40,8))==bytes(8),'enable zero must mute all channels'
 # Unsupported state at a completed RTI must fail and mute, never publish.
 journal(mem,[(0x4015,16)]);assert call(4,0x80000,6,20)==0 and mem.r32(mp+8)==99 and mem.r32(mp+20)==1 and mem.r32(mp+16)==1
 mem,call,writes=unit();journal(mem,[(0x4017,0)]);assert call(4,0x80000,6,9)==0 and mem.r32(mp+8)==99
 mem,call,writes=unit();mem.w_block(0x80000,bytes.fromhex('000140170000'));writes.clear();assert call(4,0x80000,6,9)==1 and not writes
 for size,helper in ((1,9),(65535,9),(6,9)):
  mem,call,writes=unit();mem.w16(0x80000,33596 if size==6 else 1);assert call(4,0x80000,size,helper)==0 and mem.r32(mp+8)==99
 print('PASS compiled adapter: ordered writes, stale padding, RTI gate, enable zero, unsupported atomic plan/mute, three invalid bounds; synthetic clock only')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();test(a.output)
