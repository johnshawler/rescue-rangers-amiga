"""Public carry-region guards and optional original-first full-state comparisons."""
import os,sys,struct,random,subprocess,tempfile,hashlib
from pathlib import Path
from recovery_bank_loader_collision_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME
ENTRIES=(0xd3e7,0xd40b,0xd435,0xd460)

def main():
 private='--rom' in sys.argv;rng=random.Random(136);resource=bytes(131072);cases=guards=0
 if private:
  from recovery_bank_loader_collision_oracle import ControllerBus,log_resource
  from recovery_test_active_command0e_rom import Ricoh
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411';resource=rom[16:131088]
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'carry.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_bank_loader_carry_region.s')],check=True);n=Native(out.read_bytes(),resource)
  def install(r,c,bank=5):
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638);n.mem.w_block(RUNTIME,bytes((30,0,16,bank))+bytes.fromhex('0000baddf00dd501'))
  for k in range(256):
   r=bytearray(rng.randbytes(2048));r[(0x56+k)&255]=0;r[256+((k+1)&255)]=0x34;r[256+((k+2)&255)]=0x12;c=struct.pack('>H6B',0xd40b,k,k,93,k,k,0xa7);install(r,c);assert n.run()==1
   assert n.snapshot()[:2]==(bytes(r),struct.pack('>H6B',0x1235,k,k,0,(k&125)|2,(k+2)&255,0xa7)) and not n.events and not n.reads;cases+=1
   for at,v in ((CTX,b'\x12\x34'),(RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+10,b'\0\0')):
    install(r,c);n.mem.w_block(at,v);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
  # Low nonzero indices would write the mapper rather than wrapped RAM: reject atomically.
  for y in range(1,24):
   r=bytearray(2048);r[0x56]=y;c=bytes.fromhex('d3e700000024ffa7');install(r,c);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events;guards+=1
  if private:
   for entry in ENTRIES:
    for k in range(256):
     r=bytearray(rng.randbytes(2048));x=k&1;y=(0,24,28,129,130,255)[k%6];r[0x56+x]=y;r[256+((k+1)&255)]=0x34;r[256+((k+2)&255)]=0x12;c=struct.pack('>H6B',entry,k,x,y,k,k,0xa7)
     b=ControllerBus(rom);b.map_bank(k&7);b[:2048]=r;b.events.clear();m=Ricoh(memory=b);m.pc=entry;m.a,m.x,m.y,m.p,m.sp=c[2:7]
     for count in range(10000):
      log_resource(m,b,135);m.step()
      if not 0xd3e7<=m.pc<0xd4a1:break
     else:raise AssertionError('original carry budget')
     install(r,c,k&7);assert n.run()==1,(hex(entry),k);events=[('resource',*e[1:]) if e[0]=='mapper' else e for e in n.events]
     assert n.snapshot()[:2]==(bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)) and events==b.events,(hex(entry),k)
     es=[e for e in b.events if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2;cases+=1
  n.m.cleanup()
  # Same native budget/atomic failure mechanism at a shorter diagnostic bound.
  src=Path(td)/'bounded.s';src.write_text((PORT/'src/recovery_bank_loader_carry_region.s').read_text().replace('movea.l #200000,a4','movea.l #64,a4'))
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);n=Native(out.read_bytes(),resource)
  r=bytearray(2048);r[256:512]=bytes.fromhex('09d4')*128;c=bytes.fromhex('d40b00000024ffa7');install(r,c);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1;n.m.cleanup()
 print('PASS carry',cases,'cases;',guards,'inert guards;', 'private' if private else 'public')
if __name__=='__main__':main()
