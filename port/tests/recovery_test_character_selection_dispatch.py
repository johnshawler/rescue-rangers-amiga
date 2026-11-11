"""Independent declarative dispatch and actual ROM comparison; no cartridge payload."""
import hashlib,random,struct,sys
from recovery_fade_entry_harness import Native,PORT

def model(s,c):
 r=bytearray(s);q=bytearray(c);events=[];pc=int.from_bytes(c[:2],'big');p=c[5];sp=c[6];a=c[2]
 def nz(v,p):return (p&0x7d)|(v&128)|(2 if v==0 else 0)
 def store(at,v):r[at]=v;events.append((at,v))
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)%256
 if pc==0xa089:pc=0xa06c
 elif pc==0xa06c:
  if r[0x14]&16:
   a=r[0x203];p=(p&0x7c)|(a>=40);p=nz((a-40)%256,p);pc=0xa0bb
   if a!=40:
    for x in range(28,-1,-2):
     a=r[0x340+x];push(a);a=r[0x341+x];store(0x340+x,a);sp=(sp+1)%256;a=r[256+sp];store(0x341+x,a)
    q[3]=254
    for at,a in ((0x5a2,0x8d),(0x5a4,0x8a),(0x5a6,0x95),(0x5a8,0x8e)):store(at,a)
    p=nz(a,p)
  elif r[0x14]&3:
   a=r[0x14]&1;q[4]=a;p=nz(a,p);pc=0xa07b
  else:
   a=0;p=nz(a,p);push(0xa0);push(0x88);pc=0xff04
 else:return None
 q[:2]=pc.to_bytes(2,'big');q[2]=a;q[5]=p;q[6]=sp
 return bytes(r),bytes(q),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xa06c);n=Native('recovery_character_selection_dispatch.s',196);cases=guards=0
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for status in range(256):
  for k in range(32):
   pc=0xa089 if k==31 else 0xa06c;s=bytearray(rng.randbytes(2048));s[0x14]=(status+17*k)%256;s[0x203]=(40,136,status,0)[k%4]
   c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((status,(status+17*k)%256,k));want=model(s,c)
   if private:
    bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=pc;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
    for _ in range(1000):
     ref.step()
     if ref.pc==int.from_bytes(want[1][:2],'big'):break
    else:raise AssertionError('ROM timeout')
    actual=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),[(e[1],e[2]) for e in bus.events]);assert actual==want,('ROM',c.hex(),actual[1].hex(),want[1].hex())
   got=n.run(s,c,rng);j=b''.join(struct.pack('>HBB',at,v,0) for at,v in want[2]);assert got==(want[0],want[1],j+b'\xb6'*(196-len(j)),len(want[2]),want[2]),('native',c.hex(),got[1].hex(),want[1].hex());cases+=1
 if not private:
  s=rng.randbytes(2048)
  for pc in range(65536):
   if pc in (0xa06c,0xa089):continue
   c=pc.to_bytes(2,'big')+rng.randbytes(6);assert n.run(s,c,rng)==(s,c,b'\xb6'*196,0xffffffff,[]);guards+=1
 n.close();print('PASS',cases,'ROM' if private else 'ROM-free','cases;',guards,'inert PC guards; full RAM/raw context/stores/journal tails/ABI/bounds/wrapped stack.')
if __name__=='__main__':main()
