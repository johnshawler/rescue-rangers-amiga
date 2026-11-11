#!/usr/bin/env python3
"""Synthetic assembled 68020 proof, independent per-pixel oracle. No target timing."""
import os, random, subprocess, tempfile
from pathlib import Path
import machine68k
from test_native_sprites import reference as sprite_reference
ROOT=Path(__file__).resolve().parents[2]
VASM=os.environ['VASM']
def assemble(name):
    with tempfile.TemporaryDirectory() as t:
        p=Path(t)/'code'
        subprocess.run([VASM,'-quiet','-m68020','-Fbin','-o',str(p),str(ROOT/'port/src'/name)],check=True)
        return p.read_bytes()
def world_pixels(nt,chrdata):
    # Deliberately pixel-domain: no paired-byte merge used by native implementation.
    rows=[]
    for y in range(240):
        row=[]
        for x in range(512):
            base=(x//256)*1024; tx=(x%256)//8;ty=y//8
            tile=nt[base+ty*32+tx]
            attr=nt[base+960+(ty//4)*8+tx//4]
            palette=(attr//(4**(((ty%4)//2)*2+(tx%4)//2)))%4
            offset=tile*16+y%8
            pixel=(chrdata[offset]//(2**(7-x%8)))%2+2*((chrdata[offset+8]//(2**(7-x%8)))%2)
            row.append((palette*4+pixel,pixel!=0))
        rows.append(row)
    return rows
def reference(world,origin,initial,blank=False):
    out=bytearray(initial);opacity=bytearray(7680)
    for y,row in enumerate(world):
        for byte in range(32):
            colors=[(0,False) if blank else row[(origin+byte*8+b)%512] for b in range(8)]
            for p in range(5):out[p*10240+(y+8)*40+4+byte]=sum((128>>b) for b,(c,o) in enumerate(colors) if c&(1<<p))
            opacity[y*32+byte]=sum(128>>b for b,(c,o) in enumerate(colors) if o)
    return out,opacity
class Runner:
    def __init__(self):
        self.m=machine68k.Machine(machine68k.CPUType.M68EC020,1024);self.mem=self.m.mem;self.cpu=self.m.cpu
        self.rng=random.Random(621);self.calls=0;self.traced=0
    def run(self,code,nt,chrdata,frame,opacity,params,sr,trace=False,sprite=False,oam=None):
        mem,cpu=self.mem,self.cpu;stack=0xf0000;depth=68 if sprite else 62
        inputs=[(0x1000,code),(0x3000,nt),(0x4000,chrdata)]
        if sprite:inputs=[(0x1000,code),(0x3000,oam),(0x4000,chrdata),(0x20000,opacity)]
        writes=[(0x10000,51200),(0x22000,2228 if sprite else 256)]
        if not sprite:writes.append((0x20000,7680))
        for addr,data in inputs+[(0x10000,frame),(0x20000,opacity),(0x22000,bytes([0xa5])*writes[1][1])]:mem.w_block(addr,bytes(data))
        for addr,size in writes+[(stack-depth,depth+4)]:
            mem.w_block(addr-16,bytes([0xa5])*16);mem.w_block(addr+size,bytes([0xa5])*16)
        mem.w16(0x800,0x60fe);mem.w32(stack,0x800)
        cpu.w_sr(sr);cpu.w_sp(stack);cpu.w_pc(0x1000)
        regs=list(params)+[self.rng.getrandbits(32) for _ in range(8-len(params))]+[0x3000,0x4000,0x10000,0x20000,0x22000,0x12345678,0x87654321]
        for i,v in enumerate(regs):cpu.w_reg(i,v)
        writable=[(a,a+n) for a,n in writes]+[(stack-(68 if sprite else 62),stack)]
        readable=writable+[(a,a+len(d)) for a,d in inputs]+[(stack,stack+4),(0x800,0x802)]
        rejected=not sprite and (params[0] not in (0x90,0x91) or params[1] not in (0,0x1e) or not 0<=params[2]<=255 or params[3]!=0 or params[4]!=0x1e)
        if rejected:writable=[(stack-56,stack)]
        def access(mode,width,addr,value):
            assert mode in ('R','W') and width in (0,1,2)
            if rejected and mode=='R':assert not 0x3000<=addr<0x5000
            assert any(a<=addr and addr+(1<<width)<=b for a,b in (writable if mode=='W' else readable)),(mode,width,hex(addr),params)
        if trace:mem.set_trace_func(access);mem.set_trace_mode(True);self.traced+=1
        for _ in range(5000):
            cpu.execute(10000)
            if cpu.r_pc()==0x800:break
        else:raise AssertionError('did not return')
        mem.set_trace_mode(False)
        assert cpu.r_reg(0)==(0xffffffff if rejected else 0),params
        assert [cpu.r_reg(i) for i in range(1,15)]==regs[1:]
        assert cpu.r_sp()==stack+4
        for addr,data in inputs:assert bytes(mem.r_block(addr,len(data)))==data,('immutable',hex(addr))
        for addr,size in writes+[(stack-depth,depth+4)]:
            assert bytes(mem.r_block(addr-16,16))==bytes([0xa5])*16
            assert bytes(mem.r_block(addr+size,16))==bytes([0xa5])*16
        if rejected:assert bytes(mem.r_block(0x22000,256))==bytes([0xa5])*256
        self.calls+=1
        return bytearray(mem.r_block(0x10000,51200)),bytearray(mem.r_block(0x20000,7680))
def main():
    code=assemble('recovery_scroll_view_draw.s');sprites=assemble('native_sprite_blitter.s');r=Runner();rng=random.Random(68020)
    nt=bytearray(rng.randbytes(2048));chrdata=bytearray(rng.randbytes(4096));chrdata[:16]=bytes(16)
    frame=bytearray(rng.randbytes(51200));op=bytearray(rng.randbytes(7680));world=world_pixels(nt,chrdata)
    for origin in range(512):
        expected=reference(world,origin,frame)
        for sr in (0,0x2700):
            actual=r.run(code,nt,chrdata,frame,op,[0x90+origin//256,0x1e,origin%256,0,0x1e],sr,trace=origin in (0,1,7,8,248,255,256,257,504,511))
            assert actual==expected,('origin',origin,sr)
        if origin%64==0:print('PASS origins through',origin,flush=True)
    for sr in (0,0x2700):
        for field,values in enumerate(([0,0x92,0xb0,0x190],[1,0x18,0xfe],[256,0xffffffff],[1,240],[0,0x1f])):
            for value in values:
                p=[0x90,0x1e,255,0,0x1e];p[field]=value
                assert r.run(code,nt,chrdata,frame,op,p,sr,True)==(frame,op)
        assert r.run(code,nt,chrdata,frame,op,[0x91,0,255,0,0x1e],sr,True)==reference(world,511,frame,True)
        # Redraw over old sprite composites, source edits, CHR edits, and different fine scroll.
        composite=frame
        for step in range(8):
            nt[(step*137)%2048]^=255;nt[960+step]^=0x55;nt[1984+step]^=0xaa;chrdata[(step*519)%4096]^=255
            world=world_pixels(nt,chrdata);origin=[0,1,255,256,511,7,8,166][step]
            expected,opacity=reference(world,origin,composite)
            bg,actual_op=r.run(code,nt,chrdata,composite,op,[0x90+origin//256,0x1e,origin%256,0,0x1e],sr,True)
            assert (bg,actual_op)==(expected,opacity)
            oam=bytearray(rng.randbytes(256))
            for i in range(12):oam[4*i:4*i+4]=bytes((30,i,(i%4)|((i%2)*32),i*3))
            fullchr=chrdata+chrdata
            composite,unchanged_op=r.run(sprites,nt,fullchr,bg,opacity,[0x90,0x1e],sr,True,True,oam)
            assert composite==sprite_reference(oam,fullchr,bg,opacity,0x90,0x1e)
            assert unchanged_op==opacity
    r.m.cleanup();print(f'PASS {r.calls} assembled calls; {r.traced} width-aware traced calls. All 512 origins in USER and supervisor. No target-speed claim.')
if __name__=='__main__':main()
