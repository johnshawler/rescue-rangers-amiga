#!/usr/bin/env python3
"""PRIVATE original-first long-script check; explicit cartridge path required."""
from recovery_state_dispatch_menu_long_contract import cases
from recovery_state_dispatch_menu_harness import *
from recovery_state_dispatch_menu_oracle import ControllerBus,select_boundary,log_resource,SHA
from recovery_state_dispatch_startup_contract import mapper_result
from recovery_test_active_command0e_rom import Ricoh

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--rom',type=Path,required=True)
 rom=parser.parse_args().rom.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 code=assemble();assert code==assemble();n=Native(code,rom[16:131088]);out=[]
 for ordinal,r,c,rt in cases():
  bus=ControllerBus(rom);bus.mapper.control,bus.mapper.chr0,bus.mapper.chr1,bus.mapper.prg=30,31,31,2
  bus.mapper.bits.clear();bus.map_bank(2);bus[:2048]=r;bus.events.clear();bus.dma.clear()
  ref=Ricoh(memory=bus);ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  status,index,target=select_boundary(ref,bus,1);assert (status,index,target)==(1,48,(0xc0bf,))
  ref.nmi()
  for steps in range(400000):
   log_resource(ref,bus,index);ref.step()
   if ref.pc in target:break
  else:raise AssertionError('original long script timeout')
  want=(bytes(bus[:2048]),struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,(ref.p&0xef)|32,ref.sp,0xa7),list(bus.events))
  hardware=[e for e in bus.events if e[0]!='ram'];assert len(hardware)==(33339 if ordinal&1 else 33300)
  journal=struct.pack('>H',len(hardware))+b''.join(struct.pack('>HBB',*e[1:]) for e in hardware)
  assert len(bus.dma)==1;journal+=b'\xb6'*(134382-len(journal))+bus.dma[0]
  runtime=mapper_result(rt,bus.events);runtime[6:10]=struct.pack('>HH',48,65535)
  assert bytes(runtime)==bytes.fromhex('1e03070200000030ffffd501')
  n.restore((bytes(r),c,b'\xb6'*134638,rt));assert n.run(1)==1
  assert n.snapshot()==(want[0],want[1],journal,bytes(runtime))
  assert n.events==want[2] and not n.reads
  assert tuple(runtime[:4])==bus.mapper.snapshot()[:4] and not bus.mapper.bits
  out.append(dict(case=ordinal,records=len(hardware),original_instructions=steps+1,context=want[1].hex(),runtime=bytes(runtime).hex()))
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PRIVATE original-first finite long scripts',code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest(),cases=out),indent=2))
if __name__=='__main__':main()
