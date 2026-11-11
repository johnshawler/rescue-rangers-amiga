#!/usr/bin/env python3
"""Independent public bridge qualification; optional original-ROM first comparison."""
import argparse,hashlib,random
from pathlib import Path
import recovery_test_sfx_stream_control as harness
from recovery_state_menu_sfx_models import tail

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--rom',type=Path);args=parser.parse_args()
 original=None
 if args.rom:
  from recovery_state_menu_sfx_oracle import ControllerBus,SHA
  from recovery_test_active_command0e_rom import Ricoh
  rom=args.rom.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  bus=ControllerBus(rom);bus.map_bank(3);ref=Ricoh(memory=bus)
  def original(s,c,r):
   want=tail(s,c,r)
   if want is None:return None
   bus[:2048]=s;bus.events.clear();ref.pc=0x8151;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
   for steps in range(20):
    ref.step()
    if ref.pc==0xc0f6:break
   else:raise AssertionError('original bridge timeout')
   got=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events))
   assert got==want,('original bridge',c.hex(),got[1].hex(),want[1].hex())
   return got
 harness.SOURCE='recovery_state_menu_sfx_tail';harness.SIZE=2;harness.validation_reads=lambda s,c,r:[]
 check,cleanup=harness.make_checker(original or tail)
 rng=random.Random(0x81510d);resource=rng.randbytes(16384);cases=rejects=0
 def state(p,sp,phase):
  s=bytearray(rng.randbytes(2048));s[0xdb]=sp&7;s[0xdc+s[0xdb]]=136;s[0xc0]=phase
  for i,v in enumerate(bytes.fromhex('e580f2c0'),1):s[256+((sp+i)&255)]=v
  c=bytes.fromhex('8151')+rng.randbytes(3)+bytes((p,sp,0xa7));return bytes(s),c
 for p in range(256):
  for sp in range(256):
   s,c=state(p,sp,(p*73+sp)&255);check(s,c,resource);cases+=1
 for phase in range(256):
  for sp in range(256):
   s,c=state((phase*73+sp)&255,sp,phase);check(s,c,resource);cases+=1
 for sp in range(256):
  s,c=state(255,sp,13)
  for offset in range(1,5):
   for val in range(256):
    at=256+((sp+offset)&255)
    if val==s[at]:continue
    b=bytearray(s);b[at]=val;check(bytes(b),c,resource);rejects+=1
 for at,vals in ((0xdb,range(8,256)),(0xdc+s[0xdb],[v for v in range(256) if v!=136])):
  for v in vals:
   b=bytearray(s);b[at]=v;check(bytes(b),c,resource);rejects+=1
 for pc in range(65536):
  if pc==0x8151:continue
  check(s,pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
 cleanup();print(dict(status='PASS',original=bool(args.rom),accepted=cases,inert_rejections=rejects))
if __name__=='__main__':main()
