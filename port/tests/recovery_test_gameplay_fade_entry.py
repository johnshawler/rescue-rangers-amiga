#!/usr/bin/env python3
"""Private actual-ROM differential and uninterrupted original-state composition.

Ricoh 2A03 disables BCD adjustment, but preserves the D status bit. The
reference subclasses py65's instruction executor solely for its SBC ALU:
ordinary integer subtraction, binary C/Z/V/N, and no mutation of other P bits.
No status normalization or RAM/context patch is performed between slices.
ADC is unreachable before this boundary. Test all SBC operands/carries and D
values against a separately expressed bitwise full-adder truth table first.
"""
import hashlib,random,struct
from py65.devices.mpu6502 import MPU
from recovery_fade_entry_harness import Native,PORT
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
class Ricoh2A03(MPU):
    def opSBC(self,address):
        operand=self.ByteAt(address());old=self.a
        result=old-operand-(1-(self.p&1));value=result&255
        flags=(int(result>=0) | (2 if value==0 else 0) | (value&128)
               | (64 if ((old^operand)&(old^value)&128) else 0))
        self.a=value;self.p=(self.p&0x3c)|flags

def prove_binary_sbc():
    m=Ricoh2A03();count=0
    for a in range(256):
        for b in range(256):
            for cin in (0,1):
                carry=cin;result=0;carry7=0
                for bit in range(8):
                    av=(a>>bit)&1;bv=1-((b>>bit)&1)
                    if bit==7:carry7=carry
                    result|=(av^bv^carry)<<bit
                    carry=(av&bv)|(av&carry)|(bv&carry)
                flags=carry|(2 if result==0 else 0)|(result&128)|((carry7^carry)<<6)
                for d in (0,8):
                    m.a=a;m.p=0x34|d|cin;m.memory[0]=b;m.opSBC(lambda:0)
                    assert (m.a,m.p)==(result,0x34|d|flags)
                    count+=1
    return count
class Bus(list):
    def __init__(self,rom):
        super().__init__([0]*65536)
        self[0xc000:]=rom[16+7*16384:16+8*16384];self.events=[]
    def __setitem__(self,address,value):
        if isinstance(address,int):
            assert 0<=address<2048,('external write',hex(address))
            self.events.append((address,value))
        super().__setitem__(address,value)
    def __getitem__(self,address):
        if isinstance(address,int):
            assert 0<=address<2048 or 0xc000<=address<65536,('external read',hex(address))
        return super().__getitem__(address)

def advance(ref,target):
    for _ in range(1000):
        if ref.pc==target:return
        ref.step()
    raise AssertionError(('reference timeout',hex(ref.pc)))
def compare(native,bus,ref,state,ctx,rng,resume=False,entry=0x1000):
    got=native.run(state,ctx,rng,resume=resume,entry=entry)
    journal=b''.join(struct.pack('>HBB',a,v,0) for a,v in bus.events)
    context=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
    assert got==(bytes(bus[:2048]),context,journal+b'\xb6'*(512-len(journal)),len(bus.events),bus.events),('differential',ctx.hex())
    return got

def main():
    alu=prove_binary_sbc()
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    bus=Bus(rom);ref=Ricoh2A03(memory=bus);native=Native();rng=random.Random(0xe096)
    native.install('recovery_gameplay_player_init.s',0x4000)
    cases=events=0
    for p in range(256):
        for sp in range(256):
            state=bytearray(rng.randbytes(2048));state[0x320]=(p+sp)&255
            ctx=bytes((0xc7,0,*rng.randbytes(3),p,sp,0x69))
            bus[:2048]=state;bus.events=[];ref.pc=0xc700;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
            advance(ref,0xc2a5);compare(native,bus,ref,state,ctx,rng)
            cases+=1;events+=len(bus.events)
    # Every byte in every palette position, with random surrounding full RAM.
    for pos in range(32):
        for value in range(256):
            state=bytearray(rng.randbytes(2048));state[0x320+pos]=value
            ctx=b'\xc7\x00'+rng.randbytes(6)
            bus[:2048]=state;bus.events=[];ref.pc=0xc700;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
            advance(ref,0xc2a5);compare(native,bus,ref,state,ctx,rng)
            cases+=1;events+=len(bus.events)
    # Original reference and native RAM/context remain live across C700.
    for i in range(4096):
        state=bytearray(rng.randbytes(2048));state[0x50]=i&1
        if i&2:state[0x54]=12
        if i&4:state[0x55]=12
        ctx=bytes((0xc6,0xbd,*rng.randbytes(3),(i>>4)&255,i&255,0x96))
        bus[:2048]=state;bus.events=[];ref.pc=0xc6bd;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        advance(ref,0xc700)
        first=compare(native,bus,ref,state,ctx,rng,entry=0x4000)
        first_events=list(bus.events);bus.events=[]
        advance(ref,0xc2a5)
        second=compare(native,bus,ref,first[0],first[1],rng,resume=True)
        assert first[4]+second[4]==first_events+bus.events
        events+=len(first_events)+len(bus.events)
    print(f'PASS: {alu} binary SBC truth-table cases; {cases} standalone ROM cases; 4096 continuous two-slice compositions; {events} ordered stores. All RAM/context/journal, ABI, guards and globally whitelisted native reads/writes verified. Native {len(native.code)} bytes.')
    native.close()
if __name__=='__main__':main()
