#!/usr/bin/env python3
"""Public state adapter contracts, invented states only. No original CPU/ROM."""
from recovery_state_menu_sfx_harness import *
from recovery_state_menu_sfx_models import MODELS,preflight
from recovery_state_dispatch_startup_contract import mapper_result

def check(n,s,c,index,bank,event=0):
 r=n.resource[bank*16384:(bank+1)*16384];want=MODELS[index](s,c,r)
 rt=bytes((30,17,29,bank,0,0,0xba,0xdd,0xf0,0x0d,0xd5,1));j=bytes([0xb6])*134638
 n.restore((bytes(s),c,j,rt));before=n.snapshot();result=n.run(event)
 if want is None:
  assert result==0xffffffff and n.snapshot()==before and not n.events,(index,c.hex(),'rejection')
  return False
 assert result==1,(index,c.hex(),result)
 effects=want[2];hw=[e for e in effects if e[0]!='ram']
 out=len(hw).to_bytes(2,'big')+b''.join(struct.pack('>HBB',*e[1:]) for e in hw)
 runtime=mapper_result(rt,effects);runtime[6:10]=struct.pack('>HH',index,SIZES[index])
 assert n.snapshot()==(want[0],want[1],out+j[len(out):],bytes(runtime)),('state',index,c.hex())
 assert n.events==effects,('effects',index,c.hex(),n.events,effects)
 reads=preflight(index,s,c,r)+[e[1]-0x8000 for e in hw if e[0]=='resource']
 assert n.reads==[bank*16384+i for i in reads],('reads',index,n.reads,reads)
 return True

PCS={56:(0xa07b,0xf379,0xa086),57:(0x8003,),58:(0x810d,),59:(0x8151,),60:(0x8224,),61:(0x8006,0x8298),62:(0x81a3,),63:(0x8060,0x807a,0x8085),64:(0x82b0,0x82c0),65:(0x82dc,),66:(0x830b,0x831b),67:(0xc0f6,0x8052),68:(0x86b2,),69:(0x8235,),70:(0xc0bf,),71:(0x8151,)}
def fixture(rng,index,pc,k,variant):
 s=bytearray(rng.randbytes(2048));sp=k;p=(k*73+variant*17)&255
 c=pc.to_bytes(2,'big')+bytes((39,k&3,0 if index==58 else k,p,sp,0xa7))
 s[0x80]=2;s[0x91]=0;s[0xf5]=0;s[0xdb]=k%8;s[0xdc+k%8]=39 if index==70 else 136
 s[0xc0]=1;s[0xcf]=15;s[0xd0]=0;s[0xd1]=0x90;s[0xd3]=variant&1
 s[0xc1]=0;s[0xc2]=0x90;s[0xc5]=0;s[0xc6]=0x90;s[0xd7]=variant&1
 s[0x704+(k&3)]=variant%5
 def stack(data):
  for i,v in enumerate(data,1):s[256+((sp+i)&255)]=v
 if index in (59,71):
  stack(bytes.fromhex('e580f2c0'));s[0xc0]=1 if index==59 else (k if k!=1 else 255)
 if index==60 and s[0xd3]:stack(bytes.fromhex('5f80'))
 if index==61:stack(bytes.fromhex('9782' if pc==0x8006 else '5f80'))
 if index==62:stack(bytes((0xab,0x82,k,0x5f,0x80)))
 if index==63 and pc==0x8085:stack(bytes((k&3,0x77,0xa0)))
 return s,c

def main():
 code=assemble();assert code==assemble();rng=random.Random(0x5f27)
 r=bytearray(rng.randbytes(131072));bank=3*16384
 r[bank+0xa00]=64;r[bank+0xa51:bank+0xa53]=bytes.fromhex('9000');r[bank+0x1000:bank+0x1010]=bytes([0]*16)
 r[bank+0x92e]=0;r[bank+0x6bf:bank+0x6c9]=b''.join(t.to_bytes(2,'little') for t in (0x86c9,0x86de,0x8718,0x86fa,0x890d))
 r[bank+0x2fb:bank+0x305]=b''.join(t.to_bytes(2,'little') for t in (0x8667,0x86a5,0x8652,0x869f,0x8699))
 n=Native(code,bytes(r));accepted=rejected=0;counts={}
 for index,pcs in PCS.items():
  for pc in pcs:
   for variant in range(5):
    for k in range(256):
     s,c=fixture(rng,index,pc,k,variant);b=2 if index in (56,70) else 3
     if check(n,bytes(s),c,index,b):accepted+=1;counts[str(index)]=counts.get(str(index),0)+1
     else:rejected+=1
     if variant:continue
     n.restore((bytes(s),c,bytes([0xb6])*134638,bytes((30,17,29,b,0,0,0xba,0xdd,0xf0,0x0d,0xd5,1))))
     for addr,val in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x05'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\0\0')):
      n.reject(addr,val);rejected+=1
     for event in (1,2,0x100,0xffffffff):n.reject(event=event);rejected+=1
  print('adapter',index,'accepted',counts.get(str(index),0),flush=True)
 # Newly translated tail: independent all raw status x wrapping SP, and all
 # C0 phases x wrapping SP. Other RAM remains varied; no captured states.
 for mode in ('flags','phase'):
  for v in range(256):
   for sp in range(256):
    s,c=fixture(rng,71,0x8151,sp,0)
    s[0xc0]=v if mode=='phase' else (sp if sp!=1 else 255)
    c=c[:5]+bytes((v if mode=='flags' else (v*73)&255,sp,c[7]))
    # C0=1 deliberately routes to frozen helper59, whose broader endpoint
    # is separately checked above. Keep the new bridge selector exact.
    if s[0xc0]==1:continue
    assert check(n,bytes(s),c,71,3);accepted+=1
 for sp in range(256):
  s,c=fixture(rng,71,0x8151,sp,0)
  for pos in range(1,5):
   bad=s.copy();bad[256+((sp+pos)&255)]^=1
   assert not check(n,bytes(bad),c,71,3);rejected+=1
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',accepted=accepted,inert_rejections=rejected,adapters=counts,code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest())))
if __name__=='__main__':main()
