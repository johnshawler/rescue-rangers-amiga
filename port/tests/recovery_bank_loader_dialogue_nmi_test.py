#!/usr/bin/env python3
"""Invented states and declarative NMI effects, no ROM or reference CPU."""
import random,struct
from recovery_bank_loader_dialogue_nmi_harness import Native

def expected(state,ctx):
    r=bytearray(state);c=bytearray(ctx);out=bytearray(b'\xb6'*134638);effects=[];hw=[]
    if not (r[0xf0]|r[0x9a]):
        total=0
        for flag,start in ((28,128),(29,88),(25,0)):
            if r[flag]:
                count=finite(r,start)
                if count is None:return bytes(r),bytes(c),bytes(out),0xffffffff,[]
                total+=count
        if total>33500:return bytes(r),bytes(c),bytes(out),0xffffffff,[]
    def put(a,v):r[a]=v;effects.append(('ram',a,v))
    def port(a,v=0,k=1):hw.append((a,v,k));effects.append(('ppu',a,v,k))
    s=c[6]
    for v in (*c[:2],(c[5]&0xef)|32,c[5]|0x34,*c[2:5]):put(256+s,v);s=(s-1)&255
    if not (r[0xf0]|r[0x9a]):
        port(0x2000,r[255]&0x78);port(0x2002,0,0);port(0x2001);port(0x2003)
        out[134382:]=r[512:768];port(0x4014,2)
        for flag,start,ret in ((28,128,0x2e),(29,88,0x3b),(25,0,0x46)):
            if not r[flag]:continue
            put(256+s,0xc0);put(256+((s-1)&255),ret)
            if flag==25:put(flag,0)
            x=start
            while r[0x360+x]<128:
                port(0x2006,r[0x360+x]);port(0x2006,r[0x361+x])
                count=r[0x362+x];n=count+1 if count<=128 else 1
                for _ in range(n):port(0x2007,r[0x363+x]);x=(x+1)&255
                x=(x+3)&255
                if x==0:break
            if flag!=25:put(flag,0)
        for a,shadow,addr,ret in ((0x1a,0xf2,0xbfff,0x4f),(0x1b,0xf3,0xdfff,0x58)):
            if r[a]:
                put(256+s,0xc0);put(256+((s-1)&255),ret)
                value=r[a]&31;put(shadow,value)
                for shift in range(5):
                    event=(addr,value>>shift,r[0xf5]);hw.append(event);effects.append(('mapper',*event))
                put(a,0)
        if r[24]:
            put(24,0);port(0x2002,0,0);port(0x2006,63);port(0x2006)
            for v in r[768:800]:port(0x2007,v)
            for v in (63,0,0,0):port(0x2006,v)
        port(0x2002,0,0);port(0x2005,r[252]);port(0x2005,r[250]);port(0x2001,r[254]);port(0x2000,(r[253]&1)|r[255])
    put(146,(r[146]+1)&255);put(144,255)
    for a in range(128,144,4):
        acc=r[a];carry=int(acc>=1)
        if acc==1:
            put(a+1,(r[a+1]-1)&255)
            if r[a+1]==0:acc=4;put(a,4)
    c[:7]=bytes((0xc0,0xbf,acc,16,0,(c[5]&0x6c)|6|carry,s))
    data=struct.pack('>H',len(hw))+b''.join(struct.pack('>HBB',*e) for e in hw);out[:len(data)]=data
    return bytes(r),bytes(c),bytes(out),1,effects

def finite(r,x):
    seen=set();events=0
    while x not in seen:
        seen.add(x)
        if r[0x360+x]>=128:return events
        n=r[0x362+x];n=n+1 if n<=128 else 1
        events+=n+2;x=(x+n+3)&255
        if x==0:return events
    return None

def cases(rng):
    for i in range(2048):
        r=bytearray(rng.randbytes(2048));r[0xf0]=r[0x9a]=0;r[0x1c]=i&1;r[0x1d]=(i>>1)&1;r[0x19]=(i%255)+1
        # Include arbitrary scripts, zero-X termination, high counts and wraps.
        if i<256:r[0x360:0x463]=bytes(259);r[0x362]=i
        if 256<=i<512:r[0x360]=255
        if 512<=i<768:r[0x1c+(i&1)]=1
        if 768<=i<1024:r[0xf0]=1
        yield r,bytes.fromhex('fe90')+rng.randbytes(3)+bytes((i&255,(i*73)&255,0xa7))

def main():
    import sys,hashlib
    private='--rom' in sys.argv
    if private:
        from recovery_test_chr_nmi_rom import SHA,PORT
        from recovery_test_chr_nmi_latch import LatchedBus as Bus
        from recovery_test_active_nmi_runtime_chain import SerialMapper
        from py65.devices.mpu6502 import MPU
        rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
        class QueueBus(Bus):
            def __getitem__(self,a):
                if 0xc115<=a<=0xc139:return self.fixed[a-0xc000]
                return super().__getitem__(a)
        bus=QueueBus(rom);ref=MPU(memory=bus,pc=0)
    n=Native();rng=random.Random(0xc115);count=reject=0
    for r,c in cases(rng):
        want=expected(r,c)
        if private and want[3]==1:
            pattern=count%31;length=(pattern+1).bit_length()-1;raw=pattern-((1<<length)-1)
            fields=tuple(rng.randrange(32) for _ in range(4));bits=tuple((raw>>i)&1 for i in range(length))
            bus.seed(fields,bits)
            mapper=SerialMapper();mapper.control,mapper.chr0,mapper.chr1,mapper.prg=fields;mapper.bits=list(bits)
            bus.ram[:]=r;bus.events=[];bus.dma=[];bus.status=rng.randrange(256)
            ref.pc=int.from_bytes(c[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7];ref.nmi()
            for _ in range(300000):
                if ref.pc==0xc0bf:break
                ref.step()
            else:raise AssertionError('original timeout')
            cc=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7]))
            assert (bytes(bus.ram),cc,bus.events)==(want[0],want[1],want[4]),('original mismatch',count)
        got=n.run(r,c,rng)
        assert got==want,('native mismatch',count,got[1].hex(),want[1].hex(),[(i,a,b) for i,(a,b) in enumerate(zip(got[0],want[0])) if a!=b][:10])
        if private and want[3]==1:
            for e in got[4]:
                if e[0]=='mapper':mapper.write(e[1],e[2])
            assert mapper.snapshot()==bus.snapshot(),('partial latch mismatch',count)
        count+=1;reject+=want[3]==0xffffffff
    n.close();print('PASS combined queued NMI',count,'cases;',reject,'inert guards;', 'original-ROM' if private else 'ROM-free','full RAM/context/effects/journal/DMA/ABI/bounds')
if __name__=='__main__':main()
