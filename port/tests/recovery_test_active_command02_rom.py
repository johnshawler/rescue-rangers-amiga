#!/usr/bin/env python3
"""Independent original-ROM command02 proof, no runtime native opcode interpretation."""
import hashlib,random
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_active_command02_contract import make_checker,command02,PORT
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 resource=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
 def oracle(s,c,r):
  bus[:2048]=s;bus.events.clear();ref.pc=0x83a0;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(60):
   pc=ref.pc
   if pc==0x839d:break
   assert 0x83a0<=pc<=0x83a7 or 0x8473<=pc<=0x8480 or 0x8023<=pc<=0x8037 or 0x84bd<=pc<=0x84cc
   if pc in (0x802c,0x8030):
    a=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535;bus.events.append(('resource',a,bus[a],0))
   ref.step()
  else:raise AssertionError('reference timeout')
  result=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert result==command02(s,c,r);return result
 check,cleanup=make_checker(oracle);rng=random.Random(3)
 for case in range(4096):
  c=bytes((0x83,0xa0,2,0x28+case%4,case&255,(case&0xcf)|32,case&255,case>>8));check(rng.randbytes(2048),c,resource)
 cleanup();print('PASS4096 independent original-ROM command02 cases')
if __name__=='__main__':main()
