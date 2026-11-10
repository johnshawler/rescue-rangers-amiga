#!/usr/bin/env python3
"""Build interactive native 68020 title menu. Initial NT/OAM/RAM are explicit fixtures."""
from pathlib import Path
import hashlib, json, os, struct, subprocess

P = Path(__file__).resolve().parents[1]
L = P.parent
A, B = P / 'assets', P / 'build'
B.mkdir(exist_ok=True)
VASM = os.environ.get('VASM', str(L.parent / 'nes-amiga-lab/repos/vscode-amiga-debug/bin/linux/vasmm68k_mot'))
ROM_SHA = '051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
rom = (L / 'input/rescue-rangers-europe.nes').read_bytes()
assert hashlib.sha256(rom).hexdigest() == ROM_SHA
s = (A / 'title-snapshot.bin').read_bytes()
assert len(s) == 9700 and s[:2] == bytes([0x90, 0x1e])
chr_bank = rom[16+131072+31*4096:16+131072+32*4096]
assert s[1252:9444] == chr_bank * 2
(A / 'title-chr.bin').write_bytes(chr_bank * 2)
(A / 'title-nametable.bin').write_bytes(s[228:1252])
(A / 'title-oam.bin').write_bytes(s[9444:9700])
(A / 'title-ram.bin').write_bytes((L/'artifacts/title-ram.bin').read_bytes())
pal, rgb = s[4:36], s[36:228]
colors = []
for n in range(32):
    i = pal[n if n % 4 else 0] & 63
    r,g,b = rgb[i*3:i*3+3]
    colors.append((r >> 4) << 8 | (g >> 4) << 4 | b >> 4)
(A / 'palette.s').write_text(''.join(f'        dc.w ${0x180+i*2:03x},${c:03x}\n' for i,c in enumerate(colors)))
def assemble(name, *extra):
    subprocess.run([VASM, '-m68020', '-Fbin', '-quiet', '-I'+str(A), '-I'+str(P/'src'), *extra,
                    '-o', str(B/f'{name}.bin'), str(P/f'src/{name}.s')], check=True)
assemble('title')
payload = (B/'title.bin').read_bytes()
rounded = (len(payload)+511)//512*512
assemble('boot', f'-DPAYLOAD_BYTES={rounded}')
boot=(B/'boot.bin').read_bytes()
assert len(boot) <= 1024 and rounded <= 901120-1024
disk=bytearray(901120)
disk[:len(boot)]=boot
disk[1024:1024+len(payload)]=payload
checksum=0
for i in range(0,1024,4):
    checksum += struct.unpack_from('>I',disk,i)[0]
    checksum = (checksum&0xffffffff)+(checksum>>32)
struct.pack_into('>I',disk,4,(~checksum)&0xffffffff)
adf=B/'rescue-rangers-title.adf'
adf.write_bytes(disk)
report={'milestone':'Interactive title menu rendered and controlled by native 68020 code, not gameplay',
        'payload_bytes':len(payload),'boot_allocation_bytes':rounded,
        'adf_sha256':hashlib.sha256(disk).hexdigest(),'rom_sha256':ROM_SHA,
        'graphics_source':'Original CHR bank31; snapshot nametable, palette and OAM at PAL frame200',
        'target':'PAL A1200, 2MiB Chip, 0 Fast, JIT disabled'}
(B/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
