#!/usr/bin/env python3
"""ROM-free instrument preparation contract with resource journal and global bounds."""
import random,os,subprocess,tempfile
from pathlib import Path
import machine68k
from recovery_test_music_pitched_gate_contract import PORT,BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK
NAMES=("recovery_music_duration_prepare",)
SIZES=(10,)
def make_checker(oracle=None):
    with tempfile.TemporaryDirectory(prefix='rr-event-contract-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in NAMES)+'\n'.join((PORT/'src'/(n+'.s')).read_text() for n in dict.fromkeys(NAMES)))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
    mem.w_block(CODE,code);mem.w16(STOP,0x60fe)
    rng=random.Random(0x8667859b);guard=bytes(range(16));events=[];reads=[];size=0
    def trace(mode,width,address,value):
        length=1<<width
        if RESOURCE<=address<RESOURCE+16384:
            assert mode=='R' and width==0
            reads.append(address-RESOURCE);return
        if mode=='R':
            assert any(lo<=address and address+length<=hi for lo,hi in ((CODE,CODE+len(code)+8),(STOP,STOP+4),(BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+size),(STACK-256,STACK+4))),('unknown read',width,address)
            return
        assert mode=='W'
        if BASE<=address<BASE+2048:
            assert width==0;events.append(('ram',address-BASE,value));return
        assert any(lo<=address and address+length<=hi for lo,hi in ((CTX,CTX+8),(JOURNAL,JOURNAL+size),(STACK-256,STACK))),('unknown write',width,address)
        if address==JOURNAL:
            assert width==1 and value<=5
            if value:
                at=JOURNAL+2+(value-1)*4
                events.append(('resource',mem.r16(at),mem.r8(at+2),mem.r8(at+3)))
    mem.set_trace_func(trace)
    for mode in ('R','W'):
        for address in (0,0x25000,0x30000,0x90000,0x1fffff):
            try:trace(mode,0,address,0)
            except AssertionError:pass
            else:raise AssertionError('Unmapped access escaped global whitelist')
    def check(state,context,resource,index):
        nonlocal size
        size=SIZES[index];expected,expected_reads=contract(state,context,resource,index)
        if oracle is not None and expected is not None:
            actual=oracle(state,context,index)
            assert actual==expected[:3], ("original/declarative",index,context.hex(),actual[1:],expected[1:3])
        mem.set_trace_mode(False);journal=rng.randbytes(size)
        for address,data in ((BASE,state),(CTX,context),(JOURNAL,journal),(RESOURCE,resource)):
            mem.w_block(address-16,guard+data+guard)
        registers=[rng.getrandbits(32) for _ in range(15)];registers[8:12]=[BASE,CTX,JOURNAL,RESOURCE]
        cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
        for i,value in enumerate(registers):cpu.w_reg(i,value)
        cpu.w_pc(CODE+4*index);events.clear();reads.clear();mem.set_trace_mode(True)
        for _ in range(100):
            cpu.execute(1000)
            if cpu.r_pc()==STOP:break
        else:raise AssertionError('native timeout')
        mem.set_trace_mode(False)
        assert cpu.r_sp()==STACK+4 and [cpu.r_reg(i) for i in range(1,15)]==registers[1:]
        assert cpu.r_reg(0)==(1 if expected else 0xffffffff)
        got=(bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(events),bytes(mem.r_block(JOURNAL,size)))
        assert got==(expected if expected else (state,context,[],journal)),(index,context.hex(),got[1:],None if expected is None else expected[1:])
        assert reads==expected_reads,(reads,expected_reads)
        assert bytes(mem.r_block(RESOURCE,16384))==resource
        for address,length in ((BASE,2048),(CTX,8),(JOURNAL,size),(RESOURCE,16384)):
            assert bytes(mem.r_block(address-16,16))==guard and bytes(mem.r_block(address+length,16))==guard
        return got[:3]
    return check,m.cleanup

def contract(state,ctx,resource,index=0):
 a,x,y,p,sp=ctx[2:7]
 if int.from_bytes(ctx[:2],'big')!=0x8374 or p&0x38!=0x20 or x not in range(0x28,0x2c):return None,[]
 s=bytearray(state);events=[];reads=[];journal=bytearray(10)
 def store(addr,v):s[addr]=v;events.append(('ram',addr,v))
 def nz(v):
  nonlocal p
  p=(p&0x7d)|(v&128)|(2 if not v else 0)
 def push(v):
  nonlocal sp
  store(0x100+sp,v);sp=(sp-1)&255
 def read(addr):
  reads.append(addr-0x8000);v=resource[addr-0x8000];events.append(('resource',addr,v,0))
  n=len(reads);journal[0:2]=n.to_bytes(2,'big');at=2+4*(n-1);journal[at:at+4]=addr.to_bytes(2,'big')+bytes((v,0));return v
 def adc(v,w):
  nonlocal p
  total=v+w+(p&1);r=total&255;p=(p&0x3c)|(total>255)|(64 if (~(v^w)&(v^r)&128) else 0);nz(r);return r
 y=s[0x700+x];nz(y);pc=0x837f
 if y:
  push(0x83);push(0x7b);y=(y-1)&255
  store(0xc3,0)
  for shift in (7,6,5):store(0xc3,y>>shift)
  p&=254;a=adc((y*8)&255,read(0x8a02));store(0xc5,a)
  a=adc(s[0xc3],read(0x8a01));store(0xc6,a);sp=(sp+2)&255
  push(0x83);push(0x7e);pc=0x86b2
 return (bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events,bytes(journal)),reads

def cases(count=65536):
 rng=random.Random(0x867c)
 for i in range(count):
  s=bytearray(rng.randbytes(2048));x=0x28+(i//256)%4;s[0x700+x]=i&255
  c=b'\x83\x74'+bytes((rng.randrange(256),x,rng.randrange(256),(i&0xc7)|32,(i>>8)&255,rng.randrange(256)))
  yield bytes(s),c

def main():
 check,cleanup=make_checker();rng=random.Random(0x8a01);resource=rng.randbytes(16384);count=0
 for s,c in cases():
  # Vary both table bytes, including overflow and carry cases.
  r=bytearray(resource);r[0xa01]=(count>>8)&255;r[0xa02]=count&255
  check(s,c,bytes(r),0);count+=1
 s,c=next(cases());invalid=0
 for pc in range(65536):
  if pc!=0x8374:check(s,pc.to_bytes(2,'big')+c[2:],resource,0);invalid+=1
 for p in range(256):
  if p&0x38!=0x20:check(s,c[:5]+bytes((p,))+c[6:],resource,0);invalid+=1
 for x in range(256):
  if x not in range(0x28,0x2c):check(s,c[:3]+bytes((x,))+c[4:],resource,0);invalid+=1
 cleanup();print(f'PASS {count} ROM-free instrument preparations; {invalid} inert guards; full RAM/context/journal/ABI/global bounds.')
if __name__=='__main__':main()
