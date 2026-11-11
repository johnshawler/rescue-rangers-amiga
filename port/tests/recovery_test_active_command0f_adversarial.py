"""Additional command0f state-mask Cartesian and actual-ROM raw-status/guard proofs."""
import hashlib,random
from recovery_test_active_command0f_contract import PORT,command0f,make_checker
from recovery_test_active_command0f_rom import Ricoh,reference,SHA
from recovery_test_reset_video import OriginalBus

def main():
 rng=random.Random(0x1212);r=bytearray(rng.randbytes(16384));r[0x4a1:0x4a3]=bytes.fromhex('fb84')
 check,cleanup=make_checker(command0f)
 for flags in range(256):
  for operand in range(256):
   x=0x28+(flags+operand)%4;s=bytearray(rng.randbytes(2048));s[0x728+x]=0xfd;s[0x72c+x]=0x90;s[0x748+x]=0;s[0x730+x]=flags
   rr=bytearray(r);rr[0x10fd]=operand
   c=bytes((0x83,0xa0,15,x,operand,flags,(flags+operand)&255,0xa7))
   check(bytes(s),c,bytes(rr))
 cleanup();print('PASS 65536 ROM-free channel-state/operand Cartesian cases',flush=True)
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 r=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=r;ref=Ricoh(memory=bus)
 def oracle(s,c,resource):
  want=command0f(s,c,resource)
  if want is None:return None
  bus[:2048]=s;bus.events.clear();ref.pc=0x83a0;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  reference(bus,ref)
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert got==want;return got
 check,cleanup=make_checker(oracle)
 for count in range(256):
  for status in range(256):
   x=0x28+(count+status)%4;s=bytearray(rng.randbytes(2048));s[0x728+x]=0xfe;s[0x72c+x]=0x90;s[0x748+x]=count
   c=bytes((0x83,0xa0,15,x,status,status,(count+status)&255,0xa7))
   check(bytes(s),c,r)
 rejected=0;s=bytearray(2048);s[0x754]=0x90;s=bytes(s);c=bytes.fromhex('83a00f280020ff00')
 for field in (2,3):
  for value in range(256):
   cc=bytearray(c);cc[field]=value
   if command0f(s,cc,r) is None:check(s,bytes(cc),r);rejected+=1
 for offset in (0x4a1,0x4a2):
  for value in range(256):
   if value==r[offset]:continue
   rr=bytearray(r);rr[offset]=value;check(s,c,bytes(rr));rejected+=1
 cleanup();print('PASS 65536 actual-ROM counter/raw-status Cartesian cases and',rejected,'actual-bank inert rejections')
if __name__=='__main__':main()
