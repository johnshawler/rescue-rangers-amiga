#!/usr/bin/env python3
"""Fixture-free final title from published 1024 native calls. Private ROM required."""
from pathlib import Path
import os,sys,hashlib,json,struct,subprocess
PORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PORT/'tools'))
from build_recovery_resident_chr_fade_probe import source,layout,NAMES,SHA,oracle
OUT=PORT/'build/startup-display-native'
DEVICE_INDICES={2,3,5,6,7,8,11,29,31,39,40,41,42,43,45}
def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 assert hashlib.sha256(rom).hexdigest()==SHA
 results,_,_=oracle(rom)
 assert len(results)==1024
 OUT.mkdir(exist_ok=True,parents=True)
 for bank in (2,3):
  (OUT/f'recovery-resident-chr-fade-private-bank{bank}.bin').write_bytes(rom[16+bank*16384:16+(bank+1)*16384])
 (OUT/'startup-display-private-chr.bin').write_bytes(rom[16+131072:16+262144])
 s=source(results,0)
 # Existing generator emits only schedule/status constants and reset initialization,
 # never expected RAM/context/journal bytes. Keep its complete guards/captures.
 s=s.replace(' move.l sp,36(a6)',' move.l sp,36(a6)\n bsr.l llb_amiga_clock_start')
 for index in DEVICE_INDICES:
  s=s.replace(f' bsr.l {NAMES[index]}\n',f' bsr.l {NAMES[index]}\n move.l d0,-(sp)\n move.l #{index},d0\n bsr.l startup_consume\n move.l (sp)+,d0\n')
 s=s.replace(' move.w #$0070,$180(a5)',' bsr.l startup_display')
 s=s.replace('snapshots:\n', ' include "recovery_startup_display_device.s"\n dcb.b 16,$5a\nsnapshots:\n')
 (OUT/'startup-display.s').write_text(s)
 def asm(src,dst,*extra):
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(PORT/'src'),'-I'+str(OUT),*extra,'-o',str(dst),str(src)],check=True)
 asm(OUT/'startup-display.s',OUT/'startup-display.bin')
 data=(OUT/'startup-display.bin').read_bytes();rounded=(len(data)+511)//512*512
 _,workspace=layout(results,0);allocation=(len(data)+workspace+16+511)//512*512
 assert allocation<1536*1024
 (OUT/'startup-display-boot.s').write_text((PORT/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'))
 asm(OUT/'startup-display-boot.s',OUT/'startup-display-boot.bin',f'-DPAYLOAD_BYTES={rounded}')
 boot=(OUT/'startup-display-boot.bin').read_bytes();disk=bytearray(901120)
 assert len(boot)<=1024 and len(data)<=900096
 disk[:len(boot)]=boot;disk[1024:1024+len(data)]=data
 checksum=0
 for off in range(0,1024,4):
  checksum+=struct.unpack_from('>I',disk,off)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
 struct.pack_into('>I',disk,4,(~checksum)&0xffffffff)
 (OUT/'startup-display.adf').write_bytes(disk)
 report={'scope':'Private frozen C5D1 native-startup display, no runtime CPU interpreter or fixture state','payload_bytes':len(data),'allocation_bytes':allocation,'workspace_bytes':workspace,'adf_sha256':hashlib.sha256(disk).hexdigest()}
 (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
