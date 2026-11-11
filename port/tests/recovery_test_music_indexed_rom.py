#!/usr/bin/env python3
"""Independent actual-ROM execution of indexed music parser. Cartridge stays private."""
import hashlib,random
from pathlib import Path
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_music_indexed_contract import make_checker,COMMANDS
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'

def run_original(bus,ref,reserved,index):
    start=len(bus.events)
    for steps in range(200):
        pc=ref.pc
        if steps and index!=3 and pc==(0x83a0 if index==8 else 0x839d):break
        assert (0x83a0<=pc<=0x83e6 or pc==0x839d or 0x8473<=pc<=0x8482 or
                0x856e<=pc<=0x8584 or 0x8023<=pc<=0x8037 or
                0x84cd<=pc<=0x84eb or 0x8551<=pc<=0x855b or
                0x8652<=pc<=0x8698 or 0x86a5<=pc<=0x86b1 or
                0x859b<=pc<=0x85a5 or 0x846d<=pc<=0x8472),hex(pc)
        addr=None
        if pc in (0x857a,0x802c,0x8030):addr=((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
        elif pc in (0x868c,0x8693):addr=0x8a02 if pc==0x868c else 0x8a01
        elif pc in (0x83ba,0x83c1):addr=(0x8585 if pc==0x83ba else 0x858c)+ref.y
        if addr is not None:bus.events.append(('resource',addr,bus[addr],0))
        last=index==3 and pc==0x8472
        ref.step()
        if last:break
    else:raise AssertionError('original timeout')
    raw=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved))
    context=raw[:5]+bytes(((raw[5]&0xef)|0x20,))+raw[6:]
    return bytes(bus[:2048]),context,list(bus.events[start:])

def main():
    rom=(Path(__file__).resolve().parents[2]/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[16+3*16384:16+4*16384]
    bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
    def oracle(state,context,index):
        bus[:2048]=state;bus.events.clear();ref.pc=int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=context[2:7]
        return run_original(bus,ref,context[7],index)
    check,cleanup=make_checker(oracle);rng=random.Random(0x2830);count=0
    for index in range(9):
        for case in range(4096):
            x=0x28+((case//256)%4);s=bytearray(rng.randbytes(2048))
            pointer=(0x8000,0x80ff,0xbfff,0xbffe)[case%4] if case<1024 else 0x8000+rng.randrange(16384)
            if index==5 and pointer==0xbfff:pointer-=1
            s[0x728+x]=pointer&255;s[0x72c+x]=pointer>>8
            a=COMMANDS[index] if index not in (3,8) else 32*(1+case%7) if index==3 else case&255
            p=(case&(0xc7 if index in (0,3) else 0xcf))|0x20
            c=bytes((0x83,0x9d if index==8 else 0xa0,a,x,rng.randrange(256),p,case&255,rng.randrange(256)))
            if index==0 and case%3==0:s[0x700+x]=(resource[pointer-0x8000]+1)&255
            if index==3:s[0x730+x]=case&255
            check(bytes(s),c,resource,index);count+=1
    cleanup();print(f'PASS {count} independent actual-ROM comparisons across all four channel indexes; ordered effects, full state, raw P unmodified, native ABI and bounded resources.')
if __name__=='__main__':main()
