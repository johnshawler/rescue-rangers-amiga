"""Public contracts and optional independent original-ROM title menu wait proof."""
import hashlib,random,struct,sys
from recovery_fade_entry_harness import Native,PORT

def model(s,c):
 if c[:2]!=bytes.fromhex('a000') or s[0x14]&0x33:return None
 ram=bytearray(s);cc=bytearray(c);events=[];sp=c[6]
 for v in (0xa0,0x24):
  ram[256+sp]=v;events.append((256+sp,v));sp=(sp-1)&255
 cc[:3]=bytes.fromhex('ff0400');cc[5]=(c[5]&0x7d)|2;cc[6]=sp
 return bytes(ram),bytes(cc),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xc5ce);cases=guards=0
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
  assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for pc,source,size in ((0xa000,'recovery_title_engine_wait.s',8),):
  n=Native(source,size)
  def check(s,c):
   want=model(s,c)
   if want and private:
    bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus)
    ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
    target=0xff04
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
    sp=(status+17*k)&255;s=bytearray(rng.randbytes(2048));s[0x14]=(k*16+status%16)&0xcc
    c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((status,sp,k));check(bytes(s),c);cases+=1
  if not private:
   for inp in range(256):
    s=bytearray(rng.randbytes(2048));s[0x14]=inp;check(bytes(s),bytes.fromhex("a000123456ab00a7"))
   s=rng.randbytes(2048)
   for wrong in range(65536):
    if wrong==pc:continue
    # The shared declarative model has two entry cases; this helper accepts one.
    c=wrong.to_bytes(2,'big')+rng.randbytes(6);got=n.run(s,c,rng)
    assert got==(s,c,b'\xb6'*size,0xffffffff,[]);guards+=1
  n.close()
 print(f'PASS {cases} {"original-ROM" if private else "public"} title menu wait cases; {guards} inert PC guards; plus {0 if private else 256} exhaustive-input checks; full raw context/RAM, ordered stores, journal tails, ABI and access bounds.')
if __name__=='__main__':main()
