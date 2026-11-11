#!/usr/bin/env python3
"""PUBLIC invented-state adapter contracts. No cartridge or private CPU imports."""
from recovery_state_dispatch_menu_harness import *
from recovery_test_title_engine_tables import model as tables
from recovery_test_title_menu_loop import model as menu
from recovery_test_character_menu_setup import model as setup
from recovery_test_character_selection_dispatch import model as character
from recovery_test_queued_video_nmi import expected as queue
from test_recovery_general_scheduler_contract import expected as scheduler
from recovery_state_dispatch_startup_contract import mapper_result

def check(n,r,c,rt,index,want,reads=(),event=0,pads=(0,0),raw=None):
 journal=bytes([0xb6])*134638;n.restore((bytes(r),bytes(c),journal,rt))
 before=n.snapshot();assert n.run(event,pads)==1,(index,c.hex())
 effects=want[2];hw=[e for e in effects if e[0]!='ram'];size=SIZES[index]
 out=raw if raw is not None else ((struct.pack('>H',len(hw))+b''.join(struct.pack('>HBB',e[1],e[2],e[3]) for e in hw)) if size else b'')
 out+=b'\xb6'*(size-len(out))
 runtime=mapper_result(rt,effects);runtime[6:10]=struct.pack('>HH',index,65535 if index==48 else size)
 assert n.snapshot()==(want[0],want[1],out+journal[size:],bytes(runtime)),('state',index,c.hex())
 assert n.events==effects,('effects',index)
 assert n.reads==list(reads),('reads',index,n.reads,reads)
 return before

def main():
 code=assemble();assert code==assemble();rng=random.Random(0xa06c)
 resources=rng.randbytes(131072);n=Native(code,resources);successes=rejects=0
 counts={}
 for pc,index in ((0xc5d1,43),(0xa025,44),(0xa000,45),(0xa0bb,46),(0xa05c,47),(0xfe8d,48),(0xa06c,49),(0xa089,49),(0xfe8d,50)):
  for sp in range(256):
   r=bytearray(rng.randbytes(2048));r[0x80]=2;r[0x91]=0
   r[0x14]=sp;r[0x50]=sp&1;r[0x203]=40 if sp&1 else 136
   c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes(((sp&0xcf)|32,sp,0xa7))
   rt=bytes((30,sp,255-sp,2,0,0))+rng.randbytes(4)+bytes.fromhex('d501')
   raw=None;reads=[];event=0;pads=(sp,255-sp)
   if index==43:
    want=tables(r,c,resources[114688:]);reads=[114688+e[1]-0xc000 for e in want[2] if e[0]=='resource']
   elif index==47:
    want=setup(r,c,resources[32768:49152]);reads=[32768+e[1]-0x8000 for e in want[2] if e[0]=='resource']
   elif index==48:
    event=1;r[0x80]=1;r[0x19]=255;r[0xff]|=128
    for a in (0xf0,0x9a,0x1c,0x1d):r[a]=0
    # Vary signed Y, X wrap, terminating and zero-X-ending scripts.
    r[0x360:0x463]=bytes([255])*259
    r[0x360:0x364]=bytes((0x22,sp,(0,1,127,128,129,255)[sp%6],sp))
    count=r[0x362]+1 if r[0x362]<=128 else 1
    for i in range(count):r[0x363+i]=(sp+i)&255
    r[0x360+((count+3)&255)]=255
    w=queue(r,c);assert w[3]==1;want=(w[0],w[1],w[4]);raw=w[2]
   elif index==50:
    r[0x80]=4;r[0x82]=sp;frame=(0xa024,0xa06b,0xa088)[sp%3]
    r[256+((sp+3)&255)]=frame&255;r[256+((sp+4)&255)]=frame>>8
    w=scheduler(r,c,pads);want=(w[0],w[1],w[4]);raw=w[2]
   else:
    if index==46:r[256+((sp+1)&255)]=0xf7;r[256+((sp+2)&255)]=0xc5
    w=(character if index==49 else menu)(r,c);want=(w[0],w[1],[('ram',a,v) for a,v in w[2]])
   saved=check(n,r,c,rt,index,want,reads,event,pads,raw);successes+=1;counts[index]=counts.get(index,0)+1;n.restore(saved)
   for e in (2,256,0xffffffff):n.reject(event=e,pads=pads);rejects+=1
   if index!=48:n.reject(event=1,pads=pads);rejects+=1
   else:
    before=n.snapshot();assert n.run(0,pads)==0 and n.snapshot()==before and not n.events and not n.reads
   for a,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\5'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0\0'),(CTX+5,b'\x10')):
    n.reject(a,v,event=event,pads=pads);rejects+=1
   if index not in (48,50):
    for a in (RAM+0x91,RAM+0x80):n.reject(a,b'\1');rejects+=1
   if index==46:
    for i in (1,2):n.reject(RAM+256+((sp+i)&255),b'\0');rejects+=1
   if index==50:
    for i in (3,4):n.reject(RAM+256+((sp+i)&255),b'\0',pads=pads);rejects+=1
   if index==48:
    for a in (0xf0,0x9a,0x1c,0x1d):n.reject(RAM+a,b'\1',event=1);rejects+=1
    n.reject(RAM+0xff,bytes((r[0xff]&127,)),event=1);rejects+=1
    # Initial stride five then stride four cycles nonzero X; no terminator.
    n.reject(RAM+0x360,bytes((0,0,1))+bytes(256),event=1);rejects+=1
 # Exhaust all timer values as adapter/model comparisons, including wrap and expiry.
 for timer in range(65536):
  r=bytearray(2048);r[0x80]=2;r[0xbe]=timer&255;r[0xbf]=timer>>8
  c=bytes.fromhex('a025112233')+bytes(((timer&0xcf)|32,timer&255,0xa7))
  rt=bytes.fromhex('1e1f1f020000baddf00dd501');w=menu(r,c)
  check(n,r,c,rt,44,(w[0],w[1],[('ram',a,v) for a,v in w[2]]));successes+=1
 counts[44]+=65536
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PUBLIC invented-state host contracts',successes=successes,inert_rejections=rejects,by_helper=counts,code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest()),indent=2))
if __name__=='__main__':main()
