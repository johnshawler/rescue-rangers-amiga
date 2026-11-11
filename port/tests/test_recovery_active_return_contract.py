#!/usr/bin/env python3
"""ROM-free declarative bank/frame return contract, independent of instructions."""
import random,hashlib
from recovery_active_return_harness import Native

def expected(ram,ctx):
    if ctx[:2]!=bytes.fromhex('c0f9'):
        return bytes(ram),ctx,b'\xb6'*22,0xffffffff,[]
    frame=[ram[0x100+((ctx[6]+i)&255)] for i in range(1,8)]
    y,x,a,handler,p,lo,hi=frame
    out=bytes((hi,lo,a,x,y,(p&0xef)|0x20,(ctx[6]+7)&255,ctx[7]))
    values=[ram[0xf1]//(2**i) for i in range(5)]
    journal=b'\0\5'+b''.join(bytes((255,240,v,ram[0xf5])) for v in values)
    return bytes(ram),out,journal,1,[('mapper',0xfff0,v,ram[0xf5]) for v in values]

def cases(rng):
    # All saved statuses at every stack position, including wrap and arbitrary
    # noncanonical handler status. All initial P, saved banks and busy values.
    for sp in range(256):
        for p in range(256):
            ram=bytearray(rng.randbytes(2048));ram[0xf6]=(p+sp)&255
            ram[0xf1]=p;ram[0xf5]=sp
            ram[0x100+((sp+5)&255)]=p
            ctx=bytes.fromhex('c0f9')+rng.randbytes(3)+bytes((p,sp,rng.randrange(256)))
            yield ram,ctx
    # Exhaustive target low/high combinations, independently of status range.
    for target in range(65536):
        sp=target&255;ram=bytearray(rng.randbytes(2048));ram[0xf6]=0
        ram[0x100+((sp+6)&255)]=target&255
        ram[0x100+((sp+7)&255)]=target>>8
        yield ram,bytes.fromhex('c0f9')+rng.randbytes(4)+bytes((sp,17))

def main():
    n=Native();rng=random.Random(0xc0f9);count=0
    for ram,ctx in cases(rng):
        assert n.run(ram,ctx,rng)==expected(ram,ctx),(count,ctx.hex());count+=1
    ram=bytearray(rng.randbytes(2048));ram[0xf6]=0
    ctx=bytes.fromhex('c0f9')+rng.randbytes(6);rejected=0
    for pc in range(65536):
        if pc==0xc0f9:continue
        bad=pc.to_bytes(2,'big')+ctx[2:]
        assert n.run(ram,bad,rng)==expected(ram,bad);rejected+=1
    print(f'PASS {count} ROM-free declarative returns; {rejected} inert wrong-PC cases; all F6 values preserved; bytes={len(n.code)} SHA256={hashlib.sha256(n.code).hexdigest()}')
    n.close()
if __name__=='__main__':main()
