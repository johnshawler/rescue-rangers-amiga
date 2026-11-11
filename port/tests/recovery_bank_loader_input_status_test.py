"""Private helper90 raw/canonical publication and cumulative status qualification."""
import sys,struct,random
from pathlib import Path
from recovery_bank_loader_input_harness import Native,assemble,PORT,RAM,CTX,JOURNAL,RUNTIME
from recovery_bank_loader_input_oracle import raw_module_result,ControllerBus
from recovery_object_region_test import Native as RawNative,compare_original
from recovery_test_active_command0e_rom import Ricoh

def main():
 root=Path(sys.argv[1]);base=(root/'before.ram.bin').read_bytes();entry=(root/'before.context.bin').read_bytes();runtime=(root/'before.runtime.bin').read_bytes();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();code=assemble();n=Native(code,rom[16:131088]);cases=guards=0
 for k in range(256):
  s=bytearray(base);s[256+((k+1)&255)]=0x39;s[256+((k+2)&255)]=0xc8
  c=entry[:5]+bytes(((k&207)|32,k,0xa7));before=(bytes(s),c,b'\xb6'*134638,runtime);raw=raw_module_result(before,rom,90);n.restore(before);assert n.run()==1
  assert n.raw_adapter_context==raw[1] and n.snapshot()[0]==raw[0] and n.events==raw[2]
  canonical=raw[1][:5]+bytes((raw[1][5]&239,))+raw[1][6:]
  assert n.snapshot()[1]==canonical and n.snapshot()[3][:6]==runtime[:6] and n.mem.r16(RUNTIME+6)==90 and n.mem.r16(RUNTIME+8)==60002
  es=[e for e in raw[2] if e[0]!='ram'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));cases+=1
  for at,value in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+10,b'\0\0'),(CTX+5,bytes((k|16,)))):
   n.restore(before);n.mem.w_block(at,value);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads and n.raw_adapter_context is None;guards+=1
  n.restore(before);saved=n.snapshot();assert n.run(2)==0xffffffff and n.snapshot()==saved and not n.events and not n.reads and n.raw_adapter_context is None;guards+=1
 n.m.cleanup()
 raw_native=RawNative(rom[16:131088])
 for k in range(256):
  s=bytearray(base);s[256+((k+1)&255)]=0x39;s[256+((k+2)&255)]=0xc8
  # Standalone raw helper keeps every status byte and stack-wrap convention.
  b=ControllerBus(rom);b.map_bank(5);b[:2048]=s;m=Ricoh(memory=b);m.pc=0x8000;m.a,m.x,m.y,m.p,m.sp=entry[2],entry[3],entry[4],k,k
  compare_original(raw_native,b,m)
 raw_native.close()
 print('PASS helper90',cases,'raw-allP/SP and canonical composition cases;',guards,'inert failures;',len(code),'bytes',__import__('hashlib').sha256(code).hexdigest(),flush=True)
 rng=random.Random(0x9030);histories=0
 for p in range(256):
  for sp in (0,1,2,127,254,255):
   initial=bytearray(rng.randbytes(65536));initial[0xfffa:]=bytes.fromhex('009000900090');pair=[]
   for status in (p,p&239):
    m=Ricoh(memory=list(initial));m.pc=0x8000;m.sp=sp;m.a=23;m.x=61;m.y=192;m.p=status;pair.append(m)
   for step,op in enumerate(('PHP','CLC','PLP','NMI','RTI','BRK','RTI','PHP','PLP','IRQ','RTI')):
    for m in pair:
     m.pc=0x8000+step*4
     m.memory[m.pc]={'PHP':8,'CLC':24,'PLP':40,'RTI':64,'BRK':0}.get(op,234)
     if op=='NMI':m.nmi()
     elif op=='IRQ':m.irq()
     else:m.step()
    def snap(m):return bytes(m.memory),m.pc,m.a,m.x,m.y,m.p&239,m.sp
    assert snap(pair[0])==snap(pair[1]),(p,sp,step,op)
   histories+=1
 print('PASS',histories,'cumulative 11-step PHP/PLP/NMI/IRQ/RTI/BRK histories; identical stack/RAM/real flags')
if __name__=='__main__':main()
