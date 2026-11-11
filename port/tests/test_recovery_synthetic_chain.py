#!/usr/bin/env python3
"""Public contract regression for ten native helpers. No ROM or fixtures.

Private original-ROM differential tests establish semantic equivalence; this
synthetic contract test makes basic chain regressions visible in public CI.
"""
from pathlib import Path
import os
import struct
import subprocess
import tempfile
import machine68k

P = Path(__file__).resolve().parents[1]
NAMES = ('recovery_reset_ram','recovery_reset_mapper','recovery_reset_video',
         'recovery_reset_dispatch','recovery_first_yield','recovery_first_nmi_prefix',
         'recovery_nmi_audio_entry','recovery_audio_reset_command','recovery_silent_tick_rti','recovery_scheduler_resume')
RAM,CTX,JOURNAL,STACK,STOP = 0x10000,0x12000,0x13000,0x1f0000,0x800

def main():
    with tempfile.TemporaryDirectory(prefix='rescue-synthetic-chain-') as td:
        source,binary = Path(td)/'chain.s',Path(td)/'chain.bin'
        source.write_text(''.join(' bra.w '+name+'\n' for name in NAMES)+
                          '\n'.join((P/'src'/(name+'.s')).read_text() for name in NAMES))
        subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(binary),str(source)],check=True)
        code = binary.read_bytes()
    m = machine68k.Machine(machine68k.CPUType.M68EC020,2048)
    mem,cpu = m.mem,m.cpu
    mem.w_block(0x1000,code)
    mem.w16(STOP,0x60fe)
    guard = bytes([0x5a])*16
    context = bytes.fromhex('fe2417330024fda7')
    for address,data in ((RAM,bytes([0xa5])*2048),(CTX,context),(JOURNAL,bytes([0xa5])*8754)):
        mem.w_block(address-16,guard+data+guard)
    def call(index,status):
        regs = [0x11220000+i for i in range(15)]
        regs[8:11] = [RAM,CTX,JOURNAL]
        if index == 9:
            regs[0] = regs[1] = 0  # Explicit no-button snapshots for both pads.
        cpu.w_sr(0x2700)
        cpu.w_sp(STACK)
        mem.w32(STACK,STOP)
        for i,v in enumerate(regs):
            cpu.w_reg(i,v)
        cpu.w_pc(0x1000+index*4)
        for _ in range(1000):
            cpu.execute(1000)
            if cpu.r_pc() == STOP:
                break
        else:
            raise AssertionError('Native chain call did not return')
        assert cpu.r_reg(0) == status & 0xffffffff
        assert [cpu.r_reg(i) for i in range(1,15)] == regs[1:]
        assert cpu.r_sp() == STACK+4
        for address,size in ((RAM,2048),(CTX,8),(JOURNAL,8754)):
            assert bytes(mem.r_block(address-16,16)) == guard
            assert bytes(mem.r_block(address+size,16)) == guard
    def record(address,value,kind):
        return struct.pack('>HBB',address,value,kind)
    contexts = ('fe431eff0025fda7','fe6700ff0026fda7','fe7cc0000026fda7',
                'c574c50008a5ffa7','fe8d00bb00a4bba7','c0bf00100026b4a7',
                '8003f00100a5b2a7','c0f300ff0c26b4a7','fe8d00bb00a4bba7','c584bfbf08a4bfa7')
    for index in range(10):
        journal_before = bytes(mem.r_block(JOURNAL,8754))
        call(index,1)
        assert bytes(mem.r_block(CTX,8)) == bytes.fromhex(contexts[index])
        written_size = (0,82,8754,0,6,298,22,30,22,74)[index]
        assert bytes(mem.r_block(JOURNAL+written_size,8754-written_size)) == journal_before[written_size:]
        if index == 1:
            expected = struct.pack('>H',20)
            for address,value,busy in ((0xfff0,6,1),(0x9fff,0x1e,0),(0xbfff,0,0),(0xdfff,0x10,0)):
                expected += b''.join(record(address,value>>shift,busy) for shift in range(5))
            assert bytes(mem.r_block(JOURNAL,len(expected))) == expected
        if index == 2:
            expected = struct.pack('>H',2188)
            for high in (0x20,0x24):
                expected += record(0x2002,0,0)+record(0x2000,0,1)
                expected += record(0x2006,high,1)+record(0x2006,0,1)
                expected += record(0x2007,0,1)*1024
                expected += record(0x2006,high+3,1)+record(0x2006,0xc0,1)
                expected += record(0x2007,0,1)*64
            assert bytes(mem.r_block(JOURNAL,len(expected))) == expected
        if index == 4:
            assert bytes(mem.r_block(JOURNAL,6)) == struct.pack('>H',1)+record(0x2000,0x90,1)
        if index == 5:
            events = ((0x2000,0x10,1),(0x2002,0,0),(0x2001,0,1),(0x2003,0,1),
                      (0x4014,2,1),(0x2002,0,0),(0x2005,0,1),(0x2005,0,1),
                      (0x2001,0x1e,1),(0x2000,0x90,1))
            expected = struct.pack('>H',10)+b''.join(record(*event) for event in events)
            expected += bytes([0xf8,0,0,0])*64
            assert bytes(mem.r_block(JOURNAL,298)) == expected
        if index == 6:
            expected = struct.pack('>H',5)+b''.join(record(0xfff0,3>>shift,0) for shift in range(5))
            assert bytes(mem.r_block(JOURNAL,22)) == expected
        if index == 7:
            events = ((0x4000,0x30,1),(0x4004,0x30,1),(0x4008,0,1),(0x400c,0x30,1),
                      (0x4001,8,1),(0x4005,8,1),(0x4015,0x0f,1))
            expected = struct.pack('>H',7)+b''.join(record(*event) for event in events)
            assert bytes(mem.r_block(JOURNAL,30)) == expected
        if index == 8:
            expected = struct.pack('>H',5)+b''.join(record(0xfff0,6>>shift,0) for shift in range(5))
            assert bytes(mem.r_block(JOURNAL,22)) == expected
        if index == 9:
            expected = struct.pack('>H',18)+record(0x4016,1,1)+record(0x4016,0,1)
            expected += (record(0x4016,0,0)+record(0x4017,0,0))*8
            assert bytes(mem.r_block(JOURNAL,74)) == expected
        # Repeating a completed slice must reject without mutating its buffers.
        before = tuple(bytes(mem.r_block(a,n)) for a,n in ((RAM,2048),(CTX,8),(JOURNAL,8754)))
        call(index,-1)
        after = tuple(bytes(mem.r_block(a,n)) for a,n in ((RAM,2048),(CTX,8),(JOURNAL,8754)))
        assert before == after

    # Explicit reset/startup contract, not a model that replays native opcodes.
    expected_ram = bytearray(2048)
    expected_ram[0xdc:0xe4] = bytes([0x88])*8
    expected_ram[0x200:0x300:4] = bytes([0xf8])*64
    values = {0x00:0,0x01:0,0x80:2,0x82:0xbb,0x83:0xc5,0x90:0,0x92:1,
              0x93:1,0x94:0xc5,0xc0:4,0xc1:0x94,0xc2:0x81,0xd9:0xf0,0xda:1,0xdb:1,
              0xf1:6,0xf3:0x10,0xf4:6,0xfe:0x1e,0xff:0x90,
              0x1fd:0xfe,0x1fc:0x88,0x1fb:0xfe,0x1fa:0xd7,
              0x1bf:0xc5,0x1be:0x83,0x1bd:0xbf,0x1bc:8,0x1bb:0xfe,0x1ba:0xcf,
              0x1b9:0xa4,0x1b8:0xb4,0x1b6:0xbb,0x1b4:0xc0,0x1b3:0xf8,
              0x1b0:0x80,0x1af:0x84,0x1ad:0x81,0x1ac:0xcc}
    for address,value in values.items():
        expected_ram[address] = value
    assert bytes(mem.r_block(RAM,2048)) == expected_ram
    print('PASS public synthetic ten-helper chain: full RAM/canonical RTI context, ordered journal/DMA/APU contents, guards, ABI and ten inert rejections; no ROM/firmware.')
    print('Contract regression only; private original-ROM and target tests remain required.')

if __name__ == '__main__':
    main()
