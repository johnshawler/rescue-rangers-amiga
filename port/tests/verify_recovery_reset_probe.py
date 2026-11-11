#!/usr/bin/env python3
"""Compare actual Amiga probe RAM to original cartridge reset instructions."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys
from py65.devices.mpu6502 import MPU
from recovery_test_reset_video import OriginalBus, apply_ppu, SHA

P = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('chip_dump', type=Path)
parser.add_argument('--first-yield', action='store_true', help='Verify separate five-helper first-yield marker and journal')
args = parser.parse_args()
chip = args.chip_dump.read_bytes()
assert len(chip) == 2*1024*1024, 'Expected stock 2 MiB Chip RAM dump'
marker = b'CDRRYLD1' if args.first_yield else b'CDRRST01'
assert chip.count(marker) == 1, 'Expected one live probe report'
offset = chip.index(marker)
status,steps,ram,ctx,mapper,video,stack,stack_end,sp = struct.unpack_from('>9I',chip,offset+8)
assert (status,steps) == (0,5 if args.first_yield else 4), (status,steps)
assert stack_end-stack == 4096 and sp == stack_end
ranges = [(ram,2048),(ctx,8),(mapper,82),(video,8754),(stack,4096)]
if args.first_yield:
    first_yield = struct.unpack_from('>I',chip,offset+44)[0]
    ranges.append((first_yield,6))
for address,size in ranges:
    assert 16 <= address and address+size+16 <= len(chip)
    assert chip[address-16:address] == bytes([0x5a])*16
    assert chip[address+size:address+size+16] == bytes([0x5a])*16
for i,(a,n) in enumerate(ranges):
    for b,m in ranges[i+1:]:
        assert a+n <= b or b+m <= a, 'Overlapping probe buffers'

rom = (P.parent/'input/rescue-rangers-europe.nes').read_bytes()
assert hashlib.sha256(rom).hexdigest() == SHA
bus = OriginalBus(rom)
bus[:2048] = [0xa5]*2048
ref = MPU(memory=bus)
ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp = 0xfe24,0x17,0x33,0,0x24,0xfd
bus.events.clear()
entered_task = False
for instructions in range(100000):
    if ref.pc == 0xc574:
        entered_task = True
    reached_boundary = (entered_task and ref.pc == 0xfe8d) if args.first_yield else ref.pc == 0xc574
    if reached_boundary:
        break
    ref.step()
else:
    raise AssertionError('Original reset reference did not reach requested boundary')
expected_ctx = struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
assert chip[ram:ram+2048] == bytes(bus[:2048]), 'Original/native RAM mismatch'
assert chip[ctx:ctx+8] == expected_ctx, 'Original/native context mismatch'
def journal(kind, start=None, end=None):
    events = [e for e in bus.events if e[0] == kind][start:end]
    return struct.pack('>H',len(events))+b''.join(struct.pack('>HBB',*e[1:]) for e in events)
assert chip[mapper:mapper+82] == journal('mapper')
assert chip[video:video+8754] == journal('ppu',end=2188)
if args.first_yield:
    assert entered_task
    assert chip[first_yield:first_yield+6] == journal('ppu',start=2188)
    assert len([e for e in bus.events if e[0]=='ppu']) == 2189
ppu = [e for e in bus.events if e[0]=='ppu']
for latch in (0,1):
    cleared,_,_ = apply_ppu(ppu,bytes([0xa5])*2048,latch)
    assert cleared == bytes(2048)
report = {'status':'PASS','boundary':('FE24 to first FE8D yield' if args.first_yield else 'FE24 to C574'),'native_helper_count':steps,
          'ram_bytes_equal':2048,'context_bytes_equal':8,'mapper_records_equal':20,
          'ppu_records_equal':2189 if args.first_yield else 2188,
          'guard_regions_intact':len(ranges)*2,'native_stack_balanced':True,
          'original_instruction_count':instructions,
          'limit':'Isolated reset boundary on emulated stock PAL A1200, not title/gameplay boot or speed'}
print(json.dumps(report,indent=2))
