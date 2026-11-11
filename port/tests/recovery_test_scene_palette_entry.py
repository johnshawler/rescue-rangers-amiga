"""Independent C274 contract; assembled native versus original ROM, raw status."""
import hashlib,random,struct,sys
from recovery_fade_entry_harness import Native,PORT

def model(s,c):
 if int.from_bytes(c[:2],'big')!=0xc274:return None
 r=bytearray(s);q=bytearray(c);events=[]
 def store(a,v):r[a]=v;events.append((a,v))
 for a,v in ((15,16),(13,16),(154,0),(14,4)):store(a,v)
 for y in range(31,-1,-1):store(768+y,r[800+y])
 for y in range(31,-1,-1):
  old=r[768+y];v=(old-16)&255
  cv=int(old>=16)|(64 if ((old^16)&(old^v)&128) else 0)
  store(768+y,15 if v&128 else v)
 store(24,255);store(256+c[6],4)
 q[:2]=bytes.fromhex('c2a5');q[2:5]=bytes((4,16,255));q[5]=(c[5]&60)|cv;q[6]=(c[6]-1)&255
 return bytes(r),bytes(q),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xc274);n=Native('recovery_scene_palette_entry.s',280);cases=guards=0
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for status in range(256):
  for k in range(32):
   s=bytearray(rng.randbytes(2048));s[0x320]=status
   c=bytes.fromhex('c274')+rng.randbytes(3)+bytes((status,(status+17*k)%256,k));want=model(s,c)
   if private:
    bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0xc274;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
    for _ in range(1000):
     ref.step()
     if ref.pc==0xc2a5:break
    else:raise AssertionError('ROM timeout')
    actual=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),[(e[1],e[2]) for e in bus.events]);assert actual==want,('ROM',c.hex(),actual[1].hex(),want[1].hex())
   got=n.run(s,c,rng);j=b''.join(struct.pack('>HBB',at,v,0) for at,v in want[2]);assert got==(want[0],want[1],j,len(want[2]),want[2]),('native',c.hex(),got[1].hex(),want[1].hex());cases+=1
 if not private:
  s=rng.randbytes(2048)
  for pc in range(65536):
   if pc==0xc274:continue
   c=pc.to_bytes(2,'big')+rng.randbytes(6);assert n.run(s,c,rng)==(s,c,b'\xb6'*280,0xffffffff,[]);guards+=1
 print('Binary',len(n.code),hashlib.sha256(n.code).hexdigest());n.close();print('PASS',cases,'ROM' if private else 'ROM-free','cases;',guards,'inert PC guards; full RAM/raw context/ordered stores/ABI/bounds/wrapped stack.')
if __name__=='__main__':main()
