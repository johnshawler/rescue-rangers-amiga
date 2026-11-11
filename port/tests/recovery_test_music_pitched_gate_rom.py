#!/usr/bin/env python3
"""Independent actual-ROM pitched duration/gate proof. No raw P patching."""
import hashlib,random
from pathlib import Path
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_music_pitched_gate_contract import make_checker
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def run_gate(bus,ref,reserved):
    start=len(bus.events)
    for steps in range(300):
        pc=ref.pc
        if pc==0x83fd:break
        assert 0x83a0<=pc<=0x83fa or 0x8006<=pc<=0x8022,hex(pc)
        if pc in (0x83ba,0x83c1):
            addr=(0x8585 if pc==0x83ba else 0x858c)+ref.y
            bus.events.append(('resource',addr,bus[addr],0))
        ref.step()
    else:raise AssertionError('gate reference timeout')
    return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved)),list(bus.events[start:])
def main():
    rom=(Path(__file__).resolve().parents[2]/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
    def oracle(state,context,index):
        bus[:2048]=state;bus.events.clear();ref.pc=int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=context[2:7]
        return run_gate(bus,ref,context[7])
    check,cleanup=make_checker(oracle);rng=random.Random(0x83fd)
    for case in range(16384):
        x=0x28+(case//256)%4;s=bytearray(rng.randbytes(2048))
        a=32*(1+case%7)+1+(case//7)%31
        c=bytes((0x83,0xa0,a,x,rng.randrange(256),(case&0xc7)|32,case&255,case>>8))
        s[0x730+x]=case&255;s[0x73c+x]=(case//64)&255
        check(bytes(s),c,resource,0)
    cleanup();print('PASS 16384 independent actual-ROM pitched gate cases, all four indexes, full RAM/context, ordered effects, unmodified raw P and native ABI.')
if __name__=='__main__':main()
