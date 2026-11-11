"""Generalized ordinary SFX entry: public model and original-first optional proof."""
import sys,random,struct,tempfile,subprocess,os
from pathlib import Path
from recovery_bank_loader_sfx_harness import Native,PORT,CTX,JOURNAL,RAM,RUNTIME,RESOURCE

def main():
 private='--rom' in sys.argv;rng=random.Random(0x8010);rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes() if private else None
 with tempfile.TemporaryDirectory() as td:
  src=Path(td)/'entry.s';dest=Path(td)/'entry.bin';src.write_text(' movem.l a3,-(sp)\n movea.l a5,a3\n adda.l #49152,a3\n bsr.w recovery_bank_loader_sfx_entry\n movem.l (sp)+,a3\n rts\n'+(PORT/'src/recovery_bank_loader_sfx_entry.s').read_text());subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(dest),str(src)],check=True);code=dest.read_bytes()
 cases=guards=0;max_journal=0
 for selected in ((1,2,17,64,128,239,255,None) if private else (1,2,17,64,128,239,255)):
  count=selected if selected is not None else rom[16+49152+0xa00]
  resource=bytearray(rom[16:131088] if private else rng.randbytes(131072));base=49152;resource[base+0xa00]=count
  # Generic synthetic resource view, not original assets in the public suite.
  if selected is not None:
   for k in range(256):resource[base+0xa03+k]=0 if count==2 else (k*37)&255
  n=Native(code,resource)
  for k in range(256):
   command=k%240;s=bytearray(rng.randbytes(2048));c=bytes.fromhex('8003')+bytes((command,19,23,k,k,0xa7));rt=bytes.fromhex('1e0010030000baddf00dd501');before=(bytes(s),c,b'\xb6'*134638,rt);out=bytearray(s);ctx=bytearray(c);out[0xc0]=(s[0xc0]+1)&255;events=[('ram',0xc0,out[0xc0]),('ram',256+k,0x80),('ram',256+((k-1)&255),0xe5)];out[256+k]=0x80;out[256+((k-1)&255)]=0xe5
   remainder=command%count;x=(remainder*2)&255;reads=[0x8a00]*(2*(command//count)+1)+[0x8a04+x,0x8a03+x]
   for a in reads[:-2]:events.append(('resource',a,count,0))
   hi=resource[base+reads[-2]-0x8000];lo=resource[base+reads[-1]-0x8000]
   for a,v,at in ((reads[-2],hi,0xc1),(reads[-1],lo,0xc2)):events.extend((('resource',a,v,0),('ram',at,v)));out[at]=v
   ctx[:2]=(0x810d if hi|lo else 0x8151).to_bytes(2,'big');ctx[2]=hi|lo;ctx[3]=x;ctx[4]=0 if hi|lo else c[4];ctx[5]=(k&60)|2|(remainder>>7)|(((((remainder+count)^remainder)&((remainder+count)^count)&128)>>1) if command>=count else (k&64));ctx[6]=(k-2)&255
   if private:
    from recovery_bank_loader_sfx_oracle import ControllerBus,log_resource
    from recovery_test_active_command0e_rom import Ricoh
    rr=bytearray(rom);rr[16:131088]=resource;b=ControllerBus(bytes(rr));b.map_bank(3);b[:2048]=s;b.events.clear();m=Ricoh(memory=b);m.pc=0x8003;m.a,m.x,m.y,m.p,m.sp=c[2:7]
    for _ in range(2000):
     log_resource(m,b,139);m.step()
     if m.pc in (0x810d,0x8151):break
    else:raise AssertionError('original budget')
    assert (bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7),b.events)==(bytes(out),bytes(ctx),events),(count,k,struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,0xa7).hex(),ctx.hex(),[(i,a,v) for i,(a,v) in enumerate(zip(b[:2048],out)) if a!=v][:5],b.events[:20],events[:20])
   n.restore(before);assert n.run()==1;assert n.snapshot()[:2]==(bytes(out),bytes(ctx)) and n.events==events and n.snapshot()[3]==rt
   es=[e for e in events if e[0]=='resource'];j=struct.pack('>H',len(es))+b''.join(struct.pack('>HBB',*e[1:]) for e in es);max_journal=max(max_journal,len(j));assert len(j)<=1926 and n.snapshot()[2]==j+b'\xb6'*(134638-len(j));assert n.reads==[base+0xa00]+[base+a-0x8000 for a in reads];cases+=1
  for pc in (0,0xffff,0x8000,0x8004):
   n.restore(before);n.mem.w16(CTX,pc);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  for command in range(240,256):
   n.restore(before);n.mem.w8(CTX+2,command);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and not n.reads;guards+=1
  n.m.cleanup()
 resource[base+0xa00]=0;n=Native(code,resource);n.restore(before);saved=n.snapshot();assert n.run()==0xffffffff and n.snapshot()==saved and not n.events and n.reads==[base+0xa00];n.m.cleanup();guards+=1
 assert max_journal==1926
 print('PASS ordinary SFX entry',cases,'rawP/SP/resource/modulo cases',guards,'inert guards; exact maximum journal',max_journal,'private' if private else 'public')
if __name__=='__main__':main()
