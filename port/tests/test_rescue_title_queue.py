#!/usr/bin/env python3
"""Execute original C115 PPU writes and native title nametable adapter."""
from pathlib import Path
import hashlib,random,subprocess,tempfile
from test_rescue_game import P,VASM,MPU,machine68k
ROM=(P.parent/'input/rescue-rangers-europe.nes').read_bytes()
assert hashlib.sha256(ROM).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
class Bus(list):
 def __init__(self):
  super().__init__([0]*65536);self[0xc000:]=ROM[16+7*16384:16+8*16384];self.high=True;self.addr=0;self.nt=bytearray(1024);self.writes=[]
 def __setitem__(self,k,v):
  if k==0x2006:
   self.addr=(v<<8) if self.high else self.addr|v;self.high=not self.high
  elif k==0x2007:
   assert 0x2000<=self.addr<0x3000
   self.nt[self.addr&1023]=v;self.writes.append((self.addr,v));self.addr+=1
  super().__setitem__(k,v)
def main():
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'a.bin';subprocess.run([str(VASM),'-quiet','-m68020','-Fbin','-o',str(f),str(P/'src/native_rescue_title_queue.s')],check=True);code=f.read_bytes()
 m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu;mem.w_block(0x1000,code);mem.w16(0x800,0x60fe)
 bus=Bus();ref=MPU(memory=bus);rng=random.Random(0xc115)
 original=ROM[16+2*16384+0x20c9:16+2*16384+0x20e1]
 for case in range(1024):
  state=bytearray(rng.randbytes(2048));state[0x360:0x378]=original
  # Half exact original queues; half bounded variations test inclusive length.
  if case>=512:
   count=rng.randrange(128);addr=0x2000+rng.randrange(1024-count)
   queue=bytes((addr>>8,addr&255,count))+rng.randbytes(count+1)+b'\xff';state[0x360:0x360+len(queue)]=queue
  nt=rng.randbytes(1024);bus[:2048]=state;bus.nt=bytearray(nt);bus.high=True;bus.writes=[]
  ref.pc=0xc115;ref.p=0x20
  for _ in range(5000):
   if ref.pc==0xc139:break
   ref.step()
  else:raise AssertionError('reference timeout')
  regs=[rng.getrandbits(32) for _ in range(15)];regs[8]=0x10000;regs[9]=0x11000
  mem.w_block(0x10000,bytes(state));mem.w_block(0x10ff0,b'\xa7'*16+nt+b'\xa7'*16)
  cpu.w_sr(0x2700);cpu.w_sp(0x1f0000);mem.w32(0x1f0000,0x800)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_pc(0x1000)
  for _ in range(100):
   cpu.execute(1000)
   if cpu.r_pc()==0x800:break
  else:raise AssertionError('native timeout')
  assert bytes(mem.r_block(0x10000,2048))==bytes(bus[:2048])
  assert bytes(mem.r_block(0x11000,1024))==bus.nt
  assert bytes(mem.r_block(0x10ff0,16))==b'\xa7'*16 and bytes(mem.r_block(0x11400,16))==b'\xa7'*16
  assert [cpu.r_reg(i) for i in range(15)]==regs and cpu.r_sp()==0x1f0004
  if case<512:assert [a for a,v in bus.writes]==list(range(0x2226,0x222e))+list(range(0x2232,0x223b))
 m.cleanup();print('PASS: 1024 original PPU queue vs assembled native title nametable cases; full RAM/nametable equality, guards, registers, exact 17 title tile writes.')
if __name__=='__main__':main()
