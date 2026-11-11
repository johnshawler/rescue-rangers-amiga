#!/usr/bin/env python3
"""Synthetic assembled 68020 device-consumer edge cases; never target fixtures."""
import os,struct,subprocess,tempfile
from pathlib import Path
import machine68k
PORT=Path(__file__).resolve().parents[1]
def main():
 with tempfile.TemporaryDirectory() as tmp:
  tmp=Path(tmp)
  device=(PORT/'src/recovery_state_menu_display_device.s').read_text().replace('incbin "startup-display-private-chr.bin"','dcb.b 131072,0')
  (tmp/'device.s').write_text(device)
  (tmp/'test.s').write_text(' org $1000\n bra.w test_entry\n dc.l startup_device,startup_nt,startup_palette,startup_oam\ntest_entry:\n bsr startup_consume\n rts\n include "device.s"\n')
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(tmp),'-I'+str(PORT/'src'),'-o',str(tmp/'test.bin'),str(tmp/'test.s')],check=True)
  code=(tmp/'test.bin').read_bytes()
 m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
 mem.w_block(0x1000,code);dev,nt,pal,oam=struct.unpack_from('>4I',code,4)
 initial=bytes(mem.r_block(dev,28))
 calls=0
 def reset():
  for p,n in ((dev,28),(nt,2048),(pal,32),(oam,256)):mem.clear_block(p,n,0)
  mem.w_block(dev,initial)
 def consume(index,events,dma=None):
  nonlocal calls
  j=struct.pack('>H',len(events))+b''.join(struct.pack('>HBB',*e) for e in events)
  if dma is not None:
   off={6:42,11:198,31:198,45:238,48:134382}[index];j=j+bytes(off-len(j))+bytes(dma)
  mem.w_block(0x100000,j)
  regs=[index]+[0x12345678+i for i in range(14)];regs[10]=0x100000
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_sr(0x2700);cpu.w_sp(0x1f0000);mem.w32(0x1f0000,0x800);mem.w16(0x800,0x60fe);cpu.w_pc(0x1000)
  for _ in range(20000):
   cpu.execute(1000)
   if cpu.r_pc()==0x800:break
  else:raise AssertionError('consumer timeout')
  assert [cpu.r_reg(i) for i in range(15)]==regs
  assert cpu.r_sp()==0x1f0004
  calls+=1
 def ppu(*events,index=3):consume(index,[(a,v,0 if a==0x2002 else 1) for a,v in events])
 reset()
 ppu((0x2006,0x27),(0x2002,0),(0x2006,0x20),(0x2006,0),(0x2007,0x55))
 assert mem.r8(nt)==0x55
 ppu((0x2005,17),(0x2002,0),(0x2005,0),(0x2005,0))
 assert bytes(mem.r_block(dev+2,3))==bytes(3)
 # Cross-helper serial latch and each current mirroring mode on writes.
 for mode in range(4):
  reset();bits=[(0x9fff,(0x1c|mode)>>i&1,0) for i in range(5)]
  consume(2,bits[:2]);assert mem.r8(dev+15)==2
  consume(7,bits[2:]);assert mem.r8(dev+10)==0x1c|mode and mem.r8(dev+15)==0
  for page in range(4):
   ppu((0x2006,0x20+page*4),(0x2006,page),(0x2007,0x80+page))
   physical=(0,1,page&1,page>>1)[mode]
   assert mem.r8(nt+physical*1024+page)==0x80+page
 reset();ppu((0x2000,4),(0x2006,0x20),(0x2006,0),(0x2007,1),(0x2007,2))
 assert mem.r8(nt)==1 and mem.r8(nt+32)==2
 ppu((0x2000,0),(0x2006,0x3f),(0x2006,0x10),(0x2007,0x7f))
 assert mem.r8(pal)==63 and mem.r8(pal+16)==0
 reset();ppu((0x2003,253));consume(45,[(0x4014,2,1)],range(256))
 assert bytes(mem.r_block(oam,256))==bytes(list(range(3,256))+[0,1,2])
 reset();consume(42,[(0x9fff,1,0),(0x2002,0,2),(0x2006,0x20,1),(0x2006,0,1),(0x2007,7,1)])
 assert mem.r8(nt)==7 and mem.r8(dev+15)==0 and mem.r32(dev+20)==4
 ppu((0x2004,0));assert mem.r32(dev+16)==1
 for count in (0,32768,33339):
  reset();consume(48,[(0x2002,0,0)]*count)
  assert mem.r32(dev+20)==count and mem.r32(dev+16)==0
 reset();ppu((0x2003,253));consume(48,[(0x4014,2,1)],range(256))
 assert bytes(mem.r_block(oam,256))==bytes(list(range(3,256))+[0,1,2])
 print(f'PASS {calls} assembled consumer calls: register/stack preservation, shared latch resets, four mirroring modes, serial continuity, increment32, palette alias, rotated DMA, resource filtering, unknown-register error.')
if __name__=='__main__':main()
