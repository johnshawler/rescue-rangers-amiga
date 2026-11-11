"""Public static dialogue guards/JSR proof; --rom adds randomized original slices."""
import random,struct,hashlib,sys,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_dialogue_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def code_for(name):
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'routine.bin'
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src'/('recovery_bank_loader_dialogue_'+name+'.s'))],check=True)
  return out.read_bytes()

def install(n,r,c):
 n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638);n.mem.w_block(RUNTIME,bytes.fromhex('1e0d0d020000baddf00dd501'))

def main():
 private='--rom' in sys.argv;rng=random.Random(0x92ac);guards=cases=0
 resource=bytes(131072)
 if private:
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411';resource=rom[16:131088]
 n=Native(code_for('region'),resource)
 for pc in (0x9475,0x9478,0x947b):
  for k in range(256):
   r=bytearray(rng.randbytes(2048));r[49]=11;c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((k,k,0xa7));want=bytearray(r);sp=k;e=[]
   for v in ((pc+2)>>8,(pc+2)&255):want[256+sp]=v;e.append(('ram',256+sp,v));sp=(sp-1)&255
   cc=b'\xff\x04'+c[2:6]+bytes((sp,c[7]));install(n,r,c);assert n.run()==1
   got=n.snapshot();assert got[:2]==(bytes(want),cc) and n.events==e and not n.reads
   assert got[2]==b'\0\0'+b'\xb6'*134636;cases+=1
 if not private:
  for pc in range(65536):
   if pc in (0x92ac,0x9475,0x9478,0x947b,0x947e):continue
   r=bytearray(rng.randbytes(2048));r[49]=11;c=pc.to_bytes(2,'big')+rng.randbytes(6);install(n,r,c);before=n.snapshot()
   assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
  for stage in range(256):
   if stage==11:continue
   r=bytearray(rng.randbytes(2048));r[49]=stage;c=bytes.fromhex('92ac00000024b9a7');install(n,r,c);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events;guards+=1
  # Force dialogue continuation to read text from forbidden CPU IO via real stack return.
  r=bytearray(2048);r[49]=11;r[0x1ba:0x1bc]=bytes.fromhex('e292');r[16]=0
  rr=bytearray(131072);rr[0x94c2]=0;rr[0x9536]=0;rr[0x954a]=0x20
  bad=Native(code_for('region'),rr);c=bytes.fromhex('947e00000024b9a7');install(bad,r,c);before=bad.snapshot();assert bad.run()==0xffffffff and bad.snapshot()==before and not bad.events;bad.m.cleanup();guards+=1
 n.m.cleanup()
 if private:
  from recovery_bank_loader_dialogue_oracle import ControllerBus,log_resource
  from recovery_test_startup_fade_continue import CPU
  for name,entries in [('region',(0x92ac,0x9475,0x9478,0x947b,0x947e)),('bridge',(0x911c,0x911f,0xc60a))]:
   n=Native(code_for(name),resource);index=96 if name=='region' else 99
   for k in range(384):
    pc=entries[k%len(entries)];r=bytearray(rng.randbytes(2048));r[49]=11;r[0x1ba:0x1bc]=bytes.fromhex('1e91');r[0x1bc:0x1c0]=bytes.fromhex('09c60000')
    r[16]=0;r[17]=0;r[18]=0;r[19]=23;r[12]=0;r[13]=0x96;r[14]=3
    if pc==0x947e:r[0x1ba:0x1bc]=bytes.fromhex('2194')
    c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((k&255,0xb9,0xa7))
    b=ControllerBus(rom);b.map_bank(2);b[:2048]=r;b.events.clear();m=CPU(memory=b);m.pc=pc;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for _ in range(200000):
     log_resource(m,b,index);m.step()
     if m.pc in (0xff04,0xf379,0x911f,0xc60a,0xc6b5,0x92ac):break
    else:raise AssertionError('reference safety bound')
    want=bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)
    install(n,r,c);assert n.run()==1;assert n.snapshot()[:2]==want and n.events==b.events,('original',name,c.hex(),n.snapshot()[1].hex(),want[1].hex())
    semantic=[(e[1] if e[1]<0xc000 else e[1]+0x10000) for e in b.events if e[0]=='resource'];assert n.reads==semantic*2;cases+=1
   n.m.cleanup()
 print('PASS dialogue static contract',cases,'cases;',guards,'inert guards;', 'private' if private else 'public')
if __name__=='__main__':main()
