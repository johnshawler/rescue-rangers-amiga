"""Public composed candidate scan, metadata and failure invariants."""
from recovery_bank_loader_candidate_scan_harness import *
from recovery_bank_loader_candidate_scan_test import model,ENTRIES

def main():
 n=Native(assemble(),bytes(131072));cases=guards=0
 for entry in ENTRIES:
  for k in range(256):
   s=bytearray(2048);s[0x80]=2;s[5]=3;s[3]=0;s[1]=1;s[256+((k+1)&255)]=0xff;s[256+((k+2)&255)]=0xff;c=struct.pack('>H6B',entry,k,3,2,(k&207)|32,k,0xa7);rt=bytes((30,0,16,k%8,0,0,0xba,0xdd,0xf0,13,0xd5,1));before=(bytes(s),c,b'\xb6'*134638,rt);want=model(s,c,bytes(131072));n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==want[:2] and n.events==want[2] and not n.reads and n.raw_adapter_context is None;assert after[2]==b'\0\0'+before[2][2:] and after[3]==rt[:6]+bytes.fromhex('00990012d501');cases+=1
   for at,v in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0'),(CTX+5,b'\x34'),(RAM+0x80,b'\4'),(RAM+0x91,b'\1')):
    n.restore(before);n.mem.w_block(at,v);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
   for event in (1,2,0xffffffff):
    n.restore(before);assert n.run(event)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
 n.m.cleanup();print('PASS candidate scan full dispatcher',cases,'cases;',guards,'inert guards',flush=True)
if __name__=='__main__':main()
