#!/usr/bin/env python3
"""Private source-only state-driven stock-Amiga diagnostic; no oracle import."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
PORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PORT/'tests'))
from recovery_state_dispatch_menu_harness import SOURCES
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
OUT=PORT/'build/recovery_menu_timing'
WORKSPACE=0
# Adapter IDs translate actual published helper type to the frozen consumer ABI.
DEVICE={2:2,3:3,5:5,6:6,7:7,8:8,11:11,20:29,24:39,34:40,35:41,36:42,37:43,40:45,41:7,42:8,43:42,47:42,48:48}
def source():
 s=(PORT/'src/recovery_menu_timing.s').read_text()
 s+='\n'.join(f' include "{n}.s"' for n in SOURCES)+'\n'
 s+=' include "recovery_state_menu_display_device.s"\n cnop 0,4\nreport:\n dc.b "CDRTIM01"\n dc.l -99\n dcb.l 15,0\npad_value:\n dc.b 0\ndevice_ids:\n dc.b '+','.join(str(DEVICE.get(i,255)) for i in range(56))+'\n cnop 0,4\n'
 for label,body in [('ram','dcb.b 2048,$a5'),('context','dc.b $fe,$24,$17,$33,0,$24,$fd,$a7'),('journal','dcb.b 134638,0'),('runtime','dc.b $0c,0,0,3,0,0,$ff,$ff,0,0,$d5,1'),('resource','incbin "private-prg.bin"'),('stack','dcb.b 4096,0\nstack_end:')]:
  s+=f' dcb.b 16,$5a\n{label}:\n {body}\n dcb.b 16,$5a\n'
 return s

def main():
 dependency_map=json.loads((PORT/'analysis/recovery_menu_timing_dependencies.json').read_text())
 for item in dependency_map['frozen_dependencies']:
  assert hashlib.sha256((PORT.parent/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 manifest=PORT/'analysis/recovery_state_dispatch_menu_manifest.json'
 assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='db470ae116885409b124035a6e0dc879b65b3172f9a799c6b5d39b291ab53a15'
 frozen=json.loads(manifest.read_text())
 for item in frozen['new_files']+frozen['frozen_dependencies']:
  assert hashlib.sha256((PORT.parent/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 display_manifest=PORT/'analysis/recovery_startup_display_source_manifest.json'
 assert hashlib.sha256(display_manifest.read_bytes()).hexdigest()=='3a7d605c5cec2a3b46c1880dd12d09debf2e4ce7116359e066159a4312d864ab'
 display=json.loads(display_manifest.read_text())
 for name in ('src/recovery_startup_display_device.s','src/native_background.s','src/native_sprite_blitter.s','src/amiga_clock.s','src/boot.s'):
  expected=(display['new_files']|display['existing_dependencies'])[name]
  assert hashlib.sha256((PORT/name).read_bytes()).hexdigest()==expected,name
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'private-prg.bin').write_bytes(rom[16:131088]);(OUT/'startup-display-private-chr.bin').write_bytes(rom[131088:262160])
 (OUT/'recovery_menu_timing.s').write_text(source())
 def asm(src,dst,*flags):subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(PORT/'src'),'-I'+str(OUT),*flags,'-o',str(dst),str(src)],check=True)
 asm(OUT/'recovery_menu_timing.s',OUT/'recovery_menu_timing.bin')
 data=(OUT/'recovery_menu_timing.bin').read_bytes();rounded=(len(data)+511)//512*512;allocation=(len(data)+WORKSPACE+16+511)//512*512
 assert allocation<1536*1024
 (OUT/'boot.s').write_text((PORT/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'))
 asm(OUT/'boot.s',OUT/'boot.bin',f'-DPAYLOAD_BYTES={rounded}')
 boot=(OUT/'boot.bin').read_bytes();disk=bytearray(901120);assert len(boot)<=1024 and rounded<=900096
 disk[:len(boot)]=boot;disk[1024:1024+len(data)]=data
 checksum=0
 for off in range(0,1024,4):checksum+=struct.unpack_from('>I',disk,off)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
 struct.pack_into('>I',disk,4,(~checksum)&0xffffffff);(OUT/'recovery_menu_timing.adf').write_bytes(disk)
 report=dict(payload_bytes=len(data),workspace_bytes=WORKSPACE,allocation_bytes=allocation,adf_sha256=hashlib.sha256(disk).hexdigest(),source_sha256=hashlib.sha256(source().encode()).hexdigest())
 (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
