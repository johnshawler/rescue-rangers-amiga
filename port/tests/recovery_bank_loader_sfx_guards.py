"""Public full-dispatch ordinary-command guards and delegation equivalence."""
from recovery_bank_loader_sfx_harness import *

def main():
 code=assemble();resource=bytearray(131072);resource[49152+0xa00]=1;resource[49152+0xa04]=0x90;n=Native(code,resource);cases=guards=0
 for sp in range(256):
  s=bytes(2048);c=bytes.fromhex('800310000024')+bytes((sp,0xa7));rt=bytes.fromhex('1e0010030000baddf00dd501');before=(s,c,b'\xb6'*134638,rt);n.restore(before);assert n.run()==1 and n.mem.r16(RUNTIME+6)==139 and n.mem.r16(RUNTIME+8)==1926 and n.mem.r16(CTX)==0x810d;cases+=1
  for addr,v in ((RUNTIME,b'\0'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0'),(CTX+5,b'\x34')):
   n.restore(before);n.mem.w_block(addr,v);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  for event in (1,2,0xffffffff):
   n.restore(before);saved=n.snapshot();assert n.run(event)==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 n.m.cleanup()
 # Controlled delegate proves exact new wrapper intercepts neither other banks
 # nor the earlier fully translated commands, independent of fallback behavior.
 import tempfile
 with tempfile.TemporaryDirectory() as td:
  src=Path(td)/'scope.s';dest=Path(td)/'scope.bin';src.write_text((PORT/'src/recovery_bank_loader_sfx_dispatch.s').read_text()+'\nrecovery_bank_loader_queue5_dispatch:\n moveq #-7,d0\n rts\n'+(PORT/'src/recovery_bank_loader_sfx_entry.s').read_text());subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(dest),str(src)],check=True);n=Native(dest.read_bytes(),resource)
  for bank in range(256):
   if bank==3:continue
   n.restore(before);n.mem.w8(RUNTIME+3,bank);saved=n.snapshot();assert n.run()==(-7)&0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  for command in (0,7,14,39,*range(240,256)):
   n.restore(before);n.mem.w8(CTX+2,command);saved=n.snapshot();assert n.run()==(-7)&0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  n.m.cleanup()
 print('PASS full SFX dispatcher',cases,'cases;',guards,'inert/delegation checks')
if __name__=='__main__':main()
