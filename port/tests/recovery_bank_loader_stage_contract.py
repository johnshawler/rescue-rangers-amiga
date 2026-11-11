"""Public stage fixed-video contracts and private original-prefix differential."""
import random,sys,struct,hashlib,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_stage_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME,RESOURCE

def code(name):
 with tempfile.TemporaryDirectory() as td:
  src=PORT/'src'/('recovery_bank_loader_stage_'+name+'.s');out=Path(td)/'native.bin'
  if name=='init':
   p=Path(td)/'init.s';p.write_text(' movem.l a3,-(sp)\n movea.l a5,a3\n adda.l #$10193,a3\n bsr.w recovery_bank_loader_stage_init\n movem.l (sp)+,a3\n rts\n'+src.read_text());src=p
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);return out.read_bytes()

def install(n,r,c,bank=4):
 n.mem.w_block(RAM,bytes(r));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638);n.mem.w_block(RUNTIME,bytes((30,13,13,bank,0,0,0xba,0xdd,0xf0,0x0d,0xd5,1)))

def check(n,r,c,want,reads):
 install(n,r,c);before=n.snapshot();ret=n.run()
 if want is None:assert ret==0xffffffff and n.snapshot()==before and not n.events;return
 assert ret==1 and n.snapshot()[:2]==want[:2] and n.events==want[2],('native',c.hex(),ret,n.snapshot()[1].hex(),want[1].hex(),n.events,want[2])
 e=[e for e in want[2] if e[0]!='ram'];j=len(e).to_bytes(2,'big')+b''.join(struct.pack('>HBB',*e[1:]) for e in e)
 assert n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==reads

def main():
 private='--rom' in sys.argv;rng=random.Random(0xc115);resource=rng.randbytes(131072);cases=guards=0
 if private:
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411';resource=rom[16:131088]
 n=Native(code('fixed'),resource)
 for k in range(256):
  for pc in (0xc14e,0xc158,0xc115):
   r=bytearray(rng.randbytes(2048));sp=k;r[256+((sp+1)&255)]=0x98;r[256+((sp+2)&255)]=0xc1
   c=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((k,sp,0xa7));q=bytearray(c);q[:2]=bytes.fromhex('c199');q[6]=(sp+2)&255;out=bytearray(r);e=[]
   if pc!=0xc115:
    v=0 if pc==0xc14e else 30;out[240]=(r[240]+(1 if not v else -1))&255;out[254]=v;e=[('ram',240,out[240]),('ram',254,v),('ppu',0x2001,v,1)];q[2]=v;q[5]=(k&125)|(2 if not v else 0)
   else:
    count=k;amount=count+1 if count<=128 else 1;r[0x360:0x363]=bytes((32,64,count));r[0x363:0x363+amount]=rng.randbytes(amount);r[0x363+amount]=255;out=bytearray(r);out[25]=0;e=[('ram',25,0),('ppu',0x2006,32,1),('ppu',0x2006,64,1)]+[('ppu',0x2007,r[0x363+i],1) for i in range(amount)];q[2:6]=bytes((255,amount+3,(count-amount)&255,(k&125)|128))
   check(n,r,c,(bytes(out),bytes(q),e),[]);cases+=1
   if private:
    from recovery_bank_loader_stage_oracle import ControllerBus
    from recovery_test_startup_fade_continue import CPU
    b=ControllerBus(rom);b.map_bank(4);b[:2048]=r;b.events.clear();m=CPU(memory=b);m.pc=pc;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for _ in range(10000):
     m.step()
     if m.pc==0xc199:break
    else:raise AssertionError('original bound')
    assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7),b.events)==(bytes(out),bytes(q),e)
 # Nonterminating script and forbidden PC inert copied-state preflight.
 r=bytearray(2048);r[0x360:0x463]=bytes(259);r[0x362]=1;r[0x361]=0 # deterministic cycle not necessarily nonterminating; use all count1 at every offset.
 for i in range(0x360,0x463):r[i]=1
 for pc in (0,0xffff,0xc116,0xe09a):
  c=pc.to_bytes(2,'big')+bytes.fromhex('00112224b9a7');check(n,r,c,None,[]);guards+=1
 n.m.cleanup()
 # Converted existing pointer initializer: synthetic raw status/indices/stack.
 from test_recovery_stage_resource_contract import expected as old_expected
 n=Native(code('init'),resource)
 view=resource[0x10193:0x10338]
 for k in range(256):
  r=bytearray(rng.randbytes(2048));r[246]=0;r[49]=k;c=bytes.fromhex('c6b5')+rng.randbytes(3)+bytes((k,k,0xa7))
  old=old_expected(r,c,view)
  # The old public model returns the legacy uncounted event journal.
  rr,cc,journal,count,stores,reads=old
  ordered=[]
  for at in range(0,count*4,4):
   a,v,kind=struct.unpack('>HBB',journal[at:at+4]);ordered.append(('ram',a,v) if kind==0 else ('resource',a,v,0) if kind==1 else ('mapper',a,v,(r[245]+1)&255))
  check(n,r,c,(rr,cc,ordered),[0x10000+a-0x8000 for a,v in reads]);cases+=1
  r[246]=(k%255)+1;check(n,r,c,None,[]);guards+=1
 n.m.cleanup();print('PASS stage native contract',cases,'cases',guards,'inert guards','private' if private else 'public')
if __name__=='__main__':main()
