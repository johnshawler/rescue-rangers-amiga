"""Unchanged production and reduced preflight-budget causal failures."""
from recovery_bank_loader_player_contact_test import *
def main():
 private='--rom' in sys.argv;resource=bytes(131072);r=bytearray(2048);r[256:512]=bytes.fromhex('40f9')*128;c=bytes.fromhex('f96c00030024ffa7');rt=bytes.fromhex('1e0010060000baddf00dd501');before=(bytes(r),c,b'\xb6'*134638,rt)
 n=Native(assemble(),resource);n.restore(before);assert n.run()==0xffffffff and n.snapshot()==before and not n.events and n.reads==[65536+0xf9fc];n.m.cleanup()
 if private:
  from recovery_bank_loader_player_contact_oracle import ControllerBus
  from recovery_test_active_command0e_rom import Ricoh
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();b=ControllerBus(rom);b.map_bank(6);b[:2048]=r;m=Ricoh(memory=b);m.pc=0xf96c;m.a,m.x,m.y,m.p,m.sp=c[2:7]
  for i in range(16384):m.step();assert 0xf92b<=m.pc<0xf977
  print('PASS original cyclic internal-return stack remains owned for16384 instructions')
 source=(PORT/'src/recovery_bank_loader_player_contact_region.s').read_text();assert '#8192,a4' in source
 r=bytearray(2048);r[256]=255;r[257]=255;c=bytes.fromhex('f92b00030024ffa7');before=(bytes(r),c,b'\xb6'*134638,rt)
 n=Native(assemble(),resource);n.restore(before);assert n.run()==1;n.m.cleanup()
 n=Native(assemble(source.replace('#8192,a4','#8,a4')),resource);n.restore(before);assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;n.m.cleanup()
 print('PASS player contact production cyclic and causal reduced-budget rejection',flush=True)
if __name__=='__main__':main()
