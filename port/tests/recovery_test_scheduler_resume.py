#!/usr/bin/env python3
"""Original-ROM controller bus and bounded scheduler resumption differential proof."""
from pathlib import Path
import hashlib
import os
import random
import subprocess
import tempfile
import machine68k
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus

PORT=Path(__file__).resolve().parents[1]
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
BASE,CTX,JOURNAL,STOP,STACK=0x10000,0x12000,0x13000,0x800,0x1f0000

PENDING=(0xf0,0x9a,0x18,0x19,0x1a,0x1b,0x1c,0x1d)
class AudioBus(OriginalBus):
    def __init__(self,rom):
        super().__init__(rom)
        self.rom=rom
        self.dma=[]
        self.bits=[]
        self.bank=3
        self.map_bank(3)
    def map_bank(self,bank):
        assert 0<=bank<8
        self.bank=bank
        list.__setitem__(self,slice(0x8000,0xc000),self.rom[16+bank*16384:16+(bank+1)*16384])
    def __setitem__(self,address,value):
        if address in (0x4000,0x4004,0x4008,0x400c,0x4001,0x4005,0x4015):
            self.events.append(('apu',address,value,1));return
        if address in (0x2001,0x2003,0x2005,0x4014):
            self.events.append(('ppu',address,value,1))
            if address==0x4014:
                assert value==2
                self.dma.append(bytes(self[0x200:0x300]))
            return
        super().__setitem__(address,value)
        if address==0xfff0:
            self.bits.append(value&1)
            if len(self.bits)==5:
                self.map_bank(sum(bit<<i for i,bit in enumerate(self.bits))&15)
                self.bits.clear()

class ControllerBus(AudioBus):
    inputs=(0,0)
    pos=[0,0]
    def __getitem__(self,address):
        if isinstance(address,int) and address in (0x4016,0x4017):
            port=address-0x4016; bit=self.pos[port]
            assert bit<8
            value=(self.inputs[port]>>(7-bit))&1
            self.pos[port]+=1
            self.events.append(('controller',address,value,0))
            return value
        return super().__getitem__(address)
    def __setitem__(self,address,value):
        if address==0x4016:
            self.events.append(('controller',address,value,1))
            self.pos=[0,0]
            return
        return super().__setitem__(address,value)

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    names=('recovery_audio_reset_command','recovery_reset_ram','recovery_reset_mapper','recovery_reset_video','recovery_reset_dispatch','recovery_first_yield','recovery_first_nmi_prefix','recovery_nmi_audio_entry','recovery_silent_tick_rti','recovery_scheduler_resume')
    with tempfile.TemporaryDirectory(prefix='recovery-silent-tick-rti-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in names)+
                          '\n'.join((PORT/'src'/(n+'.s')).read_text() for n in names))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu=m.mem,m.cpu
    mem.w_block(0x1000,code); mem.w16(STOP,0x60fe)
    rng=random.Random(0x8194)
    bus=ControllerBus(rom); ref=MPU(memory=bus)
    events=[]; active=0; journal_size=0
    def trace(mode,width,address,value):
        if mode!='W': return
        if BASE<=address<BASE+2048:
            assert width==0
            events.append(('ram',address-BASE,value))
        elif address==JOURNAL and journal_size:
            assert width==1
            if value:
                assert 1<=value<=(18 if active==9 else 20 if active==2 else 5 if active in (7,8) else 7 if active==0 else 10 if active==6 else 1 if active==5 else 2188)
                record=JOURNAL+2+(value-1)*4
                addr,data,last=mem.r16(record),mem.r8(record+2),mem.r8(record+3)
                if active in (2,7,8): assert last==mem.r8(BASE+0xf5)
                if active==6 and addr==0x4014:
                    assert bytes(mem.r_block(JOURNAL+42,256))==bytes(mem.r_block(BASE+0x200,256))
                events.append(('controller' if active==9 else 'apu' if active==0 else 'mapper' if active in (2,7,8) else 'ppu',addr,data,last))
        else:
            assert (JOURNAL+2<=address<JOURNAL+journal_size or CTX<=address<CTX+8
                    or STACK-128<=address<STACK), ('unexpected native write',address)
    mem.set_trace_func(trace)
    guard=bytes(range(16))
    def native(state,context,index=0,status=1,inputs=(0,0)):
        nonlocal active,journal_size
        active=index; journal_size={0:30,1:0,2:82,3:8754,4:0,5:6,6:298,7:22,8:22,9:74}[index]
        journal=rng.randbytes(journal_size)
        mem.set_trace_mode(False)
        for address,data in ((BASE,state),(CTX,context),(JOURNAL,journal)):
            mem.w_block(address-16,guard+data+guard)
        regs=[rng.getrandbits(32) for _ in range(15)]; regs[8:11]=[BASE,CTX,JOURNAL]
        if index==9:
            regs[0]=(regs[0]&0xffffff00)|inputs[0]
            regs[1]=(regs[1]&0xffffff00)|inputs[1]
        cpu.w_sr(0x2700); cpu.w_sp(STACK); mem.w32(STACK,STOP)
        for i,value in enumerate(regs): cpu.w_reg(i,value)
        cpu.w_pc(0x1000+index*4)
        events.clear(); mem.set_trace_mode(True)
        for _ in range(1000):
            cpu.execute(1000)
            if cpu.r_pc()==STOP: break
        else: raise AssertionError('native timeout')
        mem.set_trace_mode(False)
        assert cpu.r_reg(0)==status&0xffffffff
        assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
        assert cpu.r_sp()==STACK+4
        for address,size in ((BASE,2048),(CTX,8),(JOURNAL,journal_size)):
            assert bytes(mem.r_block(address-16,16))==guard
            assert bytes(mem.r_block(address+size,16))==guard
        output_journal=bytes(mem.r_block(JOURNAL,journal_size))
        if status == -1:
            assert output_journal == journal
        elif journal_size:
            kind='controller' if index==9 else 'apu' if index==0 else 'mapper' if index in (2,7,8) else 'ppu'
            published=[e for e in events if e[0]==kind]
            expected=len(published).to_bytes(2,'big')+b''.join(
                addr.to_bytes(2,'big')+bytes((data,last)) for _,addr,data,last in published)
            if index==6:
                expected += state[0x200:0x300]
            assert output_journal == expected
        return bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(events)
    def original(state,context):
        bus[:2048]=state; bus.events.clear(); bus.dma.clear(); bus.bits.clear(); bus.map_bank(3); bus.status=rng.randrange(256)
        ref.pc=int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=context[2:7]
        direct_entry = ref.pc == 0x8003
        entered_task = ref.pc in (0xc574,0xfe8d)
        injected = False
        for _ in range(50000):
            if ref.pc == 0xc574: entered_task = True
            if entered_task and ref.pc==0xfe8d and not injected:
                ref.nmi()
                injected = True
            if ref.pc==0x8003: assert bus.bank==3
            if ref.pc==0xc0f3: break
            assert (0xfe24<=ref.pc<=0xfe88 or 0xfe89<=ref.pc<=0xfec4
                    or 0xfed5<=ref.pc<=0xfee4 or 0xfef9<=ref.pc<=0xfefc
                    or 0xc1ba<=ref.pc<=0xc205 or 0xc21e<=ref.pc<=0xc234
                    or 0xff04<=ref.pc<=0xff1e or 0xff1f<=ref.pc<=0xff74
                    or ref.pc==0x8003 or 0x8023<=ref.pc<=0x8039 or 0x80e1<=ref.pc<=0x80ed
                    or 0x817d<=ref.pc<=0x8183 or 0x8194<=ref.pc<=0x81ef or 0x80bb<=ref.pc<=0x80ce
                    or 0xc000<=ref.pc<=0xc0f2 or 0xc574<=ref.pc<=0xc583 or 0xf377<=ref.pc<=0xf391 or ref.pc==0xfef7), ('unsupported original boundary',hex(ref.pc))
            ref.step()
        else: raise AssertionError('original timeout')
        ctx=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,context[7]))
        if not direct_entry:
            assert injected and len(bus.dma)==1
            assert bus.dma[0]==bytes(bus[0x200:0x300])
        return bytes(bus[:2048]),ctx,list(bus.events)
    def context_of(reserved):
        return ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved))
    def architectural_status_view(context):
        """py65 RTI's virtual B is not persistent hardware state; NEVER edit ref.p."""
        return context[:5]+bytes(((context[5]&0xef)|0x20,))+context[6:]
    def tail(reserved):
        assert ref.pc==0xc0f3 and bus.bank==3 and not bus.bits
        saved=bytes(bus[0x1b5:0x1bc]); start=len(bus.events)
        steps=0
        while ref.pc!=0xfe8d:
            assert (0xc0dc<=ref.pc<=0xc114 or ref.pc==0x8000 or
                    0x803a<=ref.pc<=0x8097 or ref.pc==0x80ba or
                    0x8363<=ref.pc<=0x836d or ref.pc==0x839c), hex(ref.pc)
            ref.step();steps+=1
            assert steps<=144
        assert steps==144 and bus.bank==6 and not bus.bits
        raw=context_of(reserved)
        assert raw[5]==saved[4]|0x30
        assert raw[5] in (0xb0,0xb4,0xb8,0xbc)
        assert bytes(bus[0x1b5:0x1bc])==saved
        part=bus.events[start:]
        assert len(part)==31 and sum(e[0]=='ram' for e in part)==26
        assert [e for e in part if e[0]=='mapper']==[('mapper',0xfff0,v,0) for v in (6,3,1,0,0)]
        assert not any(e[0]=='apu' for e in part)
        return bytes(bus[:2048]),architectural_status_view(raw),list(part),raw
    def resume(reserved,inputs):
        assert ref.pc==0xfe8d
        bus.inputs=inputs;bus.pos=[0,0]
        start=len(bus.events)
        for steps in range(1000):
            if ref.pc==0xc584:break
            assert 0xfe8d<=ref.pc<=0xfed4 or 0xc162<=ref.pc<=0xc1b9, hex(ref.pc)
            ref.step()
        else:raise AssertionError('resume timeout')
        raw=context_of(reserved)
        assert bus.pos==[8,8]
        return bytes(bus[:2048]),architectural_status_view(raw),list(bus.events[start:])
    def supported(seed,p=0xa4):
        state=bytearray(seed)
        state[0x80]=4;state[0x82]=0xbb
        state[0x1bc:0x1c0]=bytes((8,0xbf,0x83,0xc5))
        return bytes(state),bytes((0xfe,0x8d,0,0xbb,0,p,0xbb,rng.randrange(256)))
    count=0
    def check(state,ctx,inputs):
        nonlocal count
        bus[:2048]=state;bus.events.clear();bus.map_bank(6)
        ref.pc=0xfe8d;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        want=resume(ctx[7],inputs)
        got=native(state,ctx,9,inputs=inputs)
        assert got==want,('standalone',count,inputs,[(hex(i),a,b) for i,(a,b) in enumerate(zip(got[0],want[0])) if a!=b],got[1],want[1],got[2],want[2])
        assert native(got[0],got[1],9,-1,inputs)==(*got[:2],[])
        count+=1
    # Exhaust edges and opposing directions; complementary second controller.
    for current in range(256):
        for previous in range(256):
            state,ctx=supported(bytes([current])*2048,0xa0|((previous&3)<<2))
            state=bytearray(state);state[0x16]=previous;state[0x17]=previous^255
            check(bytes(state),ctx,(current,current^255))
    for _ in range(1024):
        state,ctx=supported(rng.randbytes(2048),rng.choice((0xa0,0xa4,0xa8,0xac)))
        check(state,ctx,(rng.randrange(256),rng.randrange(256)))
    for case in range(256):
        state=rng.randbytes(2048)
        ctx=bytes((0xfe,0x24))+rng.randbytes(2)+bytes((0,(case&0xcf)|0x20,case,rng.randrange(256)))
        prefix=original(state,ctx)
        tick=tail(ctx[7])
        raw_p=ref.p
        want=resume(ctx[7],(0,0))
        all_events=prefix[2]+tick[2]+want[2]
        merged=[]
        for index in (1,2,3,4,5,6,7,0,8,9):
            state,ctx,part=native(state,ctx,index);merged+=part
        assert (state,ctx,merged)==(want[0],want[1],all_events),('composition',case)
        assert raw_p==tick[3][5] and raw_p in (0xb0,0xb4,0xb8,0xbc)
        assert ref.p&0x10 and ctx[5]&0x10==0
        assert ctx[:5]==bytes((0xc5,0x84,0xbf,0xbf,8)) and ctx[6]==0xbf
    invalid=0
    state,ctx=supported(rng.randbytes(2048))
    def reject(state,ctx):
        nonlocal invalid
        assert native(state,ctx,9,-1)==(state,ctx,[])
        invalid+=1
    for pc in range(65536):
        if pc!=0xfe8d:reject(state,pc.to_bytes(2,'big')+ctx[2:])
    for offset in range(2,7):
        for value in range(256):
            if value==ctx[offset] or offset==5 and value in (0xa0,0xa4,0xa8,0xac):continue
            changed=bytearray(ctx);changed[offset]=value
            reject(state,bytes(changed))
    for address in (0x80,0x82,*range(0x1bc,0x1c0)):
        for value in range(256):
            if value==state[address]:continue
            changed=bytearray(state);changed[address]=value
            reject(bytes(changed),ctx)
    m.cleanup()
    print(f'PASS: {count} standalone original-ROM/native scheduler resume cases; full RAM/context/ordered controller and RAM events.')
    print('PASS: 256 continuous ten-helper reset/real-NMI/tick/RTI/resume compositions with no game-state patches, stopping before C584.')
    print(f'PASS: {invalid} unsupported-input and {count} completed-boundary inert rejections; buffer guards, preserved registers, balanced stack.')

if __name__=='__main__': main()
