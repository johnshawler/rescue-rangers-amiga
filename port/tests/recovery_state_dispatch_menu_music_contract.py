#!/usr/bin/env python3
"""PUBLIC invented-state guards and ABI for five menu music adapters."""
from recovery_state_dispatch_menu_contract import check
from recovery_state_dispatch_menu_harness import *
from recovery_test_active_command0e_contract import command0e,validation_reads as reads0e
from recovery_test_active_command01_contract import command01
from recovery_test_active_command12_contract import command12,validation_reads as reads12
from recovery_test_active_command13_contract import command13,validation_reads as reads13
from recovery_test_active_command0f_contract import command0f,validation_reads as reads0f
SPECS=((14,51,command0e,reads0e,0x49f,b'\xf7\x84'),(1,52,command01,lambda s,c,r:[0x485,0x486],0x485,b'\xb9\x84'),(18,53,command12,reads12,0x4a7,b'\xf7\x84'),(19,54,command13,reads13,0x4a9,b'\xfb\x84'),(15,55,command0f,reads0f,0x4a1,b'\xfb\x84'))

def main():
 code=assemble();assert code==assemble();rng=random.Random(0x900);resources=bytearray(rng.randbytes(131072))
 for command,index,model,preflight,offset,signature in SPECS:resources[49152+offset:49152+offset+2]=signature
 resources[65534:65536]=bytes(2)
 n=Native(code,resources);successes=rejects=0;counts={}
 rt=bytes.fromhex('1e1f1f030000baddf00dd501');view=resources[49152:65536]
 def trial(command,index,model,preflight,r,c):
  nonlocal successes,rejects
  want=model(r,c,view)
  if want is None:
   n.restore((bytes(r),c,b'\xb6'*134638,rt));n.reject();rejects+=1;return None
  hw=[e for e in want[2] if e[0]!='ram'];raw=struct.pack('>H',len(hw))+b''.join(struct.pack('>HBB',e[1],e[2],e[3]) for e in hw);raw+=bytes(SIZES[index]-len(raw))
  reads=[49152+i for i in preflight(r,c,view)]+[49152+e[1]-0x8000 for e in hw]
  saved=check(n,r,c,rt,index,want,reads,raw=raw);successes+=1;counts[index]=counts.get(index,0)+1
  return saved
 for command,index,model,preflight,offset,signature in SPECS:
  for channel in range(0x28,0x2c):
   for sp in range(256):
    r=bytearray(rng.randbytes(2048));ptr=0x9000+sp;r[0x728+channel]=ptr&255;r[0x72c+channel]=ptr>>8
    r[0x744+channel]=sp;r[0x748+channel]=sp;r[0x730+channel]=sp
    c=bytes((0x83,0xa0,command,channel,sp^255,(sp&0xcf)|32,sp,0xa7))
    saved=trial(command,index,model,preflight,r,c);assert saved is not None;n.restore(saved)
    for e in (1,2,256,0xffffffff):n.reject(event=e);rejects+=1
    for a,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\2'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0\0'),(CTX+5,b'\x10'),(CTX+3,b'\x27'),(CTX+3,b'\x2c')):
     n.reject(a,v);rejects+=1
   # Unsafe versus safe bank-edge operand fetches, all counter branch edges.
   if command!=1:
    for ptr in (0,0x7fff,0x8000,0xbffd,0xbffe,0xbfff,0xc000,0xffff):
     for counter in (0,1,2,128,255):
      r=bytearray(rng.randbytes(2048));r[0x728+channel]=ptr&255;r[0x72c+channel]=ptr>>8;r[0x744+channel]=r[0x748+channel]=counter
      c=bytes((0x83,0xa0,command,channel,0,0x2c,counter,0xa7));trial(command,index,model,preflight,r,c)
  # A signature mismatch must reject before writing any mutable buffer.
  r[0x728+channel]=0;r[0x72c+channel]=0x90
  assert trial(command,index,model,preflight,r,c) is not None
  n.m.cleanup()
  for byte in range(2):
   altered=bytearray(resources);altered[49152+offset+byte]^=1
   bad=Native(code,altered);bad.restore((bytes(r),c,b'\xb6'*134638,rt));bad.reject();bad.m.cleanup();rejects+=1
  n=Native(code,resources)
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PUBLIC invented-state music adapters',successes=successes,inert_rejections=rejects,by_helper=counts,code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest()),indent=2))
if __name__=='__main__':main()
