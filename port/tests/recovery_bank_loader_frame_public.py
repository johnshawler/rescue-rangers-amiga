"""ROM-free fixed player-state indirect dispatch model and atomic guards."""
import os,random,struct,subprocess,tempfile
from pathlib import Path
from recovery_bank_loader_frame_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def model(r,c,resource):
 r=bytearray(r);a,x,y,p,sp=c[2:7];events=[]
 def nz(v):
  nonlocal p
  p=(p&125)|(128 if v&128 else 0)|(2 if v==0 else 0)
 def store(at,v):r[at]=v;events.append(('ram',at,v))
 y=r[0x56+x];nz(y)
 if y:
  a=r[0x400+x]&64;nz(a);store(0,a);a=(r[0x380+y]&191)|r[0];nz(a);store(0x380+y,a)
 a=r[0x54+x];p=(p&254)|int(a>=6);nz((a-6)&255)
 if a!=6:
  a=204;nz(a);store(0x530+x,a);a=1;nz(a);store(0x540+x,a)
 a=0;nz(a);store(0x52+x,a);y=r[0x54+x];nz(y)
 for at,z in ((0xc926+y,0),(0xc933+y,1)):
  a=resource[65536+at];events.append(('resource',at,a,0));nz(a);store(z,a)
 pc=r[0]|r[1]<<8
 return bytes(r),struct.pack('>H6B',pc,a,x,y,p,sp,c[7]),events

def main():
 rng=random.Random(135);resource=rng.randbytes(131072)
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'frame.bin';subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_bank_loader_frame_region.s')],check=True);n=Native(out.read_bytes(),resource)
  for k in range(256):
   r=bytearray(rng.randbytes(2048));x=k&1;r[0x54+x]=k;c=struct.pack('>H6B',0xc8ee,rng.randrange(256),x,0,k,k,0xa7);want=model(r,c,resource)
   def install():
    n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(RUNTIME,bytes.fromhex('1e0010050000baddf00dd501'));n.mem.w_block(JOURNAL,b'\xb6'*134638)
   install();assert n.run()==1;assert n.snapshot()[:2]==want[:2] and n.events==want[2],k
   es=[e for e in want[2] if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es)
   assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[65536+e[1] for e in es]*2
   for at,data in ((RUNTIME,b'\x00'),(RUNTIME+3,b'\x08'),(RUNTIME+4,b'\x01'),(RUNTIME+10,b'\0\0'),(CTX,b'\x12\x34')):
    install();n.mem.w_block(at,data);before=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==before and not n.events and not n.reads
  n.m.cleanup()
 print('PASS frame public256 indirect table models,1280 inert guards; targets are data, never instruction fetches')
if __name__=='__main__':main()
