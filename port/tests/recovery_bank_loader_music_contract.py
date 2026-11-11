"""Stage command0 public guards and private original effects/semantic-read proof."""
import random,struct,hashlib,sys,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_music_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def assemble():
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'music.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_bank_loader_stage_music.s')],check=True);return out.read_bytes()

def main():
 private='--rom' in sys.argv;rng=random.Random(134);resource=bytes(131072)
 if private:
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411';resource=rom[16:131088]
 code=assemble();n=Native(code,resource);cases=guards=0
 def install(r,c):
  n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638);n.mem.w_block(RUNTIME,bytes.fromhex('1e0010030000baddf00dd501'))
 for k in range(256):
  r=bytearray(rng.randbytes(2048));r[207]=0;sp=k;r[256+((sp+1)&255)]=0xf2;r[256+((sp+2)&255)]=0xc0;c=bytes.fromhex('800300')+rng.randbytes(2)+bytes((k,sp,0xa7))
  if private:
   from recovery_bank_loader_music_oracle import ControllerBus,log_resource
   from recovery_test_startup_fade_continue import CPU
   b=ControllerBus(rom);b.map_bank(3);b[:2048]=r;b.events.clear();m=CPU(memory=b);m.pc=0x8003;m.a,m.x,m.y,m.p,m.sp=c[2:7]
   for _ in range(10000):
    log_resource(m,b,134);m.step()
    if m.pc==0xc0f3:break
   else:raise AssertionError('reference bound')
   install(r,c);assert n.run()==1
   want=bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)
   assert n.snapshot()[:2]==want and n.events==b.events,('original',c.hex(),n.snapshot()[1].hex(),want[1].hex())
   es=[e for e in b.events if e[0]!='ram'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es)
   assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[49152+e[1]-32768 for e in es if e[0]=='resource']*2;cases+=1
  # Wrong commands, active CF and unsupported entry PCs are inert.
  for pc,a,cf in ((0x8003,(k%255)+1,0),(0x8003,0,(k%255)+1),(0x8002,0,0)):
   rr=bytearray(r);rr[207]=cf;cc=pc.to_bytes(2,'big')+bytes((a,))+c[3:];install(rr,cc);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events;guards+=1
 if not private:
  # Resource count0 leaves original subtract loop nonterminating; reject atomically.
  r=bytearray(2048);c=bytes.fromhex('800300000024bda7');install(r,c);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events;guards+=1
 n.m.cleanup();print('PASS stage music',cases,'original cases',guards,'inert guards', 'private' if private else 'public')
if __name__=='__main__':main()
