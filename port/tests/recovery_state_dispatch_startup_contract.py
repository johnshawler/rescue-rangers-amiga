#!/usr/bin/env python3
"""PUBLIC invented-state contracts. No cartridge, py65 or private imports."""
from recovery_state_dispatch_startup_harness import *
from recovery_test_active_command03_contract import command03
from recovery_test_active_command02_contract import command02
from test_recovery_general_scheduler_contract import expected as scheduler
from test_recovery_startup_fade_native_contract import model as fade
from test_recovery_frame_yield_contract import expected as frame_yield
from recovery_test_startup_video_clear import model as video
from recovery_test_startup_bank_select import model as bank_select
from recovery_test_startup_resource_load import model as resource_load,validation_reads
from recovery_test_startup_title_setup import model as title
from recovery_test_title_fade_yield import model as title_entry
from recovery_test_chr_nmi_contract import expected as chr_nmi

def mapper_result(runtime,effects):
 result=bytearray(runtime);bits=[]
 for kind,a,v,k in (e for e in effects if e[0]=='mapper'):
  if v&128:bits=[];result[0]|=12;continue
  bits.append(v&1)
  if len(bits)==5:
   result[(a>>13)&3]=sum(v<<i for i,v in enumerate(bits));bits=[]
 assert not bits
 return result

def check(n,r,c,rt,index,want,reads=(),event=0,pads=(0,0),raw_journal=None):
 journal=bytes([0xb6])*32770
 n.restore((bytes(r),bytes(c),journal,rt))
 assert n.run(event,pads)==1,(index,c.hex())
 effects=want[2];hw=[e for e in effects if e[0]!='ram'];size=SIZES[index]
 if raw_journal is not None:out=raw_journal
 else:
  out=(struct.pack('>H',len(hw))+b''.join(struct.pack('>HBB',e[1],e[2],2 if index==36 and e[0]=='ppu' and e[3]==0 else e[3]) for e in hw)) if size else b''
  out+=(bytes([0xb6]) if index==36 else b'\0')*(size-len(out))
 run=mapper_result(rt,effects);run[6:10]=struct.pack('>HH',index,size)
 assert n.snapshot()==(want[0],want[1],out+journal[size:],bytes(run)),('state/journal',index,c.hex())
 assert n.events==effects,('effects',index,c.hex())
 assert n.reads==list(reads),('reads',index,n.reads,reads)
 return (bytes(r),bytes(c),journal,rt)

def main():
 code=assemble();assert code==assemble();rng=random.Random(0xc5d1)
 resources=bytearray(rng.randbytes(131072))
 resources[49152+0x487:49152+0x48b]=bytes.fromhex('bd84c484')
 # Invented bounded resource stream crossing a page, with repeat/single/literal counts.
 resources[32768+0x3f]=0xf8;resources[32768+0x49]=0x90
 stream=bytes((0x20,0,0,0x11,0x21,0x80,3,0x22,0x33,0x44,0x55,0x22,0,129,0x66,0))
 resources[32768+0x10f8:32768+0x10f8+len(stream)]=stream
 n=Native(code,resources);successes=rejects=0;by_id={}
 cases=[(0x83a0,29,3),(0x83a0,30,3),(0xfe8d,31,6),(0xfe8d,31,2),
        (0xc2a8,32,6),(0xc2a8,32,2),(0xc594,32,6),(0xff04,33,6),(0xc2a5,33,2),
        (0xc597,34,6),(0xc5bb,35,6),(0xc5c0,36,2),(0xc5c5,37,2),
        (0xc5cb,38,2),(0xc5ce,39,2),(0xfe8d,40,2),(0xc0bf,41,2),(0xc0f9,42,3)]
 for pc,index,bank in cases:
  for sp in range(256):
   r=bytearray(rng.randbytes(2048));r[0x91]=0;r[0x80]=2;r[0xf5]=r[0xf6]=0
   p=(rng.randrange(256)&0xcf)|32
   c=pc.to_bytes(2,'big')+bytes((3 if index==29 else 2,0x28+(sp&3),rng.randrange(256),p,sp,0xa7))
   rt=bytes((30,sp,255-sp,bank,0,0))+rng.randbytes(4)+bytes.fromhex('d501')
   pads=(sp,sp^255);event=0;reads=[];raw=None;view=resources[bank*16384:(bank+1)*16384]
   if index in (29,30):
    want=(command03 if index==29 else command02)(r,c,view)
    reads=[49152+i for i in ((0x489,0x48a) if index==29 else (0x487,0x488))]*2
   elif index==31:
    r[0x80]=4;r[0x82]=sp
    frame=0xc2a7 if sp&1 else 0xc596 if bank==6 else 0xc5cd
    r[256+((sp+3)&255)]=frame&255;r[256+((sp+4)&255)]=frame>>8
    w=scheduler(r,c,pads);want=(w[0],w[1],w[4]);raw=w[2]
   elif index==32:
    if pc==0xc2a8:
     r[256+((sp+1)&255)]=1;r[0xf]=0;r[0xd]=0x50 if bank==6 else 0xf0
     r[256+((sp+2)&255)]=0x93 if bank==6 else 0xd0;r[256+((sp+3)&255)]=0xc5
    w=fade(r,c);want=(w[0],w[1],[('ram',a,v) for a,v in w[4]])
   elif index==33:
    w=frame_yield(r,c);want=(w[0],w[1],[('ram',a,v) for a,v in w[4]])
   elif index in (34,35,36,37):
    want={34:video,35:bank_select,36:resource_load,37:title}[index](r,c,view)
    reads=([bank*16384+i for i in validation_reads(view)] if index==36 else [])+[bank*16384+e[1]-0x8000 for e in want[2] if e[0]=='resource']
   elif index in (38,39):
    w=title_entry(r,c);want=(w[0],w[1],[('ram',a,v) for a,v in w[2]])
   elif index==40:
    r[0x80]=1;r[0x19]=r[0x1c]=r[0x1d]=r[0xf0]=r[0x9a]=0;r[0xff]|=128
    r[0x1a]=sp;r[0x1b]=255-sp;r[0x18]=sp&1
    w=chr_nmi(r,c);want=(w[0],w[1],w[4]);raw=w[2];event=1
   elif index==41:
    r[0xdb]=sp&7;r[0xdc+(sp&7)]=0x88
    cc=bytearray(c);cc[:2]=bytes.fromhex('c0f6');cc[2]=0x88;cc[3]=r[0xdb];cc[5]=(p&0x7c)|3
    want=(bytes(r),bytes(cc),[('mapper',0xfff0,v,0) for v in (3,1,0,0,0)])
   else:
    r[0x80]=4;r[0xf1]=2
    frame=rng.randbytes(5)+bytes.fromhex('8dfe')
    for i,v in enumerate(frame,1):r[256+((sp+i)&255)]=v
    cc=bytes.fromhex('fe8d')+bytes((frame[2],frame[1],frame[0],(frame[4]&0xef)|32,(sp+7)&255,c[7]))
    want=(bytes(r),cc,[('mapper',0xfff0,v,0) for v in (2,1,0,0,0)])
   saved=check(n,r,c,rt,index,want,reads,event,pads,raw);successes+=1;by_id[str(index)]=by_id.get(str(index),0)+1
   n.restore(saved)
   if index==40:
    before=n.snapshot();assert n.run(0,pads)==0 and n.snapshot()==before and not n.events and not n.reads
   for e in (2,0xffffffff,0x100):n.reject(event=e,pads=pads);rejects+=1
   if index!=40:n.reject(event=1,pads=pads);rejects+=1
   for addr,value in ((RUNTIME+10,b'\0\0'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(CTX+5,b'\x10')):
    n.reject(addr,value,event=event,pads=pads);rejects+=1
   if sp==0:
    for v in range(256):
     if v!=30:n.reject(RUNTIME,bytes((v,)),event=event,pads=pads);rejects+=1
     # C2A8 has both valid banks, but the terminal frame is bank-specific.
     if v not in ((2,6) if index in (33,41) else (bank,)):n.reject(RUNTIME+3,bytes((v,)),event=event,pads=pads);rejects+=1
   if index==32 and pc==0xc2a8:
    for offset in (2,3):n.reject(RAM+256+((sp+offset)&255),b'\0');rejects+=1
   if index==31:
    n.reject(RAM+256+((sp+3)&255),b'\0',pads=pads);rejects+=1
   if index in (34,35,36,37,38,39):
    for addr in (RAM+0x91,RAM+0x80):n.reject(addr,b'\1');rejects+=1
   if index==40:
    for addr in (RAM+0x19,RAM+0x1c,RAM+0x1d,RAM+0xf0,RAM+0x9a):n.reject(addr,b'\1',event=1);rejects+=1
   if index==42:
    for offset in (6,7):n.reject(RAM+256+((sp+offset)&255),b'\0');rejects+=1
   if index in (29,30):
    for value in (0,0x27,0x2c,255):n.reject(CTX+3,bytes((value,)));rejects+=1
   if index==35:
    for addr in (RAM+0xf5,RAM+0xf6):n.reject(addr,b'\1');rejects+=1
   if index==41:
    for addr,value in ((RAM+0xf5,b'\1'),(RAM+0xdb,b'\x08'),(RAM+0xdc+(sp&7),b'\0')):
     n.reject(addr,value);rejects+=1
   if index==40:
    n.reject(RAM+0xff,bytes((r[0xff]&127,)),event=1);rejects+=1
 # Nonterminal attenuation/countdowns continue into frame yields on live buffers.
 for bank in (2,6):
  for sp in range(256):
   for count,level in ((0,16),(2,16),(128,16),(255,16),(1,0),(1,16),(1,79),(1,81)):
    r=bytearray(rng.randbytes(2048));r[0x80]=2;r[0x91]=0;r[0xf]=0;r[0xd]=level
    r[256+((sp+1)&255)]=count
    c=bytes.fromhex('c2a8')+rng.randbytes(3)+bytes(((rng.randrange(256)&0xcf)|32,sp,0xa7))
    rt=bytes((30,sp,255-sp,bank,0,0))+bytes.fromhex('baddf00dd501')
    w=fade(r,c);want=(w[0],w[1],[('ram',a,v) for a,v in w[4]])
    check(n,r,c,rt,32,want);successes+=1;by_id['32']+=1
    before=n.snapshot();w=frame_yield(before[0],before[1]);yield_id=33 if bank==2 else 23
    assert n.run()==1
    assert n.snapshot()==(w[0],w[1],before[2],before[3][:6]+struct.pack('>HH',yield_id,0)+before[3][10:])
    assert n.events==[('ram',a,v) for a,v in w[4]] and not n.reads
    successes+=1;by_id[str(yield_id)]=by_id.get(str(yield_id),0)+1
 # An invented near-budget loader stream and an over-budget stream.
 for blocks in (31,32):
  altered=bytearray(resources);altered[32768+0x3f]=0;altered[32768+0x49]=0x90
  data=(bytes((0x20,0,128))+rng.randbytes(129))*blocks+b'\0'
  altered[32768+0x1000:32768+0x1000+len(data)]=data
  n.resource=bytes(altered);n.mem.w_block(RESOURCE,n.resource)
  r=bytearray(2048);r[0x80]=2;c=bytes.fromhex('c5c000000020ffa7');rt=bytes.fromhex('1e0010020000baddf00dd501')
  view=altered[32768:49152];want=resource_load(r,c,view)
  if blocks==31:
   assert want is not None
   reads=[32768+i for i in validation_reads(view)]+[32768+e[1]-0x8000 for e in want[2] if e[0]=='resource']
   check(n,r,c,rt,36,want,reads);successes+=1;by_id['36']+=1
  else:
   assert want is None
   n.restore((bytes(r),c,bytes([0xb6])*32770,rt));n.reject();rejects+=1
 # Every command resource guard byte, and malformed loader pointers/budgets.
 for index,off in ((29,0x489),(29,0x48a),(30,0x487),(30,0x488)):
  altered=bytearray(resources);altered[49152+off]^=1;n.resource=bytes(altered);n.mem.w_block(RESOURCE,n.resource)
  r=bytes(2048);c=bytes.fromhex('83a0')+bytes((3 if index==29 else 2,0x28,0,32,255,0xa7))
  rt=bytes.fromhex('1e0010030000baddf00dd501');n.restore((bytes(r),c,bytes([0xb6])*32770,rt));n.reject();rejects+=1
 for pointer in (0,0x7fff,0xc000,0xffff,0xbfff):
  altered=bytearray(resources);altered[32768+0x3f]=pointer&255;altered[32768+0x49]=pointer>>8;altered[49151]=1
  n.resource=bytes(altered);n.mem.w_block(RESOURCE,n.resource)
  r=bytearray(2048);r[0x80]=2;n.restore((bytes(r),bytes.fromhex('c5c000000020ffa7'),bytes([0xb6])*32770,bytes.fromhex('1e0010020000baddf00dd501')));n.reject();rejects+=1
 import sys
 assert not any(name=='py65' or name.startswith('py65.') for name in sys.modules)
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PUBLIC invented states, no ROM/private imports',successes=successes,inert_rejections=rejects,successes_by_id=by_id,code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest()),indent=2))
if __name__=='__main__':main()
