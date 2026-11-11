#!/usr/bin/env python3
"""Actual Europe ROM instructions vs newly assembled 68020 stage-player slice."""
from pathlib import Path
import hashlib, os, random, subprocess, tempfile
from py65.devices.mpu6502 import MPU
import machine68k
PORT=Path(__file__).resolve().parents[1]
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
BASE,CTX,JOURNAL,STACK,STOP=0x10000,0x12000,0x13000,0x1f0000,0x800
class Bus(list):
    def __init__(self,rom):
        super().__init__([0]*65536)
        self[0xc000:]=rom[16+7*16384:16+8*16384]
        self.events=[]
    def __setitem__(self,address,value):
        if isinstance(address,int):
            assert address<2048,('unexpected external write',hex(address))
            self.events.append(address.to_bytes(2,'big')+bytes((value,0)))
        super().__setitem__(address,value)
def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'native.bin'
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_gameplay_player_init.s')],check=True)
        code=out.read_bytes()
    machine=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu=machine.mem,machine.cpu
    mem.w_block(0x1000,code);mem.w16(STOP,0x60fe)
    reads=((0x1000,len(code)),(STOP,2),(BASE,2048),(CTX,8),(JOURNAL,256),(STACK-256,260))
    writes=((BASE,2048),(CTX,8),(JOURNAL,256),(STACK-256,256))
    native_stores=[]
    def trace(mode,width,address,value):
        size=1<<width
        allowed=reads if mode=='R' else writes
        assert any(start<=address and address+size<=start+length for start,length in allowed),(mode,width,hex(address))
        if mode=='W' and BASE<=address<BASE+2048:
            assert width==0
            native_stores.append((address-BASE).to_bytes(2,'big')+bytes((value,0)))
    mem.set_trace_func(trace)
    for address,width in ((0x18000,0),(0,0),(BASE-1,0),(BASE+2047,1),(STOP+2,0)):
        try:trace('R',width,address,0)
        except AssertionError:pass
        else:raise AssertionError('read whitelist accepted invalid address')
    rng=random.Random(0xc6bd);bus=Bus(rom);ref=MPU(memory=bus)
    cases=0;events=0
    def check(state,ctx,valid=True):
        nonlocal cases,events
        mem.set_trace_mode(False)
        guard=b'\xa7'*16
        for addr,data in ((BASE,state),(CTX,ctx),(JOURNAL,b'\xb6'*256)):
            mem.w_block(addr-16,guard+data+guard)
        regs=[rng.getrandbits(32) for _ in range(15)]
        regs[8:11]=[BASE,CTX,JOURNAL]
        cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
        for i,v in enumerate(regs):cpu.w_reg(i,v)
        cpu.w_pc(0x1000);native_stores.clear();mem.set_trace_mode(True)
        for _ in range(100):
            cpu.execute(1000)
            if cpu.r_pc()==STOP:break
        else:raise AssertionError('native timeout')
        mem.set_trace_mode(False)
        assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
        assert cpu.r_sp()==STACK+4
        for addr,size in ((BASE,2048),(CTX,8),(JOURNAL,256)):
            assert bytes(mem.r_block(addr-16,16))==guard
            assert bytes(mem.r_block(addr+size,16))==guard
        if valid:
            bus[:2048]=state;bus.events=[]
            ref.pc=int.from_bytes(ctx[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=ctx[2:7]
            for _ in range(1000):
                if ref.pc==0xc700:break
                ref.step()
            else:raise AssertionError(('reference timeout',hex(ref.pc)))
            expected=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
            journal=b''.join(bus.events)
            assert native_stores==bus.events,'ordered native RAM writes'
            assert bytes(mem.r_block(BASE,2048))==bytes(bus[:2048]),'RAM mismatch'
            assert bytes(mem.r_block(CTX,8))==expected,('context',ctx.hex(),bytes(mem.r_block(CTX,8)).hex(),expected.hex())
            assert cpu.r_reg(0)==len(bus.events)
            assert bytes(mem.r_block(JOURNAL,256))==journal+b'\xb6'*(256-len(journal))
            events+=len(bus.events)
        else:
            assert cpu.r_reg(0)==0xffffffff
            assert bytes(mem.r_block(BASE,2048))==state
            assert bytes(mem.r_block(CTX,8))==ctx
            assert bytes(mem.r_block(JOURNAL,256))==b'\xb6'*256
            assert native_stores==[]
        cases+=1
    # Every player-state pair in two-player mode, including absent state $0C.
    for a in range(256):
        for b in range(256):
            state=bytearray(rng.randbytes(2048));state[0x50]=1
            state[0x54:0x56]=bytes((a,b))
            ctx=bytes((0xc6,0xbd,*rng.randbytes(6)))
            check(state,ctx)
    # Every CPU status/stack byte pair in one-player mode; inactive branch too.
    for p in range(256):
        for sp in range(256):
            state=bytearray(rng.randbytes(2048));state[0x50]=0
            state[0x54]=0x0c if sp&1 else p
            ctx=bytes((0xc6,0xbd,0x41,0x82,0xa5,p,sp,0x69))
            check(state,ctx)
    for mode in range(2,256):
        state=bytearray(rng.randbytes(2048));state[0x50]=mode
        check(state,bytes((0xc6,0xbd,1,2,3,4,5,6)),False)
    state=bytearray(2048)
    for pc in (0,0xc6bc,0xc6be,0xc700,0xffff):
        check(state,pc.to_bytes(2,'big')+bytes(6),False)
    machine.cleanup()
    print(f'PASS: {cases} cases (131072 ROM differential, 259 inert rejection); {events} ordered native RAM-write events; all RAM, context, journal, guards, native ABI and complete read/write whitelist checked. Native code {len(code)} bytes.')
if __name__=='__main__':main()
