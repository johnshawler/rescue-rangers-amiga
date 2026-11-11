"""Synthetic resource contracts and optional original palette-cycle comparisons."""
import os,sys,struct,random,subprocess,tempfile,hashlib
from pathlib import Path
from recovery_bank_loader_collision_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def main():
 rng=random.Random(137);private='--rom' in sys.argv;resource=bytearray(131072);resource[65536+0xea70:65536+0xea74]=bytes((1,2,0,4));resource[65536+0xea0f:65536+0xea14]=bytes((5,7,8,9,255));cases=guards=0
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'palette.bin';src=PORT/'src/recovery_bank_loader_palette_cycle.s';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);code=out.read_bytes();n=Native(code,bytes(resource))
  def install(r,c):
   n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638);n.mem.w_block(RUNTIME,bytes.fromhex('1e0010040000baddf00dd501'))
  for k in range(256):
   r=bytearray(rng.randbytes(2048));r[0x3d]=k&127;r[256+((k+1)&255)]=0x34;r[256+((k+2)&255)]=0x12;c=struct.pack('>H6B',0xe9c9,0,51,73,k,k,0xa7);install(r,c);assert n.run()==1
   p=(k&125)|(2 if r[0x3d]==0 else 0);assert n.snapshot()[:2]==(bytes(r),struct.pack('>H6B',0x1235,r[0x3d],51,73,p,(k+2)&255,0xa7)) and not n.events and not n.reads;cases+=1
   frame=k&1;r[0x3d]=128;r[0x3e]=2;r[0x3f]=frame;want=bytearray(r);events=[]
   def w(a,v):want[a]=v;events.append(('ram',a,v))
   def read(a):v=resource[65536+a];events.append(('resource',a,v,0));return v
   w(0,0);w(0x3e,3);read(0xea71);w(0x3e,0);w(0x3f,frame+1);read(0xea70)
   if frame:w(0x3f,0)
   read(0xea72+frame);read(0xea0f+(4 if frame else 0))
   if not frame:
    w(0,3)
    for j in range(3):v=read(0xea10+j);w(0x305+j,v);w(0,2-j)
    read(0xea13)
   w(0x18,255);install(r,c);assert n.run()==1;got_events=[('resource',*e[1:]) if e[0]=='mapper' else e for e in n.events]
   assert n.snapshot()[:2]==(bytes(want),struct.pack('>H6B',0x1235,255,4,3 if frame else 8,(k&60)|128,(k+2)&255,0xa7)) and got_events==events,k
   es=[e for e in events if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2;cases+=1
   for at,v in ((CTX,b'\x12\x34'),(RUNTIME,b'\0'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+10,b'\0\0')):
    install(r,c);n.mem.w_block(at,v);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads;guards+=1
  n.m.cleanup()
  if private:
   from recovery_bank_loader_collision_oracle import ControllerBus,log_resource
   from recovery_test_active_command0e_rom import Ricoh
   rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411';prg=rom[16:131088];n=Native(code,prg)
   bases=[];base=0
   while base<31:
    count=prg[65536+0xea70+base];end=base+count+3
    if end>31:break
    bases.append(base);base=end
   assert bases
   for k in range(1024):
    r=bytearray(rng.randbytes(2048));base=bases[k%len(bases)];r[0x3d]=128|base;r[0x3e]=prg[65536+0xea71+base] if k&1 else k&255;r[0x3f]=(k//2)%(prg[65536+0xea70+base]+1);sp=k&255;r[256+((sp+1)&255)]=0x34;r[256+((sp+2)&255)]=0x12;c=struct.pack('>H6B',0xe9c9,0,51,73,k&255,sp,0xa7)
    b=ControllerBus(rom);b.map_bank(4);b[:2048]=r;b.events.clear();m=Ricoh(memory=b);m.pc=0xe9c9;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for step in range(10000):
     log_resource(m,b,135);m.step()
     if m.pc==0x1235:break
    else:raise AssertionError('original palette bound')
    install(r,c);assert n.run()==1;events=[('resource',*e[1:]) if e[0]=='mapper' else e for e in n.events]
    assert n.snapshot()[:2]==(bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7)) and events==b.events,k
    es=[e for e in b.events if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2;cases+=1
   n.m.cleanup()
  # Deterministic malformed stream: prove the actual resource-cap rejection mechanism.
  bounded=Path(td)/'bounded.s';bounded.write_text(src.read_text().replace('#15000','#16'))
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(bounded)],check=True);n=Native(out.read_bytes(),bytes(131072))
  r=bytearray(2048);r[0x3d]=128;c=bytes.fromhex('e9c900000024ffa7');install(r,c);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and len(n.reads)==16;guards+=1;n.m.cleanup()
 print('PASS palette cycle',cases,'cases;',guards,'inert guards;', 'private' if private else 'public')
if __name__=='__main__':main()
