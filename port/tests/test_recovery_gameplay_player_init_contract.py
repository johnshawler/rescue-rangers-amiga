#!/usr/bin/env python3
"""ROM-free invented-state contract. No 6502 emulator or cartridge dependency."""
from pathlib import Path
import os, random, struct, subprocess, tempfile
PORT=Path(__file__).resolve().parents[1]
# mode, state0, state1, S, P: active/inactive pairs and both stack boundaries.
CASES=((0,2,9,0,0xff),(0,12,4,255,0x00),(1,2,3,1,0x40),
       (1,12,3,0,0x24),(1,2,12,255,0x08),(1,12,12,0,0x81))
def fixture(case):
    mode,s0,s1,sp,p=case
    state=bytearray((i*37+19)&255 for i in range(2048))
    state[0x50]=mode;state[0x54:0x56]=bytes((s0,s1))
    return state,bytes((0xc6,0xbd,0x17,0x35,0x79,p,sp,0xa7))
def expected(state,ctx):
    result=bytearray(state);stores=[]
    for slot in range(state[0x50],-1,-1):
        if state[0x54+slot]==12:continue
        stores += [(0x4d0+slot,0x80),(0x400+slot,0xd0),(0x420+slot,state[0x34c+slot]),
                   (0x510+slot,0x74),*[(base+slot,0) for base in (0x56,0x54,0x58,0x5c)],
                   (0x5e,0),(0x430+slot,0),(0x410+slot,0),
                   (0x100+ctx[6],0xc6),(0x100+((ctx[6]-1)&255),0xee),
                   (0x550+slot,0xab),(0x560+slot,0xff)]
    stores += [(0x4f0,0x18),(0x4f1,0x30),(0x99,0x55)]
    for address,value in stores:result[address]=value
    context=bytes((0xc7,0,0x55,0xff,ctx[4],(ctx[5]&0x7c)|(state[0x54]>=12),ctx[6],ctx[7]))
    journal=b''.join(struct.pack('>HBB',a,v,0) for a,v in stores)
    return bytes(result),context,journal,stores

def main():
    import machine68k
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'code.bin'
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src/recovery_gameplay_player_init.s')],check=True)
        code=out.read_bytes()
    assert len(code)==340
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
    RAM,CTX,JOURNAL,STACK,STOP=0x10000,0x12000,0x13000,0x1f0000,0x800
    mem.w_block(0x1000,code);mem.w16(STOP,0x60fe)
    reads=[(0x1000,len(code)),(STOP,2),(RAM,2048),(CTX,8),(JOURNAL,256),(STACK-256,260)]
    writes=[(RAM,2048),(CTX,8),(JOURNAL,256),(STACK-256,256)]
    stores=[]
    def trace(mode,width,address,value):
        size=1<<width
        allowed=reads if mode=='R' else writes
        assert any(base<=address and address+size<=base+length for base,length in allowed),(mode,width,hex(address))
        if mode=='W' and RAM<=address<RAM+2048:
            assert width==0;stores.append((address-RAM,value))
    mem.set_trace_func(trace)
    # Explicitly prove the whitelist rejects distant/unmapped and crossing reads.
    for address,width in ((0x18000,0),(0,0),(RAM-1,0),(RAM+2047,1),(STOP+2,0)):
        try:trace('R',width,address,0)
        except AssertionError:pass
        else:raise AssertionError('read whitelist accepted invalid address')
    rng=random.Random(0xc6bd);count=0
    cases=[fixture(c) for c in CASES]
    for mode in (0,1):
        for s0 in (0,11,12,13,255):
            for s1 in (0,12,255):
                for sp in (0,1,254,255):
                    for p in (0,2,4,8,0x10,0x20,0x40,0x80,255):
                        state=bytearray(rng.randbytes(2048));state[0x50]=mode;state[0x54:0x56]=bytes((s0,s1))
                        cases.append((state,bytes((0xc6,0xbd,13,29,47,p,sp,0x96))))
    invalid=[]
    for mode in range(2,256):
        state,ctx=fixture(CASES[0]);state[0x50]=mode;invalid.append((state,ctx))
    for pc in (0,0xc6bc,0xc6be,0xc700,65535):
        state,ctx=fixture(CASES[0]);invalid.append((state,pc.to_bytes(2,'big')+ctx[2:]))
    for valid,items in ((True,cases),(False,invalid)):
        for state,ctx in items:
            mem.set_trace_mode(False)
            guard=b'\x5a'*16
            for address,data in ((RAM,bytes(state)),(CTX,ctx),(JOURNAL,b'\xb6'*256)):
                mem.w_block(address-16,guard+data+guard)
            regs=[rng.getrandbits(32) for _ in range(15)];regs[8:11]=[RAM,CTX,JOURNAL]
            cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
            for i,v in enumerate(regs):cpu.w_reg(i,v)
            cpu.w_pc(0x1000);stores.clear();mem.set_trace_mode(True)
            for _ in range(100):
                cpu.execute(1000)
                if cpu.r_pc()==STOP:break
            else:raise AssertionError('timeout')
            mem.set_trace_mode(False)
            assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
            assert cpu.r_sp()==STACK+4
            if valid:
                want,context,journal,effects=expected(state,ctx)
                assert cpu.r_reg(0)==len(effects);assert stores==effects
            else:
                want,context,journal=bytes(state),ctx,b''
                assert cpu.r_reg(0)==0xffffffff;assert stores==[]
            assert bytes(mem.r_block(RAM,2048))==want
            assert bytes(mem.r_block(CTX,8))==context
            assert bytes(mem.r_block(JOURNAL,256))==journal+b'\xb6'*(256-len(journal))
            for address,size in ((RAM,2048),(CTX,8),(JOURNAL,256)):
                assert bytes(mem.r_block(address-16,16))==guard
                assert bytes(mem.r_block(address+size,16))==guard
            count+=1
    m.cleanup();print(f'PASS ROM-free contract: {count} cases, complete read/write whitelist, 5 bad-read rejection checks')
if __name__=='__main__':main()
