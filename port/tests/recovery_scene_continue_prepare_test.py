"""Independent F3D5 preparation contract and private original-instruction oracle."""
import hashlib, random, struct, sys
from recovery_fade_entry_harness import Native, PORT
SIZE=4382 # 1095 PPU records, count word

def model(s,c):
 if c[:2]!=bytes.fromhex('f3d5'):return None
 r=bytearray(s);q=bytearray(c);events=[];sp=c[6]
 def store(a,v):r[a]=v;events.append(('ram',a,v))
 def ppu(a,v,k=1):events.append(('ppu',a,v,k))
 store(256+sp,243);store(256+((sp-1)&255),215)
 store(240,(r[240]+1)&255);store(254,0);ppu(0x2001,0)
 store(256+sp,243);store(256+((sp-1)&255),224)
 store(0,32);store(1,0);store(2,0)
 ppu(0x2002,0,0);ppu(0x2000,r[255]&254);ppu(0x2006,32);ppu(0x2006,0)
 for _ in range(1024):ppu(0x2007,0)
 ppu(0x2006,35);ppu(0x2006,192)
 for _ in range(64):ppu(0x2007,0)
 sp=(sp+1)&255;a=r[256+sp]
 q[:2]=bytes.fromhex('ff53');q[2:5]=bytes((a,0,0));q[5]=(c[5]&60)|(a&128)|(2 if a==0 else 0);q[6]=sp
 return bytes(r),bytes(q),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xf3d5);n=Native('recovery_scene_continue_prepare.s',SIZE)
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 cases=0
 for p in range(256):
  for k in range(8):
   sp=(p+31*k)&255;s=bytearray(rng.randbytes(2048));s[256+((sp+1)&255)]=(p+17*k)&255
   c=bytes.fromhex('f3d5')+rng.randbytes(3)+bytes((p,sp,0xa7));want=model(s,c)
   if private:
    bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0xf3d5;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
    for _ in range(5000):
     ref.step()
     if ref.pc==0xff53:break
    else:raise AssertionError('ROM timeout')
    actual=bytes(bus[:2048]),struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,c[7]),bus.events
    assert actual==want,('ROM',c.hex(),actual[1].hex(),want[1].hex())
   es=[e for e in want[2] if e[0]=='ppu'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es)
   assert len(j)==SIZE
   got=n.run(s,c,rng);assert got==(want[0],want[1],j,1,[(e[1],e[2]) for e in want[2] if e[0]=='ram']),('native',c.hex(),got[1].hex(),want[1].hex())
   cases+=1
 if not private:
  s=rng.randbytes(2048)
  for pc in range(65536):
   if pc==0xf3d5:continue
   c=pc.to_bytes(2,'big')+rng.randbytes(6)
   assert n.run(s,c,rng)==(s,c,b'\xb6'*SIZE,0xffffffff,[])
 print('PASS',cases,'private' if private else 'public','cases; binary',len(n.code),hashlib.sha256(n.code).hexdigest());n.close()
if __name__=='__main__':main()
