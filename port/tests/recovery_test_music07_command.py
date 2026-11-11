#!/usr/bin/env python3
"""Original-ROM command07 and continuous fourteen-call thirteen-helper proof."""
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
    names=('recovery_audio_reset_command','recovery_reset_ram','recovery_reset_mapper','recovery_reset_video','recovery_reset_dispatch','recovery_first_yield','recovery_first_nmi_prefix','recovery_nmi_audio_entry','recovery_silent_tick_rti','recovery_scheduler_resume','recovery_resumed_task_setup','recovery_palette_nmi_prefix','recovery_music07_command')
    with tempfile.TemporaryDirectory(prefix='recovery-silent-tick-rti-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in names)+
                          '\n'.join((PORT/'src'/(n+'.s')).read_text() for n in names))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu=m.mem,m.cpu
    resources=rom[16+3*16384:16+4*16384]
    mem.w_block(0x20000,resources)
    mem.w_block(0x1000,code); mem.w16(STOP,0x60fe)
    rng=random.Random(0x8194)
    bus=ControllerBus(rom); ref=MPU(memory=bus)
    events=[]; active=0; journal_size=0; resource_reads=[]
    def trace(mode,width,address,value):
        if 0x20000<=address<0x24000:
            assert mode=='R' and width==0, ('resource write or wide read',mode,width,address)
            resource_reads.append(address-0x20000)
            return
        if mode!='W': return
        if BASE<=address<BASE+2048:
            assert width==0
            events.append(('ram',address-BASE,value))
        elif address==JOURNAL and journal_size:
            assert width==1
            if value:
                assert 1<=value<=(7 if active==12 else 49 if active==11 else 18 if active==9 else 20 if active==2 else 5 if active in (7,8) else 7 if active==0 else 10 if active==6 else 1 if active==5 else 2188)
                record=JOURNAL+2+(value-1)*4
                addr,data,last=mem.r16(record),mem.r8(record+2),mem.r8(record+3)
                if active in (2,7,8): assert last==mem.r8(BASE+0xf5)
                if active in (6,11) and addr==0x4014:
                    assert bytes(mem.r_block(JOURNAL+(198 if active==11 else 42),256))==bytes(mem.r_block(BASE+0x200,256))
                events.append(('controller' if active==9 else 'apu' if active in (0,12) else 'mapper' if active in (2,7,8) else 'ppu',addr,data,last))
        else:
            assert (JOURNAL+2<=address<JOURNAL+journal_size or CTX<=address<CTX+8
                    or STACK-128<=address<STACK), ('unexpected native write',address)
    mem.set_trace_func(trace)
    guard=bytes(range(16))
    def native(state,context,index=0,status=1,inputs=(0,0)):
        nonlocal active,journal_size
        active=index; journal_size={0:30,1:0,2:82,3:8754,4:0,5:6,6:298,7:22,8:22,9:74,10:0,11:454,12:30}[index]
        journal=rng.randbytes(journal_size)
        mem.set_trace_mode(False)
        for address,data in ((BASE,state),(CTX,context),(JOURNAL,journal)):
            mem.w_block(address-16,guard+data+guard)
        regs=[rng.getrandbits(32) for _ in range(15)]; regs[8:11]=[BASE,CTX,JOURNAL]
        if index==12: regs[11]=0x20000
        if index==9:
            regs[0]=(regs[0]&0xffffff00)|inputs[0]
            regs[1]=(regs[1]&0xffffff00)|inputs[1]
        cpu.w_sr(0x2700); cpu.w_sp(STACK); mem.w32(STACK,STOP)
        for i,value in enumerate(regs): cpu.w_reg(i,value)
        cpu.w_pc(0x1000+index*4)
        events.clear(); resource_reads.clear(); mem.set_trace_mode(True)
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
        if index==12 and status==1:
            pointer=(resources[0xa11]<<8)|resources[0xa12]
            assert resource_reads==[0xa00,0xa11,0xa12,pointer-0x8000]+list(range(pointer-0x8000+1,pointer-0x8000+9)),resource_reads
        assert bytes(mem.r_block(0x20000,16384))==resources if status==1 else True
        output_journal=bytes(mem.r_block(JOURNAL,journal_size))
        if status == -1:
            assert output_journal == journal
        elif journal_size:
            kind='controller' if index==9 else 'apu' if index in (0,12) else 'mapper' if index in (2,7,8) else 'ppu'
            published=[e for e in events if e[0]==kind]
            expected=len(published).to_bytes(2,'big')+b''.join(
                addr.to_bytes(2,'big')+bytes((data,last)) for _,addr,data,last in published)
            if index in (6,11):
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
    def setup(reserved):
        assert ref.pc==0xc584
        start=len(bus.events)
        steps=0
        while ref.pc!=0xfe8d:
            assert (0xc584<=ref.pc<=0xc593 or 0xf377<=ref.pc<=0xf391 or
                    0xc274<=ref.pc<=0xc2a7 or 0xff04<=ref.pc<=0xff1e or
                    0xfef7<=ref.pc<=0xfefc), hex(ref.pc)
            ref.step();steps+=1
            assert steps<1000
        raw=context_of(reserved)
        part=list(bus.events[start:])
        assert all(e[0]=='ram' for e in part)
        assert len(part) in (89,91),len(part)
        assert raw[:5]==bytes((0xfe,0x8d,0,0xb8,0)) and raw[6]==0xb8
        return bytes(bus[:2048]),architectural_status_view(raw),part
    def palette_nmi(reserved):
        assert ref.pc==0xfe8d
        start=len(bus.events); old_dma=len(bus.dma)
        saved_sp=ref.sp
        frame=(0xfe,0x8d,(ref.p&0xef)|0x20,ref.p|0x34,ref.a,ref.x,ref.y)
        ref.nmi()
        for steps in range(1000):
            if ref.pc==0xc0bf:break
            assert 0xc000<=ref.pc<0xc0bf,hex(ref.pc)
            ref.step()
        else:raise AssertionError('palette NMI timeout')
        assert tuple(bus[0x100+((saved_sp-i)&255)] for i in range(7))==frame
        assert ref.sp==(saved_sp-7)&255
        assert len(bus.dma)==old_dma+1
        assert bus.dma[-1]==bytes(bus[0x200:0x300])
        return bytes(bus[:2048]),architectural_status_view(context_of(reserved)),list(bus.events[start:])
    def command(reserved):
        assert ref.pc==0x8003 and ref.a==7 and bus.bank==3
        start=len(bus.events)
        for steps in range(1000):
            if ref.pc==0xc0f3: break
            assert (ref.pc==0x8003 or 0x80bb<=ref.pc<=0x80ce or
                    0x80e1<=ref.pc<=0x810f or 0x8152<=ref.pc<=0x817b or
                    0x81c0<=ref.pc<=0x81ef),hex(ref.pc)
            ref.step()
        else:raise AssertionError('command timeout')
        return bytes(bus[:2048]),architectural_status_view(context_of(reserved)),list(bus.events[start:])
    count=0
    for case in range(2048):
        state=bytearray(rng.randbytes(2048));state[0xcf]=0
        sp=case&255
        state[0x100+((sp+1)&255)]=0xf2;state[0x100+((sp+2)&255)]=0xc0
        state[0xc0]=case&255
        ctx=bytes((0x80,3,7,rng.randrange(256),rng.randrange(256),(case&0xcf)|0x20,sp,rng.randrange(256)))
        bus[:2048]=state;bus.events.clear();bus.map_bank(3)
        ref.pc=0x8003;ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
        want=command(ctx[7]);got=native(bytes(state),ctx,12)
        assert got==want,('command',case,got[1],want[1],got[2],want[2])
        assert native(got[0],got[1],12,-1)==(*got[:2],[])
        count+=1
    for case in range(256):
        state=rng.randbytes(2048)
        # D is deliberately clear: this slice rejects decimal-mode contexts.
        ctx=bytes((0xfe,0x24))+rng.randbytes(2)+bytes((0,(case&0xc7)|0x20,case,rng.randrange(256)))
        prefix=original(state,ctx)
        tick=tail(ctx[7])
        polled=resume(ctx[7],(case,case^255))
        prepared=setup(ctx[7])
        assert prepared[0][0x18]==255 and prepared[1][6]==0xb8
        assert ref.p&0x10 and prepared[1][5]&0x10==0
        queued=bytes(bus[0xd9:0xe4]); nested=bytes(bus[0x1b9:0x1c0])
        want=palette_nmi(ctx[7])
        all_events=prefix[2]+tick[2]+polled[2]+prepared[2]+want[2]
        merged=[]
        for index in (1,2,3,4,5,6,7,0,8,9,10,11):
            state,ctx,part=native(state,ctx,index,inputs=(case,case^255));merged+=part
        assert (state,ctx,merged)==(want[0],want[1],all_events),('composition',case)
        assert ref.p&0x10==0 and ctx[5]&0x10==0
        assert state[0xd9:0xe4]==queued and state[0xd9]==7
        assert 7 in state[0xdc:0xe4] and state[0x18]==0
        assert ctx[:2]==bytes((0xc0,0xbf)) and ctx[6]==0xb1
        assert state[0x1b9:0x1c0]==nested
        assert state[0x1b9:0x1c0]==bytes((0xff,0x10,0xa7,0xc2,4,0x93,0xc5))
        start=len(bus.events)
        while ref.pc!=0x8003:ref.step()
        intake=(bytes(bus[:2048]),architectural_status_view(context_of(ctx[7])),list(bus.events[start:]))
        state,ctx,part=native(state,ctx,7)
        assert (state,ctx,part)==intake
        want=command(ctx[7]); got=native(state,ctx,12)
        assert got==want,('composed command',case)
        assert sum(e[0]=='ram' for e in got[2])==122
        assert sum(e[0]=='apu' for e in got[2])==7
        assert got[1][:2]==bytes((0xc0,0xf3)) and got[1][6]==0xb1
        assert got[0][0x1b9:0x1c0]==nested

    invalid=0
    state=bytearray(rng.randbytes(2048));state[0xcf]=0
    state[0x1b0]=0xf2;state[0x1b1]=0xc0
    ctx=bytes((0x80,3,7,0,0,0x24,0xaf,0))
    def reject(state,ctx):
        nonlocal invalid
        assert native(bytes(state),bytes(ctx),12,-1)==(bytes(state),bytes(ctx),[])
        invalid+=1
    for pc in range(65536):
        if pc!=0x8003:reject(state,pc.to_bytes(2,'big')+ctx[2:])
    for value in range(256):
        if value!=7:reject(state,ctx[:2]+bytes((value,))+ctx[3:])
        if value&0x30!=0x20:reject(state,ctx[:5]+bytes((value,))+ctx[6:])
        if value:
            changed=bytearray(state);changed[0xcf]=value;reject(changed,ctx)
        for addr,expected in ((0x1b0,0xf2),(0x1b1,0xc0)):
            if value!=expected:
                changed=bytearray(state);changed[addr]=value;reject(changed,ctx)
    for value in range(8):
        mem.w8(0x20a00,value);reject(state,ctx)
    mem.w_block(0x20000,resources)
    for pointer in (0,0x7fff,0xbff8,0xffff):
        mem.w8(0x20a11,pointer>>8);mem.w8(0x20a12,pointer&255);reject(state,ctx)
    mem.w_block(0x20000,resources)
    pointer=(resources[0xa11]<<8)|resources[0xa12]
    for value in range(1,256):
        mem.w8(0x20000+pointer-0x8000,value);reject(state,ctx)
    mem.w_block(0x20000,resources)
    m.cleanup()
    print(f'PASS: {count} standalone command07 comparisons; full RAM/context/ordered RAM and APU effects/ABI.')
    print('PASS: 256 continuous fourteen-call thirteen-helper comparisons, two actual NMIs, no oracle patches; stop C0F3.')
    print(f'PASS: {invalid} unsupported guards plus {count} completed-boundary inert rejections.')

if __name__=='__main__':main()
