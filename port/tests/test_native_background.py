#!/usr/bin/env python3
"""Actual assembled 68EC020 background renderer vs independent pixel oracle.
No original assets. Musashi correctness is not Amiga timing validation.
"""
from pathlib import Path
import os, random, subprocess, tempfile
import machine68k
ROOT = Path(__file__).resolve().parents[2]
VASM = os.environ.get('VASM',str(ROOT/'repos/vscode-amiga-debug/bin/linux/vasmm68k_mot'))

def reference(nt,chrdata,frame,opacity,cache):
    frame,opacity,cache = bytearray(frame),bytearray(opacity),bytearray(cache)
    count = 0
    for ty in range(30):
        for tx in range(32):
            idx=ty*32+tx
            attr=nt[960+(ty//4)*8+tx//4]
            pal=(attr >> (((ty%4)//2)*4+((tx%4)//2)*2))&3
            key=nt[idx]+256*pal
            if int.from_bytes(cache[idx*2:idx*2+2],'big') == key:continue
            cache[idx*2:idx*2+2]=key.to_bytes(2,'big')
            count+=1
            for py in range(8):
                lo,hi=chrdata[nt[idx]*16+py],chrdata[nt[idx]*16+py+8]
                opacity[(ty*8+py)*32+tx]=lo|hi
                for px in range(8):
                    pixel=((lo>>(7-px))&1)|(((hi>>(7-px))&1)<<1)
                    color=pal*4+pixel
                    off=(8+ty*8+py)*40+4+tx
                    bit=128>>px
                    for plane in range(5):
                        addr=off+plane*10240
                        frame[addr]=(frame[addr]&(255^bit))|(bit if color&(1<<plane) else 0)
    return frame,opacity,cache,count

def main():
    with tempfile.TemporaryDirectory() as tmp:
        binary=Path(tmp)/'bg.bin'
        subprocess.run([VASM,'-quiet','-m68020','-Fbin','-o',str(binary),str(ROOT/'port/src/native_background.s')],check=True)
        code=binary.read_bytes()
    m=machine68k.Machine(machine68k.CPUType.M68EC020,1024)
    mem,cpu=m.mem,m.cpu
    rng=random.Random(68020)
    nt=bytearray(rng.randbytes(1024))
    # Every attribute byte explicitly contains four distinct quadrant palettes.
    nt[960:]=bytes([0xe4]*64)
    chrdata=bytearray(rng.randbytes(4096))
    frame=bytearray(rng.randbytes(51200))
    opacity=bytearray(rng.randbytes(7680))
    cache=bytearray([255]*1920)
    names=['initial all quadrants','unchanged rejects writes','text edits','palette-only edits','CHR change requires invalidation','CHR invalidated','new frame/cache invalidation']
    for case,name in enumerate(names):
        if case==1:
            # Deliberate external alterations must survive cache rejection.
            frame[:]=rng.randbytes(51200);opacity[:]=rng.randbytes(7680)
        if case==2:
            for index in [0,31,32,333,633,928,959]:nt[index]=(nt[index]+1)&255
        if case==3:
            nt[960]^=255;nt[1023]^=255;nt[995]^=0x55
        if case==4:chrdata[:]=rng.randbytes(4096)
        if case in (5,6):cache[:]=bytes([255]*1920)
        if case==6:
            frame[:]=rng.randbytes(51200);opacity[:]=rng.randbytes(7680)
        expected=reference(nt,chrdata,frame,opacity,cache)
        mem.clear_block(0,1024*1024,0)
        for addr,data in [(0x1000,code),(0x2000,nt),(0x3000,chrdata),(0x10000,frame),(0x20000,opacity),(0x22000,cache)]:mem.w_block(addr,bytes(data))
        for addr in [0x10000-16,0x10000+51200,0x20000-16,0x20000+7680,0x22000-16,0x22000+1920]:mem.w_block(addr,bytes([0xA5]*16))
        mem.w16(0x800,0x60fe);mem.w32(0xf0000,0x800)
        cpu.w_sr(0x2700);cpu.w_sp(0xf0000);cpu.w_pc(0x1000)
        regs=[rng.getrandbits(32) for _ in range(8)]+[0x2000,0x3000,0x10000,0x20000,0x22000,0x12345678,0x87654321]
        for i,v in enumerate(regs):cpu.w_reg(i,v)
        for _ in range(20000):
            cpu.execute(1000)
            if cpu.r_pc()==0x800:break
        else:raise AssertionError(name+': did not return')
        for addr,length,want,kind in [(0x10000,51200,expected[0],'frame'),(0x20000,7680,expected[1],'opacity'),(0x22000,1920,expected[2],'cache')]:
            actual=bytes(mem.r_block(addr,length))
            if actual!=want:
                diff=next(i for i,(a,b) in enumerate(zip(actual,want)) if a!=b)
                raise AssertionError(f'{name} {kind} offset{diff}: {actual[diff]} != {want[diff]}')
            assert bytes(mem.r_block(addr-16,16))==bytes([0xA5]*16),kind+' preguard'
            assert bytes(mem.r_block(addr+length,16))==bytes([0xA5]*16),kind+' postguard'
        assert [cpu.r_reg(i) for i in range(15)]==regs,name+': register preservation'
        assert cpu.r_sp()==0xf0004,name+': stack preservation'
        assert bytes(mem.r_block(0x2000,1024))==nt,name+': NT modified'
        assert bytes(mem.r_block(0x3000,4096))==chrdata,name+': CHR modified'
        if case in (1,4):assert expected[3]==0
        if case in (0,5,6):assert expected[3]==960
        if case==2:assert expected[3]==7
        frame,opacity,cache=expected[:3]
        print(f'PASS {name}: {expected[3]} dirty tiles')
    m.cleanup()
    print(f'{len(names)} assembled-code background cases passed; no hardware speed claim.')

if __name__=='__main__':main()
