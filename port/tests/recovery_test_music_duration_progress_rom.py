#!/usr/bin/env python3
"""Independent actual-ROM duration path versus declarative and native execution."""
import hashlib
from pathlib import Path
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_music_duration_progress_contract import Native,cases,declarative
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def main():
 path=Path(__file__).resolve().parents[2]/'input/rescue-rangers-europe.nes'
 rom=path.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 bus=OriginalBus(rom);bus[0x8000:0xc000]=rom[49168:65552];ref=MPU(memory=bus);n=Native();count=0
 for state,ctx in cases():
  bus[:2048]=state;bus.events.clear();ref.pc=0x837f
  ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
  for _ in range(40):
   if ref.pc==0x839d:break
   last=ref.pc==0x839c
   assert 0x837f<=ref.pc<=0x839c or 0x859b<=ref.pc<=0x85a5,hex(ref.pc)
   ref.step()
   if last:break
  else:raise AssertionError('reference timeout')
  want=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7])),list(bus.events))
  assert want==declarative(state,ctx),(count,want[1].hex(),declarative(state,ctx)[1].hex())
  assert n.run(state,ctx)==want;count+=1
 n.m.cleanup();assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 print(f'PASS {count} independent original-ROM duration transitions, full RAM/context/ordered effects and native ABI/bounds.')
if __name__=='__main__':main()
