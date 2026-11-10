#!/usr/bin/env python3
"""Execute original 6502 ROM bytes and actual assembled native 68020 code.
Dependencies: py65, machine68k. No source-semantic native model is used.
"""
from pathlib import Path
import hashlib, os, random, subprocess, sys, tempfile
for dep in ('/tmp/rescue-py65','/tmp/nes-sprite-test-deps'):
    if Path(dep).is_dir(): sys.path.insert(0, dep)
from py65.devices.mpu6502 import MPU
import machine68k
P=Path(__file__).resolve().parents[1]
ROM=P.parent/'input/rescue-rangers-europe.nes'
VASM=Path(os.environ.get('VASM',str(P.parents[1]/'nes-amiga-lab/repos/vscode-amiga-debug/bin/linux/vasmm68k_mot')))
ENTRIES=[('rescue_update_controllers',0xc162,0xc1b9),('rescue_nmi_timers',0xc0a1,0xc0bf),('rescue_hide_sprites',0xc21e,0xc234),('rescue_initialize_objects',0xc235,0xc246),('rescue_random_step',0xc2dc,0xc2f6)]
class Bus(list):
    def __init__(self,rom):
        super().__init__([0]*65536)
        self[0xc000:]=rom[16+7*16384:16+8*16384]
        self.inputs=[0,0];self.pos=[0,0]
    def __getitem__(self,k):
        if isinstance(k,int) and k in (0x4016,0x4017):
            i=k-0x4016;p=self.pos[i];self.pos[i]+=1
            return (self.inputs[i]>>max(0,7-p))&1 if p<8 else 1
        return super().__getitem__(k)
    def __setitem__(self,k,v):
        if k==0x4016:self.pos=[0,0]
        super().__setitem__(k,v)
def main():
    rom=ROM.read_bytes()
    assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
    with tempfile.TemporaryDirectory() as td:
        f=Path(td)/'test.s';out=Path(td)/'test.bin'
        f.write_text('\n'.join(' bra.w '+e[0] for e in ENTRIES)+'\n bra.w rescue_game_selftest\n'+(P/'src/native_rescue_game.s').read_text())
        subprocess.run([str(VASM),'-quiet','-m68020','-Fbin','-o',str(out),str(f)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
    mem.w_block(0x1000,code);mem.w16(0x800,0x60fe)
    bus=Bus(rom);ref=MPU(memory=bus);rng=random.Random(0xc1da1e)
    counts={n:0 for n,_,_ in ENTRIES}
    def native(index,state,inputs=(0,0)):
        guard=b'\xa7'*16
        mem.w_block(0xfff0,guard+state+guard)
        regs=[rng.getrandbits(32) for _ in range(15)]
        regs[0]=inputs[0];regs[1]=inputs[1];regs[8]=0x10000
        cpu.w_sr(0x2700);cpu.w_sp(0x1f0000);mem.w32(0x1f0000,0x800)
        for k,v in enumerate(regs):cpu.w_reg(k,v)
        cpu.w_pc(0x1000+index*4)
        for _ in range(100):
            cpu.execute(1000)
            if cpu.r_pc()==0x800:break
        else:raise AssertionError('native timeout')
        gotregs=[cpu.r_reg(k) for k in range(15)]
        assert gotregs[(1 if index==5 else 0):]==regs[(1 if index==5 else 0):],('register ABI',index)
        assert cpu.r_sp()==0x1f0004
        assert bytes(mem.r_block(0xfff0,16))==guard
        assert bytes(mem.r_block(0x10800,16))==guard
        return bytes(mem.r_block(0x10000,2048)),gotregs[0]
    def check(index,state,inputs=(0,0)):
        name,start,end=ENTRIES[index]
        bus[:2048]=state;bus.inputs=list(inputs);bus.pos=[0,0]
        ref.pc=start;ref.a=ref.x=ref.y=0;ref.p=0x20
        for _ in range(10000):
            if ref.pc==end:break
            ref.step()
        else:raise AssertionError(('reference timeout',name,hex(ref.pc)))
        got,_=native(index,state,inputs);want=bytes(bus[:2048])
        assert got==want,(name,[(hex(i),a,b) for i,(a,b) in enumerate(zip(want,got)) if a!=b][:12])
        counts[name]+=1
    # Exhaust all current/previous combinations; second port complementary.
    for current in range(256):
        for previous in range(256):
            state=bytearray([0xa5])*2048;state[0x16]=previous;state[0x17]=previous^255
            check(0,state,(current,current^255))
    # Random RAM proves unchanged state as well as target writes.
    for _ in range(1024):
        state=bytearray(rng.randbytes(2048))
        check(0,state,(rng.randrange(256),rng.randrange(256)))
        for i in (1,3,4):check(i,state)
        state[0x97]=rng.randrange(64)*4;check(2,state)
    # Exact timer rollover / terminal states for each of the four slots.
    for value in range(256):
        for slot in range(4):
            state=bytearray([0x55])*2048;state[0x80+4*slot]=1;state[0x81+4*slot]=value;state[0x92]=value
            check(1,state)
    # Each legal sprite cursor including wrap and special cursor 4.
    for cursor in range(0,256,4):
        state=bytearray(rng.randbytes(2048));state[0x97]=cursor;check(2,state)
    # All feedback-byte pairs, varied remaining random-state bytes.
    for a in range(256):
        for b in range(256):
            state=bytearray([0x55])*2048;state[0xe4:0xe8]=bytes((a,b,a^0xa5,b^0x5a));check(4,state)
    for _ in range(16):
        _,result=native(5,rng.randbytes(2048));assert result==0,('boot selftest',result)
    m.cleanup()
    print('PASS: original ROM bytes vs assembled 68020:',counts)
    print(f'PASS: {sum(counts.values())} differential cases + 16 native boot selftests; all 2048 RAM bytes, boundary guards and preserved registers checked.')
if __name__=='__main__':main()
