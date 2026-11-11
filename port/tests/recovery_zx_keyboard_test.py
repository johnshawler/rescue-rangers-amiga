#!/usr/bin/env python3
"""Exhaustive actual 68020 adapter execution, no game ROM required."""
import os,subprocess,tempfile,random
from pathlib import Path
import machine68k
P=Path(__file__).resolve().parents[1]
MAP={0x31:64,0x32:128,0x44:16,0x42:32,0x4e:1,0x4f:2,0x4d:4,0x4c:8}
with tempfile.TemporaryDirectory() as td:
 s=Path(td)/'test.s';b=Path(td)/'test.bin'
 s.write_text(' bra.w recovery_zx_decode\n bra.w recovery_zx_serial_decode\n'+(P/'src/recovery_zx_keyboard.s').read_text()+'\nllb_amiga_clock_read: rts\n')
 subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(b),str(s)],check=True);code=b.read_bytes()
m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
mem.w_block(0x1000,code);mem.w16(0x800,0x60fe)
rng=random.Random(314159);regs=[rng.getrandbits(32) for _ in range(15)];regs[8]=0x20000
writes=[]
def trace(mode,width,address,value):
 assert width in (0,1,2)
 end=address+(1<<width)
 def fits(lo,hi):return lo<=address and end<=hi
 if mode=='R':
  assert fits(0x1000,0x1000+len(code)) or fits(0x800,0x804) or fits(0x20000,0x20001) or fits(0x1effe0,0x1f0004),(hex(address),width)
 if mode=='W':
  assert fits(0x20000,0x20001) or fits(0x1effe0,0x1f0000),(hex(address),width)
mem.set_trace_func(trace)
for sr in (0,0x2700):
 for serial in (False,True):
  for held in range(256):
   for raw in range(256):
    mem.set_trace_mode(False);mem.w_block(0x1ffff,b'\xa5'+bytes([held])+b'\x5a'*16)
    cpu.w_sr(sr);cpu.w_sp(0x1f0000);mem.w32(0x1f0000,0x800)
    for i,v in enumerate(regs):cpu.w_reg(i,v)
    encoded=(~(((raw<<1)|(raw>>7))&255))&255 if serial else raw
    cpu.w_reg(0,0xaabbcc00|encoded);cpu.w_pc(0x1000+4*serial);mem.set_trace_mode(True)
    for _ in range(4):
     cpu.execute(1000)
     if cpu.r_pc()==0x800:break
    else:raise AssertionError('timeout')
    bit=MAP.get(raw&127,0);want=held&~bit if raw&128 else held|bit
    assert cpu.r_reg(0)==want and mem.r8(0x20000)==want,(held,raw)
    assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
    assert cpu.r_sp()==0x1f0004
    assert mem.r8(0x1ffff)==0xa5 and bytes(mem.r_block(0x20001,16))==b'\x5a'*16
mem.set_trace_mode(False)
assert bytes(mem.r_block(0x1000,len(code)))==code
print('PASS 262144 user/supervisor native cases: all held/raw and serial combinations; repeat/release/unmapped; registers, stack, read/write bounds, immutable code')
