"""Public contracts and optional independent original-ROM title yield/fade proof."""
import hashlib,random,struct,sys
from recovery_fade_entry_harness import Native,PORT

def model(s,c):
 pc=int.from_bytes(c[:2],'big')
 if pc not in (0xc5cb,0xc5ce):return None
 ram=bytearray(s);cc=bytearray(c);events=[];sp=c[6]
 def w(a,v):ram[a]=v;events.append((a,v))
 def push(v):
  nonlocal sp
  w(256+sp,v);sp=(sp-1)&255
 push(0xc5);push(0xcd if pc==0xc5cb else 0xd0)
 if pc==0xc5cb:cc[:2]=b'\xff\x04'
 else:
  for a,v in ((15,48),(13,240),(154,0),(14,4)):w(a,v)
  for y in range(31,-1,-1):w(768+y,ram[800+y])
  for y in range(31,-1,-1):
   old=ram[768+y];v=(old-48)&255
   flags=int(old>=48)|(64 if ((old^48)&(old^v)&128) else 0)
   w(768+y,15 if v&128 else v)
  w(24,255);push(4)
  cc[:6]=b'\xc2\xa5\x04\xf0\xff'+bytes(((c[5]&0x3c)|flags,))
 cc[6]=sp
 return bytes(ram),bytes(cc),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xc5ce);cases=guards=0
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
  assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for pc,source,size in ((0xc5cb,'recovery_title_yield_entry.s',8),(0xc5ce,'recovery_title_fade_entry.s',512)):
  n=Native(source,size)
  def check(s,c):
   want=model(s,c)
   if want and private:
    bus=CompleteBus(rom);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus)
    ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
    target=0xff04 if ref.pc==0xc5cb else 0xc2a5
    for _ in range(1000):
     ref.step()
     if ref.pc==target:break
    else:raise AssertionError('original timeout')
    actual=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),[(e[1],e[2]) for e in bus.events])
    assert actual==want,('model differs from ROM',c.hex(),actual[1].hex(),want[1].hex());want=actual
   got=n.run(s,c,rng)
   if want:
    j=b''.join(struct.pack('>HBB',a,v,0) for a,v in want[2])
    assert got==(want[0],want[1],j+b'\xb6'*(size-len(j)),len(want[2]),want[2]),('native mismatch',c.hex(),got[1].hex(),want[1].hex())
   else:assert got==(s,c,b'\xb6'*size,0xffffffff,[])
  for status in range(256):
   for k in range(16):
    sp=(status+17*k)&255;s=bytearray(rng.randbytes(2048));s[0x320]=k*16+status%16
    c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((status,sp,k));check(bytes(s),c);cases+=1
  if not private:
   s=rng.randbytes(2048)
   for wrong in range(65536):
    if wrong==pc:continue
    # The shared declarative model has two entry cases; this helper accepts one.
    c=wrong.to_bytes(2,'big')+rng.randbytes(6);got=n.run(s,c,rng)
    assert got==(s,c,b'\xb6'*size,0xffffffff,[]);guards+=1
  n.close()
 print(f'PASS {cases} {"original-ROM" if private else "public"} title yield/fade cases; {guards} inert guards; full raw context/RAM, ordered stores, journal tails, ABI and access bounds.')
if __name__=='__main__':main()
