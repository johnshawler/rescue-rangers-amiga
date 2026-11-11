#!/usr/bin/env python3
"""All-four-channel full pitched-event composition against continuous original ROM."""
import hashlib,random,os,subprocess,tempfile
import machine68k
from pathlib import Path
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_music_pitched_gate_contract import contract as gate_contract
from recovery_test_music_pitched_gate_contract import PORT,BASE,CTX,JOURNAL,RESOURCE,CODE,STOP,STACK
from recovery_test_music_pitched_note_contract import contract as note_contract
from recovery_test_music_pitched_gate_rom import run_gate,SHA
from recovery_test_music_pitched_note_rom import run_note

NAMES=("recovery_music_pitched_gate","recovery_music_pitched_note")
SIZES=(10,18)
def contract(state,context,resource,index):
    return (gate_contract if index==0 else note_contract)(state,context,resource)

def make_checker(oracle=None):
    with tempfile.TemporaryDirectory(prefix='rr-event-contract-') as tmp:
        source,out=Path(tmp)/'test.s',Path(tmp)/'test.bin'
        source.write_text(''.join(' bra.w '+n+'\n' for n in NAMES)+'\n'.join((PORT/'src'/(n+'.s')).read_text() for n in dict.fromkeys(NAMES)))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code=out.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu
    mem.w_block(CODE,code);mem.w16(STOP,0x60fe)
    rng=random.Random(0x8667859b);guard=bytes(range(16));events=[];reads=[];size=0
    def trace(mode,width,address,value):
        length=1<<width
        if RESOURCE<=address<RESOURCE+16384:
            assert mode=='R' and width==0
            reads.append(address-RESOURCE);return
        if mode=='R':
            assert any(lo<=address and address+length<=hi for lo,hi in ((CODE,CODE+len(code)+8),(STOP,STOP+4),(BASE,BASE+2048),(CTX,CTX+8),(JOURNAL,JOURNAL+size),(STACK-256,STACK+4))),('unknown read',width,address)
            return
        assert mode=='W'
        if BASE<=address<BASE+2048:
            assert width==0;events.append(('ram',address-BASE,value));return
        assert any(lo<=address and address+length<=hi for lo,hi in ((CTX,CTX+8),(JOURNAL,JOURNAL+size),(STACK-256,STACK))),('unknown write',width,address)
        if address==JOURNAL:
            assert width==1 and value<=5
            if value:
                at=JOURNAL+2+(value-1)*4
                events.append(('resource',mem.r16(at),mem.r8(at+2),mem.r8(at+3)))
    mem.set_trace_func(trace)
    for mode in ('R','W'):
        for address in (0,0x25000,0x30000,0x90000,0x1fffff):
            try:trace(mode,0,address,0)
            except AssertionError:pass
            else:raise AssertionError('Unmapped access escaped global whitelist')
    def check(state,context,resource,index):
        nonlocal size
        size=SIZES[index];expected,expected_reads=contract(state,context,resource,index)
        if oracle is not None and expected is not None:
            actual=oracle(state,context,index)
            assert actual==expected[:3], ("original/declarative",index,context.hex(),actual[1:],expected[1:3])
        mem.set_trace_mode(False);journal=rng.randbytes(size)
        for address,data in ((BASE,state),(CTX,context),(JOURNAL,journal),(RESOURCE,resource)):
            mem.w_block(address-16,guard+data+guard)
        registers=[rng.getrandbits(32) for _ in range(15)];registers[8:12]=[BASE,CTX,JOURNAL,RESOURCE]
        cpu.w_sr(0x2700);cpu.w_sp(STACK);mem.w32(STACK,STOP)
        for i,value in enumerate(registers):cpu.w_reg(i,value)
        cpu.w_pc(CODE+4*index);events.clear();reads.clear();mem.set_trace_mode(True)
        for _ in range(100):
            cpu.execute(1000)
            if cpu.r_pc()==STOP:break
        else:raise AssertionError('native timeout')
        mem.set_trace_mode(False)
        assert cpu.r_sp()==STACK+4 and [cpu.r_reg(i) for i in range(1,15)]==registers[1:]
        assert cpu.r_reg(0)==(1 if expected else 0xffffffff)
        got=(bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),list(events),bytes(mem.r_block(JOURNAL,size)))
        assert got==(expected if expected else (state,context,[],journal)),(index,context.hex(),got[1:],None if expected is None else expected[1:])
        assert reads==expected_reads,(reads,expected_reads)
        assert bytes(mem.r_block(RESOURCE,16384))==resource
        for address,length in ((BASE,2048),(CTX,8),(JOURNAL,size),(RESOURCE,16384)):
            assert bytes(mem.r_block(address-16,16))==guard and bytes(mem.r_block(address+length,16))==guard
        return got[:3]
    return check,m.cleanup


def main():
    rom=(Path(__file__).resolve().parents[2]/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
    def gate_oracle(state,c,index):
        bus[:2048]=state;bus.events.clear();ref.pc=int.from_bytes(c[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
        return run_gate(bus,ref,c[7])
    def note_oracle(state,c,index):
        assert state==bytes(bus[:2048])
        assert c[:7]==ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp))
        return run_note(bus,ref,c[7])
    def oracle(state,c,index):
        return (gate_oracle if index==0 else note_oracle)(state,c,index)
    check,cleanup=make_checker(oracle);rng=random.Random(0x83e9)
    for case in range(16384):
        x=0x28+(case//256)%4;s=bytearray(rng.randbytes(2048))
        s[0xc5]=0x00;s[0xc6]=0x8b;s[0x730+x]=case&255
        if case%3==0:s[0x718+x]=0
        a=32*(1+case%7)+1+(case//7)%31
        c=bytes((0x83,0xa0,a,x,rng.randrange(256),(case&0xc7)|32,case&255,case>>8))
        mid=check(bytes(s),c,resource,0);end=check(mid[0],mid[1],resource,1)
        assert end[1][6]==(c[6]+2)&255
    cleanup()
    print('PASS 16384 all-channel complete pitched-event compositions; continuous original reference, unchanged native outputs, full state and ordered effects.')
if __name__=='__main__':main()
