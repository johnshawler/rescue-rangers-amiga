#!/usr/bin/env python3
"""Bounded ROM-free contract: declarative fade state transform vs native code.
No py65, private oracle, cartridge, captured data, or status normalization.
"""
import hashlib
import random
import struct
from recovery_fade_entry_harness import Native, PORT, RAM, CTX, JOURNAL, STACK

FROZEN=(
    'src/recovery_startup_fade_continue.s',
    'tests/recovery_test_startup_fade_continue.py',
    'tests/recovery_test_startup_fade_yield_chain.py',
    'tests/test_recovery_startup_fade_alu.py',
    'analysis/recovery_startup_fade_continue.md',
)

def signed(value):
    return value if value<128 else value-256

def nz(value):
    return (value&128)|(2 if value==0 else 0)

def subtraction_flags(left,right):
    result=(left-right)&255
    overflow=not -128<=signed(left)-signed(right)<=127
    return int(left>=right)|nz(result)|(64 if overflow else 0)

def model(state,context):
    """Direct state/effect contract, not an instruction executor."""
    ram=bytearray(state);ctx=bytearray(context);writes=[]
    pc=int.from_bytes(ctx[:2],'big');sp=ctx[6];p=ctx[5]
    if pc not in (0xc2a8,0xc594):
        return bytes(ram),bytes(ctx),b'\xb6'*512,0xffffffff,[]
    def write(address,value):
        ram[address]=value;writes.append((address,value))
    if pc==0xc594:
        write(0x100+sp,0xc5)
        write(0x100+((sp-1)&255),0x96)
        ctx[:2]=b'\xff\x04';ctx[6]=(sp-2)&255
    else:
        count=ram[0x100+((sp+1)&255)]
        remaining=(count-1)&255
        if remaining:
            write(0x100+((sp+1)&255),remaining)
            ctx[2]=remaining;ctx[5]=(p&0x3c)|subtraction_flags(count,1)
            ctx[:2]=b'\xc2\xa5'
        else:
            old,step=ram[0xf],ram[0xd]
            level=(old+step)&255
            overflow=not -128<=signed(old)+signed(step)<=127
            preserved=(p&0x3c)|(64 if overflow else 0)
            write(0xf,level)
            if level==0x50 or level>=128:
                lo=ram[0x100+((sp+2)&255)]
                hi=ram[0x100+((sp+3)&255)]
                ctx[:2]=((lo+(hi<<8)+1)&65535).to_bytes(2,'big')
                ctx[2]=level;ctx[6]=(sp+3)&255
                ctx[5]=preserved|int(level>=0x50)|(2 if level==0x50 else nz(level))
            else:
                # All copy stores precede attenuation stores, both descending.
                palette=bytes(ram[0x320:0x340])
                for index in range(31,-1,-1):write(0x300+index,palette[index])
                for index in range(31,-1,-1):
                    difference=(palette[index]-level)&255
                    write(0x300+index,15 if difference>=128 else difference)
                write(0x18,255)
                delay=ram[0xe]
                write(0x100+((sp+1)&255),delay)
                ctx[:2]=b'\xc2\xa5';ctx[2]=delay;ctx[4]=255
                ctx[5]=(p&0x3c)|(subtraction_flags(palette[0],level)&0x41)|nz(delay)
    journal=b''.join(struct.pack('>HBB',a,v,0) for a,v in writes)
    return bytes(ram),bytes(ctx),journal+b'\xb6'*(512-len(journal)),len(writes),writes

def main():
    before={p:hashlib.sha256((PORT/p).read_bytes()).hexdigest() for p in FROZEN}
    native=Native('recovery_startup_fade_continue.s');rng=random.Random(0xc2a8594)
    cases=stores=wrapped_returns=0
    def case(p,sp,count=1,old=0x10,step=0x10,pc=0xc2a8,palette=None,return_word=None,delay=4):
        nonlocal cases,stores,wrapped_returns
        ram=bytearray(rng.randbytes(2048))
        ram[0xf]=old;ram[0xd]=step;ram[0xe]=delay
        if palette is not None:ram[0x320:0x340]=palette
        ram[0x100+((sp+1)&255)]=count
        if return_word is not None:
            ram[0x100+((sp+2)&255)]=return_word&255
            ram[0x100+((sp+3)&255)]=return_word>>8
        ctx=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((p,sp,rng.randrange(256)))
        expected=model(ram,ctx);got=native.run(ram,ctx,rng)
        assert got==expected,('contract mismatch',ctx.hex(),old,step,count,got[1].hex(),expected[1].hex())
        cases+=1;stores+=len(got[4])
        if return_word==65535:
            assert got[1][:2]==b'\0\0' and got[1][6]==(sp+3)&255
            wrapped_returns+=1
    # Every raw status, every stack position, and explicit page-one edge positions
    # in each state family. Preserve arbitrary register and reserved bytes.
    families=((0,0x10,0x10),(1,0x10,0x10),(2,0x10,0x10),
              (128,0x10,0x10),(1,0x40,0x10),(1,0x7f,1))
    for p in range(256):
        for sp in sorted({p,0,0xfc,0xfd,0xfe,0xff}):
            for count,old,step in families:case(p,sp,count,old,step)
            case(p,sp,pc=0xc594)
    # All countdown bytes and delay reload bytes, including zero and negative.
    for value in range(256):
        case(value,(value*29)&255,count=value)
        case(value,(value*13)&255,delay=value)
    # Arithmetic carry/overflow, termination and clipping boundaries in each slot.
    boundaries=(0,1,15,16,31,0x4f,0x50,0x7f,0x80,0x81,0xef,0xff)
    for old in boundaries:
        for step in boundaries:case((old^step),0xfe,old=old,step=step)
    for level in (0,1,15,16,31,0x4f,0x51,0x7f):
        for value in boundaries:
            for slot in range(32):
                palette=bytearray(rng.randbytes(32));palette[slot]=value
                case((value+slot)&255,slot,old=0,step=level,palette=palette)
    # Permanent regression: actual stacked FFFF RTS wraps to0000 for both
    # equal50 and negative-level exits, with the countdown/low/high across wrap.
    for p in range(256):
        for sp in (0xfc,0xfd,0xfe,0xff):
            case(p,sp,old=0x40,step=0x10,return_word=65535)
            case(p,sp,old=0x7f,step=1,return_word=65535)
    accepted=cases;rejected=0
    invalid={0,0xffff,0xc2a7,0xc2a9,0xc593,0xc595,0xc2a5,0xff04}
    invalid.update(range(0,65536,257));invalid.update(rng.randrange(65536) for _ in range(1024))
    for pc in sorted(invalid-{0xc2a8,0xc594}):
        case(rng.randrange(256),rng.randrange(256),pc=pc);rejected+=1
    # Explicit negative read/write whitelist challenges, including cross-buffer
    # widths, code writes, distant addresses and native-stack guard crossing.
    negatives=0
    for mode,width,address in (
        ('R',0,RAM-1),('R',1,RAM+2047),('R',2,CTX+7),
        ('R',1,JOURNAL+511),('R',0,0x18000),('W',0,0x1000),
        ('W',1,RAM+2047),('W',2,CTX+7),('W',1,JOURNAL+511),
        ('W',1,STACK-257),('W',0,0x18000)):
        try:native.trace(mode,width,address,0)
        except AssertionError:negatives+=1
        else:raise AssertionError(('invalid access accepted',mode,width,address))
    assert before=={p:hashlib.sha256((PORT/p).read_bytes()).hexdigest() for p in FROZEN}
    native.close()
    print(f'PASS ROM-free native fade contract: {accepted} accepted cases, {rejected} inert rejected PCs, {stores} exact ordered stores, {wrapped_returns} explicit FFFF-to-0000 RTS cases, {negatives} negative access checks; full RAM/raw-context/journal-tail, ABI/stack/guards verified. Five frozen files unchanged.')
if __name__=='__main__':main()
