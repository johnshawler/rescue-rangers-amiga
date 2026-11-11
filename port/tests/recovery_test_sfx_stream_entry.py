"""Declarative SFX fields plus independent original instruction execution."""
import os,random,sys,hashlib
from pathlib import Path
import recovery_test_sfx_header_initialize as harness
harness.SOURCE='recovery_sfx_stream_entry';harness.SIZE=18
PORT=harness.PORT

def model(s,c,r):
 ptr=s[0xd0]+256*s[0xd1];sp=c[6]
 if c[:2]!=bytes.fromhex('8224'):return None
 if s[0xd3]:
  if s[0x100+((sp+1)&255)]!=0x5f or s[0x100+((sp+2)&255)]!=0x80:return None
 elif not 0x8000<=ptr<=0xbffc:return None
 ram=bytearray(s);q=bytearray(c);ev=[]
 def w(a,v):ram[a]=v&255;ev.append(('ram',a,v&255))
 def nz(v):q[5]=(q[5]&0x7d)|(v&128)|(2 if v==0 else 0)
 def push(v):w(0x100+q[6],v);q[6]=(q[6]-1)&255
 def fetch(ret):
  push(0x82);push(ret);q[4]=0
  a=ram[0xd0]+256*ram[0xd1];v=r[a-0x8000];ev.append(('resource',a,v,0));q[2]=v
  w(0xd0,ram[0xd0]+1)
  if ram[0xd0]==0:w(0xd1,ram[0xd1]+1);nz(ram[0xd1])
  else:nz(ram[0xd0])
  q[6]=(q[6]+2)&255
  return v
 def shift():
  carry=ram[0xc4]&1;w(0xc4,ram[0xc4]>>1);q[5]=(q[5]&254)|carry;nz(ram[0xc4]);return carry
 if ram[0xd3]:
  q[2]=ram[0xd3];w(0xd3,ram[0xd3]-1);w(0xd5,ram[0xd5]-1);nz(ram[0xd5]);q[6]=(q[6]+2)&255;pc=0x8060
 else:
  command=fetch(0x2f);w(0xc4,command);q[2]=(command*2)&255;q[5]=(q[5]&254)|(command>>7);nz(q[2])
  if command&128:pc=0x8235
  elif shift():pc=0x8249
  else:
   if shift():w(0xd4,fetch(0x7e))
   if shift():w(0xd2,fetch(0x87))
   duration=fetch(0x8c);w(0xd3,duration);w(0xc1,duration);q[2]=ram[0xd4];nz(q[2]);w(0xc4,q[2]);push(0x82);push(0x97);pc=0x8006
 q[:2]=pc.to_bytes(2,'big');return bytes(ram),bytes(q),ev

def main():
 private='--rom' in sys.argv;rng=random.Random(0x8224)
 compare=model
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
  resource=rom[49168:65552]
  def compare(s,c,r):
   want=model(s,c,r)
   if want is None:return want
   bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0x8224;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
   for _ in range(200):
    if ref.pc==0x835a:
     a=bus[0xd0]+256*bus[0xd1];bus.events.append(('resource',a,bus[a],0))
    ref.step()
    if ref.pc in (0x8006,0x8060,0x8235,0x8249):break
   else:raise AssertionError('ROM timeout')
   got=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
   assert got==want,('ROM',c.hex(),got[1].hex(),want[1].hex(),got[2],want[2]);return got
 check,cleanup=harness.make_checker(compare);cases=rejects=0;r=bytearray(resource if private else rng.randbytes(16384))
 for p in range(256):
  for sp in range(256):
   s=bytearray(rng.randbytes(2048));ptr=(0x8000,0x80ff,0xbffc,0xaf5c)[sp%4];s[0xd0]=ptr&255;s[0xd1]=ptr>>8;s[0xd3]=0 if sp&1 else (p or 1)
   s[0x100+((sp+1)&255)]=0x5f;s[0x100+((sp+2)&255)]=0x80
   if not private:r[ptr-0x8000]=p
   c=bytes.fromhex('8224')+bytes((sp,p,sp,p,sp,p^sp));check(bytes(s),c,bytes(r));cases+=1
 for ptr in range(0x8000,0xbffd):
  s=bytearray(rng.randbytes(2048));s[0xd3]=0;s[0xd0]=ptr&255;s[0xd1]=ptr>>8
  check(bytes(s),bytes.fromhex('822400ff00ff00a7'),bytes(r));cases+=1
 # Bank-tail commands exercise the four-read maximum ending exactly BFFF.
 for command in range(256):
  for ptr in range(0xbff9,0xbffd):
   s=bytearray(rng.randbytes(2048));s[0xd3]=0;s[0xd0]=ptr&255;s[0xd1]=ptr>>8
   if not private:r[ptr-0x8000]=command
   check(bytes(s),bytes.fromhex('822400ff00')+bytes((command,command,0xa7)),bytes(r));cases+=1
 if not private:
  s=bytearray(rng.randbytes(2048));s[0xd3]=0;s[0xd0]=0;s[0xd1]=128;c=bytes.fromhex('822400ff00ff00a7')
  for pc in range(65536):
   if pc!=0x8224:check(bytes(s),pc.to_bytes(2,'big')+c[2:],bytes(r));rejects+=1
  for ptr in range(65536):
   if not 0x8000<=ptr<=0xbffc:
    s[0xd0]=ptr&255;s[0xd1]=ptr>>8;check(bytes(s),c,bytes(r));rejects+=1
  s[0xd3]=1
  for sp in range(256):
   for pos,correct in ((1,0x5f),(2,0x80)):
    for v in range(256):
     if v==correct:continue
     s[0x100+((sp+1)&255)]=0x5f;s[0x100+((sp+2)&255)]=0x80;s[0x100+((sp+pos)&255)]=v
     check(bytes(s),c[:6]+bytes((sp,c[7])),bytes(r));rejects+=1
 cleanup();print('PASS stream',cases,'ROM' if private else 'declarative',rejects,'inert rejects')
if __name__=='__main__':main()
