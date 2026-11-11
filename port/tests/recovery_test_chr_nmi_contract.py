#!/usr/bin/env python3
"""Invented states and declarative NMI effects, no ROM or reference CPU."""
import random,struct
from recovery_chr_nmi_harness import Native

def expected(state,ctx):
    r=bytearray(state);c=bytearray(ctx);out=bytearray(b'\xb6'*494);effects=[];hw=[]
    if not (r[0xf0]|r[0x9a]) and any(r[a] for a in (0x19,0x1c,0x1d)):
        return bytes(r),bytes(c),bytes(out),0xffffffff,[]
    def put(a,v):r[a]=v;effects.append(('ram',a,v))
    def port(a,v=0,k=1):hw.append((a,v,k));effects.append(('ppu',a,v,k))
    s=c[6]
    for v in (*c[:2],(c[5]&0xef)|32,c[5]|0x34,*c[2:5]):put(256+s,v);s=(s-1)&255
    if not (r[0xf0]|r[0x9a]):
        port(0x2000,r[255]&0x78);port(0x2002,0,0);port(0x2001);port(0x2003)
        out[238:]=r[512:768];port(0x4014,2)
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

def cases(rng):
    for i in range(65536):
        r=bytearray(rng.randbytes(2048));r[0xf0]=r[0x9a]=0;r[0x19:0x1e]=bytes(5);r[0x1a]=i&255;r[0x1b]=(i>>8)&255;r[24]=i&255 if i&256 else 0
        for j in range(4):r[128+4*j]=(0,1,2,255)[(i+j)%4];r[129+4*j]=(i+j)&255
        yield r,i.to_bytes(2,'big')+rng.randbytes(3)+bytes((i&255,(i>>8)&255,0x69))
    for i in range(512):
        r=bytearray(rng.randbytes(2048));r[0xf0]=i&255;r[0x9a]=(i>>8)+1
        yield r,bytes((0xfe,0x90,*rng.randbytes(3),i&255,i&255,0x69))

def main():
    n=Native();rng=random.Random(0x90c0);count=0
    for r,c in cases(rng):assert n.run(r,c,rng)==expected(r,c),count;count+=1
    rejects=0
    for a in (0x19,0x1c,0x1d):
        for v in range(1,256):
            r=bytearray(2048);r[a]=v;c=bytes((0xfe,0x90,1,2,3,0,255,0))
            assert n.run(r,c,rng)==expected(r,c);rejects+=1
    print(f'PASS {count} declarative NMI cases, {rejects} inert unsupported-queue rejections; {len(n.code)} native bytes');n.close()
if __name__=='__main__':main()
