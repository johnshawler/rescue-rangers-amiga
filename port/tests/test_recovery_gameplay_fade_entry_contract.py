#!/usr/bin/env python3
"""ROM-free declarative palette-fade entry contract on invented inputs."""
import random,struct
from recovery_fade_entry_harness import Native

def expected(state,ctx):
    effects=[];sp=ctx[6]
    for value in (0xc7,2,0xe0,0x98,0xc2,0x49):
        effects.append((0x100+sp,value));sp=(sp-1)&255
    effects += [(0x0f,16),(0x0d,16),(0x9a,0),(0x0e,4)]
    palette=state[0x320:0x340]
    effects += [(0x300+i,palette[i]) for i in range(31,-1,-1)]
    # Binary 8-bit subtraction followed by replacement of negative results.
    effects += [(0x300+i,15 if ((palette[i]-16)&255)>=128 else ((palette[i]-16)&255)) for i in range(31,-1,-1)]
    effects += [(0x18,255),(0x100+sp,4)];sp=(sp-1)&255
    result=bytearray(state)
    for a,v in effects:result[a]=v
    carry=int(palette[0]>=16);overflow=0x40 if 128<=palette[0]<144 else 0
    context=bytes((0xc2,0xa5,4,16,255,(ctx[5]&0x3c)|carry|overflow,sp,ctx[7]))
    journal=b''.join(struct.pack('>HBB',a,v,0) for a,v in effects)
    return bytes(result),context,journal,len(effects),effects

def main():
    rng=random.Random(0xc2a5);native=Native();count=0
    for pos in range(32):
        for value in range(256):
            state=bytearray(rng.randbytes(2048));state[0x320+pos]=value
            ctx=b'\xc7\x00'+rng.randbytes(6)
            got=native.run(state,ctx,rng);want=expected(state,ctx)
            assert got==(*want[:2],want[2]+b'\xb6'*(512-len(want[2])),*want[3:]),(pos,value)
            count+=1
    for p in range(256):
        for sp in (0,1,2,3,4,5,6,7,254,255):
            state=rng.randbytes(2048);ctx=bytes((0xc7,0,1,2,3,p,sp,0x91))
            got=native.run(state,ctx,rng);want=expected(state,ctx)
            assert got==(*want[:2],want[2]+b'\xb6'*(512-len(want[2])),*want[3:])
            count+=1
    for pc in (0,0xc6bd,0xc6ff,0xc701,0xc2a5,0xffff):
        state=rng.randbytes(2048);ctx=pc.to_bytes(2,'big')+rng.randbytes(6)
        assert native.run(state,ctx,rng)==(state,ctx,b'\xb6'*512,0xffffffff,[]);count+=1
    print(f'PASS ROM-free fade entry: {count} cases; six global bad-read checks; {len(native.code)} native bytes')
    native.close()
if __name__=='__main__':main()
