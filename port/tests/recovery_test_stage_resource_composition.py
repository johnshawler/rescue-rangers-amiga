#!/usr/bin/env python3
"""Continuous C6B5 -> C6BD -> C700 -> C2A5 with unmodified live state."""
import hashlib,random,struct
from recovery_test_stage_resource_init import Bus,SHA
from recovery_stage_resource_harness import Native,PORT
from recovery_test_gameplay_fade_entry import Ricoh2A03,prove_binary_sbc

def main():
    alu=prove_binary_sbc();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[16+4*16384+0x193:16+4*16384+0x338];bus=Bus(rom);ref=Ricoh2A03(memory=bus)
    n=Native(journal_size=512);n.install('recovery_gameplay_player_init.s',0x4000);n.install('recovery_gameplay_fade_entry.s',0x5000)
    rng=random.Random(0xc6bd);events=0
    for case in range(4096):
        state=bytearray(rng.randbytes(2048));state[0xf6]=0;state[0x50]=case&1;state[0x31]=case&255
        if case&2:state[0x54]=12
        if case&4:state[0x55]=12
        ctx=bytes((0xc6,0xb5,*rng.randbytes(3),(case>>4)&255,case&255,0x69))
        bus.ram[:]=state;bus.bank=case&7;bus.serial=[];ref.pc=0xc6b5;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        for seg,(entry,target) in enumerate(((0x1000,0xc6bd),(0x4000,0xc700),(0x5000,0xc2a5))):
            bus.events=[]
            for _ in range(1000):
                if ref.pc==target:break
                ref.step()
            else:raise AssertionError('reference timeout')
            got=n.run(state,ctx,rng,resource,entry=entry,resume=bool(seg))
            context=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
            journal=b''.join(struct.pack('>HBB',*e) for e in bus.events)
            expected=(bytes(bus.ram),context,journal+b'\xb6'*(512-len(journal)),len(bus.events),[(a,v) for a,v,k in bus.events if k==0],[(a,v) for a,v,k in bus.events if k==1])
            assert got==expected,(case,seg);state,ctx=got[:2];events+=len(bus.events)
    print(f'PASS {4096} continuous three-helper compositions, {events} ordered events, {alu} SBC truth-table cases; no RAM/context patch between segments.');n.close()
if __name__=='__main__':main()
