"""USER-mode fixed-bank sprite caller proof, ROM-free plus optional original."""
import random,sys,hashlib
from recovery_bank_loader_contract import assemble,check,original,Native,PORT

def model(s,c):
 ram=bytearray(s);q=bytearray(c);e=[];sp=c[6];pc=int.from_bytes(c[:2],'big')
 if pc not in (0xf392,0xf39f,0xf3a2,0xf3a9) or pc==0xf392 and s[151]&3:return None
 a,x,y,p=c[2:6]
 def w(at,v):ram[at]=v;e.append(('ram',at,v))
 def push(v):
  nonlocal sp
  w(256+sp,v);sp=(sp-1)&255
 def call(ret):push(ret>>8);push(ret&255)
 if pc==0xf392:
  push(ram[241]);w(154,(ram[154]+1)&255);call(0xf399)
  if ram[151]==4:w(512,248)
  i=ram[151]
  while True:
   w(512+i,248);i=(i+4)&255
   if not i:break
  sp=(sp+2)&255;a=5;x=0;p=(p&124)|(1 if ram[151]>=4 else 0);call(0xf39e);pc=0xff53
 elif pc==0xf39f:call(0xf3a1);pc=0x8000
 elif pc==0xf3a2:
  a=0;w(154,0);call(0xf3a8);p=(p&125)|2;pc=0xff04
 else:
  sp=(sp+1)&255;a=ram[256+sp];p=(p&125)|(a&128)|(2 if not a else 0);pc=0xff53
 q[:2]=pc.to_bytes(2,'big');q[2:7]=bytes((a,x,y,p,sp))
 return bytes(ram),bytes(q),e

def main():
 private='--rom' in sys.argv;rng=random.Random(0xf392);code=assemble('object_bridge');r=bytes(16384);n=Native(code,bytes(131072));cases=guards=0
 if private:
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for pc in (0xf392,0xf39f,0xf3a2,0xf3a9):
  for k in range(256):
   s=bytearray(rng.randbytes(2048));s[151]=k;c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((k,k,0xa7));want=model(s,c)
   if private:original(rom,s,c,want,91)
   check(n,bytes(s),c,r,want);cases+=want is not None;guards+=want is None
 n.m.cleanup();print('PASS',cases,'sprite caller rawP/stack cases;',guards,'inert rejects;', 'original' if private else 'public')
if __name__=='__main__':main()
