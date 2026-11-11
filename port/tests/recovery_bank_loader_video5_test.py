"""Bank5 queued NMI wait/service contracts; optional original-first comparison."""
import sys,random,struct,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_video5_harness import *
from recovery_bank_loader_dialogue_nmi_test import expected

def main():
 private='--rom' in sys.argv;rng=random.Random(0x195);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if private else None;resource=rom[16:131088] if private else bytes(131072);n=Native(assemble(),resource);cases=guards=0
 for k in range(256):
  r=bytearray(rng.randbytes(2048));r[0xf0]=1 if k%16==0 else 0;r[0x9a]=1 if k%16==1 else 0;r[0xf5]=r[0xf6]=0;r[0x80]=1;r[0xff]|=128;r[0x19]=1;r[0x1c]=k&1;r[0x1d]=(k>>1)&1;r[0x18]=k&1;r[0x360:0x463]=b'\xff'*259
  for start in (0,88,128):
   amount=k%17;r[0x360+start:0x363+start]=bytes((0x20,0x40,amount));r[0x363+start:0x364+start+amount]=rng.randbytes(amount+1)
  c=bytes.fromhex('fe8d')+rng.randbytes(3)+bytes(((k&207)|32,k,0xa7));rt=bytes.fromhex('1e0010050000baddf00dd501');before=(bytes(r),c,b'\xb6'*134638,rt);want=expected(r,c);assert want[3]==1
  n.restore(before);assert n.run(0)==0 and n.snapshot()==before and not n.events and not n.reads;cases+=1
  if private:
   from recovery_bank_loader_video5_oracle import ControllerBus
   from recovery_test_active_command0e_rom import Ricoh
   b=ControllerBus(rom);b.map_bank(5);b.mapper.control=30;b.mapper.chr0=0;b.mapper.chr1=16;b.mapper.prg=5;b[:2048]=r;b.events.clear();b.dma.clear();m=Ricoh(memory=b);m.pc=0xfe8d;m.a,m.x,m.y,m.p,m.sp=c[2:7];m.nmi()
   for _ in range(200000):
    m.step()
    if m.pc==0xc0bf:break
   else:raise AssertionError('original NMI bound')
   assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events)==(want[0],want[1],want[4])
  n.restore(before);assert n.run(1)==1;after=n.snapshot();assert after[:3]==want[:3] and n.events==want[4] and not n.reads
  fields=list(rt[:4]);bits=[]
  for e in want[4]:
   if e[0]!='mapper':continue
   a,v=e[1:3]
   if v&128:bits=[];fields[0]|=12
   else:
    bits.append(v&1)
    if len(bits)==5:fields[(a>>13)&3]=sum(bit<<i for i,bit in enumerate(bits));bits=[]
  assert not bits and after[3]==bytes(fields)+bytes.fromhex('00000062ffffd501');cases+=1
  for addr,val in ((RUNTIME,b'\0'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0'),(CTX+5,b'\x34'),(RAM+0xff,b'\0'),(RAM+0xf5,b'\1'),(RAM+0xf6,b'\1')):
   for event in (0,1):
    n.restore(before);n.mem.w_block(addr,val);saved=n.snapshot();assert n.run(event)==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  for event in (2,0xffffffff):
   n.restore(before);assert n.run(event)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
 # Nonterminating script: must reject both waiting and service, never fake wait.
 r=bytearray(r);r[0xf0]=r[0x9a]=0;r[0x360:0x463]=bytes(259);r[0x366]=124;r[0x3e6]=124;r[0x19]=1;r[0x1c]=r[0x1d]=0
 before=(bytes(r),c,b'\xb6'*134638,rt);assert expected(r,c)[3]==0xffffffff
 for event in (0,1):
  n.restore(before);assert n.run(event)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
 # Finite queues whose combined output exceeds the fixed journal are rejected.
 r[0x360:0x463]=bytes([127])*259;r[0x19]=r[0x1c]=1;r[0x1d]=0
 before=(bytes(r),c,b'\xb6'*134638,rt);assert expected(r,c)[3]==0xffffffff
 for event in (0,1):
  n.restore(before);assert n.run(event)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
 n.m.cleanup()
 with tempfile.TemporaryDirectory() as td:
  src=Path(td)/'scope.s';out=Path(td)/'scope.bin'
  src.write_text((PORT/'src/recovery_bank_loader_video5_dispatch.s').read_text()+'\nrecovery_bank_loader_scroll_status_dispatch:\n moveq #-7,d0\n rts\n'+(PORT/'src/recovery_bank_loader_video5_preflight.s').read_text()+(PORT/'src/recovery_bank_loader_dialogue_nmi.s').read_text())
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);n=Native(out.read_bytes(),resource)
  mutations=[(RUNTIME+3,bytes((b,))) for b in range(256) if b!=5]+[(RAM+0x80,bytes((b,))) for b in range(256) if b!=1]+[(RAM+0x19,b'\0'),(CTX,b'\0\0'),(CTX,b'\xfe\x90')]
  for at,value in mutations:
   n.restore(before);n.mem.w_block(at,value);saved=n.snapshot();assert n.run()==(-7)&0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  n.m.cleanup()
 print('PASS bank5 queued NMI' ,cases,'wait/service cases;',guards,'inert guards','private' if private else 'public')
if __name__=='__main__':main()
