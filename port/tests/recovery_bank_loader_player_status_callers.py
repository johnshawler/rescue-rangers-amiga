"""Private fresh caller/stack variants with original raw output before publication."""
import sys,struct,random
from pathlib import Path
from recovery_bank_loader_player_status_harness import *
from recovery_bank_loader_player_status_oracle import raw_module_result

def main():
 root=Path(sys.argv[1]);base=(root/'before.ram.bin').read_bytes();entry=(root/'before.context.bin').read_bytes();runtime=(root/'before.runtime.bin').read_bytes();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();n=Native(assemble(),rom[16:131088]);rng=random.Random(0x140f);cases=guards=0
 for caller in (0,0xffff,0xc77b,0x8f9a):
  for sp in range(256):
   r=bytearray(base);r[256+((sp+1)&255)]=rng.randrange(256);ret=(caller-1)&65535;r[256+((sp+2)&255)]=ret&255;r[256+((sp+3)&255)]=ret>>8
   c=entry[:5]+bytes(((rng.randrange(256)&207)|32,sp,0xa7));before=(bytes(r),c,b'\xb6'*134638,runtime);raw=raw_module_result(before,rom,140);n.restore(before);assert n.run()==1;after=n.snapshot();assert n.raw_adapter_context==raw[1] and after[0]==raw[0] and n.events==raw[2];assert after[1]==raw[1][:5]+bytes((raw[1][5]&239,))+raw[1][6:];assert after[3]==runtime[:6]+bytes.fromhex('008cea62d501');es=[e for e in raw[2] if e[0]!='ram'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert after[2]==j+before[2][len(j):];assert n.reads==[(6*16384+e[1]-0x8000 if e[1]<0xc000 else e[1]+65536) for e in es]*2;cases+=1
   if sp<8:
    for bank in range(8):
     if bank==6:continue
     n.restore(before);n.mem.w8(RUNTIME+3,bank);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads and n.raw_adapter_context is None;guards+=1
    n.restore(before);assert n.run(1)==0xffffffff and n.snapshot()==before and not n.events and not n.reads and n.raw_adapter_context is None;guards+=1
 n.m.cleanup();print('PASS fresh raw140 caller/SP comparison',cases,'and wrong-bank/event guards',guards,flush=True)
if __name__=='__main__':main()
