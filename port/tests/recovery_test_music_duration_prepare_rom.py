#!/usr/bin/env python3
"""Independent original-ROM instrument setup, including ordered semantic reads."""
import hashlib
from pathlib import Path
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_music_duration_prepare_contract import make_checker,cases
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def main():
 path=Path(__file__).resolve().parents[2]/'input/rescue-rangers-europe.nes';rom=path.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 resource=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
 def oracle(state,c,index):
  bus[:2048]=state;bus.events.clear();ref.pc=0x8374;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(40):
   if ref.pc in (0x837f,0x86b2):break
   assert 0x8374<=ref.pc<=0x837c or 0x867c<=ref.pc<=0x8698,hex(ref.pc)
   if ref.pc in (0x868c,0x8693):
    addr=0x8a02 if ref.pc==0x868c else 0x8a01;bus.events.append(('resource',addr,bus[addr],0))
   ref.step()
  else:raise AssertionError('reference timeout')
  return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
 check,cleanup=make_checker(oracle);count=0
 for s,c in cases():check(s,c,resource,0);count+=1
 cleanup();assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 print(f'PASS {count} independent original-ROM instrument preparations; full RAM/context, ordered resource/RAM effects, ABI and global bounds.')
if __name__=='__main__':main()
