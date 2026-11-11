#!/usr/bin/env python3
"""Original ROM differential proof: first task PPU publication, sound request and scheduler yield."""
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

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    names=('recovery_first_yield','recovery_reset_ram','recovery_reset_mapper','recovery_reset_video','recovery_reset_dispatch')
    with tempfile.TemporaryDirectory(prefix='recovery-first-yield-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in names)+
                          '\n'.join((PORT/'src'/(n+'.s')).read_text() for n in names))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu=m.mem,m.cpu
    mem.w_block(0x1000,code); mem.w16(STOP,0x60fe)
    rng=random.Random(0xc574)
    bus=OriginalBus(rom); ref=MPU(memory=bus)
    events=[]; active=0; journal_size=0
    def trace(mode,width,address,value):
        if mode!='W': return
        if BASE<=address<BASE+2048:
            assert width==0
            events.append(('ram',address-BASE,value))
        elif address==JOURNAL and journal_size:
            assert width==1
            if value:
                assert 1<=value<=(20 if active==2 else 1 if active==0 else 2188)
                record=JOURNAL+2+(value-1)*4
                addr,data,last=mem.r16(record),mem.r8(record+2),mem.r8(record+3)
                if active==2: assert last==mem.r8(BASE+0xf5)
                events.append(('mapper' if active==2 else 'ppu',addr,data,last))
        else:
            assert (JOURNAL+2<=address<JOURNAL+journal_size or CTX<=address<CTX+8
                    or STACK-128<=address<STACK), ('unexpected native write',address)
    mem.set_trace_func(trace)
    guard=bytes(range(16))
    def native(state,context,index=0,status=1):
        nonlocal active,journal_size
        active=index; journal_size={0:6,1:0,2:82,3:8754,4:0}[index]
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
            kind='mapper' if index==2 else 'ppu'
            published=[e for e in events if e[0]==kind]
            expected=len(published).to_bytes(2,'big')+b''.join(
                addr.to_bytes(2,'big')+bytes((data,last)) for _,addr,data,last in published)
            assert output_journal == expected
        return bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(events)
    def original(state,context):
        bus[:2048]=state; bus.events.clear(); bus.status=rng.randrange(256)
        ref.pc=int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=context[2:7]
        entered_task = ref.pc == 0xc574
        for _ in range(50000):
            if ref.pc == 0xc574: entered_task = True
            if entered_task and ref.pc==0xfe8d: break
            assert (0xfe24<=ref.pc<=0xfe88 or 0xfe89<=ref.pc<=0xfec4
                    or 0xfed5<=ref.pc<=0xfee4 or 0xfef9<=ref.pc<=0xfefc
                    or 0xc1ba<=ref.pc<=0xc205 or 0xc21e<=ref.pc<=0xc234
                    or 0xff04<=ref.pc<=0xff1e or 0xff1f<=ref.pc<=0xff74
                    or 0xc574<=ref.pc<=0xc583 or 0xf377<=ref.pc<=0xf391 or ref.pc==0xfef7), ('unsupported original boundary',hex(ref.pc))
            ref.step()
        else: raise AssertionError('original timeout')
        ctx=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,context[7]))
        return bytes(bus[:2048]),ctx,list(bus.events)
    cases=[]
    # All queue indices and slot byte values, including exactly $88 empty.
    for index in range(8):
        for value in range(256):
            state=bytearray(rng.randbytes(2048))
            state[0x91],state[0xda],state[0xdc+index]=0,index,value
            context=bytes((0xc5,0x74))+rng.randbytes(2)+bytes((value,value,value,rng.randrange(256)))
            cases.append((bytes(state),context))
    # Explicit empty queues across every status and saved-Y byte; vary control.
    for value in range(256):
        state=bytearray(rng.randbytes(2048)); state[0x91]=0; state[0xda]=value%8
        state[0xdc+value%8]=0x88; state[0xff]=value
        context=bytes((0xc5,0x74))+rng.randbytes(2)+bytes((value,value,value,rng.randrange(256)))
        cases.append((bytes(state),context))
    for case,(state,context) in enumerate(cases):
        want=original(state,context)
        got=native(state,context)
        assert got==want, ('standalone mismatch',case)
        ram_count=17 if state[0xdc+state[0xda]]==0x88 else 15
        assert len(got[2])==ram_count+1
        assert got[2][0]==('ppu',0x2000,state[0xff],1)
        assert native(got[0],got[1],status=-1)==(*got[:2],[])
    for case in range(256):
        state=rng.randbytes(2048)
        context=bytes((0xfe,0x24))+rng.randbytes(2)+bytes((0,case,case,rng.randrange(256)))
        want=original(state,context)
        merged=[]
        for index in (1,2,3,4,0):
            state,context,part=native(state,context,index)
            merged+=part
        assert (state,context,merged)==want, ('continuous composition mismatch',case)
        ppu=[e for e in merged if e[0]=='ppu']
        assert len(ppu)==2189 and ppu[-1]==('ppu',0x2000,0x90,1)
        for latch in (0,1):
            assert apply_ppu(ppu,rng.randbytes(2048),latch)[0]==bytes(2048)
        assert len([e for e in merged if e[0]=='mapper'])==20
        assert context[:7]==bytes((0xfe,0x8d,0,0xbb,0,(case&0x3c)|0x80,0xbb))
        assert state[0x80:0x83]==bytes((1,1,0xbb))
        assert state[0x1bc:0x1c0]==bytes((8,0xbf,0x83,0xc5))
    invalid=0
    for field,values in ((0x91,range(1,256)),(0xda,range(8,256))):
        for value in values:
            state=bytearray(rng.randbytes(2048)); state[0x91]=0; state[0xda]=0; state[field]=value
            state=bytes(state); context=bytes((0xc5,0x74))+rng.randbytes(6)
            assert native(state,context,status=-1)==(state,context,[])
            invalid+=1
    state=bytearray(rng.randbytes(2048)); state[0x91]=0; state[0xda]=0; state=bytes(state)
    for pc in range(65536):
        if pc==0xc574: continue
        context=pc.to_bytes(2,'big')+rng.randbytes(6)
        assert native(state,context,status=-1)==(state,context,[])
        invalid+=1
    m.cleanup()
    print(f'PASS: {len(cases)} original-ROM/native first-yield cases; full queue-slot/index coverage.')
    print('PASS: 256 continuous $FE24->$FE8D original runs vs five composed helpers, no state patches.')
    print(f'PASS: {len(cases)} completed-boundary + {invalid} invalid-PC/task/queue rejections.')
    print('PASS: full RAM/context, ordered PPU/queue/stack effects, saved continuation, guards and ABI.')

if __name__=='__main__': main()
