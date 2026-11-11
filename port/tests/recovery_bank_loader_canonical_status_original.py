"""Independent Ricoh instruction/interrupt equivalence for live B canonicalization.
No cartridge required, but this is an oracle test and imports private py65 support.
"""
from recovery_test_active_command0e_rom import Ricoh
import random

def snapshot(m):return bytes(m.memory),m.pc,m.a,m.x,m.y,m.p&239,m.sp

def main():
 rng=random.Random(0x6502);cases=0
 for p in range(256):
  for sp in (0,1,2,127,254,255):
   for op in ('PHP','PLP','RTI','NMI','IRQ'):
    mem=bytearray(rng.randbytes(65536));mem[0x8000]={'PHP':0x08,'PLP':0x28,'RTI':0x40}.get(op,0xea);mem[0xfffa:]=bytes.fromhex('009000900090')
    pair=[]
    for status in (p,p&239):
     m=Ricoh(memory=list(mem));m.pc=0x8000;m.sp=sp;m.a=23;m.x=61;m.y=192;m.p=status
     if op=='NMI':m.nmi()
     elif op=='IRQ':m.irq()
     else:m.step()
     pair.append(snapshot(m))
    assert pair[0]==pair[1],(p,sp,op);cases+=1
 print('PASS B canonicalization',cases,'independent PHP/PLP/RTI/NMI/IRQ transitions; identical memory/stack/real flags/registers')
if __name__=='__main__':main()
