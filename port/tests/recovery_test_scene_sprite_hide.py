"""Declarative scene sprite contract, native bounds/ABI and private ROM oracle."""
import hashlib,random,struct,sys
from recovery_fade_entry_harness import Native,PORT

def model(s,c):
 pc=int.from_bytes(c[:2],'big')
 if pc not in (0xf3cf,0xf3d2) or (pc==0xf3cf and s[151]&3):return None
 r=bytearray(s);q=bytearray(c);events=[];sp=c[6]
 def store(a,v):r[a]=v;events.append((a,v))
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)&255
 push(243);push(209 if pc==0xf3cf else 212)
 if pc==0xf3cf:
  x=s[151]
  addresses=([512] if x==4 else [])+list(range(512+x,768,4))
  for a in addresses:store(a,248)
  sp=(sp+1)&255;lo=r[256+sp];sp=(sp+1)&255;hi=r[256+sp]
  q[:2]=((lo+(hi<<8)+1)&65535).to_bytes(2,'big');q[2:4]=bytes((248,0));q[5]=(c[5]&124)|2|int(x>=4)
 else:q[:2]=bytes.fromhex('ff04')
 q[6]=sp
 return bytes(r),bytes(q),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xf3cf);n=Native('recovery_scene_sprite_hide.s',264);cases=guards=0
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for pc in (0xf3cf,0xf3d2):
  for status in range(256):
   for k in range(256):
    s=bytearray(rng.randbytes(2048));s[151]=(k%64)*4 if pc==0xf3cf else (status+k)%256
    c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((status,k,k));want=model(s,c)
    if private:
     bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=pc;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
     for _ in range(1000):
      ref.step()
      if ref.pc==int.from_bytes(want[1][:2],'big'):break
     else:raise AssertionError('ROM timeout')
     actual=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),[(e[1],e[2]) for e in bus.events]);assert actual==want,('ROM',c.hex(),actual[1].hex(),want[1].hex())
    got=n.run(s,c,rng);j=b''.join(struct.pack('>HBB',at,v,0) for at,v in want[2]);j+=b'\xb6'*(264-len(j));assert got==(want[0],want[1],j,len(want[2]),want[2]),('native',c.hex(),got[1].hex(),want[1].hex());cases+=1
 if not private:
  s=rng.randbytes(2048)
  for pc in range(65536):
   if pc in (0xf3cf,0xf3d2):continue
   c=pc.to_bytes(2,'big')+rng.randbytes(6);assert n.run(s,c,rng)==(s,c,b'\xb6'*264,0xffffffff,[]);guards+=1
  for value in range(256):
   if value%4==0:continue
   s=bytearray(rng.randbytes(2048));s[151]=value;c=bytes.fromhex('f3cf')+rng.randbytes(6)
   assert model(s,c) is None and n.run(s,c,rng)==(s,c,b'\xb6'*264,0xffffffff,[]);guards+=1
 print('Binary',len(n.code),hashlib.sha256(n.code).hexdigest());n.close();print('PASS',cases,'ROM' if private else 'ROM-free','cases;',guards,'inert guards; full RAM/raw context/ordered stores/ABI/bounds/wrapped stack.')
if __name__=='__main__':main()
