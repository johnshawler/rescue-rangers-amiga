#!/usr/bin/env python3
"""Build diagnostic ADFs; music07/fetch/command04 modes require private cartridge data."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
modes = parser.add_mutually_exclusive_group()
modes.add_argument('--first-yield', action='store_true', help='Build separate fifth-helper first-yield probe')
modes.add_argument('--nmi-audio-entry', action='store_true', help='Build separate seven-helper NMI audio-entry probe')
modes.add_argument('--audio-reset', action='store_true', help='Build separate eight-helper audio reset-command probe')
modes.add_argument('--nmi-return', action='store_true', help='Build separate ninth-helper silent tick and RTI probe')
modes.add_argument('--scheduler-resume', action='store_true', help='Build separate tenth-helper scheduler and standard-controller probe')
modes.add_argument('--resumed-task-setup', action='store_true', help='Build separate eleven-helper resumed task palette setup probe')
modes.add_argument('--palette-nmi', action='store_true', help='Build separate twelve-helper palette NMI prefix probe')
modes.add_argument('--music07', action='store_true', help='Build private fourteen-call command07 probe (requires cartridge)')
modes.add_argument('--music-fetch', action='store_true', help='Private first music stream fetch')
modes.add_argument('--music-command04', action='store_true', help='Private first music command04')
modes.add_argument('--music-channel-setup', action='store_true', help='Private 22-call channel setup, stop before command08')
modes.add_argument('--music-first-channel', action='store_true', help='Private 30-call first-channel rest return, PC8085')
args = parser.parse_args()
channel_setup = args.music_channel_setup or args.music_first_channel
command04 = args.music_command04 or channel_setup
music_fetch = args.music_fetch or command04
music07 = args.music07 or music_fetch
palette_nmi = args.palette_nmi or music07
resumed_task_setup = args.resumed_task_setup or palette_nmi
scheduler_resume = args.scheduler_resume or resumed_task_setup
nmi_return = args.nmi_return or scheduler_resume
audio_reset = args.audio_reset or nmi_return
audio_entry = args.nmi_audio_entry or audio_reset
first_yield = args.first_yield or audio_entry
name = 'recovery-music-first-channel-probe' if args.music_first_channel else 'recovery-music-channel-setup-probe' if args.music_channel_setup else 'recovery-music-command04-probe' if args.music_command04 else 'recovery-music-fetch-probe' if args.music_fetch else 'recovery-music07-probe' if music07 else 'recovery-palette-nmi-probe' if args.palette_nmi else 'recovery-resumed-task-setup-probe' if args.resumed_task_setup else 'recovery-scheduler-resume-probe' if args.scheduler_resume else 'recovery-nmi-return-probe' if args.nmi_return else 'recovery-audio-reset-probe' if args.audio_reset else 'recovery-nmi-audio-entry-probe' if args.nmi_audio_entry else 'recovery-first-yield-probe' if first_yield else 'recovery-reset-probe'
P = Path(__file__).resolve().parents[1]
B = P/'build'
B.mkdir(exist_ok=True)
vasm = os.environ['VASM']
resource_sha = None
if music07:
    rom = (P.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest() == '051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411', 'Private cartridge hash mismatch'
    resources = rom[16+3*16384:16+4*16384]
    assert len(resources) == 16384
    resource_file = B/'recovery-music07-private-bank3.bin'
    # Builder-owned output is replaced atomically; final input is read-only.
    temporary = resource_file.with_suffix('.tmp')
    temporary.write_bytes(resources)
    temporary.chmod(0o444)
    temporary.replace(resource_file)
    resource_sha = hashlib.sha256(resources).hexdigest()

payload_file = B/(name+'.bin')
subprocess.run([vasm,'-m68020','-Fbin','-quiet','-I'+str(P/'src'),
                *(['-DFIRST_YIELD=1'] if first_yield else []),
                *(['-DAUDIO_ENTRY=1'] if audio_entry else []),
                *(['-DAUDIO_RESET=1'] if audio_reset else []),
                *(['-DNMI_RETURN=1'] if nmi_return else []),
                *(['-DSCHEDULER_RESUME=1'] if scheduler_resume else []),
                *(['-DRESUMED_TASK_SETUP=1'] if resumed_task_setup else []),
                *(['-DPALETTE_NMI=1'] if palette_nmi else []),
                *(['-DMUSIC_FETCH=1'] if music_fetch else []),
                *(['-DMUSIC_COMMAND04=1'] if command04 else []),
                *(['-DMUSIC_CHANNEL_SETUP=1'] if channel_setup else []),
                *(['-DMUSIC_FIRST_CHANNEL=1'] if args.music_first_channel else []),
                *(['-DMUSIC07=1','-I'+str(B)] if music07 else []),
                '-o',str(payload_file),str(P/'src/recovery_reset_probe.s')], check=True)
payload = payload_file.read_bytes()
rounded = (len(payload)+511)//512*512
boot_file = B/(name+'-boot.bin')
subprocess.run([vasm,'-m68020','-Fbin','-quiet',f'-DPAYLOAD_BYTES={rounded}',
                '-o',str(boot_file),str(P/'src/boot.s')],check=True)
boot = boot_file.read_bytes()
assert len(boot) <= 1024 and rounded <= 901120-1024
disk = bytearray(901120)
disk[:len(boot)] = boot
disk[1024:1024+len(payload)] = payload
checksum = 0
for offset in range(0,1024,4):
    checksum += struct.unpack_from('>I',disk,offset)[0]
    checksum = (checksum&0xffffffff)+(checksum>>32)
struct.pack_into('>I',disk,4,(~checksum)&0xffffffff)
out = B/(name+'.adf')
out.write_bytes(disk)
report = {'artifact':out.name,'purpose':('PRIVATE first-channel rest return, 30 calls/23 helpers, PC8085' if args.music_first_channel else 'PRIVATE channel setup, 22 calls/19 helpers, stop 839D before command08' if args.music_channel_setup else 'PRIVATE first command04, sixteen calls/fifteen helpers, stop 839D' if args.music_command04 else 'PRIVATE first stream fetch, fifteen calls/fourteen helpers, stop 83A0' if args.music_fetch else 'PRIVATE command07 initialization, fourteen calls/thirteen helpers, stop before subsequent tick' if music07 else 'Isolated second palette-capable NMI, stop before C0BF audio dispatch' if args.palette_nmi else 'Isolated resumed task palette setup, stop at nested FE8D yield' if args.resumed_task_setup else 'Isolated scheduler resumption with no pressed buttons, stop before C584' if args.scheduler_resume else 'Isolated first silent tick and RTI, stop before scheduler' if args.nmi_return else 'Isolated reset/NMI startup APU command return, no playback' if args.audio_reset else 'Isolated reset/NMI to bank-3 audio entry, no audio execution' if args.nmi_audio_entry else 'Isolated FE24-to-first-FE8D yield, not game boot' if args.first_yield else 'Isolated FE24-to-C574 reset boundary, not game boot'),
          'payload_bytes':len(payload),'allocation_bytes':rounded,
          'sha256':hashlib.sha256(disk).hexdigest(),'proprietary_inputs':bool(music07)}
if music07:
    report.update(resource_bytes=16384, resource_sha256=resource_sha, native_helper_count=23 if args.music_first_channel else 19 if args.music_channel_setup else 15 if args.music_command04 else 14 if music_fetch else 13, native_helper_calls=30 if args.music_first_channel else 22 if args.music_channel_setup else 16 if args.music_command04 else 15 if music_fetch else 14, distribution='PRIVATE: cartridge-bearing diagnostic; never a source-only disk')
(B/(name+'-build.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
