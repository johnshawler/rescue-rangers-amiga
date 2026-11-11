"""ROM-free stage0 finish flow and genuine fade-entry contracts, USER mode."""
import random,struct,os,tempfile,subprocess,sys,hashlib
from pathlib import Path
from recovery_bank_loader_music_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def assemble(name):
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'finish.bin';src=PORT/'src'/('recovery_bank_loader_stage_'+name+'.s')
  if name=='fade_in':
   p=Path(td)/'wrapper.s';p.write_text(' movem.l a2,-(sp)\n suba.w #512,sp\n movea.l sp,a2\n bsr.w recovery_bank_loader_stage_fade_in\n adda.w #512,sp\n movem.l (sp)+,a2\n rts\n'+src.read_text());src=p
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);return out.read_bytes()

def model(r,c):
 s=bytearray(r);q=bytearray(c);e=[];sp=c[6];pc=int.from_bytes(c[:2],'big');a,x,y,p=c[2:6]
 if s[49]!=0 or pc not in (0xe106,0xe10c,0xe10f,0xc262,0xc265,0xc703,0xc617):return None
 def w(at,v):s[at]=v;e.append(('ram',at,v))
 def call(ret):
  nonlocal sp
  w(256+sp,ret>>8);sp=(sp-1)&255;w(256+sp,ret&255);sp=(sp-1)&255
 if pc==0xe106:
  call(0xe108);sp=(sp+2)&255;call(0xe10b);pc=0xc158;a=0;p=(p&124)|128
 elif pc==0xe10c:call(0xe10e);pc=0xff04
 elif pc==0xe10f:
  w(62,0);w(63,0);a=5;p&=124;call(0xc261);pc=0xff53
 elif pc==0xc262:call(0xc264);pc=0x8000
 elif pc==0xc265:pc=0xc26e
 elif pc==0xc703:
  w(110,0);x=s[80]
  while True:
   a=s[0x4f0+x];w(104+x,a);a=s[0x500+x];w(106+x,a);x=(x-1)&255
   if x&128:break
  p=(p&125)|128;sp=(sp+1)&255;lo=s[256+sp];sp=(sp+1)&255;pc=((s[256+sp]<<8|lo)+1)&65535
  if pc==0xc617:pc=0xc77b
 else:pc=0xc77b
 q[:2]=pc.to_bytes(2,'big');q[2:7]=bytes((a,x,y,p,sp));return bytes(s),bytes(q),e

def install(n,r,c):
 n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(RUNTIME,bytes.fromhex('1e0010050000baddf00dd501'));n.mem.w_block(JOURNAL,b'\xb6'*134638)

def main():
 private='--rom' in sys.argv;rng=random.Random(130);cases=guards=0;resource=bytes(131072)
 if private:
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411';resource=rom[16:131088]
 n=Native(assemble('finish'),resource)
 for pc in (0xe106,0xe10c,0xe10f,0xc262,0xc265,0xc703,0xc617):
  for k in range(256):
   r=bytearray(rng.randbytes(2048));r[49]=0;r[80]=k&1;r[256+((k+1)&255)]=0x16;r[256+((k+2)&255)]=0xc6;c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((k,k,0xa7));want=model(r,c)
   if private:
    from recovery_bank_loader_stage_oracle import ControllerBus
    from recovery_test_startup_fade_continue import CPU
    b=ControllerBus(rom);b.map_bank(5);b[:2048]=r;b.events.clear();m=CPU(memory=b);m.pc=pc;m.a,m.x,m.y,m.p,m.sp=c[2:7];target=int.from_bytes(want[1][:2],'big')
    for _ in range(2000):
     m.step()
     if m.pc==target:break
    else:raise AssertionError('original safety bound')
    assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7),b.events)==want
   install(n,r,c);assert n.run()==1;assert n.snapshot()[:2]==want[:2] and n.events==want[2] and not n.reads;assert n.snapshot()[2]==b'\0\0'+b'\xb6'*134636;cases+=1
   r[49]=(k%255)+1;install(n,r,c);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events;guards+=1
 n.m.cleanup()
 from recovery_test_title_fade_yield import model as title_model
 n=Native(assemble('fade_in'),resource)
 for k in range(256):
  r=rng.randbytes(2048);c=bytes.fromhex('c26e')+rng.randbytes(3)+bytes((k,k,0xa7));oldc=bytes.fromhex('c5ce')+c[2:6]+bytes(((k+2)&255,0xa7));rr,cc,events=title_model(r,oldc);events=events[2:];rr=bytearray(r)
  for a,v in events:rr[a]=v
  install(n,r,c);assert n.run()==70;assert n.snapshot()[:2]==(bytes(rr),cc) and n.events==[('ram',a,v) for a,v in events];assert n.snapshot()[2]==b'\xb6'*134638;cases+=1
 n.m.cleanup();print('PASS stage finish',cases,'cases;',guards,'inert guards', 'private' if private else 'public')
if __name__=='__main__':main()
