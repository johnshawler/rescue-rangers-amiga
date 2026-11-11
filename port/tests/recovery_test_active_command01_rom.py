#!/usr/bin/env python3
"""Independent original-ROM command01 proof, no runtime native opcode interpretation."""
import hashlib,random
from recovery_test_active_command0e_rom import Ricoh as MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_active_command01_contract import make_checker,command01,PORT
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def reference(bus,ref):
 for _ in range(60):
  pc=ref.pc
  if pc==0x839d:return
  assert 0x83a0<=pc<=0x83a7 or 0x8473<=pc<=0x8480 or 0x8023<=pc<=0x8037 or 0x84b9<=pc<=0x84cc
  if pc in (0x802c,0x8030):
   a=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535;bus.events.append(('resource',a,bus[a],0))
  ref.step()
 raise AssertionError('reference timeout')
def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 resource=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
 def oracle(s,c,r):
  if command01(s,c,r) is None:return None
  bus[:2048]=s;bus.events.clear();ref.pc=0x83a0;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  reference(bus,ref)
  result=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert result==command01(s,c,r);return result
 check,cleanup=make_checker(oracle);rng=random.Random(3)
 for case in range(65536):
  c=bytes((0x83,0xa0,1,0x28+case%4,case&255,case&255,case&255,(case>>8)&255));s=bytearray(rng.randbytes(2048));s[0x730+c[3]]=case>>8;check(bytes(s),c,resource)
 for channel in range(0x28,0x2c):
  for value in range(256):
   s=bytearray(rng.randbytes(2048));s[0x730+channel]=value
   c=bytes((0x83,0xa0,1,channel,rng.randrange(256),value,(255-value)&255,0xa7))
   check(bytes(s),c,resource)
 guards=0;s=bytes(2048);c=bytes.fromhex('83a0012800ff0000')
 for field in (2,3):
  for value in range(256):
   cc=bytearray(c);cc[field]=value
   if command01(s,cc,resource) is None:check(s,bytes(cc),resource);guards+=1
 for offset in (0x485,0x486):
  for value in range(256):
   if value==resource[offset]:continue
   rr=bytearray(resource);rr[offset]=value;check(s,c,bytes(rr));guards+=1
 cleanup();print(f'PASS66560 independent original-ROM command01 cases and {guards} inert actual-bank rejections')
if __name__=='__main__':main()
