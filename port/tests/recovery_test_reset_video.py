#!/usr/bin/env python3
"""Original-ROM proof of video-clear slice and composition of reset helpers."""
from pathlib import Path
import hashlib
import os
import random
import subprocess
import tempfile
import machine68k
from py65.devices.mpu6502 import MPU

PORT = Path(__file__).resolve().parents[1]
SHA = '051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
BASE, CTX, JOURNAL, STOP, STACK = 0x10000, 0x12000, 0x13000, 0x800, 0x1f0000
SIZE = 8754

class OriginalBus(list):
    def __init__(self, rom):
        super().__init__([0]*65536)
        self[0xc000:] = rom[16+7*16384:16+8*16384]
        self.events = []
        self.status = 0
    def __getitem__(self, address):
        if address == 0x2002:
            self.events.append(('ppu', 0x2002, 0, 0))
            return self.status  # Value unused; read still resets the PPU address latch.
        return super().__getitem__(address)
    def __setitem__(self, address, value):
        if isinstance(address, int):
            if address in (0xfff0, 0x9fff, 0xbfff, 0xdfff):
                self.events.append(('mapper', address, value, self[0xf5]))
                return
            if address in (0x2000,0x2006,0x2007):
                self.events.append(('ppu', address, value, 1))
                return
            assert 0 <= address < 2048, ('unsupported write', hex(address))
            self.events.append(('ram', address, value))
        super().__setitem__(address, value)

# Small host-only PPU adapter, independent of source translation. It interprets
# register events, never 6502 opcodes. Support precisely the proven clear boundary.
def apply_ppu(events, initial, latch):
    ram = bytearray(initial)
    address, high, control = 0x2aaa, 0x2a, 0
    touched = []
    for _, port, value, kind in events:
        if kind == 0:
            assert port == 0x2002
            latch = 0
        elif port == 0x2000:
            control = value
        elif port == 0x2006:
            if latch == 0:
                high = value & 0x3f
            else:
                address = (high << 8) | value
            latch ^= 1
        else:
            assert port == 0x2007 and 0x2000 <= address < 0x2800
            assert not control & 4
            ram[address-0x2000] = value
            touched.append(address)
            address = (address+1) & 0x3fff
    return bytes(ram), touched, latch

def main():
    rom = (PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest() == SHA
    with tempfile.TemporaryDirectory(prefix='recovery-video-') as tmp:
        source, out = Path(tmp)/'test.s', Path(tmp)/'test.bin'
        source.write_text(' bra.w recovery_reset_video\n bra.w recovery_reset_ram\n bra.w recovery_reset_mapper\n'+
                          '\n'.join((PORT/'src'/name).read_text() for name in
                                    ('recovery_reset_video.s','recovery_reset_ram.s','recovery_reset_mapper.s')))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(source)],check=True)
        code = out.read_bytes()
    m = machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu = m.mem,m.cpu
    mem.w_block(0x1000,code); mem.w16(STOP,0x60fe)
    rng = random.Random(0xfe67)
    bus, events = OriginalBus(rom), []
    ref = MPU(memory=bus)
    active = 0
    def trace(mode,width,address,value):
        if mode != 'W':
            return
        if BASE <= address < BASE+2048:
            assert width == 0
            events.append(('ram',address-BASE,value))
        elif address == JOURNAL:
            assert width == 1
            if value:
                limit = 20 if active == 2 else 2188
                assert 1 <= value <= limit
                record = JOURNAL+2+(value-1)*4
                addr,data,last = mem.r16(record),mem.r8(record+2),mem.r8(record+3)
                if active == 2:
                    assert last == mem.r8(BASE+0xf5)
                events.append(('mapper' if active == 2 else 'ppu',addr,data,last))
        else:
            assert (JOURNAL+2 <= address < JOURNAL+SIZE or CTX <= address < CTX+8
                    or STACK-128 <= address < STACK), ('unexpected native write',address)
    mem.set_trace_func(trace)
    guard = bytes(range(16))
    def native(state,context,journal,status,index=0):
        nonlocal active
        active = index
        mem.set_trace_mode(False)
        for address,data in ((BASE,state),(CTX,context),(JOURNAL,journal)):
            mem.w_block(address-16,guard+data+guard)
        regs = [rng.getrandbits(32) for _ in range(15)]
        regs[8:11] = [BASE,CTX,JOURNAL]
        cpu.w_sr(0x2700); cpu.w_sp(STACK); mem.w32(STACK,STOP)
        for i,value in enumerate(regs):
            cpu.w_reg(i,value)
        cpu.w_pc(0x1000+index*4)
        events.clear(); mem.set_trace_mode(True)
        for _ in range(1000):
            cpu.execute(1000)
            if cpu.r_pc() == STOP:
                break
        else:
            raise AssertionError('native timeout')
        mem.set_trace_mode(False)
        assert cpu.r_reg(0) == status & 0xffffffff
        assert [cpu.r_reg(i) for i in range(1,15)] == regs[1:]
        assert cpu.r_sp() == STACK+4
        for address,size in ((BASE,2048),(CTX,8),(JOURNAL,len(journal))):
            assert bytes(mem.r_block(address-16,16)) == guard
            assert bytes(mem.r_block(address+size,16)) == guard
        return (bytes(mem.r_block(BASE,2048)),bytes(mem.r_block(CTX,8)),
                bytes(mem.r_block(JOURNAL,len(journal))),list(events))
    def original(state,context,end):
        bus[:2048] = state; bus.events.clear(); bus.status = rng.randrange(256)
        ref.pc = int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp = context[2:7]
        for _ in range(50000):
            if ref.pc == end:
                break
            assert (0xfe24 <= ref.pc < 0xfe7c or 0xc1ba <= ref.pc <= 0xc205
                    or 0xc21e <= ref.pc <= 0xc234 or 0xff1f <= ref.pc <= 0xff74), hex(ref.pc)
            ref.step()
        else:
            raise AssertionError('original timeout')
        ctx = ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,context[7]))
        return bytes(bus[:2048]),ctx,list(bus.events)
    def verify_video(events):
        ppu = [e for e in events if e[0] == 'ppu']
        assert len(ppu) == 2188
        for latch in (0,1):
            got,touched,final_latch = apply_ppu(ppu,rng.randbytes(2048),latch)
            assert got == bytes(2048) and final_latch == 0
            expected = list(range(0x2000,0x2400))+list(range(0x23c0,0x2400))
            expected += list(range(0x2400,0x2800))+list(range(0x27c0,0x2800))
            assert touched == expected
        return len(ppu).to_bytes(2,'big')+b''.join(
            address.to_bytes(2,'big')+bytes((data,kind)) for _,address,data,kind in ppu)
    cases = [(i,i,i&0xfc,i&0xfb,bytes([v])*2048) for i in range(256) for v in (0,255,0xa5,0x5a)]
    cases += [(rng.randrange(256),rng.randrange(256),rng.randrange(64)*4,
               rng.randrange(256)&0xfb,rng.randbytes(2048)) for _ in range(256)]
    for case,(flags,sp,cursor,control,initial) in enumerate(cases):
        state = bytearray(initial); state[0x97],state[0xff] = cursor,control; state=bytes(state)
        context = bytes((0xfe,0x67))+rng.randbytes(3)+bytes((flags,sp,rng.randrange(256)))
        want,wantctx,wantevents = original(state,context,0xfe7c)
        journal = verify_video(wantevents)
        got = native(state,context,rng.randbytes(SIZE),1)
        assert got == (want,wantctx,journal,wantevents), ('differential mismatch',case)
        assert native(got[0],got[1],got[2],-1) == (*got[:3],[])
    # Continuous original execution vs sequential calls, with no state patching.
    for case in range(128):
        state = rng.randbytes(2048)
        context = bytes((0xfe,0x24))+rng.randbytes(2)+bytes((0,rng.randrange(256),rng.randrange(256),rng.randrange(256)))
        want,wantctx,wantevents = original(state,context,0xfe7c)
        chain_events = []
        for index,size in ((1,0),(2,82),(0,SIZE)):
            got = native(state,context,rng.randbytes(size),1,index)
            state,context = got[:2]
            chain_events += got[3]
        assert (state,context,chain_events) == (want,wantctx,wantevents), ('composition mismatch',case)
        assert got[2] == verify_video(wantevents)
    invalid = 0
    for cursor in range(256):
        if cursor % 4 == 0:
            continue
        state=bytearray(rng.randbytes(2048)); state[0x97]=cursor; state[0xff]&=0xfb; state=bytes(state)
        context=bytes((0xfe,0x67))+rng.randbytes(6); journal=rng.randbytes(SIZE)
        assert native(state,context,journal,-1) == (state,context,journal,[])
        invalid += 1
    for control in range(256):
        if not control & 4:
            continue
        state=bytearray(rng.randbytes(2048)); state[0x97]=0; state[0xff]=control; state=bytes(state)
        context=bytes((0xfe,0x67))+rng.randbytes(6); journal=rng.randbytes(SIZE)
        assert native(state,context,journal,-1) == (state,context,journal,[])
        invalid += 1
    state=bytearray(rng.randbytes(2048)); state[0x97]=0; state[0xff]=0; state=bytes(state)
    journal=rng.randbytes(SIZE)
    for pc in range(65536):
        if pc == 0xfe67:
            continue
        context=pc.to_bytes(2,'big')+rng.randbytes(6)
        assert native(state,context,journal,-1) == (state,context,journal,[])
        invalid += 1
    m.cleanup()
    print(f'PASS: {len(cases)} standalone original-ROM/native cases; 2188 ordered PPU events each.')
    print('PASS: 128 continuous $FE24->$FE7C original runs vs composed RAM/mapper/video native helpers.')
    print(f'PASS: {len(cases)} completed-boundary + {invalid} invalid-PC/cursor/increment-mode rejections.')
    print('PASS: full RAM/context/journal, original stack stores, ordered events, both PPU latch states, guards and ABI.')

if __name__ == '__main__':
    main()
