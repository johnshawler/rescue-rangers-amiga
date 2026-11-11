"""Private actual-dispatch adapter proof, retaining raw helper evidence before mask."""
import sys,struct
from pathlib import Path
from recovery_bank_loader_collision_harness import Native,assemble,PORT,RAM,CTX,JOURNAL,RUNTIME
from recovery_bank_loader_collision_oracle import raw_module_result

def main():
 index=int(sys.argv[2]) if len(sys.argv)>2 else 151;root=Path(sys.argv[1]);base=(root/'default.ram.bin').read_bytes();context=(root/'default.context.bin').read_bytes();runtime=(root/'default.runtime.bin').read_bytes();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();n=Native(assemble(),rom[16:131088]);cases=guards=0
 for k in range(256):
  c=context[:5]+bytes(((k&207)|32,k,0xa7));before=(base,c,b'\xb6'*134638,runtime);raw=raw_module_result(before,rom,index);n.restore(before);assert n.run()==1
  assert n.raw_adapter_context==raw[1] and n.snapshot()[0]==raw[0] and n.events==raw[2]
  canonical=raw[1][:5]+bytes((raw[1][5]&239,))+raw[1][6:]
  assert n.snapshot()[1]==canonical and n.snapshot()[3][:6]==runtime[:6] and n.mem.r16(RUNTIME+6)==index and n.mem.r16(RUNTIME+8)==60002
  es=[e for e in raw[2] if e[0]!='ram'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));cases+=1
  for at,value in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+10,b'\0\0')):
   n.restore(before);n.mem.w_block(at,value);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads and n.raw_adapter_context is None;guards+=1
 n.m.cleanup();print('PASS actual',index,'adapter',cases,'raw-original/module/canonical comparisons;',guards,'whole-dispatch atomic guards')
if __name__=='__main__':main()
