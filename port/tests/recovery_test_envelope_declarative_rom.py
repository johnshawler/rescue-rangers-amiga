#!/usr/bin/env python3
"""Independent envelope-domain model checked against actual unmodified ROM."""
import hashlib,random
from py65.devices.mpu6502 import MPU
from recovery_test_active_envelope_rom import PORT,SHA,EnvelopeBus,run_original
from recovery_music_envelope_declarative import envelope

def main():
 path=PORT.parent/'input/rescue-rangers-europe.nes';rom=path.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 resource=rom[49168:65552];bus=EnvelopeBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus);rng=random.Random(0x890d)
 for case in range(16384):
  s=bytearray(rng.randbytes(2048));x=0x28+case%4;s[0x704+x]=(s[0x704+x]&248)|(case//4)%5
  ptr=0x8a80+(case%32)*8;s[0xc5]=ptr&255;s[0xc6]=ptr>>8
  c=bytes((0x86,0xb2,rng.randrange(256),x,rng.randrange(256),(case&0xc7)|32,case&255,(case>>8)&255))
  bus[:2048]=s;bus.events.clear();ref.pc=0x86b2;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  want=run_original(bus,ref,c[7]);got=envelope(s,c,resource)
  assert got==want,(case,got[1].hex(),want[1].hex(),[(i,a,b) for i,(a,b) in enumerate(zip(got[0],want[0])) if a!=b],got[2],want[2])
 assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 print('PASS 16384 independent envelope declarative/original-ROM comparisons, full RAM/context/ordered effects.')
if __name__=='__main__':main()
