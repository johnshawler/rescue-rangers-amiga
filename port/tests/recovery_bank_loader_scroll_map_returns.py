"""Private map-helper original-first external-return and stack-wrap qualification.
The fixture comes from independent original-only continuous execution, not a
replacement for any continuing native chain. No frozen module is changed.
"""
import sys,struct,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_scroll_status_harness import Native,PORT
from recovery_bank_loader_scroll_status_oracle import ControllerBus,REGIONS,RETURNS
from recovery_stage_map_test import log_read
from recovery_test_active_command0e_rom import Ricoh

def main():
 root=Path(sys.argv[1]);state=(root/'map_return.ram.bin').read_bytes();ctx=(root/'map_return.context.bin').read_bytes();runtime=(root/'map_return.runtime.bin').read_bytes();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'map.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_stage_map_region.s')],check=True);n=Native(out.read_bytes(),rom[16:131088])
  cases=0;aliases=[]
  variants=[(p,ctx[6],0xdaad) for p in range(256)]+[(0x24,sp,target) for sp in (0,1,2,127,254,255) for target in (0xdaad,0xc77b,0xe106,0x1234,0,0xffff)]
  for p,sp,target in variants:
   s=bytearray(state)
   for off in range(1,5):s[256+((sp+off)&255)]=state[256+((ctx[6]+off)&255)]
   stored=(target-1)&65535;s[256+((sp+3)&255)]=stored&255;s[256+((sp+4)&255)]=stored>>8
   c=ctx[:5]+bytes((p,sp,ctx[7]));before=(bytes(s),c,b'\xb6'*134638,runtime)
   b=ControllerBus(rom);b.map_bank(runtime[3]);b[:2048]=s;b.events.clear();m=Ricoh(memory=b);m.pc=0xdf97;m.a,m.x,m.y,m.p,m.sp=c[2:7]
   for steps in range(20000):
    last_pc=m.pc;op=b[m.pc];log_read(m,b);m.step()
    if op==0x6c or op==0x60 and m.pc not in RETURNS[100] or not any(a<=m.pc<z for a,z in REGIONS[100]):break
   else:raise AssertionError('map boundary budget')
   # An arbitrary earlier exit must fail, even if it is outside the owned region.
   assert last_pc==0xdd09 and m.sp==(sp+4)&255,(hex(last_pc),hex(m.pc),hex(target),m.sp,sp)
   actual=((b[256+((sp+3)&255)]|b[256+((sp+4)&255)]<<8)+1)&65535
   assert m.pc==actual
   assert m.pc==target,(hex(m.pc),hex(target),sp)
   raw=struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]);n.restore(before);assert n.run()==1;after=n.snapshot()
   assert after[0]==bytes(b[:2048]) and after[1]==raw and n.events==b.events and after[3]==runtime and n.raw_adapter_context is None
   es=[e for e in b.events if e[0]!='ram'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert after[2]==j+b'\xb6'*(134638-len(j))
   reads=[e[1]+65536 if e[1]>=49152 else runtime[3]*16384+e[1]-32768 for e in es];assert n.reads==reads*2;cases+=1
  n.m.cleanup()
 print('PASS',cases,'independent map external-return comparisons; all rawP, six stack-wrap positions and six caller targets, wrapped stack and exact return depth; original RAM/stack aliases',aliases)
if __name__=='__main__':main()
