"""Additional candidate-scan causal budget and original cyclic-loop evidence."""
import struct,sys
from recovery_bank_loader_candidate_scan_test import *
def main():
 private='--rom' in sys.argv;resource=bytes(131072);r=bytearray(2048);r[256]=0xff;r[257]=0xff;c=bytes.fromhex('f97700100024ffa7');rt=bytes.fromhex('1e0010060000baddf00dd501');before=(bytes(r),c,b'\xb6'*134638,rt)
 n=Native(assemble(),resource);n.restore(before);assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;n.m.cleanup()
 if private:
  from recovery_bank_loader_candidate_scan_oracle import ControllerBus,log_resource
  from recovery_test_active_command0e_rom import Ricoh
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();b=ControllerBus(rom);b.map_bank(6);b[:2048]=r;m=Ricoh(memory=b);m.pc=0xf977;m.a,m.x,m.y,m.p,m.sp=c[2:7];seen=set()
  for i in range(16384):
   seen.add(m.pc);m.step();assert 0xf977<=m.pc<0xf9f2
  assert m.x==16 and b[5]==16 and 0xf9eb in seen
  print('PASS original X16 cyclic scan remains inside region for16384 instructions')
 source=(PORT/'src/recovery_bank_loader_candidate_scan_region.s').read_text();assert '#8192,a4' in source
 c=bytes.fromhex('f97700030024ffa7');before=(bytes(r),c,b'\xb6'*134638,rt)
 n=Native(assemble(),resource);n.restore(before);assert n.run()==1;n.m.cleanup()
 n=Native(assemble(source.replace('#8192,a4','#8,a4')),resource);n.restore(before);assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;n.m.cleanup()
 print('PASS unchanged production cyclic budget and causal reduced-budget rejection')
if __name__=='__main__':main()
