"""Source-only negative contracts for new palette, frame-resume and scroll wrappers."""
import struct
from recovery_bank_loader_play_harness import Native,assemble,RAM,CTX,JOURNAL,RUNTIME

def main():
 n=Native(assemble(),bytes(131072));guards=0
 for pc,bank in ((0xe9c9,4),(0xd6a3,6),(0xfe8d,5)):
  r=bytearray(2048);r[0x80]=4 if pc==0xfe8d else 2;r[0x82]=255;r[0x102]=0x47;r[0x103]=0xc8
  def install(p=32):
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,struct.pack('>H6B',pc,0,0,0,p,255,0xa7));n.mem.w_block(JOURNAL,b'\xb6'*134638);n.mem.w_block(RUNTIME,bytes((30,0,16,bank))+bytes.fromhex('0000baddf00dd501'))
  for p in range(256):
   if p&48==32:continue
   install(p);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads and n.raw_adapter_context is None;guards+=1
  for at,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+5,b'\x01'),(RUNTIME+10,b'\0\0')):
   install();n.mem.w_block(at,v);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
  for event in (1,2,256,0xffffffff):
   install();before=n.snapshot();assert n.run(event=event)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
 n.m.cleanup();print('PASS new frame-wrapper',guards,'raw-status/runtime/event atomic guards')
if __name__=='__main__':main()
