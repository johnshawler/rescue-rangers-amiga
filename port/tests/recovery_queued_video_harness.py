"""ROM-free native execution support; no expected gameplay results here."""
from pathlib import Path
import os, subprocess, tempfile
import machine68k
PORT=Path(__file__).resolve().parents[1]
RAM,CTX,JOURNAL,STACK,STOP,CODE=0x10000,0x12000,0x40000,0x1f0000,0x800,0x1000
class Native:
    def __init__(self,source='recovery_queued_video_nmi_prefix.s',journal_size=134638):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'native.bin'
            subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src'/source)],check=True)
            self.code=out.read_bytes()
        self.size=journal_size
        self.machine=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
        self.mem,self.cpu=self.machine.mem,self.machine.cpu
        self.mem.w_block(CODE,self.code);self.mem.w16(STOP,0x60fe)
        self.reads=[(CODE,len(self.code)),(STOP,2),(RAM,2048),(CTX,8),(JOURNAL,self.size),(STACK-256,260)]
        self.writes=[(RAM,2048),(CTX,8),(JOURNAL,self.size),(STACK-256,256)]
        self.effects=[];self.stores=[];self.mem.set_trace_func(self.trace)
        for address,width in ((0x18000,0),(0,0),(RAM-1,0),(RAM+2047,1),(STOP+2,0),(0x1fffff,0)):
            try:self.trace('R',width,address,0)
            except AssertionError:pass
            else:raise AssertionError('invalid read accepted')
    def trace(self,mode,width,address,value):
        assert mode in ('R','W')
        size=1<<width
        assert any(b<=address and address+size<=b+n for b,n in (self.reads if mode=='R' else self.writes)),(mode,width,hex(address))
        if mode=='W' and RAM<=address<RAM+2048:
            assert width==0;self.stores.append((address-RAM,value));self.effects.append(('ram',address-RAM,value))
        elif mode=='W' and address==JOURNAL and value:
            assert width==1 and 1<=value<=33595
            at=JOURNAL+2+4*(value-1)
            a,v,k=self.mem.r16(at),self.mem.r8(at+2),self.mem.r8(at+3)
            if a==0x4014:assert bytes(self.mem.r_block(JOURNAL+134382,256))==bytes(self.mem.r_block(RAM+512,256))
            self.effects.append(('mapper' if a>=0x8000 else 'ppu',a,v,k))
    def install(self,source,address):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'native.bin'
            subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src'/source)],check=True)
            code=out.read_bytes()
        self.mem.set_trace_mode(False);self.mem.w_block(address,code);self.reads.append((address,len(code)))
    def run(self,state,ctx,rng,entry=CODE,resume=False,inputs=(0,0)):
        m,c=self.mem,self.cpu;m.set_trace_mode(False)
        guard=b'\x5a'*16
        for address,data in ((RAM,bytes(state)),(CTX,ctx),(JOURNAL,b'\xb6'*self.size)):
            if not resume or address==JOURNAL:m.w_block(address-16,guard+data+guard)
        m.w_block(STACK-272,b'\x69'*272)
        regs=[rng.getrandbits(32) for _ in range(15)];regs[8:11]=[RAM,CTX,JOURNAL]
        regs[0]=(regs[0]&0xffffff00)|inputs[0];regs[1]=(regs[1]&0xffffff00)|inputs[1]
        c.w_sr(0x2700);c.w_sp(STACK);m.w32(STACK,STOP)
        for i,v in enumerate(regs):c.w_reg(i,v)
        c.w_pc(entry);self.stores.clear();self.effects.clear();m.set_trace_mode(True)
        for _ in range(5000):
            c.execute(1000)
            if c.r_pc()==STOP:break
        else:raise AssertionError('native timeout')
        m.set_trace_mode(False)
        assert [c.r_reg(i) for i in range(1,15)]==regs[1:]
        assert c.r_sp()==STACK+4
        assert bytes(m.r_block(STACK-272,16))==b'\x69'*16
        for address,size in ((RAM,2048),(CTX,8),(JOURNAL,self.size)):
            assert bytes(m.r_block(address-16,16))==guard
            assert bytes(m.r_block(address+size,16))==guard
        return bytes(m.r_block(RAM,2048)),bytes(m.r_block(CTX,8)),bytes(m.r_block(JOURNAL,self.size)),c.r_reg(0),self.effects.copy()
    def close(self):self.machine.cleanup()
