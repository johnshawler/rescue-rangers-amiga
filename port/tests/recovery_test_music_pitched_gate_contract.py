#!/usr/bin/env python3
"""ROM-free independent declarative pitched duration/gate and native ABI proof."""
from pathlib import Path
import os, random, subprocess, tempfile
import machine68k
PORT=Path(__file__).resolve().parents[1]
NAMES=('recovery_music_pitched_gate',)
SIZES=(10,)
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000

def adc(a,b,c=0):
    total=a+b+c;r=total&255
    return r,(total>255)| (64 if (~(a^b)&(a^r)&128) else 0)

def contract(state,context,resource,index=0):
    s=bytearray(state);c=bytearray(context);a,x,y,p,sp=c[2:7]
    if c[:2]!=bytes.fromhex('83a0') or not 0x28<=x<=0x2b or p&0x38!=0x20 or a<0x20 or not a&31:return None,[]
    events=[];reads=[];records=[]
    def wr(addr,v):
        s[addr]=v&255;events.append(('ram',addr,v&255))
    def rd(addr):
        v=resource[addr-0x8000];reads.append(addr-0x8000)
        events.append(('resource',addr,v,0));records.append(addr.to_bytes(2,'big')+bytes((v,0)));return v
    def push(v):
        nonlocal sp
        wr(0x100+sp,v);sp=(sp-1)&255
    def pop():
        nonlocal sp
        sp=(sp+1)&255;return s[0x100+sp]
    push(a);slot=(a>>5)-1;f=s[0x730+x];duration=None
    if f&32:
        duration=rd(0x8585+slot)
        if not duration:duration=None;f=0
    if duration is None:
        duration=rd(0x858c+slot)
        if f&16:
            wr(0xc3,duration);wr(0x730+x,s[0x730+x]&0xef)
            duration=(duration+(duration>>1))&255
    y,flags=adc(duration,s[0x738+x]);p=(p&0x2c)|flags
    wr(0x738+x,y);a=pop()&31;push(a);wr(0xc4,y)
    wr(0xc1,s[0x73c+x]);push(0x83);push(0xf3);wr(0xc2,0)
    for _ in range(8):
        lo=s[0xc2];hi=s[0xc1]
        wr(0xc2,lo<<1);wr(0xc1,(hi<<1)|(lo>>7));p&=~1
        if hi&128:
            low,flags=adc(s[0xc2],s[0xc4]);wr(0xc2,low)
            high,flags=adc(s[0xc1],0,flags&1);wr(0xc1,high)
            p=(p&0x2c)|flags
    sp=(sp+2)&255;a=s[0xc1] or 1;wr(0x740+x,a)
    c[:2]=bytes.fromhex('83fd');c[2]=a;c[4]=0;c[5]=(p&0x6d)|(a&128);c[6]=sp
    journal=len(records).to_bytes(2,'big')+b''.join(records)+bytes(8-4*len(records))
    return (bytes(s),bytes(c),events,journal),reads

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

def main():
    check,cleanup=make_checker();rng=random.Random(0x83fd);count=0
    for case in range(16384):
        s=bytearray(rng.randbytes(2048));r=bytearray(rng.randbytes(16384));x=0x28+(case//256)%4
        a=32*(1+case%7)+1+(case//7)%31
        c=bytes((0x83,0xa0,a,x,case&255,(case&0xc7)|32,case&255,case>>8))
        s[0x730+x]=case&255;s[0x73c+x]=(case//64)&255;s[0x738+x]=(case//17)&255
        slot=(a>>5)-1;r[0x585+slot]=0 if case%3==0 else case&255;r[0x58c+slot]=(case//5)&255
        check(bytes(s),c,bytes(r),0);count+=1
    s=bytes(s);r=bytes(r);base=bytearray(c);rejected=0
    for field,values in ((-1,range(65536)),(2,range(256)),(3,range(256)),(5,range(256))):
        for value in values:
            c=bytearray(base)
            if field==-1:c[:2]=value.to_bytes(2,'big')
            else:c[field]=value
            check(s,bytes(c),r,0);rejected+=1
    cleanup();print(f'PASS {count} ROM-free pitched gate cases, {rejected} guard comparisons; ordered effects, global access bounds, native ABI.')
if __name__=='__main__':main()
