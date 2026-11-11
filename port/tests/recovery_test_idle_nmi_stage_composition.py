#!/usr/bin/env python3
"""One live reference/native stage prefix -> scheduler FE90 -> actual NMI C0BF."""
import hashlib,random,struct
from recovery_test_stage_resource_init import Bus as StageBus,SHA
from recovery_general_scheduler_harness import Native as Scheduler,RAM,CTX,JOURNAL,STACK,STOP
from recovery_test_general_scheduler import advance as schedule
from recovery_stage_resource_harness import Native,PORT
from recovery_test_gameplay_fade_entry import Ricoh2A03,prove_binary_sbc
from recovery_idle_nmi_harness import Native as NMI
from recovery_test_idle_nmi_prefix import Bus as NMIBus,compare
class Bus(StageBus):
    nmi_mode=False
    status=0
    def __getitem__(self,a):
        if self.nmi_mode:return NMIBus.__getitem__(self,a)
        return super().__getitem__(a)
    def __setitem__(self,a,v):
        if self.nmi_mode:return NMIBus.__setitem__(self,a,v)
        return super().__setitem__(a,v)
def main():
    alu=prove_binary_sbc();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[16+4*16384+0x193:16+4*16384+0x338];bus=Bus(rom);bus.fixed=rom[16+7*16384:16+8*16384];ref=Ricoh2A03(memory=bus)
    n=Native(journal_size=512)
    for source,at in (('gameplay_player_init',0x4000),('gameplay_fade_entry',0x5000),('gameplay_frame_yield',0x6000),('general_task_scheduler',0x7000),('idle_nmi_prefix',0x8000)):n.install('recovery_'+source+'.s',at)
    def shared(cls,size,code_range):
        x=cls.__new__(cls);x.__dict__.update(n.__dict__);x.size=size;x.effects=[];x.stores=[]
        x.reads=[code_range,(STOP,2),(RAM,2048),(CTX,8),(JOURNAL,size),(STACK-256,260)]
        x.writes=[(RAM,2048),(CTX,8),(JOURNAL,size),(STACK-256,256)]
        return x
    scheduler=shared(Scheduler,74,n.reads[-2]);interrupt=shared(NMI,454,n.reads[-1])
    rng=random.Random(0xc690);events=0
    for case in range(4096):
        state=bytearray(rng.randbytes(2048));state[0xf6]=0;state[0x91]=0
        # Declared initial synthetic-stage environment, never patched after entry.
        state[0xf0]=state[0x9a]=0;state[0x19:0x1e]=bytes(5)
        for i in range(4):state[0x80+4*i]=0
        state[0x50]=case&1;state[0x31]=case&255
        if case&2:state[0x54]=12
        if case&4:state[0x55]=12
        ctx=bytes((0xc6,0xb5,*rng.randbytes(3),(case>>4)&255,case&255,0x69))
        bus.ram[:]=state;bus.bank=case&7;bus.serial=[];bus.nmi_mode=False;ref.pc=0xc6b5;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        for seg,(entry,target) in enumerate(((0x1000,0xc6bd),(0x4000,0xc700),(0x5000,0xc2a5),(0x6000,0xfe8d))):
            bus.events=[]
            for _ in range(1000):
                if ref.pc==target:break
                ref.step()
            else:raise AssertionError('reference timeout')
            n.mem.set_trace_func(n.trace);got=n.run(state,ctx,rng,resource,entry=entry,resume=bool(seg))
            context=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
            journal=b''.join(struct.pack('>HBB',*e) for e in bus.events)
            expected=(bytes(bus.ram),context,journal+b'\xb6'*(512-len(journal)),len(bus.events),[(a,v) for a,v,k in bus.events if k==0],[(a,v) for a,v,k in bus.events if k==1])
            assert got==expected,(case,seg);state,ctx=got[:2];events+=len(bus.events)
        for scan in range(2):
            bus.events=[];assert schedule(ref)==0
            n.mem.set_trace_func(scheduler.trace);out=scheduler.run(state,ctx,rng,entry=0x7000,resume=True)
            context=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
            assert out[0]==bus.ram and out[1]==context and out[3]==0
            assert out[4]==[('ram',a,v) for a,v,k in bus.events]
            state,ctx=out[:2];assert ctx[:2]==b'\xfe\x90' and state[0x80]==1 and state[0x18]==255
        bus.nmi_mode=True;bus.status=case&255;bank=bus.bank
        n.mem.set_trace_func(interrupt.trace);got=compare(interrupt,bus,ref,state,ctx,rng,entry=0x8000,resume=True)
        assert got[0][0x80]==4 and got[0][0x81]==0 and got[0][0x18]==0
        assert bus.bank==bank and not bus.serial and ref.pc==0xc0bf
        events+=len(bus.events)
    print(f'PASS 4096 continuous stage/player/fade/yield/two-idle-scan/NMI compositions; {events} ordered prefix/NMI effects; {alu} SBC cases. No captured state or between-call RAM/context patches; stop C0BF.');n.close()
if __name__=='__main__':main()
