#!/usr/bin/env python3
"""Continuous C6B5 -> C6BD -> C700 -> C2A5 -> FE8D with unmodified live state."""
import hashlib,random,struct
from recovery_test_stage_resource_init import Bus,SHA
from recovery_general_scheduler_harness import Native as Scheduler,RAM,CTX,JOURNAL,STACK,STOP
from recovery_test_general_scheduler import Bus as SchedulerBus,advance as schedule
from recovery_stage_resource_harness import Native,PORT
from recovery_test_gameplay_fade_entry import Ricoh2A03,prove_binary_sbc

def main():
    alu=prove_binary_sbc();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[16+4*16384+0x193:16+4*16384+0x338];bus=Bus(rom);ref=Ricoh2A03(memory=bus)
    n=Native(journal_size=512);n.install('recovery_gameplay_player_init.s',0x4000);n.install('recovery_gameplay_fade_entry.s',0x5000);n.install('recovery_gameplay_frame_yield.s',0x6000)
    n.install('recovery_general_task_scheduler.s',0x7000)
    scheduler=Scheduler.__new__(Scheduler);scheduler.__dict__.update(n.__dict__);scheduler.size=74;scheduler.effects=[];scheduler.stores=[]
    scheduler.reads=[n.reads[-1],(STOP,2),(RAM,2048),(CTX,8),(JOURNAL,74),(STACK-256,260)]
    scheduler.writes=[(RAM,2048),(CTX,8),(JOURNAL,74),(STACK-256,256)]
    sb=SchedulerBus(rom);sr=Ricoh2A03(memory=sb,pc=0xfe8d)
    rng=random.Random(0xc6bd);events=0
    for case in range(4096):
        state=bytearray(rng.randbytes(2048));state[0xf6]=0;state[0x91]=0;
        for i in range(4):state[0x80+4*i]=0
        state[0x50]=case&1;state[0x31]=case&255
        if case&2:state[0x54]=12
        if case&4:state[0x55]=12
        ctx=bytes((0xc6,0xb5,*rng.randbytes(3),(case>>4)&255,case&255,0x69))
        bus.ram[:]=state;bus.bank=case&7;bus.serial=[];ref.pc=0xc6b5;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        for seg,(entry,target) in enumerate(((0x1000,0xc6bd),(0x4000,0xc700),(0x5000,0xc2a5),(0x6000,0xfe8d))):
            bus.events=[]
            for _ in range(1000):
                if ref.pc==target:break
                ref.step()
            else:raise AssertionError('reference timeout')
            n.mem.set_trace_func(n.trace)
            got=n.run(state,ctx,rng,resource,entry=entry,resume=bool(seg))
            context=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
            journal=b''.join(struct.pack('>HBB',*e) for e in bus.events)
            expected=(bytes(bus.ram),context,journal+b'\xb6'*(512-len(journal)),len(bus.events),[(a,v) for a,v,k in bus.events if k==0],[(a,v) for a,v,k in bus.events if k==1])
            assert got==expected,(case,seg);state,ctx=got[:2];events+=len(bus.events)
        # No readiness patch: the yielded task is waiting and others inactive.
        sb.ram[:]=state;sb.events=[];sr.pc=0xfe8d;sr.a,sr.x,sr.y,sr.p,sr.sp=ctx[2:7]
        status=schedule(sr);assert status==0
        assert state[0x80]==1 and state[0x18]==255
        n.mem.set_trace_func(scheduler.trace)
        out=scheduler.run(state,ctx,rng,entry=0x7000,resume=True)
        expected_ctx=sr.pc.to_bytes(2,'big')+bytes((sr.a,sr.x,sr.y,sr.p,sr.sp,ctx[7]))
        assert out[0]==sb.ram and out[1]==expected_ctx and out[3]==0 and out[4]==sb.events
        # Reentry at the honest scan boundary cannot make a task ready.
        sb.events=[];assert schedule(sr)==0
        again=scheduler.run(out[0],out[1],rng,entry=0x7000,resume=True)
        assert again[0]==sb.ram and again[3]==0 and again[4]==sb.events
    print(f'PASS {4096} continuous stage/frame-yield/general-scheduler idle compositions, {events} ordered events, {alu} SBC truth-table cases; no RAM/context patch between segments.');n.close()
if __name__=='__main__':main()
