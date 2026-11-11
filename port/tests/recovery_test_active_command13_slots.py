"""Command 13 slot separation, arbitrary destination, and bank-edge proofs."""
import hashlib,random
from recovery_test_active_command13_contract import PORT,command13,make_checker
from recovery_test_active_command13_rom import Ricoh,reference,SHA
from recovery_test_reset_video import OriginalBus

def main():
 rng=random.Random(0x1313);r=bytearray(rng.randbytes(16384));r[0x4a9:0x4ab]=bytes.fromhex('fb84')
 check,cleanup=make_checker(command13)
 for selected in range(256):
  for decoy in range(256):
   x=0x28+(selected+decoy)%4;s=bytearray(rng.randbytes(2048))
   s[0x728+x]=0xfe;s[0x72c+x]=0x90
   for offset in (0x744,0x74c,0x750):s[offset+x]=decoy
   # 0750+X is not a stream pointer for X28..2B. Only 0748+X is selected.
   s[0x748+x]=selected
   c=bytes((0x83,0xa0,19,x,decoy,selected,decoy,0xa7))
   check(bytes(s),c,bytes(r))
 print('PASS 65536 selected/other-slot Cartesian cases',flush=True)
 for destination in range(65536):
  x=0x28+destination%4;s=bytearray(rng.randbytes(2048));s[0x728+x]=0xfd;s[0x72c+x]=0xbf;s[0x748+x]=1
  rr=bytearray(r);rr[-3:]=bytes((destination&255,destination>>8,destination&255))
  c=bytes((0x83,0xa0,19,x,0,destination&255,destination>>8,0xa7))
  got=check(bytes(s),c,bytes(rr));assert got[0][0x728+x]+256*got[0][0x72c+x]==destination
 cleanup();print('PASS all 65536 jump destinations at last legal three-byte stream',flush=True)
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 r=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=r;ref=Ricoh(memory=bus)
 def oracle(s,c,resource):
  want=command13(s,c,resource)
  if want is None:return None
  bus[:2048]=s;bus.events.clear();ref.pc=0x83a0;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  reference(bus,ref)
  got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert got==want;return got
 check,cleanup=make_checker(oracle);total=0
 for ptr in (0x7fff,0x8000,0x80fe,0x80ff,0xbffc,0xbffd,0xbffe,0xbfff,0xc000,0xffff):
  for count in range(256):
   for x in range(0x28,0x2c):
    s=bytearray(rng.randbytes(2048));s[0x728+x]=ptr&255;s[0x72c+x]=ptr>>8;s[0x748+x]=count
    c=bytes((0x83,0xa0,19,x,count,count,(count+x)&255,0xa7));check(bytes(s),c,r);total+=1
 cleanup();print('PASS',total,'actual-ROM bank-edge/counter/channel cases')
if __name__=='__main__':main()
