#!/usr/bin/env python3
"""PUBLIC finite long-script regressions crossing the signed journal-count limit."""
from recovery_state_dispatch_menu_contract import check,queue
from recovery_state_dispatch_menu_harness import *

def cases():
 rng=random.Random(0x33339)
 for ordinal in range(4):
  r=bytearray(2048) if ordinal<2 else bytearray(rng.randbytes(2048))
  for a in (0xf0,0x9a,0x1c,0x1d):r[a]=0
  r[0x80]=1;r[0x19]=1;r[0xff]=128;r[0x1a]=3;r[0x1b]=7;r[0x18]=ordinal&1
  r[0x360:0x463]=bytes([127])*259
  c=bytes.fromhex('fe8d11223324fda7') if ordinal<2 else bytes.fromhex('fe8d')+rng.randbytes(3)+bytes(((ordinal*37&0xcf)|32,(0,255)[ordinal&1],0xa7))
  rt=bytes.fromhex('1e1f1f020000baddf00dd501')
  yield ordinal,r,c,rt

def main():
 code=assemble();assert code==assemble();n=Native(code,bytes(131072));out=[]
 for ordinal,r,c,rt in cases():
  w=queue(r,c);assert w[3]==1
  count=int.from_bytes(w[2][:2],'big');assert count==(33339 if ordinal&1 else 33300)
  saved=check(n,r,c,rt,48,(w[0],w[1],w[4]),event=1,raw=w[2])
  assert n.snapshot()[3]==bytes.fromhex('1e03070200000030ffffd501')
  n.restore(saved);before=n.snapshot();assert n.run(0)==0 and n.snapshot()==before and not n.events and not n.reads
  for event in (2,256,0xffffffff):n.reject(event=event)
  for at,value in ((RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0\0'),(RAM+0x1c,b'\1'),(RAM+0x1d,b'\1')):n.reject(at,value,event=1)
  out.append(dict(case=ordinal,records=count,expected_runtime='1e03070200000030ffffd501',inert_rejections=8))
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PUBLIC invented finite long scripts',code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest(),cases=out),indent=2))
if __name__=='__main__':main()
