#!/usr/bin/env python3
"""ROM-free semantic scheduler specification, independently expressed as state operations."""
import random,struct
from recovery_general_scheduler_harness import Native

def expected(state,ctx,inputs):
    if int.from_bytes(ctx[:2],'big') not in (0xfe8d,0xfe90):return bytes(state),ctx,b'\xb6'*74,0xffffffff,[]
    r=bytearray(state);c=bytearray(ctx);events=[];hw=[];s=255 if ctx[:2]==b'\xfe\x8d' else ctx[6]
    def put(a,v):r[a]=v;events.append(('ram',a,v))
    def push(v):
        nonlocal s
        put(256+s,v);s=(s-1)%256
    def pop():
        nonlocal s
        s=(s+1)%256;return r[256+s]
    def io(a,v,k):hw.append((a,v,k));events.append(('controller',a,v,k))
    def flags(v,carry):return (ctx[5]&0x7c)|(v&128)|(2 if v==0 else 0)|carry
    put(0x90,0)
    slot=next((i for i in range(4) if r[128+4*i]>=4),None)
    if slot is None:
        c[:7]=bytes((0xfe,0x90,r[140],16,0,(ctx[5]&0x7c)|2,s));status=0
    else:
        off=slot*4;put(0x91,slot);kind=r[128+off];put(128+off,2);carry=int(kind>=8)
        if kind==8:
            put(0x93,r[130+off]);put(0x94,r[131+off]);a=r[0x94]
            c[:7]=bytes((a,r[0x93],a,off,kind,flags(a,carry),s));status=2
        else:
            s=r[130+off]
            if slot==0:
                push(0xfe);push(0xcf);io(0x4016,1,1);io(0x4016,0,1)
                for bit in range(7,-1,-1):
                    for pad in range(2):
                        v=(inputs[pad]>>bit)&1;io(0x4016+pad,v,0)
                        put(0x14+pad,((r[0x14+pad]<<1)|v)&255);put(pad,(r[pad]<<1)&255)
                put(0x14,r[0x14]|r[0]);put(0x15,r[0x15]|r[1])
                for pad in (1,0):
                    now=r[0x14+pad];put(0x14+pad,now&~r[0x16+pad]);put(0x16+pad,now)
                for i in (3,2,1,0):
                    v=r[0x14+i];carry=int((v&12)==12 or (v&3)==3)
                    if carry:put(0x14+i,v&240)
                pop();pop()
            y=pop();x=pop();lo=pop();hi=pop();pc=((hi<<8|lo)+1)&65535
            c[:7]=pc.to_bytes(2,'big')+bytes((x,x,y,flags(x,carry),s));status=1
    journal=struct.pack('>H',len(hw))+b''.join(struct.pack('>HBB',*v) for v in hw)
    return bytes(r),bytes(c),journal+b'\xb6'*(74-len(journal)),status,events

def cases(rng):
    for slot in range(4):
        for kind in range(4,256):
            for p in (0,0x10,0x20,0xff):
                r=bytearray(rng.randbytes(2048))
                for i in range(slot):r[128+4*i]=rng.randrange(4)
                r[128+4*slot]=kind;r[130+4*slot]=(kind+p)&255
                yield r,b'\xfe\x8d'+rng.randbytes(3)+bytes((p,rng.randrange(256),0xa5)),(rng.randrange(256),rng.randrange(256))
    for p in range(256):
        for pc in (0xfe8d,0xfe90):
            r=bytearray(rng.randbytes(2048))
            for i in range(4):r[128+4*i]=i
            yield r,pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((p,p,0x69)),(0,0)
    for pad in range(256):
        for prev in range(256):
            r=bytearray(rng.randbytes(2048));r[128]=4;r[130]=prev;r[22]=prev;r[23]=prev^255
            yield r,b'\xfe\x90'+rng.randbytes(3)+bytes((pad,prev,0x69)),(pad,pad^255)

def main():
    n=Native();rng=random.Random(0xfeed);count=0
    for r,c,i in cases(rng):
        got=n.run(r,c,rng,inputs=i);want=expected(r,c,i);assert got==want,(count,got[1:4],want[1:4]);count+=1
    for pc in (0,0xfe8c,0xfe91,0xfed0,0xffff):
        r=rng.randbytes(2048);c=pc.to_bytes(2,'big')+rng.randbytes(6)
        assert n.run(r,c,rng)==expected(r,c,(0,0));count+=1
    print(f'PASS {count} ROM-free cases; {len(n.code)} native bytes');n.close()
if __name__=='__main__':main()
