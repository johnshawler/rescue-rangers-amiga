#!/usr/bin/env python3
"""Original ROM differential proof: actual bank-3 startup $F0 reset/mute command, returning to fixed NMI."""
from pathlib import Path
import hashlib
import os
import random
import subprocess
import tempfile
import machine68k
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus, apply_ppu

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

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    names=('recovery_audio_reset_command','recovery_reset_ram','recovery_reset_mapper','recovery_reset_video','recovery_reset_dispatch','recovery_first_yield','recovery_first_nmi_prefix','recovery_nmi_audio_entry')
    with tempfile.TemporaryDirectory(prefix='recovery-audio-reset-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in names)+
                          '\n'.join((PORT/'src'/(n+'.s')).read_text() for n in names))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu=m.mem,m.cpu
    mem.w_block(0x1000,code); mem.w16(STOP,0x60fe)
    rng=random.Random(0x8194)
    bus=AudioBus(rom); ref=MPU(memory=bus)
    events=[]; active=0; journal_size=0
    def trace(mode,width,address,value):
        if mode!='W': return
        if BASE<=address<BASE+2048:
            assert width==0
            events.append(('ram',address-BASE,value))
        elif address==JOURNAL and journal_size:
            assert width==1
            if value:
                assert 1<=value<=(20 if active==2 else 5 if active==7 else 7 if active==0 else 10 if active==6 else 1 if active==5 else 2188)
                record=JOURNAL+2+(value-1)*4
                addr,data,last=mem.r16(record),mem.r8(record+2),mem.r8(record+3)
                if active in (2,7): assert last==mem.r8(BASE+0xf5)
                if active==6 and addr==0x4014:
                    assert bytes(mem.r_block(JOURNAL+42,256))==bytes(mem.r_block(BASE+0x200,256))
                events.append(('apu' if active==0 else 'mapper' if active in (2,7) else 'ppu',addr,data,last))
        else:
            assert (JOURNAL+2<=address<JOURNAL+journal_size or CTX<=address<CTX+8
                    or STACK-128<=address<STACK), ('unexpected native write',address)
    mem.set_trace_func(trace)
    guard=bytes(range(16))
    def native(state,context,index=0,status=1):
        nonlocal active,journal_size
        active=index; journal_size={0:30,1:0,2:82,3:8754,4:0,5:6,6:298,7:22}[index]
        journal=rng.randbytes(journal_size)
        mem.set_trace_mode(False)
        for address,data in ((BASE,state),(CTX,context),(JOURNAL,journal)):
            mem.w_block(address-16,guard+data+guard)
        regs=[rng.getrandbits(32) for _ in range(15)]; regs[8:11]=[BASE,CTX,JOURNAL]
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
            kind='apu' if index==0 else 'mapper' if index in (2,7) else 'ppu'
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
    def make_state(flags,sp,c0,y,initial):
        state=bytearray(initial);state[0xcf]=0;state[0xc0]=c0
        state[0x100+((sp+1)&255)]=0xf2;state[0x100+((sp+2)&255)]=0xc0
        context=bytes((0x80,3,0xf0,rng.randrange(256),y,flags,sp,rng.randrange(256)))
        return bytes(state),context
    cases=[make_state(i,i,i,i,bytes([v])*2048) for i in range(256) for v in (0,255,0xa5,0x5a)]
    cases += [make_state(rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randbytes(2048)) for _ in range(1024)]
    expected_apu=[('apu',a,v,1) for a,v in ((0x4000,0x30),(0x4004,0x30),(0x4008,0),(0x400c,0x30),(0x4001,8),(0x4005,8),(0x4015,15))]
    for case,(state,context) in enumerate(cases):
        want=original(state,context);got=native(state,context)
        assert got==want, ('bank-3 reset command mismatch',case)
        assert [e for e in got[2] if e[0]=='apu']==expected_apu
        assert len(got[2])==48
        assert native(got[0],got[1],status=-1)==(*got[:2],[])
    for case in range(256):
        state=rng.randbytes(2048)
        context=bytes((0xfe,0x24))+rng.randbytes(2)+bytes((0,(case&0xcf)|0x20,case,rng.randrange(256)))
        want=original(state,context);merged=[]
        for index in (1,2,3,4,5,6,7,0):
            state,context,part=native(state,context,index);merged+=part
        assert (state,context,merged)==want, ('eight-helper composition mismatch',case)
        assert [e for e in merged if e[0]=='apu']==expected_apu
        assert len([e for e in merged if e[0]=='mapper'])==25 and bus.bank==3
        assert context[:7]==bytes((0xc0,0xf3,0,0xff,0x0c,(case&0x0c)|0x26,0xb4))
        assert state[0xc0]==0 and state[0xcf]==0 and state[0xdb]==1
    def supported():
        return make_state(rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randbytes(2048))
    invalid=0
    for value in range(256):
        if value==0xf0: continue
        state,context=supported();ctx=bytearray(context);ctx[2]=value
        assert native(state,bytes(ctx),status=-1)==(state,bytes(ctx),[]);invalid+=1
    for value in range(1,256):
        state,ctx=supported();state=bytearray(state);state[0xcf]=value;state=bytes(state)
        assert native(state,ctx,status=-1)==(state,ctx,[]);invalid+=1
    for offset,expected in ((1,0xf2),(2,0xc0)):
        for value in range(256):
            if value==expected: continue
            state,ctx=supported();state=bytearray(state);state[0x100+((ctx[6]+offset)&255)]=value;state=bytes(state)
            assert native(state,ctx,status=-1)==(state,ctx,[]);invalid+=1
    state,context=supported()
    for pc in range(65536):
        if pc==0x8003: continue
        ctx=pc.to_bytes(2,'big')+context[2:]
        assert native(state,ctx,status=-1)==(state,ctx,[]);invalid+=1
    m.cleanup()
    print(f'PASS: {len(cases)} actual bank-3 ROM/native $F0 command cases, 48 ordered events each including 7 APU writes.')
    print('PASS: 256 continuous eight-helper reset/yield/hardware-NMI/bank-3-command paths without patches.')
    print(f'PASS: {len(cases)} completed-boundary + {invalid} unsupported-input rejections.')
    print('PASS: full RAM/context/journal, real ROM bank switching, dispatcher scratch/stack, guards and ABI; stop $C0F3.')

if __name__=='__main__': main()
