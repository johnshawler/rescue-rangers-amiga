#!/usr/bin/env python3
"""Build additive input-only diagnostic; no ROM or game resources required."""
import os, subprocess, struct, hashlib, json, argparse
from pathlib import Path
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
B=parser.parse_args().output.resolve();B.mkdir(parents=True,exist_ok=False)
v=os.environ['VASM']
def asm(source,out,*extra):
 subprocess.run([v,'-quiet','-m68020','-Fbin','-I'+str(P/'src'),*extra,'-o',str(out),str(source)],check=True)
asm(P/'src/recovery_zx_probe.s',B/'probe.bin')
payload=(B/'probe.bin').read_bytes();size=(len(payload)+511)&~511
asm(P/'src/boot.s',B/'boot.bin','-DPAYLOAD_BYTES='+str(size))
disk=bytearray(901120);boot=(B/'boot.bin').read_bytes();disk[:len(boot)]=boot;disk[1024:1024+len(payload)]=payload
checksum=0
for i in range(0,1024,4):
 checksum+=struct.unpack_from('>I',disk,i)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
struct.pack_into('>I',disk,4,(~checksum)&0xffffffff)
(B/'input-probe.adf').write_bytes(disk)
r={'classification':'Input-only diagnostic, not playable-game integration or speed evidence','allocation_bytes':size,'provenance':{str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'src/recovery_zx_keyboard.s',P/'src/recovery_zx_probe.s',P/'src/amiga_clock.s',P/'src/boot.s')},'payload_sha256':hashlib.sha256(payload).hexdigest(),'boot_sha256':hashlib.sha256(boot).hexdigest(),'sha256':hashlib.sha256(disk).hexdigest()}
(B/'build.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
