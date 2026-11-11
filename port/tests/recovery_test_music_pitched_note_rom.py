#!/usr/bin/env python3
"""Independent original-ROM pitched-note comparison, natural channel RTS."""
import hashlib
from pathlib import Path
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus
from recovery_test_music_pitched_note_contract import make_checker,cases,fast_retrigger_cases
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
def run_note(bus,ref,reserved):
    start=len(bus.events)
    for steps in range(300):
        pc=ref.pc
        assert 0x83fd<=pc<=0x8472 or 0x85a6<=pc<=0x8651,hex(pc)
        addr=None
        if pc==0x844d:addr=0x8593+ref.y
        if pc in (0x8626,0x862b):addr=(0x8934 if pc==0x8626 else 0x8935)+ref.y
        if pc==0x8638:addr=((bus[0xc5]|bus[0xc6]<<8)+ref.y)&65535
        if addr is not None:bus.events.append(('resource',addr,bus[addr],0))
        ref.step()
        if pc==0x8472:break
    else:raise AssertionError('note reference timeout')
    return bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,reserved)),list(bus.events[start:])
def main():
    rom=(Path(__file__).resolve().parents[2]/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
    resource=rom[49168:65552];bus=OriginalBus(rom);bus[0x8000:0xc000]=resource;ref=MPU(memory=bus)
    def oracle(state,context,index):
        bus[:2048]=state;bus.events.clear();ref.pc=int.from_bytes(context[:2],'big')
        ref.a,ref.x,ref.y,ref.p,ref.sp=context[2:7]
        return run_note(bus,ref,context[7])
    check,cleanup=make_checker(oracle);cases(check,resource);extra=fast_retrigger_cases(check,resource);cleanup()
    print(f'PASS 16384 independent actual-ROM pitched-note cases plus {extra} out-of-window unused-pointer cases, full state/ordered effects, resource reads, global bounds and native ABI; raw P unchanged.')
if __name__=='__main__':main()
