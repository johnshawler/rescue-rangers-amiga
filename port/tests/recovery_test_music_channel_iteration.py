#!/usr/bin/env python3
"""Independent actual-cartridge execution of outer-channel iteration."""
import hashlib
from recovery_test_music_channel_iteration_contract import Native,cases,PORT
from recovery_test_music_event_block import AudioBus,SHA
from py65.devices.mpu6502 import MPU

def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 bus=AudioBus(rom);ref=MPU(memory=bus);native=Native();count=0;ends={}
 for state,ctx in cases(16384):
  bus[:2048]=state;bus.events.clear();ref.pc=0x8085;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
  for steps in range(300):
   if ref.pc==0x839d:break
   last=ref.pc==0x80ba
   assert 0x8072<=ref.pc<=0x80ba or 0x8363<=ref.pc<=0x8372 or ref.pc==0x839c,hex(ref.pc)
   ref.step()
   if last:break
  else:raise AssertionError('reference timeout')
  out=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
  want=bytes(bus[:2048]),out,list(bus.events)
  got=native.run(state,ctx);assert got==want,(count,got[1].hex(),out.hex(),got[2],want[2])
  ends['fetch' if ref.pc==0x839d else 'return']=ends.get('fetch' if ref.pc==0x839d else 'return',0)+1;count+=1
 native.m.cleanup();print('PASS',count,'actual-ROM comparisons',ends,'complete RAM/context, ordered effects, ABI/global whitelist')
if __name__=='__main__':main()
