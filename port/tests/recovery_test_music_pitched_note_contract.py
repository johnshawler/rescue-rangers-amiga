#!/usr/bin/env python3
"""ROM-free independent declarative pitched duration/note and native ABI proof."""
from pathlib import Path
import os, random, subprocess, tempfile
import machine68k
PORT=Path(__file__).resolve().parents[1]
NAMES=('recovery_music_pitched_note',)
SIZES=(18,)
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000

def adc(a,b,c=0):
    total=a+b+c;r=total&255
    return r,(total>255)| (64 if (~(a^b)&(a^r)&128) else 0)

def contract(state,context,resource,index=0):
    s=bytearray(state);c=bytearray(context);a,x,y,p,sp=c[2:7];reads=[]
    if c[:2]!=bytes.fromhex('83fd') or not 0x28<=x<=0x2b or p&0x38!=0x20:return None,reads
    note=s[0x100+((sp+1)&255)]
    if not 1<=note<=31:return None,reads
    y=note-1;f=s[0x730+x];need=True
    if f&128 and not s[0x718+x]:need=False
    elif x!=0x28:
        octave=((f+2)&255 if f&8 else f)&7
        reads.append(0x593+octave)
        target=min((y+resource[0x593+octave]+s[0xcb]+s[0x734+x])&255,95)+1
        if s[0x71c+x]==target and f&128:need=False
    pointer=((s[0xc5]|s[0xc6]<<8)+4)&65535
    if need and not 0x8000<=pointer<=0xbfff:return None,reads
    events=[];records=[]
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
    def jsr(low):push(0x84);push(low)
    def ret():
        nonlocal sp
        sp=(sp+2)&255
    def retrigger(force=False):
        if force or s[0x704+x]&8:
            wr(0x708+x,0);wr(0x704+x,s[0x704+x]&0x37)
    def instrument(a):
        wr(0x724+x,a);wr(0x720+x,s[0xc3]);retrigger(rd(pointer)&128)
    a=pop();y=a-1
    if f&128 and not s[0x718+x]:jsr(0x0c);retrigger();ret()
    else:
        if not f&128:
            jsr(0x12);push(y);wr(0x704+x,s[0x704+x]&0xf8)
            if x==0x29:
                wr(0x704+x,s[0x704+x]+1);wr(0x704+x,s[0x704+x]+1)
            wr(0x710+x,int(x==0x29));y=pop();ret()
            if not s[0xcf]&1:
                wr(0xc3,y);wr(0x77c+(x&3),255);y=s[0xc3]
        if x==0x28:
            wr(0xc3,0);a=(y&15)^15;jsr(0x33);instrument(a);ret()
        else:
            wr(0xc4,8);a=f
            if f&8:a,flags=adc(a,2);p=(p&0x2c)|flags
            wr(0xc3,y);octave=a&7;a,flags=adc(s[0xc3],rd(0x8593+octave))
            a,flags=adc(a,s[0xcb]);a,flags=adc(a,s[0x734+x]);p=(p&0x2c)|flags
            jsr(0x59);a=min(a,95);wr(0xc3,a);wr(0xc3,s[0xc3]+1)
            prev=s[0x71c+x]
            if prev and prev==s[0xc3] and f&128:retrigger()
            else:
                if prev and prev!=s[0xc3] and s[0x718+x]:
                    wr(0x718+x,(s[0x718+x]|128) if prev<s[0xc3] else (s[0x718+x]&127))
                    wr(0x704+x,s[0x704+x]|32);a=s[0xc3];y=prev;wr(0xc3,y)
                else:wr(0x704+x,s[0x704+x]&0xdf);a=s[0xc3]
                wr(0x71c+x,a);wr(0xc3,s[0xc3]<<1);y=s[0xc3]
                wr(0xc3,rd(0x8934+y));a=rd(0x8935+y);instrument(a)
            ret()
    y=s[0x730+x];wr(0xc4,(y&64)<<1);a=(y&127)|s[0xc4];wr(0x730+x,a)
    if a&128:a=255;wr(0x740+x,a)
    pc=(pop()|(pop()<<8))+1
    c[:2]=(pc&65535).to_bytes(2,'big');c[2]=a;c[4]=y;c[5]=(p&0x6c)|(a&128)|(2 if not a else 0);c[6]=sp
    journal=len(records).to_bytes(2,'big')+b''.join(records)+bytes(16-4*len(records))
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

def cases(check,resource=None,count=16384):
    rng=random.Random(0x862e)
    for case in range(count):
        s=bytearray(rng.randbytes(2048));r=bytearray(rng.randbytes(16384)) if resource is None else resource;x=0x28+(case//256)%4
        c=bytes((0x83,0xfd,case&255,x,rng.randrange(256),(case&0xc7)|32,case&255,case>>8))
        s[0x100+((c[6]+1)&255)]=1+(case%31);s[0x730+x]=case&255
        ptr=(0x7ffc,0x8000,0xbffb,0x80fc)[case%4];s[0xc5]=ptr&255;s[0xc6]=ptr>>8
        if case%3==0:s[0x718+x]=0
        if case%5==0:s[0x71c+x]=0
        if x!=0x28 and case%7==0:
            f=s[0x730+x];octave=((f+2) if f&8 else f)&7;y=s[0x100+((c[6]+1)&255)]-1
            s[0x71c+x]=min((y+r[0x593+octave]+s[0xcb]+s[0x734+x])&255,95)+1
        check(bytes(s),c,bytes(r),0)
    return bytes(s),c,bytes(r)
def fast_retrigger_cases(check,resource=None):
    """Unused instrument pointers must not reject the genuine no-read branch."""
    r=bytes(resource) if resource is not None else random.Random(0x83fd64).randbytes(16384)
    count=0
    for x in range(0x28,0x2c):
        for sp in (0,1,254,255):
            for pointer in (0,0x7ffb,0xbffc,0xffff):
                state=bytearray(2048);state[0x730+x]=0x80;state[0x704+x]=8
                state[0x718+x]=0;state[0x100+((sp+1)&255)]=1
                state[0xc5]=pointer&255;state[0xc6]=pointer>>8
                context=bytes((0x83,0xfd,0,x,0,0x20,sp,0xa7))
                expected,reads=contract(bytes(state),context,r)
                assert expected is not None and reads==[]
                check(bytes(state),context,r,0);count+=1
    return count
def main():
    check,cleanup=make_checker();s,c,r=cases(check);base=bytearray(c);count=0
    for field,values in ((-1,range(65536)),(3,range(256)),(5,range(256)),(-2,range(256)),(-3,range(65536))):
        for value in values:
            c=bytearray(base);state=bytearray(s)
            if field==-1:c[:2]=value.to_bytes(2,'big')
            elif field==-2:state[0x100+((c[6]+1)&255)]=value
            elif field==-3:state[0xc5]=value&255;state[0xc6]=value>>8;state[0x730+c[3]]=0
            else:c[field]=value
            check(bytes(state),bytes(c),r,0);count+=1
    extra=fast_retrigger_cases(check)
    cleanup();print(f'PASS 16384 ROM-free pitched-note cases plus {extra} out-of-window unused-pointer cases, {count} guard/resource comparisons, full ordered effects, global bounds, native ABI.')
if __name__=='__main__':main()
