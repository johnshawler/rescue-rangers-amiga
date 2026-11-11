#!/usr/bin/env python3
"""PUBLIC ROM-free synthetic contract. Resource bytes are invented, no py65.
Does not read cartridge files, private dumps, or differential results.
"""
from recovery_state_dispatch_palette_harness import *
from test_recovery_music07_contract import expected_result,EXPECTED_JOURNAL,APU

def main():
 code=assemble();assert code==assemble()
 rng=random.Random(0xd512);resource=bytearray(131072)
 # All eight banks deliberately have distinct valid-looking headers. Only
 # the actual supported bank-3 mapping may ever be read or admitted.
 for bank in range(8):
  o=bank*16384;resource[o+0xa00]=8
  resource[o+0xa11:o+0xa13]=b'\x90\x00'
  resource[o+0x1000:o+0x1009]=bytes([0]+[bank+1]*8)
 n=Native(code,resource);passes=rejections=waits=0
 def install(ram,ctx,runtime,resources=resource):
  n.resource=bytes(resources);n.mem.w_block(RESOURCE,n.resource)
  n.mem.w_block(RAM,bytes(ram));n.mem.w_block(CTX,ctx)
  n.mem.w_block(RUNTIME,runtime);n.mem.w_block(JOURNAL,bytes([0xa6])*8754)
 def inert(addr=None,val=None,event=0):
  nonlocal rejections
  n.reject(addr,val,event);rejections+=1
 def fixture(sp=0xb0,p=0x24,pointer=0x9000):
  ram=bytearray(rng.randbytes(2048));ram[0xcf]=0;ram[0xc0]=sp
  ram[0x100+((sp+1)&255)]=0xf2;ram[0x100+((sp+2)&255)]=0xc0
  ctx=bytes([0x80,3,7,0x42,0x61,p,sp,0xa7])
  run=bytes.fromhex('1e0010030000baddf00dd501')
  res=bytearray(resource);o=3*16384;res[o+0xa11:o+0xa13]=pointer.to_bytes(2,'big')
  channels=[(1+sp%8,2),(0,0),(0x93,sp),(0,sp)]
  if 0x8000<=pointer<=0xbff7:
   res[o+pointer-0x8000:o+pointer-0x8000+9]=bytes([0]+[v for pair in reversed(channels) for v in pair])
  return ram,ctx,run,res,channels
 # Every original SP including wrap, varied canonical flags/nesting/header.
 for sp in range(256):
  ram,ctx,run,res,channels=fixture(sp,0x20|((sp&0xcf)))
  install(ram,ctx,run,res)
  assert n.run()==1
  er,ec=expected_result(ram,ctx,0x9000,channels)
  assert n.snapshot()==(er,ec,EXPECTED_JOURNAL+bytes([0xa6])*(8754-30),run[:6]+bytes.fromhex('000c001ed501'))
  assert [e[1:] for e in n.events if e[0]=='apu']==[(a,v,1) for a,v in APU]
  assert n.reads==[3*16384+i for i in [0xa00,0xa11,0xa12,*range(0x1000,0x1009)]]
  passes+=1
 # Both permitted header endpoints, synthetic guard data and return-frame cases.
 for pointer in (0x8000,0xbff7):
  ram,ctx,run,res,channels=fixture(pointer=pointer);install(ram,ctx,run,res)
  assert n.run()==1
  er,ec=expected_result(ram,ctx,pointer,channels)
  assert n.snapshot()[:2]==(er,ec);passes+=1
 ram,ctx,run,res,channels=fixture();install(ram,ctx,run,res)
 for offset,expected in [(0,30),(3,3),(4,0),(5,0)]:
  for value in range(256):
   if value!=expected:inert(RUNTIME+offset,bytes([value]));assert not n.reads
 for p in range(256):
  if p&0x30!=0x20:inert(CTX+5,bytes([p]))
 for address in (RAM+0xcf,RAM+0x1b1,RAM+0x1b2):inert(address,b'\x01')
 for event in (1,2,255,256,0x7fffffff,0xffffffff):inert(event=event)
 inert(RUNTIME+10,b'\0\0')
 for pointer in (0,0x7fff,0xbff8,0xbfff,0xc000,0xffff):
  ram,ctx,run,res,channels=fixture(pointer=pointer);install(ram,ctx,run,res);inert()
 for count in range(8):
  ram,ctx,run,res,channels=fixture();res[3*16384+0xa00]=count
  install(ram,ctx,run,res);inert()
 for header in (1,7,128,255):
  ram,ctx,run,res,channels=fixture();res[3*16384+0x1000]=header
  install(ram,ctx,run,res);inert()
 # Pending palette wait/event selection uses only RAM/context, no resources.
 ram=bytearray(2048);ram[0x18]=255;ram[0x80]=1;ram[0x81]=4;ram[0xff]=0x80
 ctx=bytes.fromhex('fe8d00b800a4b8a7');run=bytes.fromhex('1e0010060000baddf00dd501')
 install(ram,ctx,run);saved=n.snapshot()
 for _ in range(31):
  assert n.run()==0 and n.snapshot()==saved and not n.events and not n.reads;waits+=1
 for event in (0,1):
  for address in (0xf0,0x9a,0x19,0x1a,0x1b,0x1c,0x1d):inert(RAM+address,b'\x01',event)
  inert(RAM+0xff,b'\x00',event);inert(RAM+0x80,b'\x04',event)
  for offset,expected in [(0,30),(3,6),(4,0),(5,0)]:
   for value in range(256):
    if value!=expected:inert(RUNTIME+offset,bytes([value]),event)
  for p in range(256):
   if p&0x30!=0x20:inert(CTX+5,bytes([p]),event)
 for event in (2,255,256,0x80000000,0xffffffff):inert(event=event)
 # Full synthetic palette effects, not merely the result PC/count.
 er=bytearray(ram);events=[]
 for i,value in enumerate((0xfe,0x8d,0xa4,0xb4,0,0xb8,0)):
  address=0x1b8-i;er[address]=value;events.append(('ram',address,value))
 records=[(0x2000,0,1),(0x2002,0,0),(0x2001,0,1),(0x2003,0,1),(0x4014,2,1)]
 events += [('ppu',*record) for record in records]
 er[0x18]=0;events.append(('ram',0x18,0))
 rest=[(0x2002,0,0),(0x2006,0x3f,1),(0x2006,0,1)]+[(0x2007,0,1)]*32
 rest += [(0x2006,0x3f,1)]+[(0x2006,0,1)]*3
 rest += [(0x2002,0,0),(0x2005,0,1),(0x2005,0,1),(0x2001,0,1),(0x2000,0x80,1)]
 records += rest;events += [('ppu',*record) for record in rest]
 for address,value in ((0x92,1),(0x90,255),(0x81,3)):
  er[address]=value;events.append(('ram',address,value))
 journal=struct.pack('>H',49)+b''.join(struct.pack('>HBB',*record) for record in records)+bytes(256)
 assert n.run(1)==1 and not n.reads
 assert n.snapshot()==(bytes(er),bytes.fromhex('c0bf00100026b1a7'),journal+bytes([0xa6])*(8754-454),run[:6]+bytes.fromhex('000b01c6d501'))
 assert n.events==events
 passes+=1
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PUBLIC ROM-free synthetic contract',
  successful_cases=passes,inert_rejections=rejections,delayed_waits=waits,
  code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest()),indent=2))
if __name__=='__main__':main()
