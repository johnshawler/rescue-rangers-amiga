"""Independent contracts and private-ROM oracle for post-confirmation calls."""
import hashlib,random,struct,sys
from recovery_fade_entry_harness import Native,PORT
ENTRIES=(0xc5f8,0x9000,0xf3c9)

def model(s,c):
 pc=int.from_bytes(c[:2],'big')
 if pc not in ENTRIES:return None
 r=bytearray(s);q=bytearray(c);events=[];sp=c[6];p=c[5];a=c[2]
 def store(at,v):r[at]=v;events.append((at,v))
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)%256
 if pc==0xc5f8:
  a=r[0xbd] if r[0xb8] else 11
  p=(p&0x7d)|(a&128)|(2 if not a else 0)
  store(0x31,a)
  target,ret=(0xc63b,0xc610) if r[0xb8] else (0x9000,0xc609)
 elif pc==0x9000:target,ret=0xf3c9,0x9002
 else:
  a=r[0xf1];p=(p&0x7d)|(a&128)|(2 if not a else 0)
  push(a);target,ret=0xc274,0xf3ce
 push(ret>>8);push(ret&255)
 q[:2]=target.to_bytes(2,'big');q[2]=a;q[5]=p;q[6]=sp
 return bytes(r),bytes(q),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xc5f89000);n=Native('recovery_post_confirmation_entry.s',12);cases=guards=0
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for status in range(256):
  for k in range(32):
   pc=ENTRIES[k%3];s=bytearray(rng.randbytes(2048));s[0xb8]=(0,1,128,255)[k%4];s[0xbd]=(0,128,255,status)[k%4];s[0xf1]=(0,128,255,status)[k%4]
   c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((status,(status+17*k)%256,k));want=model(s,c)
   if private:
    bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=pc;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
    for _ in range(20):
     ref.step()
     if ref.pc==int.from_bytes(want[1][:2],'big'):break
    else:raise AssertionError('ROM timeout')
    actual=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),[(e[1],e[2]) for e in bus.events]);assert actual==want,('ROM',c.hex(),actual[1].hex(),want[1].hex())
   got=n.run(s,c,rng);j=b''.join(struct.pack('>HBB',at,v,0) for at,v in want[2]);assert got==(want[0],want[1],j+b'\xb6'*(12-len(j)),len(want[2]),want[2]),('native',c.hex(),got[1].hex(),want[1].hex());cases+=1
 if not private:
  s=rng.randbytes(2048)
  for pc in range(65536):
   if pc in ENTRIES:continue
   c=pc.to_bytes(2,'big')+rng.randbytes(6);assert n.run(s,c,rng)==(s,c,b'\xb6'*12,0xffffffff,[]);guards+=1
 n.close();print('PASS',cases,'ROM' if private else 'ROM-free','cases;',guards,'inert PC guards; full RAM/raw context/ordered stores/journal tails/ABI/bounds/wrapped stack.')
if __name__=='__main__':main()
