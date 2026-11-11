#!/usr/bin/env python3
"""Synthetic complete-target scroll/background/sprite composition and ABI proof."""
from pathlib import Path
import json,random,sys
import machine68k
from recovery_scroll_view_test import world_pixels,reference
from test_native_sprites import reference as sprites

def test(out):
 code=(out/'target.bin').read_bytes();syms=json.loads((out/'target.symbols.json').read_text())
 base=0x1000;addr=lambda k:base+syms[k];rng=random.Random(9116)
 m=machine68k.Machine(machine68k.CPUType.M68EC020,16384);mem,cpu=m.mem,m.cpu
 mem.w16(0x800,0x60fe);stack=0x180000
 nt=rng.randbytes(2048);cartridge=rng.randbytes(131072);pal=bytes(i%64 for i in range(32));oam=bytearray(rng.randbytes(256))
 for i in range(12):oam[4*i:4*i+4]=bytes((30,i,(i%4)|((i%2)*32),i*3))
 selected=cartridge[:4096]+cartridge[16*4096:17*4096]
 world=world_pixels(nt,selected[4096:])
 cases=0
 for sr in (0,0x2700):
  for origin in (0,1,7,255,256,257,504,511):
   mem.w_block(base,code);mem.w_block(addr('startup_nt'),nt);mem.w_block(addr('startup_cartridge_chr'),cartridge)
   mem.w_block(addr('startup_oam'),bytes(oam));mem.w_block(addr('startup_palette'),pal)
   initial=rng.randbytes(51200);mem.w_block(addr('startup_frame'),initial)
   dev=bytearray(28);dev[0]=0x90+origin//256;dev[1]=0x1e;dev[3]=origin%256;dev[10:14]=bytes((0x1e,0,16,5));mem.w_block(addr('startup_device'),bytes(dev))
   mem.w16(addr('runtime')+6,42)
   mem.w_block(stack-4096,b'\x5a'*4116);mem.w32(stack,0x800)
   before=bytes(mem.r_block(base,len(code)))
   regs=[rng.getrandbits(32) for _ in range(15)];regs[12]=addr('runtime');regs[14]=addr('report')
   for i,v in enumerate(regs):cpu.w_reg(i,v)
   cpu.w_sr(sr);cpu.w_sp(stack);cpu.w_pc(addr('recovery_live_render'))
   for _ in range(5000):
    cpu.execute(10000)
    if cpu.r_pc()==0x800:break
   else:raise AssertionError('linked composition timeout')
   assert cpu.r_sp()==stack+4 and [cpu.r_reg(i) for i in range(15)]==regs
   bg,opacity=reference(world,origin,initial)
   expected=sprites(oam,selected,bg,opacity,dev[0],0x1e)
   assert bytes(mem.r_block(addr('startup_frame'),51200))==expected,('pixels',origin,sr)
   assert bytes(mem.r_block(addr('startup_opacity'),7680))==opacity
   assert bytes(mem.r_block(addr('startup_chr'),8192))==selected
   assert mem.r32(addr('startup_display_report')+8)==0
   assert mem.r32(addr('recovery_live_report')+16)==mem.r32(addr('recovery_live_report')+36)==1
   assert mem.r_block(stack-4096,16)==b'\x5a'*16 and mem.r_block(stack+4,16)==b'\x5a'*16
   after=bytearray(mem.r_block(base,len(code)))
   adapter_symbols={x.split()[-1]:int(x.split()[0],16) for x in (out/'adapter.symbols').read_text().splitlines() if len(x.split()) in (3,4)}
   mutable=[('startup_frame',51200),('startup_opacity',7680),('startup_chr',8192),('startup_scratch',2196),('startup_copper',220),('startup_display_report',48),('recovery_live_report',44)]
   for key,n in mutable:
    lo=syms[key];after[lo:lo+n]=before[lo:lo+n]
   lo=syms['paula_adapter']+adapter_symbols['mp'];after[lo:lo+72]=before[lo:lo+72]
   assert after==before,'unexpected linked-target mutation'
   cases+=1
 m.cleanup();print('PASS',cases,'linked composed frames: ctrl90/91, wrap/fine scroll, distinct CHR0/16, first8 sprites, full-register/stack preservation, bounded mutations; synthetic only.')
if __name__=='__main__':test(Path(sys.argv[1]))
