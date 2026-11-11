#!/usr/bin/env python3
"""Source-only compiled extension vs frozen planner; no cartridge or timing claim."""
from pathlib import Path
import sys,struct,random
import machine68k

def test(out):
 code=(out/'adapter.bin').read_bytes()
 syms={x.split()[-1]:int(x.split()[0],16) for x in (out/'adapter.symbols').read_text().splitlines() if len(x.split()) in (3,4)}
 m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
 base,inp,dst,sp,stop=0x1000,0x80000,0x81000,0x180000,0x800
 mem.w_block(base,code);mem.w16(stop,0x60fe)
 rng=random.Random(188);calls=0
 def call(name,r,en):
  nonlocal calls
  mem.w_block(inp,bytes(r));mem.w_block(dst,b'\xa5'*24)
  cpu.w_sr(0);cpu.w_sp(sp);mem.w_block(sp,struct.pack('>4I',stop,inp,en,dst))
  saved={i:rng.getrandbits(32) for i in (*range(2,8),*range(10,15))}
  for i,v in saved.items():cpu.w_reg(i,v)
  cpu.w_pc(base+syms[name])
  for _ in range(100):
   cpu.execute(1000)
   if cpu.r_pc()==stop:break
  else:raise AssertionError('planner timeout')
  assert cpu.r_sp()==sp+4 and all(cpu.r_reg(i)==v for i,v in saved.items())
  assert mem.r_block(inp,16)==bytes(r) and mem.r_block(base,len(code))==code
  calls+=1;return cpu.r_reg(0),bytes(mem.r_block(dst,24))
 old='experimental_direct_paula_plan';new='recovery_live_gameplay_noise06_plan'
 seed=list(bytes.fromhex('b70809093b08120aff0009093b000808'))
 cases=[]
 for noise in range(256):
  for enable in range(32):
   r=seed.copy();r[14]=noise;cases.append((r,enable))
 for mode in (6,8,142):
  for index in (0,1,4,5,8,12):
   for value in range(256):
    r=seed.copy();r[14]=mode;r[index]=value;cases.append((r,15))
  for timer in range(2048):
   r=seed.copy();r[14]=mode;r[2]=timer&255;r[3]=timer>>8;cases.append((r,15))
 accepted=0
 for r,en in cases:
  ref=r.copy()
  if r[14] in (6,8,142):ref[14]=7
  status,want=call(old,ref,en)
  if status and r[14] in (6,8,142):want=want[:22]+bytes((0,10 if r[14]==6 else 8 if r[14]==8 else 9))
  actual=call(new,r,en)
  assert actual==(status,want),(r,en,actual,status,want.hex())
  if not status:assert want==b'\xa5'*24
  accepted+=bool(status)
 assert accepted>0
 print('PASS compiled stage planner:',len(cases),'cases;',calls,'USER-mode calls; old-byte compatibility,06 wave10 /08 wave8 /8E wave9, atomic reject, immutable inputs/code, C ABI.')
 m.cleanup()
if __name__=='__main__':test(Path(sys.argv[1]))
