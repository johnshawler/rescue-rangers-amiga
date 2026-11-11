#!/usr/bin/env python3
"""Original ROM differential proof: fixed-bank continuation, stopping at bank-3 audio entry."""
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
class NmiBus(OriginalBus):
    def __init__(self,rom):
        super().__init__(rom)
        self.dma=[]
    def __setitem__(self,address,value):
        if address in (0x2001,0x2003,0x2005,0x4014):
            self.events.append(('ppu',address,value,1))
            if address==0x4014:
                assert value==2
                self.dma.append(bytes(self[0x200:0x300]))
            return
        super().__setitem__(address,value)

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    names=('recovery_nmi_audio_entry','recovery_reset_ram','recovery_reset_mapper','recovery_reset_video','recovery_reset_dispatch','recovery_first_yield','recovery_first_nmi_prefix')
    with tempfile.TemporaryDirectory(prefix='recovery-audio-entry-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in names)+
                          '\n'.join((PORT/'src'/(n+'.s')).read_text() for n in names))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu=m.mem,m.cpu
    mem.w_block(0x1000,code); mem.w16(STOP,0x60fe)
    rng=random.Random(0xc0bf)
    bus=NmiBus(rom); ref=MPU(memory=bus)
    events=[]; active=0; journal_size=0
    def trace(mode,width,address,value):
        if mode!='W': return
        if BASE<=address<BASE+2048:
            assert width==0
            events.append(('ram',address-BASE,value))
        elif address==JOURNAL and journal_size:
            assert width==1
            if value:
                assert 1<=value<=(20 if active==2 else 5 if active==0 else 10 if active==6 else 1 if active==5 else 2188)
                record=JOURNAL+2+(value-1)*4
                addr,data,last=mem.r16(record),mem.r8(record+2),mem.r8(record+3)
                if active in (0,2): assert last==mem.r8(BASE+0xf5)
                if active==6 and addr==0x4014:
                    assert bytes(mem.r_block(JOURNAL+42,256))==bytes(mem.r_block(BASE+0x200,256))
                events.append(('mapper' if active in (0,2) else 'ppu',addr,data,last))
        else:
            assert (JOURNAL+2<=address<JOURNAL+journal_size or CTX<=address<CTX+8
                    or STACK-128<=address<STACK), ('unexpected native write',address)
    mem.set_trace_func(trace)
    guard=bytes(range(16))
    def native(state,context,index=0,status=1):
        nonlocal active,journal_size
        active=index; journal_size={0:22,1:0,2:82,3:8754,4:0,5:6,6:298}[index]
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
            kind='mapper' if index in (0,2) else 'ppu'
            published=[e for e in events if e[0]==kind]
            expected=len(published).to_bytes(2,'big')+b''.join(
                addr.to_bytes(2,'big')+bytes((data,last)) for _,addr,data,last in published)
            if index==6:
                expected += state[0x200:0x300]
            assert output_journal == expected
        return bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(events)
    def original(state,context):
        bus[:2048]=state; bus.events.clear(); bus.dma.clear(); bus.status=rng.randrange(256)
        ref.pc=int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=context[2:7]
        direct_entry = ref.pc == 0xc0bf
        entered_task = ref.pc in (0xc574,0xfe8d)
        injected = False
        for _ in range(50000):
            if ref.pc == 0xc574: entered_task = True
            if entered_task and ref.pc==0xfe8d and not injected:
                ref.nmi()
                injected = True
            if ref.pc==0x8003: break
            assert (0xfe24<=ref.pc<=0xfe88 or 0xfe89<=ref.pc<=0xfec4
                    or 0xfed5<=ref.pc<=0xfee4 or 0xfef9<=ref.pc<=0xfefc
                    or 0xc1ba<=ref.pc<=0xc205 or 0xc21e<=ref.pc<=0xc234
                    or 0xff04<=ref.pc<=0xff1e or 0xff1f<=ref.pc<=0xff74
                    or 0xc000<=ref.pc<=0xc0f2 or 0xc574<=ref.pc<=0xc583 or 0xf377<=ref.pc<=0xf391 or ref.pc==0xfef7), ('unsupported original boundary',hex(ref.pc))
            ref.step()
        else: raise AssertionError('original timeout')
        ctx=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,context[7]))
        if not direct_entry:
            assert injected and len(bus.dma)==1
            assert bus.dma[0]==bytes(bus[0x200:0x300])
        return bytes(bus[:2048]),ctx,list(bus.events)
    cases=[]
    for index in range(8):
        for value in range(256):
            if value==0x88: continue
            state=bytearray(rng.randbytes(2048));state[0xf5]=0;state[0xdb]=index;state[0xdc+index]=value
            context=bytes((0xc0,0xbf))+rng.randbytes(3)+bytes((value,value,rng.randrange(256)))
            cases.append((bytes(state),context))
    # Ensure every original SP/status byte is covered, including excluded command $88.
    for value in range(256):
        state=bytearray(rng.randbytes(2048));state[0xf5]=0;state[0xdb]=value%8;state[0xdc+value%8]=0xf0
        context=bytes((0xc0,0xbf))+rng.randbytes(3)+bytes((value,value,rng.randrange(256)))
        cases.append((bytes(state),context))
    for case,(state,context) in enumerate(cases):
        want=original(state,context);got=native(state,context)
        assert got==want, ('audio entry mismatch',case)
        assert len(got[2])==10
        assert [e[2] for e in got[2][:5]]==[3,1,0,0,0]
        assert native(got[0],got[1],status=-1)==(*got[:2],[])
    for case in range(256):
        state=rng.randbytes(2048)
        context=bytes((0xfe,0x24))+rng.randbytes(2)+bytes((0,(case&0xcf)|0x20,case,rng.randrange(256)))
        want=original(state,context);merged=[]
        for index in (1,2,3,4,5,6,0):
            state,context,part=native(state,context,index);merged+=part
        assert (state,context,merged)==want, ('continuous audio-entry mismatch',case)
        assert len([e for e in merged if e[0]=='ppu'])==2199
        assert len([e for e in merged if e[0]=='mapper'])==25
        assert state[0xdc]==0x88 and state[0xdb]==1 and state[0xf1]==6
        assert context[:7]==bytes((0x80,3,0xf0,1,0,(case&0x0c)|0xa5,0xb2))
        assert state[0x1b3:0x1b5]==bytes((0xf2,0xc0))
    def supported():
        state=bytearray(rng.randbytes(2048));state[0xf5]=0;state[0xdb]=0;state[0xdc]=0xf0
        return state,bytes((0xc0,0xbf))+rng.randbytes(6)
    invalid=0
    for field,values in ((0xf5,range(1,256)),(0xdb,range(8,256))):
        for value in values:
            state,ctx=supported();state[field]=value
            assert native(bytes(state),ctx,status=-1)==(bytes(state),ctx,[]);invalid+=1
    for index in range(8):
        state,ctx=supported();state[0xdb]=index;state[0xdc+index]=0x88
        assert native(bytes(state),ctx,status=-1)==(bytes(state),ctx,[]);invalid+=1
    state,context=supported();state=bytes(state)
    for pc in range(65536):
        if pc==0xc0bf: continue
        ctx=pc.to_bytes(2,'big')+context[2:]
        assert native(state,ctx,status=-1)==(state,ctx,[]);invalid+=1
    m.cleanup()
    print(f'PASS: {len(cases)} original-ROM/native audio-entry cases, all supported queue indices/commands.')
    print('PASS: 256 continuous reset/yield/hardware-NMI/audio-entry compositions without patches.')
    print(f'PASS: {len(cases)} completed-boundary + {invalid} unsupported-input rejections.')
    print('PASS: full RAM/context/journal, ordered bank/dequeue/stack effects, guards and ABI; no audio opcode executed.')

if __name__=='__main__': main()
