#!/usr/bin/env python3
"""Original ROM differential proof: reset task setup and first dispatch only."""
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
    names=('dispatch','ram','mapper','video')
    with tempfile.TemporaryDirectory(prefix='recovery-dispatch-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w recovery_reset_'+n+'\n' for n in names)+
                          '\n'.join((PORT/'src'/('recovery_reset_'+n+'.s')).read_text() for n in names))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu=m.mem,m.cpu
    mem.w_block(0x1000,code); mem.w16(STOP,0x60fe)
    rng=random.Random(0xfe7c)
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
                assert 1<=value<=(20 if active==2 else 2188)
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
        active=index; journal_size={0:0,1:0,2:82,3:8754}[index]
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
        return bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(events)
    def original(state,context):
        bus[:2048]=state; bus.events.clear(); bus.status=rng.randrange(256)
        ref.pc=int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=context[2:7]
        for _ in range(50000):
            if ref.pc==0xc574: break
            assert (0xfe24<=ref.pc<=0xfe88 or 0xfe89<=ref.pc<=0xfec4
                    or 0xfed5<=ref.pc<=0xfee4 or 0xfef9<=ref.pc<=0xfefc
                    or 0xc1ba<=ref.pc<=0xc205 or 0xc21e<=ref.pc<=0xc234
                    or 0xff1f<=ref.pc<=0xff74), ('unsupported original boundary',hex(ref.pc))
            ref.step()
        else: raise AssertionError('original timeout')
        ctx=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,context[7]))
        return bytes(bus[:2048]),ctx,list(bus.events)
    cases=[(i,i,bytes([v])*2048) for i in range(256) for v in (0,255,0xa5,0x5a)]
    cases += [(rng.randrange(256),rng.randrange(256),rng.randbytes(2048)) for _ in range(1024)]
    for case,(flags,sp,state) in enumerate(cases):
        context=bytes((0xfe,0x7c))+rng.randbytes(3)+bytes((flags,sp,rng.randrange(256)))
        want=original(state,context)
        got=native(state,context)
        assert got==want, ('standalone mismatch',case)
        assert len(got[2])==15 and all(e[0]=='ram' for e in got[2])
        assert native(got[0],got[1],status=-1)==(*got[:2],[])
    for case in range(256):
        state=rng.randbytes(2048)
        context=bytes((0xfe,0x24))+rng.randbytes(2)+bytes((0,case,case,rng.randrange(256)))
        want=original(state,context)
        merged=[]
        for index in (1,2,3,0):
            state,context,part=native(state,context,index)
            merged+=part
        assert (state,context,merged)==want, ('continuous composition mismatch',case)
        ppu=[e for e in merged if e[0]=='ppu']
        assert len(ppu)==2188
        for latch in (0,1):
            assert apply_ppu(ppu,rng.randbytes(2048),latch)[0]==bytes(2048)
        assert len([e for e in merged if e[0]=='mapper'])==20
        assert context[:7]==bytes((0xc5,0x74,0xc5,0,8,(case&0x3c)|0x81,0xff))
    state=rng.randbytes(2048)
    invalid=0
    for pc in range(65536):
        if pc==0xfe7c: continue
        context=pc.to_bytes(2,'big')+rng.randbytes(6)
        assert native(state,context,status=-1)==(state,context,[])
        invalid+=1
    m.cleanup()
    print(f'PASS: {len(cases)} original-ROM/native dispatch cases; 15 ordered RAM writes each.')
    print('PASS: 256 continuous $FE24->$C574 original runs vs four composed native helpers, no state patches.')
    print(f'PASS: {len(cases)} completed-boundary + {invalid} invalid-PC rejections.')
    print('PASS: full RAM/context including stack wrap, ordered RAM/mapper/PPU effects, guards and ABI.')

if __name__=='__main__': main()
