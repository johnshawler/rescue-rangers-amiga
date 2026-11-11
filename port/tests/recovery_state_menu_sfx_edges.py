#!/usr/bin/env python3
"""Public rejected mapping, resource and boundary cases for the full composition."""
from recovery_state_menu_sfx_contract import *

def main():
 code=assemble();rng=random.Random(0x8027);r=bytearray(131072);b=3*16384
 r[b+0xa00]=64;r[b+0xa51:b+0xa53]=bytes.fromhex('9000')
 r[b+0x6bf:b+0x6c9]=b''.join(t.to_bytes(2,'little') for t in (0x86c9,0x86de,0x8718,0x86fa,0x890d))
 r[b+0x2fb:b+0x305]=b''.join(t.to_bytes(2,'little') for t in (0x8667,0x86a5,0x8652,0x869f,0x8699))
 n=Native(code,bytes(r));accepted=rejected=0
 for index,pcs in PCS.items():
  for pc in pcs:
   s,c=fixture(rng,index,pc,254,1);bank=2 if index in (56,70) else 3
   assert check(n,bytes(s),c,index,bank);accepted+=1
   saved=(bytes(s),c,bytes([0xb6])*134638,bytes((30,17,29,bank,0,0,0xba,0xdd,0xf0,0x0d,0xd5,1)))
   n.restore(saved)
   for control in range(32):
    if control==30:continue
    n.reject(RUNTIME,bytes((control,)));rejected+=1
   for wrong in range(8):
    if wrong==bank or index==70 and wrong==6:continue
    n.reject(RUNTIME+3,bytes((wrong,)));rejected+=1
   for latch in range(1,32):n.reject(RUNTIME+4,bytes((latch,)));rejected+=1
   for length in range(1,6):n.reject(RUNTIME+5,bytes((length,)));rejected+=1
   if index==56:
    n.reject(RAM+0x91,b'\1');n.reject(RAM+0x80,b'\4');rejected+=2
   if index==69:
    assert check(n,bytes(s),c,index,bank) and n.mem.r16(CTX)==0x80fb
    n.reject();rejected+=1
 # Range preflights and branch-specific pointer validity; all are independent
 # invented configurations rather than copies of successful ROM boundaries.
 for index,pc in ((58,0x810d),(60,0x8224),(61,0x8298),(65,0x82dc),(66,0x831b),(68,0x86b2)):
  for ptr in (0,0x7fff,0x8000,0x80ff,0xbff8,0xbff9,0xbffc,0xbffd,0xbffe,0xbfff,0xc000,0xffff):
   s,c=fixture(rng,index,pc,255,0)
   if index==66:c=c[:4]+b'\0'+c[5:]
   at=0xc1 if index==58 else 0xc5 if index in (66,68) else 0xd0
   s[at]=ptr&255;s[at+1]=ptr>>8
   good=check(n,bytes(s),c,index,3);accepted+=good;rejected+=not good
 n.m.cleanup()
 for index,pc,locations in ((57,0x8003,[0xa00]),(65,0x82dc,list(range(0x2fb,0x305))),(68,0x86b2,[0x92e]+list(range(0x6bf,0x6c9)))):
  s,c=fixture(rng,index,pc,0,0)
  for offset in locations:
   rr=r.copy();rr[b+offset]=0 if index==57 else rr[b+offset]^1
   probe=Native(code,bytes(rr));assert not check(probe,bytes(s),c,index,3);probe.m.cleanup();rejected+=1
 n=Native(code,bytes(r))
 for pc in (0x80fb,0x8249,0x8152,0xc5f8,0x1234):
  s,c=fixture(rng,71,pc,0,0);n.restore((bytes(s),c,bytes(134638),bytes.fromhex('1e111d030000baddf00dd501')));n.reject();rejected+=1
 n.m.cleanup();print(json.dumps(dict(status='PASS',accepted=accepted,inert_rejections=rejected)))
if __name__=='__main__':main()
