#!/usr/bin/env python3
"""Private ROM differential for static complete fade between-yield continuation.
Reference uses binary Ricoh ADC/SBC without changing raw status or saved frames.
Continuous real-reset oracle samples are tested independently, not claimed as
an all-native multi-NMI runtime. Audio always executes in that reference.
"""
import hashlib, random, struct
from recovery_fade_entry_harness import Native, PORT
from recovery_test_gameplay_fade_entry import Ricoh2A03, Bus, SHA, prove_binary_sbc
from verify_recovery_runtime_probe import oracle

class CPU(Ricoh2A03):
    def opADC(self,address):
        operand=self.ByteAt(address());old=self.a
        result=old+operand+(self.p&1);value=result&255
        self.p=(self.p&0x3c)|int(result>255)|(2 if value==0 else 0)|(value&128)|(64 if (~(old^operand)&(old^value)&128) else 0)
        self.a=value

def advance(ref):
    for _ in range(1000):
        pc=ref.pc;ref.step()
        if ref.pc==0xc2a5 or pc==0xc2bd or pc==0xc594:return
    raise AssertionError(('timeout',hex(ref.pc)))

def compare(native,state,ctx,ref,bus,rng):
    got=native.run(state,ctx,rng)
    expected=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
    journal=b''.join(struct.pack('>HBB',a,v,0) for a,v in bus.events)
    assert got==(bytes(bus[:2048]),expected,journal+b'\xb6'*(512-len(journal)),len(bus.events),bus.events),('differential',ctx.hex(),got[1].hex(),expected.hex())
    return got

class RecordBus:
    """Delegate live mapper/PPU/APU/controller bus, additionally observe RAM stores."""
    def __init__(self,base):self.base=base;self.events=[]
    def __getitem__(self,key):return self.base[key]
    def __setitem__(self,key,value):
        if isinstance(key,int) and (0x4000<=key<=0x4013 or key==0x4015):
            self.base.events.append(('apu',key,value,1));return
        if isinstance(key,int) and key<2048:self.events.append((key,value))
        self.base[key]=value

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    rng=random.Random(0xc2a8);native=Native('recovery_startup_fade_continue.s')
    bus=Bus(rom);ref=CPU(memory=bus);cases=0;stores=0
    def case(state,ctx):
        nonlocal cases,stores
        bus[:2048]=state;bus.events=[]
        ref.pc=int.from_bytes(ctx[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        advance(ref);got=compare(native,state,ctx,ref,bus,rng)
        cases+=1;stores+=len(bus.events);return got
    # All raw status bytes and every SP, including wrapped PLA/PHA/RTS.
    for p in range(256):
        for sp in range(256):
            state=bytearray(rng.randbytes(2048))
            state[0x100+((sp+1)&255)]=(0,1,2,128)[(p+sp)&3]
            case(state,b'\xc2\xa8'+rng.randbytes(3)+bytes((p,sp,0xa7)))
    print('PASS raw-status/stack cross product',flush=True)
    for countdown in range(256):
        for p in (0,8,0x55,0xff):
            state=bytearray(rng.randbytes(2048));sp=(countdown+p)&255
            state[0x100+((sp+1)&255)]=countdown
            case(state,b'\xc2\xa8'+rng.randbytes(3)+bytes((p,sp,0xa7)))
    # Exhaustive ADC operands on the countdown-expired path.
    for a in range(256):
        for b in range(256):
            state=bytearray(rng.randbytes(2048));sp=(a+b)&255
            state[0xf]=a;state[0xd]=b;state[0x100+((sp+1)&255)]=1
            case(state,b'\xc2\xa8'+rng.randbytes(3)+bytes(((a^b),sp,0xa7)))
    print('PASS exhaustive ADC operands and all countdown bytes',flush=True)
    # Every source palette byte at every position; each attenuation value.
    for value in range(256):
        for pos in range(32):
            state=bytearray(rng.randbytes(2048));state[0xf]=0;state[0xd]=value&127
            if state[0xd]==80:state[0xd]=79
            state[0x320+pos]=value;state[0x1bd]=1
            case(state,b'\xc2\xa8'+rng.randbytes(3)+bytes((value,0xbc,0xa7)))
    for p in range(256):
        for sp in range(256):
            case(bytearray(rng.randbytes(2048)),b'\xc5\x94'+rng.randbytes(3)+bytes((p,sp,0xa7)))
    print('PASS palette and outer-yield cases',flush=True)
    # Every unsupported PC must reject before any mutation, including journal.
    rejected=0
    state=rng.randbytes(2048)
    for pc in range(65536):
        if pc in (0xc2a8,0xc594):continue
        ctx=pc.to_bytes(2,'big')+rng.randbytes(6)
        got=native.run(state,ctx,rng)
        assert got==(state,ctx,b'\xb6'*512,0xffffffff,[])
        rejected+=1
    print('PASS exhaustive inert rejections',flush=True)
    # Real reset state, then uninterrupted original CPU execution through all
    # sixteen fade resumptions and the outer yield to C597. No ready/frame edits.
    results,base,steps=oracle(rom)
    raw=results[-1][5];live=RecordBus(base);ref=CPU(memory=live)
    ref.pc=int.from_bytes(raw[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=raw[2:7]
    samples=0;nmis=0;fade_values=[];audio_events=len([e for e in base.events if e[0]=='apu'])
    for _ in range(1000000):
        if ref.pc in (0xc2a8,0xc594):
            state=bytes(live[:2048]);ctx=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7))
            live.events=[];advance(ref)
            compare(native,state,ctx,ref,live,rng);samples+=1
            fade_values.append(live[0xf])
            continue
        if ref.pc==0xc597:break
        # Interrupt only genuine completed idle scheduler scans, not arrivals.
        pc=ref.pc;ref.step()
        if pc==0xfea3 and ref.pc==0xfe90:
            ref.nmi();nmis+=1
    else:raise AssertionError(('lifecycle timeout',hex(ref.pc)))
    assert samples==17 and nmis==16,(samples,nmis)
    assert live[0xf]==0x50 and ref.sp==0xbf and base.bank==6
    assert set(fade_values)=={0x10,0x20,0x30,0x40,0x50}
    audio_delta=len([e for e in base.events if e[0]=='apu'])-audio_events
    assert audio_delta>0
    assert hashlib.sha256((PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()).hexdigest()==SHA
    print(f'PASS {cases} standalone ROM cases; {stores} exact ordered stores; {rejected} inert rejects; 17 continuous-reference-derived fade/outer-yield samples, {nmis} further real NMIs and {audio_delta} APU events through C597. All RAM/raw context/journal tails, ABI, guards/access whitelist verified. Native {len(native.code)} bytes SHA256 {hashlib.sha256(native.code).hexdigest()}. This is not an all-native repeated-NMI composition.')
    native.close()
if __name__=='__main__':main()
