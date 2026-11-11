#!/usr/bin/env python3
"""Private independently executed actual-ROM FF04/C2A5 differential."""
import hashlib,random
from recovery_test_gameplay_fade_entry import Bus,Ricoh2A03,SHA,advance,compare
from recovery_frame_yield_harness import Native,PORT

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    bus=Bus(rom);ref=Ricoh2A03(memory=bus);n=Native();rng=random.Random(0xfe8d);count=events=0
    for pc in (0xc2a5,0xff04):
        for p in range(256):
            for sp in range(256):
                ram=bytearray(rng.randbytes(2048));ram[0x91]=(p+sp)&255
                ctx=pc.to_bytes(2,'big')+rng.randbytes(3)+bytes((p,sp,0x96))
                bus[:2048]=ram;bus.events=[];ref.pc=pc;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
                advance(ref,0xfe8d);compare(n,bus,ref,ram,ctx,rng);count+=1;events+=len(bus.events)
    print(f'PASS {count} actual-ROM cases; {events} ordered stores');n.close()
if __name__=='__main__':main()
