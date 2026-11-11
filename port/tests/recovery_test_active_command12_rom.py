#!/usr/bin/env python3
"""Independent cartridge CPU proof of command12, both branches, raw flags."""
import hashlib,random
from recovery_test_active_command12_contract import make_checker,command12,PORT
from recovery_test_reset_video import OriginalBus
from recovery_test_gameplay_fade_entry import Ricoh2A03,prove_binary_sbc
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
from recovery_test_active_command0e_rom import Ricoh,prove_binary_adc
def reference(bus,ref):
 for _ in range(180):
  pc=ref.pc
  if pc==0x839d:return
  assert (0x83a0<=pc<=0x83a7 or 0x8473<=pc<=0x8480 or 0x8023<=pc<=0x8037 or 0x84f7<=pc<=0x8510 or 0x8523<=pc<=0x855b or 0x856e<=pc<=0x8584),hex(pc)
  if pc in (0x802c,0x8030,0x857a):
   a=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535;bus.events.append(('resource',a,bus[a],0))
  ref.step()
 raise AssertionError('reference timeout')
def main():
 print("PASS binary ADC/SBC truth-table cases",prove_binary_adc(),prove_binary_sbc())
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 resource=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=Ricoh(memory=bus)
 def oracle(s,c,r):
  expected=command12(s,c,r)
  if expected is None:return None
  bus[:2048]=s;bus.events.clear();ref.pc=0x83a0;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  reference(bus,ref)
  result=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert result==expected,('model',c.hex(),result[1].hex(),expected[1].hex(),result[2],expected[2]);return result
 check,cleanup=make_checker(oracle);rng=random.Random(14);total=0
 # All mapped pointers under all four channels; rotating counter/P/SP expose wrapping.
 for x in range(0x28,0x2c):
  for ptr in range(0x8000,0xc000):
   s=bytearray(rng.randbytes(2048));s[0x728+x]=ptr&255;s[0x72c+x]=ptr>>8;s[0x744+x]=ptr&255
   c=bytes((0x83,0xa0,18,x,ptr>>8,ptr&255,(ptr+x)&255,0xa7));check(bytes(s),c,resource);total+=1
 cleanup();print(f'PASS {total} independent original-ROM command12 cases')
if __name__=='__main__':main()
