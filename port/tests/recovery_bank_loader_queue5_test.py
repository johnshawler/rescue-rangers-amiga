"""Public queue-entry semantics and optional original-first differential tests."""
import sys,random,struct
from recovery_bank_loader_queue5_harness import *

def main():
 private='--rom' in sys.argv;rng=random.Random(0xc0bf05);rom=None;resource=bytes(131072)
 if private:rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();resource=rom[16:131088]
 n=Native(assemble(),resource);cases=guards=0
 for k in range(256):
  for empty in (False,True):
   s=bytearray(rng.randbytes(2048));s[0xf5]=s[0xf6]=0;s[0xdb]=k%8;command=0x88 if empty else (k if k!=0x88 else 0x10);s[0xdc+s[0xdb]]=command
   c=bytes.fromhex('c0bf')+rng.randbytes(3)+bytes(((k&207)|32,k,0xa7));rt=bytes.fromhex('1e0010050000baddf00dd501');before=(bytes(s),c,b'\xb6'*134638,rt)
   out=bytearray(s);ctx=bytearray(c);events=[('mapper',0xfff0,v,0) for v in (3,1,0,0,0)];db=s[0xdb];sp=c[6]
   if empty:
    ctx[:2]=bytes.fromhex('c0f6');ctx[2]=0x88;ctx[3]=db;ctx[5]=(c[5]&124)|3;idx=41
   else:
    writes=((256+sp,command),(0xdc+db,0x88),(0xdb,(db+1)&7),(256+sp,0xc0),(256+((sp-1)&255),0xf2))
    for a,v in writes:out[a]=v;events.append(('ram',a,v))
    ctx[:2]=bytes.fromhex('8003');ctx[2]=command;ctx[3]=db+1;ctx[5]=(c[5]&124)|(2 if command==0 else 0)|(command&128)|(1 if command>=0x88 else 0);ctx[6]=(sp-2)&255;idx=70
   if private:
    from recovery_bank_loader_queue5_oracle import ControllerBus
    from recovery_test_active_command0e_rom import Ricoh
    b=ControllerBus(rom);b.map_bank(5);b[:2048]=s;b.events.clear();m=Ricoh(memory=b);m.pc=0xc0bf;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    target=0xc0f6 if empty else 0x8003
    for _ in range(1000):
     m.step()
     if m.pc==target:break
    else:raise AssertionError('original budget')
    assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7),b.events)==(bytes(out),bytes(ctx),events)
   n.restore(before);assert n.run()==1;after=n.snapshot();assert after[:2]==(bytes(out),bytes(ctx)) and n.events==events and not n.reads
   j=struct.pack('>H',5)+b''.join(struct.pack('>HBB',*e[1:]) for e in events if e[0]=='mapper');assert after[2]==j+b'\xb6'*(134638-len(j));assert after[3]==bytes.fromhex('1e0010030000')+struct.pack('>HH',idx,22)+bytes.fromhex('d501');cases+=1
   for at,val in ((RAM+0xf5,b'\1'),(RAM+0xf6,b'\1'),(RAM+0xdb,b'\10'),(RUNTIME,b'\0'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0'),(CTX+5,b'\x34')):
    n.restore(before);n.mem.w_block(at,val);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads and n.raw_adapter_context is None;guards+=1
   n.restore(before);saved=n.snapshot();assert n.run(1)==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
 n.m.cleanup()
 # Exact wrapper must delegate every non-bank5 case, without touching buffers.
 import tempfile,subprocess
 with tempfile.TemporaryDirectory() as td:
  src=Path(td)/'scope.s';dest=Path(td)/'scope.bin'
  src.write_text((PORT/'src/recovery_bank_loader_queue5_dispatch.s').read_text()+'\nrecovery_bank_loader_input_dispatch:\n moveq #-7,d0\n rts\n'+(PORT/'src/recovery_nmi_audio_entry.s').read_text()+(PORT/'src/recovery_music_empty_queue_entry.s').read_text())
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(dest),str(src)],check=True);n=Native(dest.read_bytes(),bytes(131072))
  for bank in range(256):
   if bank==5:continue
   n.restore(before);n.mem.w8(RUNTIME+3,bank);saved=n.snapshot();assert n.run()==(-7)&0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  n.m.cleanup()
 print('PASS queue5' ,cases,'cases',guards,'inert guards','private' if private else 'public')
if __name__=='__main__':main()
