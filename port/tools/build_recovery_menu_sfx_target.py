#!/usr/bin/env python3
"""Source/ROM-only bounded stock diagnostic. No original oracle import."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
PORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PORT/'tests'))
from recovery_state_menu_sfx_harness import SOURCES
OUT=PORT/'build/recovery_menu_sfx_target'
HISTORIES=('default','right_hold','move_back')
CAPACITY=262144
DEVICE={2:2,3:3,5:5,6:6,7:7,8:8,11:11,20:29,24:39,34:40,35:41,36:42,37:43,40:45,41:7,42:8,43:42,47:42,48:48,70:7}
def sample(history,n):
 if not n:return 0
 if history=='default':return 16 if n<3 else 0 if n<5 else 16
 if history=='right_hold':return 16 if n<3 else 0 if n<5 else 1 if n<8 else 0 if n<40 else 16
 if history=='move_back':return 16 if n<3 else 0 if n<5 else 1 if n<8 else 0 if n<10 else 2 if n<13 else 0 if n<45 else 2 if n<48 else 0 if n<80 else 16
 raise ValueError(history)
def source(history):
 s=(PORT/'src/recovery_menu_sfx_target.s').read_text()
 s+='\n'.join(f' include "{n}.s"' for n in SOURCES)+'\n'
 s+=' include "recovery_state_menu_display_device.s"\n cnop 0,4\nreport:\n dc.b "CDRSFX01"\n dc.l -99\n dcb.l 15,0\n dc.l capture,0,0,0,0\npad_value:\n dc.b 0\ndevice_ids:\n dc.b '+','.join(str(DEVICE.get(i,255)) for i in range(72))+'\ninput_samples:\n dc.b '+','.join(str(sample(history,i)) for i in range(128))+'\n cnop 0,4\n'
 for label,body in [('ram','dcb.b 2048,$a5'),('context','dc.b $fe,$24,$17,$33,0,$24,$fd,$a7'),('journal','dcb.b 134638,0'),('runtime','dc.b $0c,0,0,3,0,0,$ff,$ff,0,0,$d5,1'),('resource','incbin "private-prg.bin"'),('stack','dcb.b 4096,0\nstack_end:'),('capture',f'dcb.b {CAPACITY},0')]:
  s+=f' dcb.b 16,$5a\n{label}:\n {body}\n dcb.b 16,$5a\n'
 return s

def main():
 manifest=PORT/'analysis/recovery_state_menu_sfx_manifest.json'
 assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='2bd2c5764f3d13798e662c9b8260def979b1188f3d1eeb583ca02bb198821651'
 frozen=json.loads(manifest.read_text())
 for key in ('files',):
  for item in frozen.get(key,[]):assert hashlib.sha256((PORT.parent/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 dependencies=json.loads((PORT/'analysis/recovery_menu_sfx_target_dependencies.json').read_text())
 for item in dependencies['frozen_dependencies']:assert hashlib.sha256((PORT.parent/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 for history in HISTORIES:
  out=OUT/history;out.mkdir(parents=True,exist_ok=True)
  (out/'private-prg.bin').write_bytes(rom[16:131088]);(out/'startup-display-private-chr.bin').write_bytes(rom[131088:262160])
  (out/'recovery_menu_sfx_target.s').write_text(source(history))
  def asm(src,dst,*flags):subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(PORT/'src'),'-I'+str(out),*flags,'-o',str(dst),str(src)],check=True)
  asm(out/'recovery_menu_sfx_target.s',out/'recovery_menu_sfx_target.bin')
  data=(out/'recovery_menu_sfx_target.bin').read_bytes();rounded=(len(data)+511)//512*512;allocation=(len(data)+16+511)//512*512
  assert allocation<1536*1024 and rounded<=900096
  (out/'boot.s').write_text((PORT/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'))
  asm(out/'boot.s',out/'boot.bin',f'-DPAYLOAD_BYTES={rounded}')
  boot=(out/'boot.bin').read_bytes();disk=bytearray(901120);assert len(boot)<=1024
  disk[:len(boot)]=boot;disk[1024:1024+len(data)]=data
  checksum=0
  for off in range(0,1024,4):checksum+=struct.unpack_from('>I',disk,off)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
  struct.pack_into('>I',disk,4,(~checksum)&0xffffffff);(out/'recovery_menu_sfx_target.adf').write_bytes(disk)
  report=dict(history=history,payload_bytes=len(data),journal_capture_capacity=CAPACITY,allocation_bytes=allocation,adf_sha256=hashlib.sha256(disk).hexdigest(),source_sha256=hashlib.sha256(source(history).encode()).hexdigest())
  (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
