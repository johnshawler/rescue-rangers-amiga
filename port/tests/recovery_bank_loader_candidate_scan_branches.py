"""All candidate-type paths with varied raw status/stack and live table indexes."""
from recovery_bank_loader_candidate_scan_test import *
def main():
 private='--rom' in sys.argv;rng=random.Random(0xf977);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if private else None;resource=rom[16:131088] if private else rng.randbytes(131072);n=Native(assemble(),resource);coverage=set();cases=0
 for kind in (1,0x60,0x3a,0):
  for k in range(256):
   r=bytearray(2048);r[0x4d2]=128;r[0x402]=128;r[0x4e2]=kind;r[0x422]=k;r[0x575]=k;r[256+((k+1)&255)]=255;r[256+((k+2)&255)]=255;c=struct.pack('>H6B',0xf977,k,5,k,k,k,0xa7);rt=bytes((30,0,16,k%8,0,0,0xba,0xdd,0xf0,13,0xd5,1));before=(bytes(r),c,b'\xb6'*134638,rt);want=model(r,c,resource)
   if private:
    from recovery_bank_loader_candidate_scan_oracle import ControllerBus,log_resource
    from recovery_test_active_command0e_rom import Ricoh
    b=ControllerBus(rom);b.map_bank(k%8);b[:2048]=r;b.events.clear();m=Ricoh(memory=b);m.pc=0xf977;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for step in range(8192):
     old=m.pc;coverage.add(old);log_resource(m,b,153);m.step()
     if old==0xf9f1 or not 0xf977<=m.pc<0xf9f2:break
    else:raise AssertionError('original bound')
    assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events)==want
   n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==want[:2] and n.events==want[2] and after[3]==rt
   es=[e for e in want[2] if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert after[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2;cases+=1
 n.m.cleanup();print('PASS candidate types',cases,'PCs',len(coverage),'private' if private else 'public',flush=True)
if __name__=='__main__':main()
