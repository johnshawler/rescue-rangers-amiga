"""ROM-free declarative menu models, plus independent original-ROM differentials."""
import hashlib,random,struct,sys
from recovery_fade_entry_harness import Native,PORT
SPECS=((0xa025,'recovery_title_menu_countdown.s',16),(0xa000,'recovery_title_menu_dispatch.s',16),(0xa0bb,'recovery_title_menu_exit.s',256))
def model(s,c):
 r=bytearray(s);q=bytearray(c);events=[];pc=int.from_bytes(c[:2],'big');p=c[5];sp=c[6]
 def store(a,v):r[a]=v;events.append((a,v))
 def nz(v,p):return (p&0x7d)|(v&128)|(2 if v==0 else 0)
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)%256
 if pc==0xa025:
  old=r[0xbe]+256*r[0xbf];new=(old-1)%65536;lo,hi=new%256,new//256
  store(0xbe,lo);store(0xbf,hi)
  # Last SBC consumes low-byte borrow; ORA then overwrites N/Z only.
  p=(p&0x3c)|(1 if old>=1 else 0)|(64 if r[0xbf]==127 and s[0xbf]==128 else 0)
  a=lo|hi;p=nz(a,p);pc=0xa000
  if new==0:a=1;p=nz(a,p);store(0x50,1);store(0xb8,1);pc=0xa0bb
 elif pc==0xa000:
  inp=r[0x14]
  if inp&16:
   a=r[0x50];p=nz(a,p);pc=0xa0bb if a else 0xa05c
  elif inp&35:
   selected=(r[0x50]^1) if inp&32 else (0 if inp&2 else 1)
   store(0x50,selected);q[3]=0x88 if selected else 0x28;store(0x203,q[3]);a=0x27;p=nz(a,p)
   push(0xa0);push(0x54);pc=0xf379
  else:a=0;p=nz(a,p);push(0xa0);push(0x24);pc=0xff04
 elif pc==0xa0bb:
  for x in range(0,256,4):store(0x200+x,0xf8)
  q[3]=0;a=0xf8;p=nz(0,p);sp=(sp+1)%256;lo=r[256+sp];sp=(sp+1)%256;pc=(lo+256*r[256+sp]+1)%65536
 else:return None
 q[:2]=pc.to_bytes(2,'big');q[2]=a;q[5]=p;q[6]=sp
 return bytes(r),bytes(q),events

def main():
 private='--rom' in sys.argv;rng=random.Random(0xa025);cases=guards=0
 if private:
  from recovery_test_startup_fade_continue import CPU
  from recovery_test_resident_startup_resources import CompleteBus
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
  assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for pc,source,size in SPECS:
  n=Native(source,size)
  def check(s,c):
   nonlocal cases
   want=model(s,c)
   if private:
    bus=CompleteBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus)
    ref.pc=pc;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
    for _ in range(1000):
     at=ref.pc;ref.step()
     if (pc==0xa0bb and at==0xa0c8) or (pc!=0xa0bb and ref.pc==int.from_bytes(want[1][:2],'big')):break
    else:raise AssertionError('reference timeout')
    actual=(bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),[(e[1],e[2]) for e in bus.events])
    assert actual==want,('model/ROM',source,c.hex(),actual[1].hex(),want[1].hex());want=actual
   got=n.run(s,c,rng);j=b''.join(struct.pack('>HBB',a,v,0) for a,v in want[2])
   assert got==(want[0],want[1],j+b'\xb6'*(size-len(j)),len(want[2]),want[2]),('native',source,c.hex(),got[1].hex(),want[1].hex())
   cases+=1
  for status in range(256):
   for k in range(16):
    s=bytearray(rng.randbytes(2048));s[0x14]=(status+17*k)%256
    s[0x50]=(0,1,128,255)[k%4]
    timer=(0,1,2,255,256,257,32768,32769,65535,900,899,0x8000,0x80ff,0x8100,0x7fff,0x7f00)[k]
    s[0xbe]=timer%256;s[0xbf]=timer//256
    c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((status,(status+17*k)%256,k));check(bytes(s),c)
  if pc==0xa025:
   for timer in range(65536):
    s=bytearray(rng.randbytes(2048));s[0xbe]=timer%256;s[0xbf]=timer//256
    check(bytes(s),pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((timer%256,(timer//256)%256,0xa7)))
  if not private:
   s=rng.randbytes(2048)
   for wrong in range(65536):
    if wrong==pc:continue
    c=wrong.to_bytes(2,'big')+rng.randbytes(6);got=n.run(s,c,rng)
    assert got==(s,c,b'\xb6'*size,0xffffffff,[]);guards+=1
  n.close()
 print(f'PASS {cases} {"original-ROM" if private else "synthetic"} menu cases; {guards} inert PC guards; complete RAM/raw context, ordered stores/journals/tails, ABI, stack wraps and bounds.')
if __name__=='__main__':main()
