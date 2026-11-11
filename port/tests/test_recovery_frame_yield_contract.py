#!/usr/bin/env python3
"""ROM-free declarative frame-yield contract, invented RAM/context only."""
import random,struct
from recovery_frame_yield_harness import Native

def expected(state,ctx):
    if int.from_bytes(ctx[:2],'big') not in (0xc2a5,0xff04):
        return bytes(state),ctx,b'\xb6'*512,0xffffffff,[]
    ram=bytearray(state);out=bytearray(ctx);events=[];sp=ctx[6]
    def put(a,v):ram[a]=v;events.append((a,v))
    def push(v):
        nonlocal sp
        put(256+sp,v);sp=(sp-1)%256
    if ctx[:2]==b'\xc2\xa5':push(0xc2);push(0xa7)
    put(0x93,1);push(ctx[3]);push(ctx[4]);push(255);push(14)
    task=ram[0x91];offset=(task*4)%256;sp=(sp+2)%256
    put((0x81+offset)%256,ram[0x93]);put((0x80+offset)%256,1);put((0x82+offset)%256,sp)
    out[:2]=b'\xfe\x8d';out[2:7]=bytes((offset,sp,offset,(ctx[5]&0x7c)|((task>>6)&1)|(sp&128)|(2 if sp==0 else 0),sp))
    j=b''.join(struct.pack('>HBB',a,v,0) for a,v in events)
    return bytes(ram),bytes(out),j+b'\xb6'*(512-len(j)),len(events),events

def main():
    n=Native();rng=random.Random(0xff04);count=0
    for pc in (0xc2a5,0xff04):
        for task in range(256):
            for sp in range(256):
                ram=bytearray(rng.randbytes(2048));ram[0x91]=task
                ctx=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes(((task+sp)&255,sp,0xa5))
                assert n.run(ram,ctx,rng)==expected(ram,ctx),(pc,task,sp)
                count+=1
    for pc in (0,0xc2a4,0xc2a6,0xff03,0xff05,0xfe8d):
        ram=rng.randbytes(2048);ctx=pc.to_bytes(2,'big')+rng.randbytes(6)
        assert n.run(ram,ctx,rng)==expected(ram,ctx);count+=1
    print(f'PASS {count} ROM-free contracts; {len(n.code)} native bytes');n.close()
if __name__=='__main__':main()
