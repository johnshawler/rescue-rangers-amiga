"""Private raw-state comparisons across all static frame-region entry points."""
import os,struct,subprocess,tempfile,sys
from pathlib import Path
from recovery_bank_loader_frame_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME
from recovery_bank_loader_frame_oracle import ControllerBus,ENTRIES,log_resource
from recovery_test_startup_fade_continue import CPU

def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();root=Path(sys.argv[1]);ram=(root/'default.ram.bin').read_bytes();runtime=(root/'default.runtime.bin').read_bytes();cases=skipped=0
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'frame.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_bank_loader_frame_region.s')],check=True);n=Native(out.read_bytes(),rom[16:131088])
  for entry in ENTRIES:
   for k in range(0,256,17):
    c=struct.pack('>H6B',entry,k,k&1,k,k,k,0xa7);r=bytearray(ram);r[256+((k+1)&255)]=0xff;r[256+((k+2)&255)]=0x7f
    b=ControllerBus(rom);b.map_bank(5);b[:2048]=r;b.events.clear();m=CPU(memory=b);m.pc=entry;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for count in range(10000):
     pc=m.pc;log_resource(m,b,135);m.step()
     if pc==0xc85e or not any(a<=m.pc<z for a,z in ((0xc21e,0xc235),(0xc2dc,0xc2f7),(0xc77b,0xc926),(0xf379,0xf392))):break
    else:skipped+=1;continue
    n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(RUNTIME,runtime);n.mem.w_block(JOURNAL,b'\xb6'*134638);assert n.run()==1,(hex(entry),k)
    want=bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)
    assert n.snapshot()[:2]==want,(hex(entry),k,n.snapshot()[1].hex(),want[1].hex())
    assert n.events==b.events,(hex(entry),k,n.events,b.events)
    es=[e for e in b.events if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es)
    assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2;cases+=1
  n.m.cleanup()
 print('PASS frame private',cases,'raw-state entry variants;',skipped,'unbounded original variants excluded')
if __name__=='__main__':main()
