"""ROM-free native execution support; no expected gameplay results here."""
from pathlib import Path
import os, subprocess, tempfile, struct
import machine68k
PORT=Path(__file__).resolve().parents[1]
RAM,CTX,JOURNAL,STACK,STOP,CODE=0x10000,0x12000,0x13000,0x1f0000,0x800,0x1000
class Native:
    def __init__(self,source='recovery_stage_resource_init.s',journal_size=256):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'native.bin'
            subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src'/source)],check=True)
            self.code=out.read_bytes()
        self.size=journal_size
        self.machine=machine68k.Machine(machine68k.CPUType.M68EC020,2048)
        self.mem,self.cpu=self.machine.mem,self.machine.cpu
        self.mem.w_block(CODE,self.code);self.mem.w16(STOP,0x60fe)
        self.reads=[(CODE,len(self.code)),(STOP,2),(RAM,2048),(CTX,8),(JOURNAL,self.size),(STACK-256,260),(0x15000,421)]
        self.writes=[(RAM,2048),(CTX,8),(JOURNAL,self.size),(STACK-256,256)]
        self.accesses=[];self.resources=[];self.stores=[];self.mem.set_trace_func(self.trace)
        for address,width in ((0x18000,0),(0,0),(RAM-1,0),(RAM+2047,1),(STOP+2,0),(0x1fffff,0),(0x14fff,0),(0x151a5,0),(0x151a4,1)):
            try:self.trace('R',width,address,0)
            except AssertionError:pass
            else:raise AssertionError('invalid read accepted')
        for address in (0x15000,0x151a4):
            try:self.trace('W',0,address,0)
            except AssertionError:pass
            else:raise AssertionError('resource write accepted')
    def trace(self,mode,width,address,value):
        assert mode in ('R','W')
        size=1<<width
        assert any(b<=address and address+size<=b+n for b,n in (self.reads if mode=='R' else self.writes)),(mode,width,hex(address))
        if mode=='W' and RAM<=address<RAM+2048:
            assert width==0;self.stores.append((address-RAM,value));self.accesses.append((address-RAM,value,0))
        if mode=='R' and 0x15000<=address<0x15000+421:
            assert width==0;self.resources.append((0x8193+address-0x15000,value));self.accesses.append((0x8193+address-0x15000,value,1))
    def install(self,source,address):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'native.bin'
            subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(PORT/'src'/source)],check=True)
            code=out.read_bytes()
        self.mem.set_trace_mode(False);self.mem.w_block(address,code);self.reads.append((address,len(code)))
    def run(self,state,ctx,rng,resource,entry=CODE,resume=False):
        m,c=self.mem,self.cpu;m.set_trace_mode(False)
        guard=b'\x5a'*16
        m.w_block(0x15000-16,guard+bytes(resource)+guard)
        for address,data in ((RAM,bytes(state)),(CTX,ctx),(JOURNAL,b'\xb6'*self.size)):
            if not resume or address==JOURNAL:m.w_block(address-16,guard+data+guard)
        m.w_block(STACK-272,b'\x69'*272)
        regs=[rng.getrandbits(32) for _ in range(15)];regs[8:12]=[RAM,CTX,JOURNAL,0x15000]
        c.w_sr(0x2700);c.w_sp(STACK);m.w32(STACK,STOP)
        for i,v in enumerate(regs):c.w_reg(i,v)
        c.w_pc(entry);self.accesses.clear();self.resources.clear();self.stores.clear();m.set_trace_mode(True)
        for _ in range(100):
            c.execute(1000)
            if c.r_pc()==STOP:break
        else:raise AssertionError('native timeout')
        m.set_trace_mode(False)
        assert [c.r_reg(i) for i in range(1,15)]==regs[1:]
        assert c.r_sp()==STACK+4
        assert bytes(m.r_block(STACK-272,16))==b'\x69'*16
        for address,size in ((RAM,2048),(CTX,8),(JOURNAL,self.size),(0x15000,421)):
            assert bytes(m.r_block(address-16,16))==guard
            assert bytes(m.r_block(address+size,16))==guard
        assert bytes(m.r_block(0x15000,421))==bytes(resource)
        if c.r_reg(0)!=0xffffffff:
            data=bytes(m.r_block(JOURNAL,4*c.r_reg(0)))
            assert self.accesses==[e for e in struct.iter_unpack('>HBB',data) if e[2]!=2]
        else:assert not self.accesses
        return bytes(m.r_block(RAM,2048)),bytes(m.r_block(CTX,8)),bytes(m.r_block(JOURNAL,self.size)),c.r_reg(0),self.stores.copy(),self.resources.copy()
    def close(self):self.machine.cleanup()
