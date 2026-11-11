"""ROM-free main-frame scheduler138 wrapper with optional original comparison."""
import random,struct,sys,hashlib
from recovery_bank_loader_play_harness import Native,assemble,PORT,RAM,CTX,JOURNAL,RUNTIME
from test_recovery_general_scheduler_contract import expected

def main():
 private='--rom' in sys.argv;resource=bytes(131072);rng=random.Random(138);cases=guards=0
 if private:
  from recovery_test_general_scheduler import Bus,advance
  from py65.devices.mpu6502 import MPU
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411';resource=rom[16:131088]
 n=Native(assemble(),resource)
 for k in range(256):
  r=bytearray(rng.randbytes(2048));r[0x80]=4;r[0x82]=k;r[256+((k+3)&255)]=0x47;r[256+((k+4)&255)]=0xc8;c=bytes.fromhex('fe8d')+rng.randbytes(3)+bytes(((k&207)|32,k,0xa7));pads=(k,k^255);want=expected(r,c,pads)
  if private:
   b=Bus(rom);b.ram[:]=r;b.inputs=pads;b.pos=[0,0];b.events=[];m=MPU(memory=b,pc=0xfe8d);m.a,m.x,m.y,m.p,m.sp=c[2:7];status=advance(m)
   assert (bytes(b.ram),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7),status,b.events)==(want[0],want[1],want[3],want[4])
  def install():
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638);n.mem.w_block(RUNTIME,bytes.fromhex('1e0010050000baddf00dd501'))
  install();assert n.run(pads=pads)==1
  assert n.snapshot()[:2]==want[:2] and n.events==want[4] and not n.reads and n.raw_adapter_context is None
  assert n.snapshot()[2]==want[2]+b'\xb6'*(134638-74) and n.mem.r16(RUNTIME+6)==138 and n.mem.r16(RUNTIME+8)==74;cases+=1
  for at,value in ((RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+10,b'\0\0'),(RAM+256+((k+3)&255),b'\x34')):
   install();n.mem.w_block(at,value);before=n.snapshot();assert n.run(pads=pads)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
  install();before=n.snapshot();assert n.run(event=1,pads=pads)==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
 n.m.cleanup();print('PASS main-frame scheduler138',cases,'all pads/stack cases;',guards,'inert guards;', 'private' if private else 'public')
if __name__=='__main__':main()
