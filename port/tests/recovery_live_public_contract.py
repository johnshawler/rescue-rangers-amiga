#!/usr/bin/env python3
"""ROM-free user-mode title continuation and scanout access/ABI contract."""
from pathlib import Path
import tempfile,subprocess,os,re,random
import machine68k
from recovery_state_menu_sfx_harness import Native
P=Path(__file__).resolve().parents[1]
def assemble(s):
 with tempfile.TemporaryDirectory() as t:
  p=Path(t);(p/'x.s').write_text(s)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-L',str(p/'x.lst'),'-o',str(p/'x.bin'),str(p/'x.s')],check=True)
  symbols={n:int(a,16) for a,n in re.findall(r'^([0-9A-Fa-f]{8}) ([A-Za-z_][A-Za-z_0-9]*)$',(p/'x.lst').read_text(),re.M)}
  return (p/'x.bin').read_bytes(),symbols
code,_=assemble((P/'src/recovery_live_dispatch.s').read_text()+'\nrecovery_state_menu_sfx:\n moveq #-1,d0\n rts\n')
# Existing ABI harness sets SR2700. Override just this contract to user mode.
old=Native.run
import inspect
ns={};src=inspect.getsource(old);src='\n'.join(x[1:] for x in src.splitlines());assert src.count('cpu.w_sr(0x2700)')==1;src=src.replace('cpu.w_sr(0x2700)','cpu.w_sr(0)')
exec(src,old.__globals__,ns);Native.run=ns['run']
n=Native(code,bytes(131072));rng=random.Random(7272)
for sp in range(256):
 for status in (0x20,0x24,0x28,0xef):
  r=bytearray(rng.randbytes(2048));r[0x80]=2;r[0x91]=0
  c=bytes((0xa0,0x55,0x27,0x88,0xff,status,sp,0xa7));rt=bytes.fromhex('1e1f1f02000000480000d501')
  n.restore((bytes(r),c,bytes(134638),rt));assert n.run()==1
  want=bytearray(r);want[256+sp]=0xa0;want[256+((sp-1)&255)]=0x24
  rr,cc,j,rrt=n.snapshot();assert rr==want and cc==bytes((0xff,4,0x27,0x88,0xff,status,(sp-2)&255,0xa7))
  assert j==bytes(134638) and rrt==rt[:6]+bytes.fromhex('00480000d501')
  assert n.events==[('ram',256+sp,0xa0),('ram',256+((sp-1)&255),0x24)]
n.m.cleanup();Native.run=old
s=' bra.w recovery_live_scanout\n'+(P/'src/recovery_live_scanout.s').read_text()+'''
failed: rts
 cnop 0,4
startup_device: dcb.b 28,0
startup_palette: dcb.b 32,0
startup_rgb12:
'''+''.join(' dc.w '+str(i*17)+'\n' for i in range(64))+'''
startup_colors: dcb.b 128,0
recovery_live_report: dcb.b 44,0
startup_display_report: dcb.b 48,0
'''
code,syms=assemble(s);base=0x1000
for mode in ('disabled','warmup','valid'):
 for pal in range(64):
  m=machine68k.Machine(machine68k.CPUType.M68EC020,16384);mem,cpu=m.mem,m.cpu
  mem.w_block(base,code);mem.w16(0x800,0x60fe);stack=0x18000;mem.w32(stack,0x800)
  dev=base+syms['startup_device'];mem.w8(dev,0x90);mem.w8(dev+1,0 if mode=='disabled' else 0x1a if mode=='warmup' else 0x1e);mem.w8(dev+10,0x1e)
  mem.w8(base+syms['startup_palette'],pal);writes=[]
  def trace(kind,width,addr,value):
   size=1<<width
   if kind=='R':assert base<=addr and addr+size<=base+len(code) or stack-24<=addr and addr+size<=stack+4 or 0x800<=addr and addr+size<=0x804
   else:
    assert stack-24<=addr and addr+size<=stack or width==1 and addr in (0xdff096,0xdff180,base+syms['startup_colors']+2),(kind,width,hex(addr))
    if not stack-24<=addr<stack:writes.append((addr,value))
  mem.set_trace_func(trace);regs=[rng.getrandbits(32) for _ in range(15)];cpu.w_sr(0);cpu.w_sp(stack)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_pc(base);mem.set_trace_mode(True)
  for _ in range(100):
   cpu.execute(1000)
   if cpu.r_pc()==0x800:break
  else:raise AssertionError('scanout timeout')
  mem.set_trace_mode(False)
  assert [cpu.r_reg(i) for i in range(15)]==regs and cpu.r_sp()==stack+4
  assert writes==([] if mode=='valid' else [(0xdff096,0x100),(base+syms['startup_colors']+2,pal*17),(0xdff180,pal*17)])
  assert bytes(mem.r_block(base,syms['startup_device']))==code[:syms['startup_device']]
  m.cleanup()
print('PASS ROM-free USER-mode:1024 title continuations,192 scanout cases; exact registers, stack, ordered effects and width-aware bounds. No hardware timing claim.')
