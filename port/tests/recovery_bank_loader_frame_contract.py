"""Private initial main-frame slice proof using independently reached stage state."""
import os,sys,struct,hashlib,subprocess,tempfile
from pathlib import Path
from recovery_bank_loader_frame_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def main():
 from recovery_bank_loader_music_oracle import ControllerBus,log_resource
 from recovery_test_startup_fade_continue import CPU
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 root=Path(sys.argv[1]);ram=(root/'default.ram.bin').read_bytes();ctx=(root/'default.context.bin').read_bytes();runtime=(root/'default.runtime.bin').read_bytes()
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'frame.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_bank_loader_frame_region.s')],check=True);n=Native(out.read_bytes(),rom[16:131088])
  for k in range(256):
   c=ctx[:5]+bytes((k,k,0xa7));b=ControllerBus(rom);b.map_bank(5);b[:2048]=ram;b.events.clear();m=CPU(memory=b);m.pc=0xc77b;m.a,m.x,m.y,m.p,m.sp=c[2:7]
   for steps in range(10000):
    log_resource(m,b,134);m.step()
    if not any(a<=m.pc<b for a,b in ((0xc21e,0xc235),(0xc2dc,0xc2f7),(0xc77b,0xc926),(0xf379,0xf392))):break
   else:raise AssertionError('original safety bound')
   n.mem.w_block(RAM,ram);n.mem.w_block(CTX,c);n.mem.w_block(RUNTIME,runtime);n.mem.w_block(JOURNAL,b'\xb6'*134638)
   assert n.run()==1
   want=bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)
   assert n.snapshot()[:2]==want,(k,n.snapshot()[1].hex(),want[1].hex())
   assert n.events==b.events,(k,n.events,b.events)
   es=[e for e in b.events if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2
  n.m.cleanup()
 print('PASS frame initial slice 256 raw flags/stack variants, original reached stage snapshot')
if __name__=='__main__':main()
