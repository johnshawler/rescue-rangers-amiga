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
from recovery_test_first_nmi_prefix import NmiBus
from recovery_test_audio_reset_command import AudioBus
from recovery_test_scheduler_resume import ControllerBus

P = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('chip_dump', type=Path)
modes = parser.add_mutually_exclusive_group()
modes.add_argument('--first-yield', action='store_true', help='Verify separate five-helper first-yield marker and journal')
modes.add_argument('--nmi-audio-entry', action='store_true', help='Verify separate seven-helper NMI audio-entry probe')
modes.add_argument('--audio-reset', action='store_true', help='Verify separate eight-helper audio reset-command probe')
modes.add_argument('--nmi-return', action='store_true', help='Verify ninth-helper silent tick and RTI probe')
modes.add_argument('--scheduler-resume', action='store_true', help='Verify tenth-helper scheduler and standard-controller probe')
args = parser.parse_args()
nmi_return_mode = args.nmi_return or args.scheduler_resume
audio_reset_mode = args.audio_reset or nmi_return_mode
audio_entry_mode = args.nmi_audio_entry or audio_reset_mode
first_yield_mode = args.first_yield or audio_entry_mode
chip = args.chip_dump.read_bytes()
assert len(chip) == 2*1024*1024, 'Expected stock 2 MiB Chip RAM dump'
marker = b'CDRRRES1' if args.scheduler_resume else b'CDRRRTI1' if args.nmi_return else b'CDRRAPU1' if args.audio_reset else b'CDRRAUD1' if args.nmi_audio_entry else b'CDRRYLD1' if first_yield_mode else b'CDRRST01'
assert chip.count(marker) == 1, 'Expected one live probe report'
offset = chip.index(marker)
status,steps,ram,ctx,mapper,video,stack,stack_end,sp = struct.unpack_from('>9I',chip,offset+8)
assert (status,steps) == (0,10 if args.scheduler_resume else 9 if args.nmi_return else 8 if args.audio_reset else 7 if args.nmi_audio_entry else 5 if first_yield_mode else 4), (status,steps)
assert stack_end-stack == 4096 and sp == stack_end
ranges = [(ram,2048),(ctx,8),(mapper,82),(video,8754),(stack,4096)]
if first_yield_mode:
    first_yield = struct.unpack_from('>I',chip,offset+44)[0]
    ranges.append((first_yield,6))
if audio_entry_mode:
    nmi_prefix,audio_entry = struct.unpack_from('>2I',chip,offset+48)
    ranges.extend(((nmi_prefix,298),(audio_entry,22)))
if audio_reset_mode:
    apu = struct.unpack_from('>I',chip,offset+56)[0]
    ranges.append((apu,30))
if nmi_return_mode:
    restore = struct.unpack_from('>I',chip,offset+60)[0]
    ranges.append((restore,22))
if args.scheduler_resume:
    controller = struct.unpack_from('>I',chip,offset+64)[0]
    ranges.append((controller,74))
for address,size in ranges:
    assert 16 <= address and address+size+16 <= len(chip)
    assert chip[address-16:address] == bytes([0x5a])*16
    assert chip[address+size:address+size+16] == bytes([0x5a])*16
for i,(a,n) in enumerate(ranges):
    for b,m in ranges[i+1:]:
        assert a+n <= b or b+m <= a, 'Overlapping probe buffers'

rom = (P.parent/'input/rescue-rangers-europe.nes').read_bytes()
assert hashlib.sha256(rom).hexdigest() == SHA
bus = ControllerBus(rom) if args.scheduler_resume else AudioBus(rom) if audio_reset_mode else NmiBus(rom) if audio_entry_mode else OriginalBus(rom)
if args.scheduler_resume:
    bus.inputs = (0,0)  # Explicit standard pads: no pressed buttons.
    bus.pos = [0,0]
bus[:2048] = [0xa5]*2048
ref = MPU(memory=bus)
ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp = 0xfe24,0x17,0x33,0,0x24,0xfd
bus.events.clear()
entered_task = False
injected = False
banked_audio_instructions = 0
returned_context = None
returned_frame = None
for instructions in range(100000):
    if ref.pc == 0xc574:
        entered_task = True
    if audio_entry_mode and entered_task and ref.pc == 0xfe8d and not injected:
        ref.nmi()
        injected = True
    if nmi_return_mode and injected and ref.pc == 0xfe8d:
        assert returned_context is None
        returned_context = struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
        returned_frame = bytes(bus[0x1b5:0x1bc])
        assert ref.p == 0xb4 and returned_frame == bytes((0,0xbb,0,0xb4,0xa4,0x8d,0xfe))
        assert bus.bank == 6 and not bus.bits
    reached_boundary = (returned_context is not None and ref.pc == 0xc584) if args.scheduler_resume else (injected and ref.pc == 0xfe8d) if args.nmi_return else (injected and ref.pc == 0xc0f3) if args.audio_reset else (injected and ref.pc == 0x8003) if audio_entry_mode else (entered_task and ref.pc == 0xfe8d) if first_yield_mode else ref.pc == 0xc574
    if reached_boundary:
        break
    if audio_reset_mode and 0x8000 <= ref.pc < 0xc000:
        assert bus.bank == 3
        banked_audio_instructions += 1
    ref.step()
else:
    raise AssertionError('Original reset reference did not reach requested boundary')
expected_ctx = struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
def architectural_status_view(context):
    """Comparison only: canonical B=0/U=1; never mutate oracle P or RAM."""
    return context[:5]+bytes(((context[5]&0xef)|0x20,))+context[6:]
raw_oracle_ctx = expected_ctx
if nmi_return_mode:
    assert returned_context[5] == 0xb4
    assert bus[0x1b9] == 0xa4 and bus[0x1b8] == 0xb4
    if args.scheduler_resume:
        assert ref.p == 0xb4 and bytes(bus[0x1ba:0x1c0]) == bytes((0xcf,0xfe,8,0xbf,0x83,0xc5))
        assert bus.pos == [8,8]
    else:
        assert bytes(bus[0x1b5:0x1bc]) == returned_frame
    assert bus.bank == 6 and not bus.bits
    expected_ctx = architectural_status_view(raw_oracle_ctx)
assert chip[ram:ram+2048] == bytes(bus[:2048]), 'Original/native RAM mismatch'
assert chip[ctx:ctx+8] == expected_ctx, 'Original/native context mismatch'
def journal(kind, start=None, end=None):
    events = [e for e in bus.events if e[0] == kind][start:end]
    return struct.pack('>H',len(events))+b''.join(struct.pack('>HBB',*e[1:]) for e in events)
assert chip[mapper:mapper+82] == journal('mapper',end=20)
assert chip[video:video+8754] == journal('ppu',end=2188)
if first_yield_mode:
    assert entered_task
    assert chip[first_yield:first_yield+6] == journal('ppu',start=2188,end=2189)
    assert len([e for e in bus.events if e[0]=='ppu']) == (2199 if audio_entry_mode else 2189)
if audio_entry_mode:
    assert injected and len(bus.dma) == 1
    assert chip[nmi_prefix:nmi_prefix+298] == journal('ppu',start=2189)+bus.dma[0]
    assert chip[audio_entry:audio_entry+22] == journal('mapper',start=20,end=25)
    assert len([e for e in bus.events if e[0]=='mapper']) == (30 if nmi_return_mode else 25)
if audio_reset_mode:
    assert chip[apu:apu+30] == journal('apu')
    assert len([e for e in bus.events if e[0]=='apu']) == 7
if nmi_return_mode:
    assert chip[restore:restore+22] == journal('mapper',start=25)
    assert ref.p == raw_oracle_ctx[5] == 0xb4
if args.scheduler_resume:
    assert chip[controller:controller+74] == journal('controller')
    assert len([e for e in bus.events if e[0]=='controller']) == 18
ppu = [e for e in bus.events if e[0]=='ppu'][:2188]
for latch in (0,1):
    cleared,_,_ = apply_ppu(ppu,bytes([0xa5])*2048,latch)
    assert cleared == bytes(2048)
report = {'status':'PASS','boundary':('FE24 through first scheduler resume, before C584 task instruction' if args.scheduler_resume else 'FE24 through first silent tick and RTI, before FE8D scheduler instruction' if args.nmi_return else 'FE24 through startup APU reset command return C0F3' if args.audio_reset else 'FE24 through explicit NMI to bank-3 8003 entry' if audio_entry_mode else 'FE24 to first FE8D yield' if first_yield_mode else 'FE24 to C574'),'native_helper_count':steps,
          'ram_bytes_equal':2048,'context_bytes_equal':8,'mapper_records_equal':30 if nmi_return_mode else 25 if audio_entry_mode else 20,
          'ppu_records_equal':2199 if audio_entry_mode else 2189 if first_yield_mode else 2188,
          'guard_regions_intact':len(ranges)*2,'native_stack_balanced':True,
          'original_instruction_count':instructions,
          'limit':'Isolated reset boundary on emulated stock PAL A1200, not title/gameplay boot or speed'}
if audio_entry_mode:
    report['dma_bytes_equal'] = 256
    report['banked_audio_instructions_executed'] = banked_audio_instructions
if audio_reset_mode:
    report['apu_records_equal'] = 7
if nmi_return_mode:
    report['status_representation'] = {'native_canonical_P':'A4','raw_py65_RTI_P':'B4',
        'hardware_saved_P':'A4','handler_saved_P':'B4',
        'comparison':'architectural_status_view clears virtual B, sets U; N/V/D/I/Z/C exact',
        'oracle_P_and_RAM_unchanged':True,'restored_PRG_bank':bus.bank}
if args.scheduler_resume:
    report['controller_records_equal'] = 18
    report['decoded_controller_inputs'] = [0,0]
    report['status_representation']['raw_py65_RTI_P'] = f'{returned_context[5]:02X}'
    report['status_representation']['raw_py65_final_P'] = f'{raw_oracle_ctx[5]:02X}'
print(json.dumps(report,indent=2))
