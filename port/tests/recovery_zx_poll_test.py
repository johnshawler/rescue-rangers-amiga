#!/usr/bin/env python3
"""Execute polling adapter with deterministic CIA-register/clock test doubles.
This proves bus accesses and preservation, not hardware timing; stock capture
provides independent real CIA serial/CIAB elapsed evidence.
"""
import os,subprocess,tempfile
from pathlib import Path
import machine68k
P=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 s=Path(td)/'test.s';b=Path(td)/'test.bin'
 s.write_text(' bra.w recovery_zx_poll\n'+(P/'src/recovery_zx_keyboard.s').read_text()+'''\nllb_amiga_clock_read:
 move.l $30000,d0
 addq.l #8,d0
 move.l d0,$30000
 rts
''')
 subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(b),str(s)],check=True);code=b.read_bytes()
m=machine68k.Machine(machine68k.CPUType.M68EC020,16384);mem,cpu=m.mem,m.cpu
mem.w_block(0x1000,code);mem.w16(0x800,0x60fe)
regs=[0x12345600+i for i in range(15)];regs[8]=0x20000
access=[]
def trace(mode,width,address,value):
 assert width in (0,1,2)
 end=address+(1<<width)
 def fits(lo,hi):return lo<=address and end<=hi
 cia=address in (0xbfee01,0xbfed01,0xbfec01) and width==0
 clock=address==0x30000 and width==2
 state=(fits(0x20000,0x20004) and width==0) or (address in (0x20004,0x20008) and width==2)
 if mode=='R':
  assert fits(0x1000,0x1000+len(code)) or fits(0x800,0x804) or clock or cia or state or fits(0x1effa0,0x1f0004),(hex(address),width)
 if address>=0xbf0000:access.append((mode,width,address,value))
 if mode=='W':
  assert state or fits(0x1effa0,0x1f0000) or clock or (address==0xbfee01 and width==0),(hex(address),width)
mem.set_trace_func(trace)
for sr in (0,0x2700):
 for cra in range(256):
  if cra&64:continue # Input-mode precondition.
  for pending in (False,True):
   mem.set_trace_mode(False);mem.w_block(0x1ffff,b'\xa5'+bytes(12)+b'\x5a');mem.w32(0x30000,0xfffffff0)
   mem.w8(0xbfee01,cra);mem.w8(0xbfed01,8 if pending else 0);mem.w8(0xbfec01,0x9d) # serial Z down
   cpu.w_sr(sr);cpu.w_sp(0x1f0000);mem.w32(0x1f0000,0x800)
   for i,v in enumerate(regs):cpu.w_reg(i,v)
   access.clear();cpu.w_pc(0x1000);mem.set_trace_mode(True)
   for _ in range(10):
    cpu.execute(1000)
    if cpu.r_pc()==0x800:break
   else:raise AssertionError('timeout')
   mem.set_trace_mode(False)
   assert cpu.r_reg(0)==(64 if pending else 0)
   assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
   assert cpu.r_sp()==0x1f0004 and mem.r8(0x1ffff)==0xa5 and mem.r8(0x2000c)==0x5a
   assert mem.r8(0xbfee01)==cra
   writes=[(a,v) for mode,w,a,v in access if mode=='W']
   assert writes==([(0xbfee01,cra|64),(0xbfee01,cra)] if pending else [])
   if pending:
    assert mem.r32(0x20004)==64 and mem.r32(0x20008)==1
    assert mem.r8(0x20001)==0x31 and mem.r8(0x20002)==0x9d
   else:assert bytes(mem.r_block(0x20000,12))==bytes(12)
assert bytes(mem.r_block(0x1000,len(code)))==code
print('PASS 512 user/supervisor native poll cases: input-mode CRA preservation, pending/no-pending, wrap-safe >=64-tick acknowledgement, register/stack/read/write bounds')
