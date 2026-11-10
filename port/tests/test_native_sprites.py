#!/usr/bin/env python3
"""Execute assembled 68EC020 bytes against an independent synthetic NES oracle.
Requires machine68k (Musashi) and vasm. No ROM assets or Amiga speed claims.
"""
from pathlib import Path
import os, random, subprocess, tempfile
import machine68k
ROOT = Path(__file__).resolve().parents[2]
VASM = os.environ.get('VASM', str(ROOT/'repos/vscode-amiga-debug/bin/linux/vasmm68k_mot'))

def reference(oam, chrdata, initial, opacity, ctrl, mask):
    out = bytearray(initial)
    if ctrl & 32 or not mask & 16:
        return out
    for y in range(240):
        candidates = [i for i in range(64) if 0 <= y-oam[4*i]-1 < 8][:8]
        for x in range(256):
            if x < 8 and not mask & 4:
                continue
            for i in candidates:
                sy, tile, attr, sx = oam[4*i:4*i+4]
                if not sx <= x < sx+8:
                    continue
                dy, dx = y-sy-1, x-sx
                if attr & 128: dy = 7-dy
                if attr & 64: dx = 7-dx
                off = (4096 if ctrl & 8 else 0) + tile*16 + dy
                pixel = ((chrdata[off] >> (7-dx)) & 1) | (((chrdata[off+8] >> (7-dx)) & 1) << 1)
                if not pixel: continue
                if not (attr & 32 and opacity[y*32+x//8] & (128 >> (x%8))):
                    color = 16+(attr&3)*4+pixel
                    off = (y+8)*40+(x+32)//8
                    bit = 128 >> (x%8)
                    for plane in range(5):
                        p = off+plane*10240
                        out[p] = (out[p] & (255^bit)) | (bit if color & (1<<plane) else 0)
                break
    return out

def main():
    with tempfile.TemporaryDirectory() as tmp:
        binary = Path(tmp)/'sprites.bin'
        subprocess.run([VASM,'-quiet','-m68020','-Fbin','-o',str(binary),str(ROOT/'port/src/native_sprite_blitter.s')],check=True)
        code = binary.read_bytes()
    m = machine68k.Machine(machine68k.CPUType.M68EC020,1024)
    mem, cpu = m.mem, m.cpu
    rng = random.Random(1200)
    cases = []
    # All flip combinations and palettes, plus both pattern tables.
    for ctrl in (0,8):
        oam = bytearray([255,0,0,0]*64)
        for i in range(16): oam[4*i:4*i+4] = bytes((12+(i//4)*20,i,(i&3)|((i//4)*64),16+(i%4)*32))
        cases.append(('palettes/flips/table'+str(ctrl),oam,ctrl,20,None))
    # Nine overlapping entries, transparent early entries count toward eight.
    oam = bytearray([255,0,0,0]*64)
    for i in range(9): oam[4*i:4*i+4] = bytes((30,0 if i<8 else 1,0,40))
    cases.append(('eight sprite limit',oam,0,20,'limit'))
    oam = bytearray([255,0,0,0]*64)
    oam[0:8] = bytes((40,1,32,50,40,2,0,50))
    cases.append(('hidden first sprite blocks later',oam,0,20,'priority'))
    for mask in (0,16,20):
        oam = bytearray([255,0,0,0]*64)
        for i,(y,x) in enumerate([(0,0),(237,253),(255,0),(239,255)]):oam[i*4:i*4+4] = bytes((y,1,0,x))
        cases.append(('clipping/mask'+str(mask),oam,0,mask,None))
    cases.append(('unsupported 8x16',bytearray(rng.randbytes(256)),32,20,None))
    for i in range(12):
        oam = bytearray(rng.randbytes(256))
        if i%2:
            for j in range(64):oam[j*4]=50+(j%4) # dense overflow/overlap
        cases.append(('random'+str(i),oam,(i&1)*8,16+(i%2)*4,None))
    for name,oam,ctrl,mask,special in cases:
        chrdata = bytearray(rng.randbytes(8192))
        opacity = bytearray(rng.randbytes(7680))
        initial = bytearray(rng.randbytes(51200))
        if special == 'limit': chrdata[:16] = bytes(16);chrdata[16:32] = bytes([255]*16)
        if special == 'priority': chrdata[16:48] = bytes([255]*32);opacity[:] = bytes([255]*7680)
        expected = reference(oam,chrdata,initial,opacity,ctrl,mask)
        mem.clear_block(0,1024*1024,0)
        for addr,data in [(0x1000,code),(0x2000,oam),(0x3000,chrdata),(0x10000,initial),(0x20000,opacity),(0x22000,bytes([0xA5]*2228))]:mem.w_block(addr,bytes(data))
        mem.w16(0x800,0x60fe)
        mem.w32(0xf0000,0x800)
        cpu.w_sr(0x2700);cpu.w_sp(0xf0000);cpu.w_pc(0x1000)
        regs = [ctrl,mask]+[rng.getrandbits(32) for _ in range(6)]+[0x2000,0x3000,0x10000,0x20000,0x22000,0x12345678,0x87654321]
        for i,v in enumerate(regs):cpu.w_reg(i,v)
        for _ in range(10000):
            cpu.execute(1000)
            if cpu.r_pc() == 0x800:break
        else:raise AssertionError(name+': did not return')
        actual = bytes(mem.r_block(0x10000,51200))
        if actual != expected:
            diff = next(i for i,(a,b) in enumerate(zip(actual,expected)) if a != b)
            raise AssertionError(f'{name}: framebuffer offset {diff}: {actual[diff]:02x} != {expected[diff]:02x}')
        assert cpu.r_reg(0) == (0xffffffff if ctrl&32 else 0),name
        assert [cpu.r_reg(i) for i in range(1,15)] == regs[1:],name+': preserved registers'
        assert cpu.r_sp() == 0xf0004,name+': stack'
        if ctrl & 32:
            assert bytes(mem.r_block(0x22000,2228)) == bytes([0xA5]*2228),name+': unsupported changed scratch'
        assert bytes(mem.r_block(0x22894,32)) == bytes([0xA5]*32),name+': scratch guard'
        assert bytes(mem.r_block(0x2000,256)) == oam,name+': OAM modified'
        assert bytes(mem.r_block(0x3000,8192)) == chrdata,name+': CHR modified'
        assert bytes(mem.r_block(0x20000,7680)) == opacity,name+': opacity modified'
        print('PASS',name)
    m.cleanup()
    print(f'{len(cases)} assembled-code cases passed; not a hardware performance measurement.')

if __name__ == '__main__':main()
