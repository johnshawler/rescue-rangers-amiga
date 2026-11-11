#!/usr/bin/env python3
"""Original-ROM and declarative control comparison."""
import hashlib,random
from py65.devices.mpu6502 import MPU
from recovery_test_active_control_contract import Native,declarative,PORT,return_regressions
from recovery_test_reset_video import OriginalBus
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def run_control(bus,ref,reserved):
 start=len(bus.events)
 continuation=ref.pc==0x8085 and bytes(bus[0x100+((ref.sp+i)&255)] for i in range(2,7))==bytes.fromhex('005180f8c0')
 for _ in range(1000):
  pc=ref.pc
  if pc in (0x8374,0x839d):break
  assert pc in (0xc0f6,0x8000,0x839c) or 0x803a<=pc<=0x80ba or 0x8363<=pc<=0x8372,hex(pc)
  if pc==0x804f:continuation=True
  ref.step()
  if pc==0x80ba:
   if continuation and ref.pc==0x8052:continuation=False
   else:break
  elif pc==0x839c:assert ref.pc==0x8085
 else:raise AssertionError('control timeout')
 return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,(ref.p&0xef)|32,ref.sp,reserved)),list(bus.events[start:])
def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 bus=OriginalBus(rom);bus[0x8000:0xc000]=rom[49168:65552];ref=MPU(memory=bus);n=Native();rng=random.Random(0x803a)
 for case in range(16384):
  s=bytearray(rng.randbytes(2048));s[0xcf]=s[0xd0]=s[0xd1]=0;sp=case&255
  pc=0xc0f6 if case&1 else 0x8085;s[0x100+((sp+1)&255)]=(case>>1)%4
  if case%5==0:s[0x750:0x758]=bytes(8)
  c=pc.to_bytes(2,'big')+bytes((rng.randrange(256),rng.randrange(256),rng.randrange(256),(case&0xc7)|32,sp,case>>8))
  bus[:2048]=s;bus.events.clear();ref.pc=pc;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  want=run_control(bus,ref,c[7]);assert want==declarative(bytes(s),c),(case,want[1].hex(),declarative(bytes(s),c)[1].hex())
  assert n.run(bytes(s),c)==want
 regressions=0
 for s,c in return_regressions():
  bus[:2048]=s;bus.events.clear();ref.pc=0x8085;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  want=run_control(bus,ref,c[7]);assert want==declarative(s,c);assert n.run(s,c)==want;regressions+=1
 n.m.cleanup();print(f'PASS 16384 original-ROM control cases and{regressions} bounded-return regressions with independent declarative comparison')
if __name__=='__main__':main()
