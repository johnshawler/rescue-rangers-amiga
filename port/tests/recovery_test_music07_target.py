#!/usr/bin/env python3
"""Corrupt private command07 target dump and reject all eight earlier modes.

Requires the private target dump, eight prior dumps and original-ROM input.
Run after the stock target probe/verifier. No cartridge or dump bytes embedded.
"""
from pathlib import Path
import subprocess, struct, tempfile, json, os, sys
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
names=['reset','first-yield','nmi-audio-entry','audio-reset','nmi-return','scheduler-resume','resumed-task-setup','palette-nmi']
cmd=[sys.executable,'port/tests/verify_recovery_reset_probe.py']
p=Path('port/build/recovery-music07-probe-chip.bin');data=p.read_bytes();o=data.index(b'CDRRM071');r=struct.unpack_from('>19I',data,o+8)
status,steps,ram,ctx,mapper,video,stack,end,sp,yieldp,nmi,entry,apu,restore,controller,palette,music_entry,music_apu,resource=r
ranges=[(ram,2048),(ctx,8),(mapper,82),(video,8754),(stack,4096),(yieldp,6),(nmi,298),(entry,22),(apu,30),(restore,22),(controller,74),(palette,454),(music_entry,22),(music_apu,30),(resource,16384)]
new=['--music07']
# Rejecting corrupt input proves nothing unless all matching baselines succeed.
subprocess.run(cmd+new+[str(p)],check=True,capture_output=True,timeout=30)
for n in names:
 mode=[] if n=='reset' else ['--'+n]
 subprocess.run(cmd+mode+[f'port/build/recovery-{n}-probe-chip.bin'],check=True,capture_output=True,timeout=30)
positions=set(range(o,o+84))|set(range(ctx,ctx+8))|set(range(controller,controller+74))|set(range(palette,palette+454))
positions|={o+40+i for i in range(4)}|set(range(o+68,o+72))
positions|={ram+a for a in [0,1,0x18,0x80,0x81,0x82,0x91,0x92,0xd9,0xda,0xdb,0xdc,0xdd,*range(0x1b2,0x1c0),*range(0x300,0x340)]}
for a,n in ranges:positions|={a-1,a+n}
for a,n in [(mapper,82),(video,8754),(yieldp,6),(nmi,298),(entry,22),(apu,30),(restore,22)]:positions|={a,a+2,a+n-1}
positions|={apu+4+4*i for i in range(7)}|{nmi+42+i for i in range(256)}
positions |= set(range(music_entry,music_entry+22)) | set(range(music_apu,music_apu+30))
positions |= {resource+i for i in [0,1,0xa00,0xa11,0xa12,16382,16383,*range(0,16384,257)]}
private_pointer=(data[resource+0xa11]<<8)|data[resource+0xa12]
positions |= set(range(resource+private_pointer-0x8000,resource+private_pointer-0x8000+9))
with tempfile.TemporaryDirectory() as t:
 q=Path(t)/'bad.bin'
 for at in sorted(positions):
  d=bytearray(data);d[at]^=1;q.write_bytes(d)
  x=subprocess.run(cmd+new+[str(q)],capture_output=True,timeout=30)
  assert x.returncode!=0,at
# Explicit alias/out-of-range report-pointer mutations in addition to bit flips.
with tempfile.TemporaryDirectory() as t:
 q=Path(t)/'bad-pointer.bin'
 pointer_rejections=0
 for field in (72,76,80):
  for destination in (0,len(data)-1,ram,stack,entry,palette):
   d=bytearray(data);struct.pack_into('>I',d,o+field,destination);q.write_bytes(d)
   assert subprocess.run(cmd+new+[str(q)],capture_output=True,timeout=30).returncode!=0
   pointer_rejections+=1
for n in names:
 mode=[] if n=='reset' else ['--'+n]
 assert subprocess.run(cmd+mode+[str(p)],capture_output=True,timeout=30).returncode!=0
 assert subprocess.run(cmd+new+[f'port/build/recovery-{n}-probe-chip.bin'],capture_output=True,timeout=30).returncode!=0
report={'corruption_rejections':len(positions),'cross_mode_rejections':16, 'positive_baselines':9, 'alias_range_rejections':pointer_rejections}
Path('logs/recovery-music07-probe-verifier-negative.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
