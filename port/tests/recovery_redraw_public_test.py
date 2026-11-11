#!/usr/bin/env python3
"""Synthetic native redraw checks. No original assets or hardware timing claims."""
from pathlib import Path
import os, random, subprocess, tempfile, importlib.util, hashlib
import machine68k
ROOT=Path(__file__).resolve().parents[2]
VASM=os.environ['VASM']
def load(name,sha):
 p=ROOT/'port/tests'/name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
BG=load('test_native_background.py','7e6ed0f74bccc9dbf2c8628c6366c3487aace3ae347732bbe42e2aaee86b76f2')
SP=load('test_native_sprites.py','fef2fc39db6484421230e768b86fbd548570e976830e6e82b852a5e2271a8f6e')
def assemble(source):
 with tempfile.TemporaryDirectory() as t:
  p=Path(t);(p/'test.s').write_text(source)
  subprocess.run([VASM,'-quiet','-m68020','-Fbin','-o',str(p/'out'),str(p/'test.s')],check=True)
  return (p/'out').read_bytes()
def invalidated(cache,oam):
 out=bytearray(cache)
 for i in range(64):
  y=oam[i*4]+1;x=oam[i*4+3]
  # Independent pixel enumeration, not bounding-box arithmetic.
  for py in range(y,min(y+8,240)):
   for px in range(x,min(x+8,256)):
    k=2*((py//8)*32+px//8);out[k:k+2]=b'\xff\xff'
 return out
class Harness:
 def __init__(self,source,sr):
  self.code=assemble(source);self.m=machine68k.Machine(machine68k.CPUType.M68EC020,1024);self.mem=self.m.mem;self.cpu=self.m.cpu;self.sr=sr
  self.mem.w_block(0x1000,self.code);self.mem.w16(0x800,0x60fe)
 def call(self,regs,stack=60,regions=(),reads=(),trace=True):
  mem,cpu=self.mem,self.cpu
  mem.w_block(0xeff00,b'\xa5'*256);mem.w32(0xf0000,0x800);mem.w_block(0xf0004,b'\xa5'*16)
  cpu.w_sr(self.sr);cpu.w_sp(0xf0000);cpu.w_pc(0x1000)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  writable=tuple(regions)+((0xf0000-stack,0xf0000),)
  readable=writable+tuple(reads)+((0x1000,0x1000+len(self.code)),(0x800,0x802),(0xf0000,0xf0004))
  def access(mode,width,addr,value):
   assert any(lo<=addr and addr+(1<<width)<=hi for lo,hi in (writable if mode=='W' else readable)),(mode,width,hex(addr))
  if trace:mem.set_trace_func(access);mem.set_trace_mode(True)
  for _ in range(40000):
   cpu.execute(1000)
   if cpu.r_pc()==0x800:break
  else:raise AssertionError('did not return')
  mem.set_trace_mode(False)
  assert cpu.r_sp()==0xf0004
  assert bytes(mem.r_block(0xf0000-stack-16,16))==b'\xa5'*16
  assert bytes(mem.r_block(0xf0004,16))==b'\xa5'*16
  assert bytes(mem.r_block(0x1000,len(self.code)))==self.code
  return [cpu.r_reg(i) for i in range(15)]
 def close(self):self.m.cleanup()
def main():
 src=(ROOT/'port/src/recovery_redraw_invalidate.s').read_text()
 rng=random.Random(68020);count=0
 for sr in (0,0x2700):
  h=Harness(src,sr);mem=h.mem
  for y in range(256):
   for group in range(4):
    # All 65536 possible byte X/Y pairs per mode, grouped in OAM batches.
    oam=bytes(v for x in range(group*64,group*64+64) for v in (y,rng.randrange(256),rng.randrange(256),x))
    cache=rng.randbytes(1920);mem.w_block(0x2000,oam);mem.w_block(0x22000,cache)
    regs=[rng.getrandbits(32) for _ in range(15)];regs[8]=0x2000;regs[12]=0x22000
    assert h.call(regs,regions=((0x22000,0x22780),),reads=((0x2000,0x2100),))==regs
    assert bytes(mem.r_block(0x22000,1920))==invalidated(cache,oam)
    assert bytes(mem.r_block(0x2000,256))==oam;count+=1
  h.close()
  full=Harness(' bra recovery_redraw_invalidate_all\n'+src,sr);full.mem.w_block(0x22000,rng.randbytes(1920))
  assert full.call(regs,stack=12,regions=((0x22000,0x22780),))==regs
  assert bytes(full.mem.r_block(0x22000,1920))==b'\xff'*1920;full.close()
 print('PASS',count,'exhaustive-position OAM batches (131072 sprite positions), both CPU modes; all register/SP, immutable source and width-aware bounds checks')
 # Composite path: restores former sprite tiles via prior postdraw invalidation.
 # Independent fresh per-pixel oracle forces all 960 background tiles every frame.
 program=''' bsr nes_draw_background
 movem.l d0-d1/a0/a4,-(sp)
 movea.l #$6000,a0
 movea.l #$24000,a4
 bsr nes_draw_sprites_8x8
 movea.l #$22000,a4
 bsr recovery_redraw_invalidate_oam
 movem.l (sp)+,d0-d1/a0/a4
 rts
'''+(ROOT/'port/src/recovery_background_single_read.s').read_text()+'\n'+(ROOT/'port/src/native_sprite_blitter.s').read_text()+'\n'+src
 frames=0
 for sr in (0,0x2700):
  h=Harness(program,sr);mem=h.mem
  nt=bytearray(rng.randbytes(1024));chrdata=bytearray(rng.randbytes(8192));initial=rng.randbytes(51200)
  mem.w_block(0x10000,initial);mem.w_block(0x20000,bytes(7680));mem.w_block(0x22000,b'\xff'*1920)
  for step in range(80):
   oam=bytearray([255,0,0,0]*64);ctrl=(step%2)*8;mask=(20,16,0)[step%3]
   if step%10!=9:
    for i in range(64 if step%4==0 else 12):
     x=(step*7+i*23)%256;y=(step*3+i*19)%256
     if step%4==0:y=step*3%240 # overflow/overlap/priority
     oam[i*4:i*4+4]=bytes((y,i,(i%4)|((i%4)<<6)|(32 if i%3==0 else 0),x))
   if step%10==8: # Identical consecutive OAM/NT/CHR/mask/control, no new pixel work.
    oam,ctrl,mask=previous_oam,previous_ctrl,previous_mask
   else:
    nt[(step*37)%960]^=0xff;nt[960+step%64]^=0x55
   previous_oam,previous_ctrl,previous_mask=oam,ctrl,mask
   if step%11==0:
    chrdata[:]=rng.randbytes(8192);mem.w_block(0x22000,b'\xff'*1920) # caller full-context fallback
   if step%17==0:
    initial=rng.randbytes(51200);mem.w_block(0x10000,initial);mem.w_block(0x22000,b'\xff'*1920)
   expected,opacity,cache,_=BG.reference(nt,chrdata[:4096],initial,bytes(7680),b'\xff'*1920)
   expected=SP.reference(oam,chrdata,expected,opacity,ctrl,mask)
   for addr,data in ((0x3000,chrdata),(0x7000,nt),(0x6000,oam)):mem.w_block(addr,bytes(data))
   regs=[ctrl,mask]+[rng.getrandbits(32) for _ in range(6)]+[0x7000,0x3000,0x10000,0x20000,0x22000,0x12345678,0x87654321]
   got=h.call(regs,stack=92,regions=((0x10000,0x1c800),(0x20000,0x21e00),(0x22000,0x22780),(0x24000,0x24894)),reads=((0x3000,0x5000),(0x6000,0x6100),(0x7000,0x7400)))
   assert got==regs,(step,'registers')
   assert bytes(mem.r_block(0x10000,51200))==expected,(sr,step,'frame')
   assert bytes(mem.r_block(0x20000,7680))==opacity,(step,'opacity')
   assert bytes(mem.r_block(0x22000,1920))==invalidated(cache,oam),(step,'cache')
   for addr,data in ((0x3000,chrdata),(0x7000,nt),(0x6000,oam)):assert bytes(mem.r_block(addr,len(data)))==data
   frames+=1
  h.close()
 print('PASS',frames,'repeated composed frames vs fresh independent per-pixel background+sprite oracle; both modes; clipping, removals, overflow, flips, priority, masks, NT/attributes, CHR and new buffers; no target timing claim')
if __name__=='__main__':main()
