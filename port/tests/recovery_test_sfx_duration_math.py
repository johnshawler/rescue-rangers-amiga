"""ROM-free arithmetic contract and native ABI proof; --rom adds original-code oracle."""
import random,sys,hashlib
import recovery_test_sfx_header_initialize as harness
harness.SOURCE='recovery_sfx_duration_math';harness.SIZE=6
PORT=harness.PORT

def model(s,c,r):
 pc=int.from_bytes(c[:2],'big');sp=c[6];ptr=s[0xd0]+256*s[0xd1]
 if pc not in (0x8006,0x8298):return None
 ret=0x8297 if pc==0x8006 else 0x805f
 if s[0x100+((sp+1)&255)]!=ret&255 or s[0x100+((sp+2)&255)]!=ret>>8:return None
 if pc==0x8298 and not 0x8000<=ptr<=0xbfff:return None
 ram=bytearray(s);q=bytearray(c);ev=[]
 def w(a,v):ram[a]=v&255;ev.append(('ram',a,v&255))
 def nz(v):q[5]=(q[5]&0x7d)|(v&128)|(2 if v==0 else 0)
 def push(v):w(0x100+q[6],v);q[6]=(q[6]-1)&255
 if pc==0x8006:
  # Partial product rotates the raw duration from high to low significance.
  q[2]=0;w(0xc2,0)
  for remaining in range(7,-1,-1):
   pair=(ram[0xc1]*256+ram[0xc2])*2
   w(0xc2,pair&255);w(0xc1,(pair>>8)&255)
   q[5]=(q[5]&254)|int(pair>65535)
   if pair>65535:
    for a,b,addr,carry in ((ram[0xc2],ram[0xc4],0xc2,0),):
     total=a+b+carry;value=total&255
     q[5]=(q[5]&0x3c)|int(total>255)|(64 if (~(a^b)&(a^value)&128) else 0)
     q[2]=value;w(addr,value)
    a=ram[0xc1];total=a+(q[5]&1);value=total&255
    q[5]=(q[5]&0x3c)|int(total>255)|(64 if (~a&(a^value)&128) else 0)
    q[2]=value;w(0xc1,value)
   nz(remaining)
  assert ram[0xc1]*256+ram[0xc2]==s[0xc1]*s[0xc4]
  q[4]=0;q[6]=(q[6]+2)&255;target=0x8298
 else:
  w(0xd5,ram[0xc1]+1);w(0xc0,ram[0xc0]+1)
  push(0x82);push(0xa1);q[4]=0
  v=r[ptr-0x8000];ev.append(('resource',ptr,v,0))
  w(0xd0,ptr+1)
  if ram[0xd0]==0:w(0xd1,ram[0xd1]+1)
  q[6]=(q[6]+2)&255;push(v);q[2]=v^ram[0xcf];nz(q[2])
  if q[2]:
   w(0xcf,q[2]);push(0x82);push(0xab);target=0x81a3
  else:
   q[6]=(q[6]+1)&255;q[2]=ram[0x100+q[6]];nz(q[2]);w(0xcf,q[2]);q[6]=(q[6]+2)&255;target=0x8060
 q[:2]=target.to_bytes(2,'big');return bytes(ram),bytes(q),ev

def main():
 private='--rom' in sys.argv;rng=random.Random(0x8006);compare=model
 resource=rng.randbytes(16384)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
  def compare(s,c,r):
   want=model(s,c,r)
   if want is None:return None
   bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus)
   ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
   target=int.from_bytes(want[1][:2],'big')
   for _ in range(200):
    if ref.pc==0x835a:
     addr=bus[0xd0]+256*bus[0xd1];bus.events.append(('resource',addr,bus[addr],0))
    ref.step()
    if ref.pc==target:break
   else:raise AssertionError('ROM timeout')
   got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
   assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=harness.make_checker(compare);cases=rejects=0
 def case(pc,a,b,p,sp,ptr=0x8000,equal=False):
  nonlocal cases
  s=bytearray(rng.randbytes(2048));s[0xc1]=a;s[0xc4]=b;s[0xd0]=ptr&255;s[0xd1]=ptr>>8
  s[0xcf]=resource[ptr-0x8000] if equal else resource[ptr-0x8000]^255
  ret=0x8297 if pc==0x8006 else 0x805f
  s[0x100+((sp+1)&255)]=ret&255;s[0x100+((sp+2)&255)]=ret>>8
  c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((p,sp,0xa7));check(bytes(s),c,resource);cases+=1
 # All multiplication operand pairs, under all combinations of input C and D.
 for flags in (0,1,8,9):
  for a in range(256):
   for b in range(256):case(0x8006,a,b,flags, (a+b)&255)
 print('PASS all operand pairs x C/D',cases,flush=True)
 # All raw P x wrapped SP, both entries and tail branches.
 for p in range(256):
  for sp in range(256):
   case(0x8006,p,sp,p,sp)
   case(0x8298,p,sp,p,sp,(0x8000,0x80ff,0xbfff,0xaf5f)[sp%4],bool(sp&1))
 # Every accepted resource address and both equality branches.
 for ptr in range(0x8000,0xc000):
  for equal in (False,True):case(0x8298,ptr&255,ptr>>8,ptr&255,ptr&255,ptr,equal)
 if not private:
  s=bytearray(rng.randbytes(2048));sp=0xfe
  s[0x1ff]=0x97;s[0x100]=0x82
  c=bytes.fromhex('8006000000fff ea7'.replace(' ',''))
  for pc in range(65536):
   if pc not in (0x8006,0x8298):check(bytes(s),pc.to_bytes(2,'big')+c[2:],resource);rejects+=1
  s[0x1ff]=0x5f;s[0x100]=0x80;c=bytes.fromhex('8298000000fffea7')
  for ptr in range(65536):
   if not 0x8000<=ptr<0xc000:
    s[0xd0]=ptr&255;s[0xd1]=ptr>>8;check(bytes(s),c,resource);rejects+=1
  s[0xd0]=0;s[0xd1]=128
  for pc,ret in ((0x8006,0x8297),(0x8298,0x805f)):
   for sp in range(256):
    for pos,correct in ((1,ret&255),(2,ret>>8)):
     for v in range(256):
      if v==correct:continue
      s[0x100+((sp+1)&255)]=ret&255;s[0x100+((sp+2)&255)]=ret>>8;s[0x100+((sp+pos)&255)]=v
      c=pc.to_bytes(2,'big')+bytes((0,0,0,255,sp,0xa7));check(bytes(s),c,resource);rejects+=1
 cleanup();print('PASS duration',cases,'ROM' if private else 'declarative',rejects,'inert rejects')
if __name__=='__main__':main()
