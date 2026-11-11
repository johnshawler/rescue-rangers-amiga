"""ROM-free scene wrapper guards, metadata and user-mode execution."""
import random,struct
from recovery_scene_continue_harness import *
from recovery_scene_continue_prepare_test import model

def main():
 code=assemble();n=Native(code,bytes(131072));rng=random.Random(0xf3d5);guards=0
 for pc in (0xc5f8,0x9000,0xf3c9,0xc274,0xf3cf,0xf3d2,0xc2a8,0xfe8d,0xf3d5):
  ram=bytearray(rng.randbytes(2048));ram[0x80]=4 if pc==0xfe8d else 2;ram[0x91]=0;ram[0x97]=4;ram[0xb8]=0
  ram[0x82]=0xb0;ram[0x1b3:0x1b5]=bytes.fromhex('d4f3');ram[0x1bc:0x1be]=bytes.fromhex('cef3')
  ctx=pc.to_bytes(2,'big')+bytes((2,0,0,0x24,0xba,0xa7))
  n.mem.w_block(RAM,bytes(ram));n.mem.w_block(CTX,ctx);n.mem.w_block(RUNTIME,bytes.fromhex('1e1f1f020000baddf00dd501'))
  for address,value in [(RUNTIME,b'\0'),(RUNTIME+3,b'\x03'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\0\0'),(CTX+5,b'\x34')]:
   n.reject(address,value);guards+=1
  for event in (1,2,256,0xffffffff):n.reject(event=event);guards+=1
  if pc!=0xfe8d:
   n.reject(RAM+0x91,b'\x01');n.reject(RAM+0x80,b'\x01');guards+=2
  if pc==0xf3cf:n.reject(RAM+0x97,b'\x01');guards+=1
 # One accepted clear for each raw flag combination's canonical physical form,
 # every wrapped SP, and nonzero deferred-audio counters retained.
 for value in range(256):
  ram=bytearray(rng.randbytes(2048));ram[0x80]=2;ram[0x91]=0;ram[0xf6]=value
  ctx=bytes.fromhex('f3d5')+rng.randbytes(3)+bytes(((value&0xcf)|0x20,value,0xa7))
  n.mem.w_block(RAM,bytes(ram));n.mem.w_block(CTX,ctx);n.mem.w_block(RUNTIME,bytes.fromhex('1e1f1f020000baddf00dd501'));n.mem.w_block(JOURNAL,b'\xb6'*134638)
  want=model(ram,ctx);assert n.run()==1
  got=n.snapshot();assert got[:2]==want[:2] and n.events==want[2] and not n.reads
  es=[e for e in want[2] if e[0]=='ppu'];journal=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es)
  assert got[2]==journal+b'\xb6'*(134638-len(journal));assert got[3][6:10]==struct.pack('>HH',78,4382)
  assert got[0][0xf6]==value
 n.m.cleanup();print('PASS',guards,'inert wrapper guards, 256 user-mode full clear/raw flags/wrapped SP/F6 preservation cases')
if __name__=='__main__':main()
