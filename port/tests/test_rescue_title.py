#!/usr/bin/env python3
"""Original title coroutine vs assembled native menu, at real frame yields."""
from pathlib import Path
import hashlib,random,subprocess,tempfile,sys
from test_rescue_game import P,VASM,MPU,machine68k
ROM=(P.parent/'input/rescue-rangers-europe.nes').read_bytes()
assert hashlib.sha256(ROM).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def main():
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'a.bin';subprocess.run([str(VASM),'-quiet','-m68020','-Fbin','-o',str(f),str(P/'src/native_rescue_title.s')],check=True);code=f.read_bytes()
 m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
 mem.w_block(0x1000,code);mem.w16(0x800,0x60fe)
 bus=[0]*65536;bus[0x8000:0xc000]=ROM[16+2*16384:16+3*16384];bus[0xc000:]=ROM[16+7*16384:16+8*16384]
 ref=MPU(memory=bus);rng=random.Random(0xa000);count=0
 def check(state,phase,x):
  nonlocal count
  bus[:2048]=state;ref.pc=[0xa000,0xa025,0xa06c][phase];ref.x=x;ref.y=ref.a=0;ref.p=0x20;ref.sp=0xff
  for _ in range(2000):
   if ref.pc in (0xa022,0xa069,0xa086):
    wantphase=1 if ref.pc==0xa022 else 2;break
   if ref.pc==0xa0c8:wantphase=3;break
   ref.step()
  else:raise AssertionError(('reference timeout',hex(ref.pc)))
  regs=[rng.getrandbits(32) for _ in range(15)];regs[8]=0x10000;regs[9]=0x11000
  mem.w_block(0xfff0,b'\xa7'*16+state+b'\xa7'*16);mem.w_block(0x11000,bytes((phase,x,0x7a,0x7a)))
  cpu.w_sr(0x2700);cpu.w_sp(0x1f0000);mem.w32(0x1f0000,0x800)
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_pc(0x1000)
  for _ in range(100):
   cpu.execute(1000)
   if cpu.r_pc()==0x800:break
  else:raise AssertionError('native timeout')
  assert [cpu.r_reg(i) for i in range(15)]==regs
  assert cpu.r_sp()==0x1f0004
  got=bytes(mem.r_block(0x10000,2048));want=bytes(bus[:2048])
  # Original 6502 call/temporary stack writes are removed, not game state.
  assert got[:256]+got[512:]==want[:256]+want[512:],(phase,x,[(hex(i),a,b) for i,(a,b) in enumerate(zip(want,got)) if a!=b and not 256<=i<512])
  assert got[256:512]==state[256:512]
  assert bytes(mem.r_block(0xfff0,16))==b'\xa7'*16 and bytes(mem.r_block(0x10800,16))==b'\xa7'*16
  context=bytes(mem.r_block(0x11000,4));assert context==bytes((wantphase,ref.x,0x7a,0x7a)),(context,wantphase,ref.x)
  count+=1;return got,wantphase,ref.x
 for phase in range(3):
  for input in range(256):
   for selection in (0,1):
    for full in (False,True):
     state=bytearray(rng.randbytes(2048));state[0x14]=input;state[0x50]=selection;state[0xda]=rng.randrange(8)
     state[0xdc:0xe4]=bytes([0x27 if full else 0x88])*8
     state[0x203]=[0x28,0x88][selection]
     check(state,phase,rng.randrange(256))
 for low in range(256):
  for high in (0,1,255):
   state=bytearray(rng.randbytes(2048));state[0x14]=0;state[0x50]=0;state[0xda]=0;state[0xbe]=low;state[0xbf]=high
   check(state,1,0)
 # Real captured title RAM and sequences: 2-player, Chip, Dale, demo timeout.
 initial=(P.parent/'artifacts/title-ram.bin').read_bytes()
 assert len(initial)==2048
 sequences=[[0x20,0x10],[0x10,0,0x10],[0x10,1,0,0x10],[0]*901]
 outcomes=[]
 for sequence in sequences:
  state=initial;phase=1;x=0xff
  for input in sequence:
   state=bytearray(state);state[0x14]=input
   state,phase,x=check(state,phase,x)
   if phase==3:break
  assert phase==3,(sequence[:8],phase)
  outcomes.append({'players':state[0x50]+1,'demo':state[0xb8],'cursor':state[0x203]})
 m.cleanup();print(f'PASS: {count} original-title vs assembled 68020 yield intervals, full non-stack RAM, native untouched stack, guards, context and preserved registers.');print('Captured-title scenarios:',outcomes)
if __name__=='__main__':main()
