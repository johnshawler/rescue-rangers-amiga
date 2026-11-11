"""Genuine internal F941 return shape across all raw status and stack bytes."""
from recovery_bank_loader_player_contact_test import *
def main():
 private='--rom' in sys.argv;rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if private else None;resource=rom[16:131088] if private else bytes([128])*131072;n=Native(assemble(),resource);coverage=set();cases=0
 for entry in (0xf95a,0xf96c):
  for k in range(256):
   r=bytearray(2048);r[0]=k;r[1]=0;r[2]=k;r[16]=0;r[0x4d1]=128 if k&1 else 0;r[0x403]=128
   for i,v in enumerate((0x40,0xf9,0xff,0xff),1):r[256+((k+i)&255)]=v
   c=struct.pack('>H6B',entry,k,3,0,k,k,0xa7);rt=bytes.fromhex('1e0010060000baddf00dd501');before=(bytes(r),c,b'\xb6'*134638,rt);want=model(r,c,resource)
   if private:
    from recovery_bank_loader_player_contact_oracle import ControllerBus,log_resource
    from recovery_test_active_command0e_rom import Ricoh
    b=ControllerBus(rom);b.map_bank(6);b[:2048]=r;b.events.clear();m=Ricoh(memory=b);m.pc=entry;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for step in range(8192):
     old=m.pc;coverage.add(old);log_resource(m,b,154);m.step()
     if old==0xf976 and m.pc!=0xf941 or not 0xf92b<=m.pc<0xf977:break
    else:raise AssertionError('original bound')
    assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events)==want
   n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==want[:2] and n.events==want[2] and after[3]==rt
   es=[e for e in want[2] if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert after[2]==j+before[2][len(j):];assert n.reads==[65536+e[1] for e in es]*2;cases+=1
 if private:assert 0xf941 in coverage
 n.m.cleanup();print('PASS internal F941 return',cases,'private' if private else 'public',flush=True)
if __name__=='__main__':main()
