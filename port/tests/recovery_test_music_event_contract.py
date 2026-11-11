#!/usr/bin/env python3
"""ROM-free declarative instrument/control/rest contract; synthetic caller resources only."""
from pathlib import Path
import os, random, subprocess, tempfile
import machine68k

PORT=Path(__file__).resolve().parents[1]
NAMES=('recovery_music_event_instrument08','recovery_music_event_command18','recovery_music_event_command09','recovery_music_event_rest')
BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK=0x10000,0x12000,0x13000,0x20000,0x1000,0x800,0x1f0000
SIZES=(22,14,14,10)
COMMANDS=(8,24,9)
DISPATCH=((0x8493,0x8667),(0x84b3,0x86a5),(0x8495,0x84e1))

def nz(a):return (a&128)|(2 if a==0 else 0)
def adc(a,b,c=0):
    total=a+b+c;r=total&255
    return r,(1 if total>255 else 0)|nz(r)|(64 if (~(a^b)&(a^r)&128) else 0)

def contract(state,context,resource,index):
    """Pure architectural transition, not a CPU instruction decoder or captured state."""
    s=bytearray(state);c=bytearray(context);events=[];reads=[];records=[]
    pc=int.from_bytes(c[:2],'big');a,x,y,p,sp=c[2:7]
    pointer=s[0x753]|s[0x757]<<8
    if pc!=0x83a0 or x!=0x2b or p&(0x38 if index in (0,3) else 0x30)!=0x20:
        return None,reads
    if index==3:
        if a not in range(32,256,32):return None,reads
    else:
        if a!=COMMANDS[index] or not 0x8000<=pointer<=0xbfff:return None,reads
        table,target=DISPATCH[index]
        for address,want in ((table,target&255),(table+1,target>>8)):
            reads.append(address-0x8000)
            if resource[address-0x8000]!=want:return None,reads
    def wr(address,value):
        value&=255;s[address]=value;events.append(('ram',address,value))
    def rd(address):
        value=resource[address-0x8000];reads.append(address-0x8000)
        events.append(('resource',address,value,0));records.append(address.to_bytes(2,'big')+bytes((value,0)))
        return value
    def push(value):
        nonlocal sp
        wr(0x100+sp,value);sp=(sp-1)&255
    def pop():
        nonlocal sp
        sp=(sp+1)&255;return s[0x100+sp]
    if index!=3:
        push(0x83);push(0xa6);wr(0xc4,a);push(0x84);push(0x7b)
        wr(0xc1,s[0x753]);wr(0xc2,s[0x757]);operand=rd(pointer)
        wr(0x753,s[0x753]+1)
        if not s[0x753]:wr(0x757,s[0x757]+1)
        sp=(sp+2)&255;wr(0xc3,operand)
        push(0x84);push(0x82);wr(0xc1,pop());wr(0xc2,pop())
        low=rd(table);push(low);high=rd(table+1);wr(0xc2,high);wr(0xc1,pop())
        y=a*2+2
        if index==0:
            wr(0xc3,s[0xc3]+1);a=s[0xc3]
            if a==s[0x72b]:p=(p&0x6c)|3
            else:
                wr(0x72b,a);wr(0x72f,s[0x72f]|8);y=(a-1)&255
                wr(0xc3,0)
                for shift in (1,2,3):wr(0xc3,(y<<shift)>>8)
                low=rd(0x8a02);product=(y*8)&255
                sumlow,flags=adc(product,low);wr(0xc5,sumlow)
                high=rd(0x8a01);a,flags=adc(s[0xc3],high,flags&1);wr(0xc6,a)
                p=(p&0x2c)|flags
        elif index==1:
            a=(s[0x737]&15)|s[0xc3]|0x30;wr(0x737,a);p=(p&0x6c)|nz(a)
        else:
            a=(s[0x75b]&0xf8)|s[0xc3];wr(0x75b,a);p=(p&0x6c)|nz(a)
        sp=(sp+2)&255;pc=0x839d
    else:
        push(a);slot=(a>>5)-1;flags=s[0x75b]
        duration=None
        if flags&0x20:
            duration=rd(0x8585+slot)
            if duration==0:duration=None;flags=0
        if duration is None:
            duration=rd(0x858c+slot)
            if flags&0x10:
                wr(0xc3,duration);wr(0x75b,s[0x75b]&0xef)
                duration=(duration+(duration>>1))&255
        y,flags=adc(duration,s[0x763]);wr(0x763,y)
        pop();push(0x83);push(0xe5);wr(0x72f,(s[0x72f]&0xf8)|3)
        sp=(sp+2)&255;wr(0x76b,255);low=pop();high=pop();pc=((low|high<<8)+1)&65535
        a=255;p=(p&0x2c)|(flags&0x41)|128
    c[:2]=pc.to_bytes(2,'big');c[2:7]=bytes((a,x,y,p,sp))
    journal=len(records).to_bytes(2,'big')+b''.join(records)
    journal+=bytes(SIZES[index]-len(journal))
    return (bytes(s),bytes(c),events,journal),reads

def main():
    with tempfile.TemporaryDirectory(prefix='rr-event-contract-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in NAMES)+'\n'.join((PORT/'src'/(n+'.s')).read_text() for n in NAMES))
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
    cases=0
    for index in range(4):
        for case in range(8192):
            s=bytearray(rng.randbytes(2048));r=bytearray(rng.randbytes(16384))
            for address,target in DISPATCH:r[address-0x8000:address-0x8000+2]=bytes((target&255,target>>8))
            pointer=(0x8000,0x80ff,0xbfff,0xbffe)[case%4] if case<256 else 0x8000+rng.randrange(16384)
            s[0x753]=pointer&255;s[0x757]=pointer>>8
            a=COMMANDS[index] if index!=3 else 32*(1+case%7)
            status=(case&(0xc7 if index in (0,3) else 0xcf))|0x20
            c=bytes((0x83,0xa0,a,0x2b,rng.randrange(256),status,case&255,rng.randrange(256)))
            if index==0:
                # Exhaustive operands, low/high base carry, signed overflow and same-instrument branch.
                r[pointer-0x8000]=case&255
                if case%3==0:s[0x72b]=(r[pointer-0x8000]+1)&255
                r[0xa01]=(case//32)&255;r[0xa02]=(case//8)&255
            if index==3:
                # Every flag byte, duration, zero-special fallback, all return SPs.
                s[0x75b]=case&255
                slot=(a>>5)-1;r[0x585+slot]=0 if case%3==0 else (case//7)&255
                r[0x58c+slot]=(case//5)&255
                # Return PC wrap is explicitly represented, including stack wrap.
                if case%13==0:s[0x100+((c[6]+1)&255)]=255;s[0x100+((c[6]+2)&255)]=255
            check(bytes(s),c,bytes(r),index);cases+=1
    rejected=0
    for index in range(4):
        for case in range(2048):
            s=bytearray(rng.randbytes(2048));r=bytearray(rng.randbytes(16384));s[0x753]=0;s[0x757]=0x80
            for address,target in DISPATCH:r[address-0x8000:address-0x8000+2]=bytes((target&255,target>>8))
            c=bytearray((0x83,0xa0,COMMANDS[index] if index!=3 else 0x80,0x2b,0,0x24,0xab,0))
            field=case%8
            if field==0:c[:2]=(case).to_bytes(2,'big')
            elif field==1:c[3]=0x2a
            elif field==2:c[5]=0x10
            elif field==3:c[2]=0x1f
            elif index in (0,3):c[5]|=8
            elif field==4:s[0x757]=0xc0
            else:r[DISPATCH[index][0]-0x8000+(case%2)]^=255
            check(bytes(s),bytes(c),bytes(r),index);rejected+=1
    m.cleanup()
    print(f'PASS: {cases} ROM-free declarative comparisons, synthetic resources, ordered effects, global access whitelist and native ABI.')
    print(f'PASS: {rejected} ROM-free inert rejection comparisons; no cartridge, CPU oracle, extracts or captured states required.')

if __name__=='__main__':main()
