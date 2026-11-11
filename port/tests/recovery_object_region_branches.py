"""Private original-first bounded branch probes with synthetic external resources.
Original instructions stay immutable; synthetic data never drives target runtime.
"""
import hashlib,random
from recovery_object_region_test import ROOT,Native,compare_original
from recovery_test_resident_startup_resources import CompleteBus
from recovery_test_active_command0e_rom import Ricoh,SHA
rom=(ROOT/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
rng=random.Random(0x81df);cases=reads=steps=0
# All table reads are deliberately supplied synthetic values; low/high frame-map
# branch, signed coordinate offsets, animation phase and clipping cases vary.
for variant in range(16):
 r=bytearray(rom);base=16+5*16384
 def put(a,v):r[base+a-0x8000]=v
 put(0xb4b7,0);put(0xb560,0x90)
 put(0x9000,0x80 if variant&1 else 2);put(0x9001,1);put(0x9002,0);put(0x9003,0)
 for a in (0x9b82,0x9c82):put(a,0x20)
 for a in (0x9cae,0x9dae):put(a,0x90)
 put(0x9020,(0,1,127,128)[variant%4]);put(0x9021,0)
 for a in (0xb08e,0xb08f):put(a,0x42)
 for a in (0xb145,0xb146):put(a,0x91)
 for i in range(2,256):put(0x9020+i,i&255);put(0x9140+i,(0,1,127,128,255)[(i+variant)%5])
 n=Native(r[16:16+131072]);bus=CompleteBus(bytes(r));bus.map_bank(5);bus.mapper.prg=5;bus.mapper.control=0x1e;m=Ricoh(memory=bus)
 for trial in range(256):
  s=bytearray(2048);s[0x95]=trial&1;s[0x97]=(4,248,252,0)[trial%4]
  x=trial%16;s[0x4d0+x]=128;s[0x400+x]=(0,0x10,0x40,0x60,0x18,0x50,0x70,8)[trial%8]
  s[0x420+x]=1;s[0x410+x]=trial&1;s[0x430+x]=(0,1,127,128)[trial%4]
  s[0x4f0+x]=(0,1,96,128,255)[trial%5];s[0x500+x]=(0,1,255)[trial%3]
  s[0x510+x]=(0,1,15,128,255)[(trial//5)%5];s[0x520+x]=(0,1,255)[(trial//3)%3]
  s[0xfa]=16 if trial&32 else 0;s[0xfc]=32 if trial&64 else 0;s[0x5e+(x%2)]=trial%3
  sp=trial;s[256+((sp+1)&255)]=0x34;s[256+((sp+2)&255)]=0xc1
  bus[:2048]=s;m.pc=0x8000;m.a,m.x,m.y,m.p,m.sp=17,19,23,trial,sp
  a,b=compare_original(n,bus,m);steps+=a;reads+=b;cases+=1
 n.close()
print('PASS',cases,'original-first synthetic-resource/coordinate/animation/clip probes;',steps,'instructions;',reads,'semantic reads; every rawP and SP')
