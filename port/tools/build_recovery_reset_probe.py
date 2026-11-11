#!/usr/bin/env python3
"""Build a source-only reset-boundary ADF, separate from all game disks."""
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
args = parser.parse_args()
audio_entry = args.nmi_audio_entry or args.audio_reset
first_yield = args.first_yield or audio_entry
name = 'recovery-audio-reset-probe' if args.audio_reset else 'recovery-nmi-audio-entry-probe' if args.nmi_audio_entry else 'recovery-first-yield-probe' if first_yield else 'recovery-reset-probe'
P = Path(__file__).resolve().parents[1]
B = P/'build'
B.mkdir(exist_ok=True)
vasm = os.environ['VASM']
payload_file = B/(name+'.bin')
subprocess.run([vasm,'-m68020','-Fbin','-quiet','-I'+str(P/'src'),
                *(['-DFIRST_YIELD=1'] if first_yield else []),
                *(['-DAUDIO_ENTRY=1'] if audio_entry else []),
                *(['-DAUDIO_RESET=1'] if args.audio_reset else []),
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
report = {'artifact':out.name,'purpose':('Isolated reset/NMI startup APU command return, no playback' if args.audio_reset else 'Isolated reset/NMI to bank-3 audio entry, no audio execution' if args.nmi_audio_entry else 'Isolated FE24-to-first-FE8D yield, not game boot' if args.first_yield else 'Isolated FE24-to-C574 reset boundary, not game boot'),
          'payload_bytes':len(payload),'allocation_bytes':rounded,
          'sha256':hashlib.sha256(disk).hexdigest(),'proprietary_inputs':False}
(B/(name+'-build.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
