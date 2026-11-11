#!/usr/bin/env python3
"""ROM-free declarative contract using synthetic resources and arbitrary RAM."""
import random,struct
from recovery_stage_resource_harness import Native
DEST=(0x74,0x75,0x72,0x73,0x78,0x79,0x76,0x77,0x7a,0x7b,0x7c,0x7d)
def expected(state,ctx,resource):
    if ctx[:2]!=b'\xc6\xb5' or state[0xf6]:
        return bytes(state),ctx,b'\xb6'*256,0xffffffff,[],[]
    sp=ctx[6];idx=state[0x31];events=[]
    for v in (0xc6,0xb9):events.append((0x100+sp,v,0));sp=(sp-1)&255
    events += [(0xf1,4,0),(0xf4,4,0),(0xf5,(state[0xf5]+1)&255,0)]
    events += [(0xfff0,v,2) for v in (4,2,1,0,0)]
    events += [(0xf5,0,0)];sp=(sp+2)&255
    for v in (0xc6,0xbc):events.append((0x100+sp,v,0));sp=(sp-1)&255
    for i,dest in enumerate(DEST):
        v=resource[i*15+idx];events += [(0x8193+i*15+idx,v,1),(dest,v,0)]
    out=bytearray(state)
    for a,v,k in events:
        if k==0:out[a]=v
    a=resource[165+idx];p=(ctx[5]&0x7c)|(a&128)|(2 if a==0 else 0)
    context=bytes((0xc6,0xbd,a,idx,ctx[4],p,ctx[6],ctx[7]))
    journal=b''.join(struct.pack('>HBB',*e) for e in events)
    return bytes(out),context,journal+b'\xb6'*(256-len(journal)),len(events),[(a,v) for a,v,k in events if k==0],[(a,v) for a,v,k in events if k==1]
def main():
    n=Native();rng=random.Random(0x8193);count=0
    for idx in range(256):
        for p in range(256):
            state=bytearray(rng.randbytes(2048));state[0xf6]=0;state[0x31]=idx
            ctx=bytes((0xc6,0xb5,*rng.randbytes(3),p,(idx+p)&255,0x97))
            resource=bytearray(rng.randbytes(421));resource[165+idx]=p
            assert n.run(state,ctx,rng,resource)==expected(state,ctx,resource),(idx,p)
            count+=1
    for sp in range(256):
        for f5 in range(256):
            state=bytearray(rng.randbytes(2048));state[0xf6]=0;state[0xf5]=f5
            ctx=bytes((0xc6,0xb5,*rng.randbytes(4),sp,0x69));resource=rng.randbytes(421)
            assert n.run(state,ctx,rng,resource)==expected(state,ctx,resource),(sp,f5)
            count+=1
    for f6 in range(1,256):
        state=bytearray(rng.randbytes(2048));state[0xf6]=f6;ctx=b'\xc6\xb5'+rng.randbytes(6);resource=rng.randbytes(421)
        assert n.run(state,ctx,rng,resource)==expected(state,ctx,resource);count+=1
    for pc in (0,0xc6b4,0xc6b6,0x8000,0xc6bd,0xffff):
        state=bytearray(rng.randbytes(2048));state[0xf6]=0;ctx=pc.to_bytes(2,'big')+rng.randbytes(6);resource=rng.randbytes(421)
        assert n.run(state,ctx,rng,resource)==expected(state,ctx,resource);count+=1
    print(f'PASS ROM-free stage resource contract: {count} cases; native {len(n.code)} bytes');n.close()
if __name__=='__main__':main()
