#!/usr/bin/env python3
"""PUBLIC: invented RAM/resources only; no ROM, py65 or private oracle import."""
from recovery_state_dispatch_scheduler_harness import *
from test_recovery_general_scheduler_contract import expected
from test_recovery_startup_fade_native_contract import model as fade_model
from test_recovery_frame_yield_contract import expected as yield_model
from recovery_test_active_control_contract import declarative as control_model
from recovery_test_music_duration_prepare_contract import contract as prepare_model
from recovery_test_music_duration_progress_contract import declarative as progress_model
from recovery_music_envelope_declarative import envelope as envelope_model

def main():
 code=assemble();assert code==assemble()
 resources=bytes(i//16384 for i in range(131072))
 n=Native(code,resources);rng=random.Random(0x21c2a8);count=rejects=0
 for sp in range(256):
  for variant in range(8):
   r=bytearray(rng.randbytes(2048));r[0x80]=4;r[0x82]=sp
   r[256+((sp+3)&255)]=0xa7;r[256+((sp+4)&255)]=0xc2
   p=(rng.randrange(256)&0xcf)|0x20
   c=bytes.fromhex('fe8d')+rng.randbytes(3)+bytes((p,rng.randrange(256),0xa7))
   pads=((sp+variant*31)&255,sp^255)
   rt=bytes((0x1e,variant,255-variant,6,0,0))+rng.randbytes(4)+bytes.fromhex('d501')
   journal=bytes([0xb6])*8754
   n.restore((bytes(r),c,journal,rt))
   want=expected(r,c,pads)
   assert n.run(0,pads)==1
   ram,ctx,j,run=n.snapshot()
   assert (ram,ctx,j[:74],n.events)==(want[0],want[1],want[2],want[4])
   assert ctx[:2]==bytes.fromhex('c2a8')
   assert j[74:]==journal[74:] and run==rt[:6]+bytes.fromhex('0015004a')+rt[10:]
   assert not n.reads
   # Previous pad bytes are independently randomized in synthetic RAM.
   count+=1
   if variant==0:
    n.restore((bytes(r),c,journal,rt))
    for addr,v in [(RUNTIME+10,b'\0\0'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),
     (CTX+5,b'\x10'),(CTX,b'\x12\x34'),(RAM+0x80,b'\x03'),
     (RAM+256+((sp+3)&255),b'\x00'),(RAM+256+((sp+4)&255),b'\x00')]:
     n.reject(addr,v,pads=pads);rejects+=1
    for event in (1,2,0x100,0xffffffff):n.reject(event=event,pads=pads);rejects+=1
    for bank in range(256):
     if bank!=6:n.reject(RUNTIME+3,bytes((bank,)),pads=pads);rejects+=1
    for control in range(256):
     if control!=0x1e:n.reject(RUNTIME,bytes((control,)),pads=pads);rejects+=1
 fade_cases=yield_cases=0
 for sp in range(256):
  for count_byte,level in ((0,16),(2,16),(128,16),(255,16),(1,0),(1,16),(1,79),(1,81)):
   r=bytearray(rng.randbytes(2048));r[0x80]=2;r[0x91]=0
   r[256+((sp+1)&255)]=count_byte;r[0xf]=0;r[0xd]=level
   c=bytes.fromhex('c2a8')+rng.randbytes(3)+bytes(((rng.randrange(256)&0xcf)|0x20,sp,0xa7))
   rt=bytes.fromhex('1e0010060000baddf00dd501');j=bytes([0xb6])*8754
   n.restore((bytes(r),c,j,rt))
   want=fade_model(r,c)
   assert n.run()==1
   got=n.snapshot()
   assert got==(want[0],want[1],j,rt[:6]+bytes.fromhex('00160000')+rt[10:])
   assert n.events==[('ram',a,v) for a,v in want[4]] and not n.reads
   fade_cases+=1
   # Live native buffers continue without state reload into the next frame yield.
   want_yield=yield_model(want[0],want[1])
   assert n.run()==1
   assert n.snapshot()==(want_yield[0],want_yield[1],j,rt[:6]+bytes.fromhex('00170000')+rt[10:])
   assert n.events==[('ram',a,v) for a,v in want_yield[4]] and not n.reads
   yield_cases+=1
   if count_byte==0:
    for pc in (b'\xc2\xa8',b'\xc2\xa5'):
     n.restore((bytes(r),pc+c[2:],j,rt))
     for addr,value in ((RUNTIME+3,b'\x03'),(RUNTIME,b'\x00'),(RUNTIME+4,b'\x01'),
      (RUNTIME+5,b'\x01'),(RUNTIME+10,b'\x00\x00'),(CTX+5,b'\x10'),(RAM+0x91,b'\x01'),(RAM+0x80,b'\x01')):
      n.reject(addr,value);rejects+=1
     for event in (1,2,0x100,0xffffffff):n.reject(event=event);rejects+=1
    r[256+((sp+1)&255)]=1
    for level_bad in (0x50,0x80,0xff):
     r[0xd]=level_bad;n.restore((bytes(r),c,j,rt));n.reject();rejects+=1
 n.m.cleanup()
 # New active-audio operations use distinct invented banks and public models.
 resource=bytearray(rng.randbytes(131072));bank=bytearray(resource[49152:65536])
 bank[0x92e]=0
 for i,target in enumerate((0x86c9,0x86de,0x8718,0x86fa,0x890d)):
  bank[0x6bf+2*i:0x6c1+2*i]=target.to_bytes(2,'little')
 resource[49152:65536]=bank;n=Native(code,bytes(resource));audio_cases=0;audio_counts={}
 for pc,index in ((0xc0bf,24),(0xc0f6,25),(0x8085,25),(0x8374,26),(0x86b2,27),(0x837f,28)):
  for sp in range(256):
   for channel in range(4):
    r=bytearray(rng.randbytes(2048));x=0x28+channel
    r[0xcf]=r[0xd0]=r[0xd1]=r[0xf5]=0;r[0xdb]=sp&7;r[0xdc+(sp&7)]=0x88
    r[0xc0]=(sp%4)*4
    r[0x704+x]=(r[0x704+x]&248)|(sp%5)
    ptr=0x8000 if sp%2 else 0xbff8;r[0xc5]=ptr&255;r[0xc6]=ptr>>8
    frame=(channel,0,0xf8,0xc0) if sp%2 else (channel,0,0x51,0x80,0xf8,0xc0)
    if pc==0x86b2:frame=(0x7e,0x83)
    if pc==0x837f:frame=(0x84,0x80)
    for i,v in enumerate(frame,1):r[256+((sp+i)&255)]=v
    p=(rng.randrange(256)&0xc7)|0x20
    c=pc.to_bytes(2,'big')+bytes((rng.randrange(256),x,rng.randrange(256),p,sp,0xa7))
    bankno=6 if index==24 else 3
    rt=bytes((0x1e,sp,255-sp,bankno,0,0))+rng.randbytes(4)+bytes.fromhex('d501');j=bytes([0xb6])*8754
    reads=[]
    if index==24:
     out=bytearray(c);out[:2]=bytes.fromhex('c0f6');out[2]=0x88;out[3]=r[0xdb];out[5]=(p&0x7c)|3
     events=[('mapper',0xfff0,v,0) for v in (3,1,0,0,0)]
     want=(bytes(r),bytes(out),events)
    elif index==25:want=control_model(r,c)
    elif index==26:
     model,reads=prepare_model(r,c,bank);want=model[:3]
    elif index==27:
     want=envelope_model(r,c,bank)
     reads=[0x92e]+list(range(0x6bf,0x6c9))+[e[1]-0x8000 for e in want[2] if e[0]=='resource']
    else:want=progress_model(r,c)
    n.restore((bytes(r),c,j,rt));assert n.run()==1,(pc,sp,channel)
    got=n.snapshot();effects=[e for e in want[2] if e[0]!='ram'];size=SIZES[index]
    journal=(struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',*e[1:]) for e in effects)) if size else b''
    journal+=bytes(size-len(journal));journal+=j[size:]
    run=bytearray(rt);run[6:10]=struct.pack('>HH',index,size)
    if index==24:run[3]=3
    assert got==(want[0],want[1],journal,bytes(run)),(pc,sp,channel)
    assert n.events==want[2] and n.reads==[49152+i for i in reads],(pc,sp,channel,n.reads,reads)
    audio_cases+=1;audio_counts[str(pc)]=audio_counts.get(str(pc),0)+1
    if sp==0:
     n.restore((bytes(r),c,j,rt))
     for address,value in ((RUNTIME+10,b'\0\0'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(CTX+5,b'\x10')):
      n.reject(address,value);rejects+=1
     for event in (1,2,0x100,0xffffffff):n.reject(event=event);rejects+=1
     if channel==0:
      for b in range(256):
       if b!=bankno:n.reject(RUNTIME+3,bytes((b,)));rejects+=1
       if b!=0x1e:n.reject(RUNTIME,bytes((b,)));rejects+=1
     if pc in (0x8085,0x837f,0x86b2):
      offset=3 if pc==0x8085 else 1
      n.reject(RAM+256+((sp+offset)&255),b'\0');rejects+=1
     if pc in (0xc0f6,0x8085):
      for a in (0xcf,0xd0,0xd1):n.reject(RAM+a,b'\1');rejects+=1
     if index in (26,27,28):n.reject(CTX+3,b'\x27');rejects+=1
     if index==27:
      n.reject(RAM+0xc6,b'\x7f');rejects+=1
      n.reject(RAM+0x704+x,b'\7');rejects+=1
 # Corrupt each immutable envelope guard byte in a separate caller allocation.
 # The resource is changed only between calls, never while native code runs.
 for offset in (0x92e,*range(0x6bf,0x6c9)):
  r=bytearray(rng.randbytes(2048));r[0xc5]=0;r[0xc6]=0x80;r[0x72c]=0
  r[0x101]=0x7e;r[0x102]=0x83
  c=bytes.fromhex('86b20028002000a7');rt=bytes.fromhex('1e0010030000baddf00dd501')
  altered=bytearray(resource);altered[49152+offset]^=1
  n.resource=bytes(altered);n.mem.w_block(RESOURCE,n.resource)
  n.restore((bytes(r),c,bytes([0xb6])*8754,rt));n.reject();rejects+=1
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PUBLIC ROM-free host M68EC020',successes=count+fade_cases+yield_cases+audio_cases,audio_operations=audio_cases,audio_by_pc=audio_counts,scheduler_resumes=count,fade_continuations=fade_cases,live_frame_yields=yield_cases,
  inert_rejections=rejects,code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest()),indent=2))
if __name__=='__main__':main()
