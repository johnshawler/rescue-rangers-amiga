"""Directed SFX pitch, direct volume, glide flags, and resource-edge contracts."""
import hashlib,random,sys
from recovery_test_sfx_envelope import PORT,TARGETS,make_checker,model,run_original

def main():
 rng=random.Random(0x881588a8);private='--rom' in sys.argv
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_active_envelope_rom import EnvelopeBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552];bus=EnvelopeBus(rom);bus[0x8000:0xc000]=resource;ref=CPU(memory=bus)
 else:
  rt=bytearray(rng.randbytes(16384));rt[0x92e]=0;rt[0x6bf:0x6c9]=b''.join(v.to_bytes(2,'little') for v in TARGETS);resource=bytes(rt)
 def compare(s,c,r):
  if not private:return model(s,c,r)
  bus[:2048]=s;bus.events.clear();ref.pc=0x86b2;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  expected=run_original(bus,ref,c[7]);assert expected==model(s,c,r);return expected
 check,cleanup=make_checker(compare);count=0
 def trial(x,p,sp,updates):
  nonlocal count
  s=bytearray(rng.randbytes(2048));s[0x704+x]=2;s[0x708+x]=0;s[0x77c+x]=128
  pointer=0x8a80 if private else (0x8000,0x80ff,0xbff7,0xbff8)[count%4]
  s[0xc5]=pointer&255;s[0xc6]=pointer>>8
  for at,v in updates.items():s[at]=v
  c=bytes((0x86,0xb2,17,x,29,p,sp,0xa7));check(bytes(s),c,resource);count+=1
 for x in range(4):
  for high in (0,1,7,8,15,16,127,128,254,255):
   for low in (0,1,127,128,254,255):
    for scale in (0,1,2,127,128,254,255):
     trial(x,0xff,count&255,{0xd6:128,0xd8:scale,0x724+x:high,0x720+x:low})
 # Direct publication covers all 256 control bytes and all 16 amplitude nibbles.
 for x in range(4):
  for control in range(256):
   for amplitude in range(0,256,16):
    trial(x,control,(control+amplitude)&255,{0x70c+x:control,0x710+x:amplitude})
 # PHP/PLP, both glide directions and every raw flag byte at stack-wrap edges.
 for x in range(4):
  for p in range(256):
   for sp in (0,1,2,255):
    for step in (1,127,128,255):
     trial(x,p,sp,{0x704+x:34,0x718+x:step,0x71c+x:(p+sp)&255})
 cleanup();print({'directed_cases':count,'original':private})
if __name__=='__main__':main()
