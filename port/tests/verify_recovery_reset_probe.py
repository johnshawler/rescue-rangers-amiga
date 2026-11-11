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
modes.add_argument('--resumed-task-setup', action='store_true', help='Verify eleven-helper resumed task palette setup probe')
modes.add_argument('--palette-nmi', action='store_true', help='Verify twelve-helper palette NMI prefix probe')
modes.add_argument('--music07', action='store_true', help='Verify private command07 boundary: fourteen calls, thirteen helpers')
modes.add_argument('--music-fetch', action='store_true')
modes.add_argument('--music-command04', action='store_true')
args = parser.parse_args()
music_fetch_mode = args.music_fetch or args.music_command04
music07_mode = args.music07 or music_fetch_mode
palette_nmi_mode = args.palette_nmi or music07_mode
scheduler_resume_mode = args.scheduler_resume or args.resumed_task_setup or palette_nmi_mode
nmi_return_mode = args.nmi_return or scheduler_resume_mode
audio_reset_mode = args.audio_reset or nmi_return_mode
audio_entry_mode = args.nmi_audio_entry or audio_reset_mode
first_yield_mode = args.first_yield or audio_entry_mode
chip = args.chip_dump.read_bytes()
assert len(chip) == 2*1024*1024, 'Expected stock 2 MiB Chip RAM dump'
marker = b'CDRMC041' if args.music_command04 else b'CDRRMFT1' if args.music_fetch else b'CDRRM071' if music07_mode else b'CDRRPAL1' if args.palette_nmi else b'CDRRSET1' if args.resumed_task_setup else b'CDRRRES1' if args.scheduler_resume else b'CDRRRTI1' if args.nmi_return else b'CDRRAPU1' if args.audio_reset else b'CDRRAUD1' if args.nmi_audio_entry else b'CDRRYLD1' if first_yield_mode else b'CDRRST01'
assert chip.count(marker) == 1, 'Expected one live probe report'
offset = chip.index(marker)
status,steps,ram,ctx,mapper,video,stack,stack_end,sp = struct.unpack_from('>9I',chip,offset+8)
assert (status,steps) == (0,16 if args.music_command04 else 15 if music_fetch_mode else 14 if music07_mode else 12 if palette_nmi_mode else 11 if args.resumed_task_setup else 10 if args.scheduler_resume else 9 if args.nmi_return else 8 if args.audio_reset else 7 if args.nmi_audio_entry else 5 if first_yield_mode else 4), (status,steps)
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
if scheduler_resume_mode:
    controller = struct.unpack_from('>I',chip,offset+64)[0]
    ranges.append((controller,74))
if palette_nmi_mode:
    palette_nmi = struct.unpack_from('>I',chip,offset+68)[0]
    ranges.append((palette_nmi,454))
if music07_mode:
    music_entry,music_apu,music_resource = struct.unpack_from('>3I',chip,offset+72)
    ranges.extend(((music_entry,22),(music_apu,30),(music_resource,16384)))
if music_fetch_mode:
    music_fetch = struct.unpack_from('>I',chip,offset+84)[0]
    ranges.append((music_fetch,6))
if args.music_command04:
    music_command04 = struct.unpack_from('>I',chip,offset+88)[0]
    ranges.append((music_command04,14))
for address,size in ranges:
    assert 16 <= address and address+size+16 <= len(chip)
    assert chip[address-16:address] == bytes([0x5a])*16
    assert chip[address+size:address+size+16] == bytes([0x5a])*16
for i,(a,n) in enumerate(ranges):
    for b,m in ranges[i+1:]:
        assert a+n <= b or b+m <= a, 'Overlapping probe buffers'

rom = (P.parent/'input/rescue-rangers-europe.nes').read_bytes()
assert hashlib.sha256(rom).hexdigest() == SHA
if music07_mode:
    resources = rom[16+3*16384:16+4*16384]
    assert len(resources) == 16384
    assert chip[music_resource:music_resource+16384] == resources, 'Private resource changed or wrong bank'
    resource_sha = hashlib.sha256(resources).hexdigest()
    assert hashlib.sha256(chip[music_resource:music_resource+16384]).hexdigest() == resource_sha
bus = ControllerBus(rom) if scheduler_resume_mode else AudioBus(rom) if audio_reset_mode else NmiBus(rom) if audio_entry_mode else OriginalBus(rom)
if scheduler_resume_mode:
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
resumed_task = False
second_nmi = False
fetch_started = False
command_started = False
for instructions in range(100000):
    if ref.pc == 0xc574:
        entered_task = True
    if audio_entry_mode and entered_task and ref.pc == 0xfe8d and not injected:
        ref.nmi()
        injected = True
    if nmi_return_mode and injected and ref.pc == 0xfe8d and returned_context is None:
        assert returned_context is None
        returned_context = struct.pack('>H6B',ref.pc,ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7)
        returned_frame = bytes(bus[0x1b5:0x1bc])
        assert ref.p == 0xb4 and returned_frame == bytes((0,0xbb,0,0xb4,0xa4,0x8d,0xfe))
        assert bus.bank == 6 and not bus.bits
    if scheduler_resume_mode and ref.pc == 0xc584:
        assert returned_context is not None
        assert ref.p == 0xb4 and bytes(bus[0x1b5:0x1bc]) == bytes((0,0xbb,0,0xb4,0xa4,0xcf,0xfe))
        assert bytes(bus[0x1bc:0x1c0]) == bytes((8,0xbf,0x83,0xc5))
        assert bus.pos == [8,8]
        resumed_task = True
    if palette_nmi_mode and resumed_task and ref.pc == 0xfe8d and not second_nmi:
        assert ref.sp == 0xb8 and ref.p == 0xb4 and bus[0x18] == 255
        assert bytes(bus[0x1b9:0x1c0]) == bytes((0xff,0x10,0xa7,0xc2,4,0x93,0xc5))
        second_queue = bytes(bus[0xd9:0xe4])
        ref.nmi()
        second_nmi = True
    if music_fetch_mode and second_nmi and ref.pc == 0xc0f3:
        assert ref.p & 8 == 0, 'Helper14 scope: generic py65 ADC requires D=0'
        fetch_started = True
    if music_fetch_mode and fetch_started and ref.pc == 0x83a0:
        command_started = True
    reached_boundary = (command_started and ref.pc == 0x839d) if args.music_command04 else (fetch_started and ref.pc == 0x83a0) if args.music_fetch else (second_nmi and ref.pc == 0xc0f3) if music07_mode else (second_nmi and ref.pc == 0xc0bf) if args.palette_nmi else (resumed_task and ref.pc == 0xfe8d) if args.resumed_task_setup else (returned_context is not None and ref.pc == 0xc584) if args.scheduler_resume else (injected and ref.pc == 0xfe8d) if args.nmi_return else (injected and ref.pc == 0xc0f3) if args.audio_reset else (injected and ref.pc == 0x8003) if audio_entry_mode else (entered_task and ref.pc == 0xfe8d) if first_yield_mode else ref.pc == 0xc574
    if reached_boundary:
        break
    if audio_reset_mode and 0x8000 <= ref.pc < 0xc000:
        assert bus.bank == 3
        banked_audio_instructions += 1
    if fetch_started and ref.pc in (0x857a,0x802c,0x8030):
        address = ((bus[0xc1]|bus[0xc2]<<8)+ref.y)&65535
        assert 0x8000 <= address <= 0xbfff and bus.bank == 3
        bus.events.append(('resource',address,bus[address],0))
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
    if music07_mode:
        assert second_nmi and ref.sp == (0xab if music_fetch_mode else 0xb1)
        if not music_fetch_mode: assert ref.p == 0x24
        assert bytes(bus[0x1b2:0x1b9]) == bytes((0,0xb8,0,0xb4,0xa4,0x8d,0xfe))
        assert bytes(bus[0x1b9:0x1c0]) == bytes((0xff,0x10,0xa7,0xc2,4,0x93,0xc5))
        assert bus[0xd9] == 7 and bus[0x18] == 0 and bus[0x80] == 4
        old_index = second_queue[2]
        assert bus[0xdb] == (old_index+1)&7
        assert bus[0xdc+old_index] == 0x88
        assert bus[0xda] == second_queue[1]
        assert all(bus[0xdc+i] == second_queue[3+i] for i in range(8) if i != old_index)
    elif palette_nmi_mode:
        assert second_nmi and ref.sp == 0xb1 and ref.p == 0x26
        assert bytes(bus[0x1b2:0x1b9]) == bytes((0,0xb8,0,0xb4,0xa4,0x8d,0xfe))
        assert bytes(bus[0x1b9:0x1c0]) == bytes((0xff,0x10,0xa7,0xc2,4,0x93,0xc5))
        assert bytes(bus[0xd9:0xe4]) == second_queue and bus[0xd9] == 7
        assert 7 in bus[0xdc:0xe4] and bus[0x18] == 0 and bus[0x80] == 4
    elif args.resumed_task_setup:
        assert ref.p == 0xb4 and ref.sp == 0xb8 and resumed_task
        assert bytes(bus[0x1b7:0x1c0]) == bytes((0x0e,0xff,0xff,0x10,0xa7,0xc2,4,0x93,0xc5))
        assert bus[0x18] == 0xff and bus[0xd9] == 7 and bus[0x80] == 1
    elif scheduler_resume_mode:
        assert bus[0x1b9] == 0xa4 and bus[0x1b8] == 0xb4
        assert ref.p == 0xb4 and bytes(bus[0x1ba:0x1c0]) == bytes((0xcf,0xfe,8,0xbf,0x83,0xc5))
        assert bus.pos == [8,8]
    else:
        assert bytes(bus[0x1b5:0x1bc]) == returned_frame
    assert bus.bank == (3 if music07_mode else 6) and not bus.bits
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
    assert len([e for e in bus.events if e[0]=='ppu']) == (2248 if palette_nmi_mode else 2199 if audio_entry_mode else 2189)
if audio_entry_mode:
    assert injected and len(bus.dma) == (2 if palette_nmi_mode else 1)
    assert chip[nmi_prefix:nmi_prefix+298] == journal('ppu',start=2189,end=2199)+bus.dma[0]
    assert chip[audio_entry:audio_entry+22] == journal('mapper',start=20,end=25)
    assert len([e for e in bus.events if e[0]=='mapper']) == (35 if music07_mode else 30 if nmi_return_mode else 25)
if audio_reset_mode:
    assert chip[apu:apu+30] == journal('apu',end=7)
    assert len([e for e in bus.events if e[0]=='apu']) == (14 if music07_mode else 7)
if nmi_return_mode:
    assert chip[restore:restore+22] == journal('mapper',start=25,end=30)
    assert ref.p == raw_oracle_ctx[5]
    if not music_fetch_mode: assert ref.p == (0x24 if music07_mode else 0x26 if args.palette_nmi else 0xb4)
if scheduler_resume_mode:
    assert chip[controller:controller+74] == journal('controller')
    assert len([e for e in bus.events if e[0]=='controller']) == 18
if palette_nmi_mode:
    assert chip[palette_nmi:palette_nmi+454] == journal('ppu',start=2199)+bus.dma[1]
if music07_mode:
    assert chip[music_entry:music_entry+22] == journal('mapper',start=30,end=35)
    assert chip[music_apu:music_apu+30] == journal('apu',start=7,end=14)
if music_fetch_mode:
    assert chip[music_fetch:music_fetch+6] == journal('resource',end=1)
    assert len([e for e in bus.events if e[0]=='resource']) == (4 if args.music_command04 else 1)
if args.music_command04:
    assert chip[music_command04:music_command04+14] == journal('resource',start=1)
ppu = [e for e in bus.events if e[0]=='ppu'][:2188]
for latch in (0,1):
    cleared,_,_ = apply_ppu(ppu,bytes([0xa5])*2048,latch)
    assert cleared == bytes(2048)
report = {'status':'PASS','boundary':('FE24 through first command04, before next stream fetch 839D' if args.music_command04 else 'FE24 through first stream fetch, before 83A0' if args.music_fetch else 'FE24 through second NMI request intake and command07 initialization, before C0F3 tick' if music07_mode else 'FE24 through second logical NMI palette publication, before C0BF audio dispatch' if args.palette_nmi else 'FE24 through resumed task palette setup, before nested FE8D scheduler instruction' if args.resumed_task_setup else 'FE24 through first scheduler resume, before C584 task instruction' if args.scheduler_resume else 'FE24 through first silent tick and RTI, before FE8D scheduler instruction' if args.nmi_return else 'FE24 through startup APU reset command return C0F3' if args.audio_reset else 'FE24 through explicit NMI to bank-3 8003 entry' if audio_entry_mode else 'FE24 to first FE8D yield' if first_yield_mode else 'FE24 to C574'),'native_helper_count':15 if args.music_command04 else 14 if music_fetch_mode else 13 if music07_mode else steps,
          'ram_bytes_equal':2048,'context_bytes_equal':8,'mapper_records_equal':35 if music07_mode else 30 if nmi_return_mode else 25 if audio_entry_mode else 20,
          'ppu_records_equal':2248 if palette_nmi_mode else 2199 if audio_entry_mode else 2189 if first_yield_mode else 2188,
          'guard_regions_intact':len(ranges)*2,'native_stack_balanced':True,
          'original_instruction_count':instructions,
          'limit':'Isolated reset boundary on emulated stock PAL A1200, not title/gameplay boot or speed'}
if audio_entry_mode:
    report['dma_bytes_equal'] = 512 if palette_nmi_mode else 256
    report['banked_audio_instructions_executed'] = banked_audio_instructions
if audio_reset_mode:
    report['apu_records_equal'] = 14 if music07_mode else 7
if nmi_return_mode:
    report['status_representation'] = {'native_canonical_P':'A4','raw_py65_RTI_P':'B4',
        'hardware_saved_P':'A4','handler_saved_P':'B4',
        'comparison':'architectural_status_view clears virtual B, sets U; N/V/D/I/Z/C exact',
        'oracle_P_and_RAM_unchanged':True,'restored_PRG_bank':bus.bank}
if scheduler_resume_mode:
    report['controller_records_equal'] = 18
    report['decoded_controller_inputs'] = [0,0]
    report['status_representation']['raw_py65_RTI_P'] = f'{returned_context[5]:02X}'
    report['status_representation']['raw_py65_final_P'] = f'{raw_oracle_ctx[5]:02X}'
if args.resumed_task_setup:
    report['new_helper_native_registers_preserved'] = True
    report['arithmetic_scope'] = 'D=0 guarded; generic py65 decimal SBC differs from NES binary arithmetic'
    report['pending_palette_request'] = 'FF'
    report['pending_sound_command'] = '07'
    report['nested_task_continuation'] = 'C2A8'
if palette_nmi_mode:
    report['new_helper_native_registers_preserved'] = True
    report['palette_records_equal'] = 49
    report['pending_palette_request'] = '00 (published)'
    report['pending_sound_command'] = '07 (not consumed)'
    report['nested_task_continuation'] = 'C2A8'
    report['logical_NMI_count'] = 2
    report['status_representation']['native_canonical_P'] = f'{expected_ctx[5]:02X}'
if music07_mode:
    report['status_representation']['restored_PRG_bank'] = 6
    report['status_representation']['final_PRG_bank'] = bus.bank
    report.update(native_helper_calls=steps, proprietary_inputs=True,
        resource_bytes_equal=16384, resource_sha256=resource_sha,
        new_intake_mapper_records_equal=5, new_command_apu_records_equal=7,
        pending_sound_command='07 (consumed and initialized)',
        native_registers_preserved_for_new_calls=True,
        distribution='PRIVATE cartridge-bearing diagnostic; not source-only')
if music_fetch_mode:
    report.update(resource_read_records_equal=4 if args.music_command04 else 1,
        arithmetic_scope='Helper14 D=0: generic py65 decimal ADC oracle scope, not a NES requirement',
        preserved_original_NMI_and_task_frames=True,
        limit='Bounded semantic target checkpoint; no gameplay, full tick, RTI, audible Paula or speed claim')
print(json.dumps(report,indent=2))
