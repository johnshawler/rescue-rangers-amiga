"""Public native USER-mode contracts; --rom also compares original instructions."""
import hashlib,random,struct,sys,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME,CODE
from recovery_bank_loader_models import model
from recovery_bank_loader_models import validation_reads
SPECS={'restore':(0xff53,79),'prefix':(0x9003,80),'resource':(0x8000,81),'second':(0x9034,82),'assets':(0x9039,83),'fade':(0xf3e5,84)}

def assemble(name):
 source=' movem.l a3,-(sp)\n movea.l a5,a3\n adda.l #32768,a3\n bsr.w recovery_bank_loader_'+name+'\n movem.l (sp)+,a3\n rts\n'
 source+=(PORT/'src'/('recovery_bank_loader_'+name+'.s')).read_text()
 with tempfile.TemporaryDirectory() as t:
  src=Path(t)/'test.s';out=Path(t)/'test.bin';src.write_text(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True)
  return out.read_bytes()

def check(n,s,c,r,want):
 n.mem.w_block(RAM,s);n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,b'\xb6'*134638)
 before=n.snapshot();ret=n.run();got=n.snapshot()
 if want is None:
  assert ret==0xffffffff and got==before and not n.events
  return
 assert ret==1,(c.hex(),ret)
 assert got[:2]==want[:2] and n.events==want[2],('effects',c.hex(),got[1].hex(),want[1].hex(),n.events,want[2])
 effects=[e for e in want[2] if e[0]!='ram']
 if effects:
  journal=struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',e[1],e[2],2 if e[0]=='ppu' and e[3]==0 else e[3]) for e in effects)
  assert got[2]==journal+b'\xb6'*(134638-len(journal))
 else:assert got[2]==before[2]
 pre=validation_reads(r,c[3]) if c[:2]==b'\x80\x00' else []
 assert n.reads==[32768+i for i in pre]+[32768+e[1]-0x8000 for e in effects if e[0]=='resource']

def original(rom,s,c,want,index):
 if want is None:return
 from recovery_bank_loader_oracle import ControllerBus,log_resource
 from recovery_test_startup_fade_continue import CPU
 bus=ControllerBus(rom);bus.map_bank(2);bus[:2048]=s;bus.events.clear()
 cpu=CPU(memory=bus);cpu.pc=int.from_bytes(c[:2],'big');cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=c[2:7]
 target=int.from_bytes(want[1][:2],'big')
 for _ in range(100000):
  log_resource(cpu,bus,index);cpu.step()
  if cpu.pc==target:break
 else:raise AssertionError('original bound')
 actual=bytes(bus[:2048]),struct.pack('>H6B',cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,c[7]),bus.events
 assert actual==want,('original',c.hex(),actual[1].hex(),want[1].hex(),actual[2],want[2])

def main():
 private='--rom' in sys.argv;rng=random.Random(0xff539003);cases=guards=0
 if private:
  rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for name,(pc,index) in SPECS.items():
  code=assemble(name)
  for k in range(256):
   r=rom[32784:49168] if private else rng.randbytes(16384)
   s=bytearray(rng.randbytes(2048));s[0xf6]=0;s[0x31]=11 if name=='assets' else k
   sp=k;stagepc=pc
   if name=='fade':stagepc=(0xf3e5,0xf3f1,0x910c)[k%3];s[0x31]=11
   c=stagepc.to_bytes(2,'big')+bytes((k,(4,8,9)[k%3] if private else k,127,k,sp,0xa7))
   if name=='resource' and not private:
    r=bytearray(r);ptr=0x91f8;r[0x3d+c[3]]=ptr&255;r[0x47+c[3]]=ptr>>8
    count=k;n=count+1 if count<=128 else 1
    payload=bytes((0x20,k,count))+rng.randbytes(n)+bytes((0x23,0,2,1,2,3,0))
    r[ptr-0x8000:ptr-0x8000+len(payload)]=payload;r=bytes(r)
   full=bytes(32768)+r+bytes(81920);n=Native(code,full)
   want=model(s,c,r)
   if private:original(rom,s,c,want,index)
   check(n,bytes(s),c,r,want);cases+=want is not None;guards+=want is None
   if name=='restore':
    s[0xf6]=(k%255)+1;check(n,bytes(s),c,r,None);guards+=1
   if name=='assets':
    s[0x31]=12;check(n,bytes(s),c,r,None);guards+=1
   n.m.cleanup()
  print('PASS',name,'private' if private else 'public',hashlib.sha256(code).hexdigest(),flush=True)
 # Generalized resource pointer/budget failures must be inert and bounded.
 if not private:
  code=assemble('resource');s=bytes(2048);c=bytes.fromhex('8000000000ff00a7')
  for ptr in (0,0x7fff,0xbffe,0xbfff,0xc000,0xffff,0x8000):
   r=bytearray([1]*16384);r[0x3d]=ptr&255;r[0x47]=ptr>>8;r=bytes(r)
   n=Native(code,bytes(32768)+r+bytes(81920));check(n,s,c,r,None);n.m.cleanup();guards+=1
 print('PASS bank-loader',cases,'full-state/effects cases;',guards,'inert guards')
if __name__=='__main__':main()
