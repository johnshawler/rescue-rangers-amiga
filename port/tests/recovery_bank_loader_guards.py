"""ROM-free composite inert guards and independent fade-entry raw-status proof."""
import random,struct,sys
from recovery_bank_loader_harness import *
from recovery_test_title_fade_yield import model as title_model
from recovery_bank_loader_contract import original

def main():
 private='--rom' in sys.argv
 if private:
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 code=assemble();n=Native(code,bytes(131072));rng=random.Random(0x9000);guards=0
 for pc in (0xff53,0x9003,0x8000,0x9034,0x9039,0x9041,0xf3e5,0xf3ee,0xc2a8,0xfe8d,0xf3f1,0x910c):
  ram=bytearray(rng.randbytes(2048));ram[128]=4 if pc==0xfe8d else 2;ram[145]=0;ram[49]=11;ram[246]=0
  ram[130]=0xb0;ram[0x1b3:0x1b5]=bytes.fromhex('edf3');ram[0x1bc:0x1be]=bytes.fromhex('f0f3')
  ctx=pc.to_bytes(2,'big')+bytes((2,0,0,0x24,0xba,0xa7))
  n.mem.w_block(RAM,bytes(ram));n.mem.w_block(CTX,ctx);n.mem.w_block(RUNTIME,bytes.fromhex('1e1f1f020000baddf00dd501'))
  for at,v in [(RUNTIME,b'\0'),(RUNTIME+3,b'\x03'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\0\0'),(CTX+5,b'\x34')]:n.reject(at,v);guards+=1
  for event in (1,2,256,0xffffffff):n.reject(event=event);guards+=1
  if pc!=0xfe8d:
   n.reject(RAM+145,b'\x01');n.reject(RAM+128,b'\x01');guards+=2
  if pc==0xff53:
   for f6 in range(1,256):n.reject(RAM+246,bytes((f6,)));guards+=1
   for a in (0,1,3,5,128,255):n.reject(CTX+2,bytes((a,)));guards+=1
 # Actual new F3EE entry, every raw physical status and every wrapped stack.
 for k in range(256):
  ram=bytearray(rng.randbytes(2048));ram[128]=2;ram[145]=0
  c=bytes.fromhex('f3ee')+rng.randbytes(3)+bytes(((k&0xcf)|0x20,k,0xa7))
  # Declarative model uses original F3F0 caller instead of title's C5D0.
  want=title_model(ram,bytes.fromhex('c5ce')+c[2:]);rr,cc,events=want;rr=bytearray(rr)
  events=[(at,0xf3 if j==0 else 0xf0 if j==1 else v) for j,(at,v) in enumerate(events)]
  rr=bytearray(ram)
  for at,v in events:rr[at]=v
  want=bytes(rr),cc,[('ram',a,v) for a,v in events]
  if private:original(rom,ram,c,want,85)
  n.mem.w_block(RAM,bytes(ram));n.mem.w_block(CTX,c);n.mem.w_block(RUNTIME,bytes.fromhex('1e1f1f020000baddf00dd501'));n.mem.w_block(JOURNAL,b'\xb6'*134638)
  assert n.run()==1;got=n.snapshot();assert got[:2]==want[:2] and n.events==want[2] and not n.reads
  assert got[2]==b'\xb6'*134638 and got[3][6:10]==struct.pack('>HH',85,0)
 n.m.cleanup();print('PASS',guards,'inert guards;256 USER-mode fade entry cases', 'and original instructions' if private else '')
if __name__=='__main__':main()
