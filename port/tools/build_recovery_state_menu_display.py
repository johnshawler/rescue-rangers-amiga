#!/usr/bin/env python3
"""Private source-only state-driven stock-Amiga diagnostic; no oracle import."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
PORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PORT/'tests'))
from recovery_state_dispatch_menu_harness import SOURCES
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
OUT=PORT/'build/recovery_state_menu_display'
WORKSPACE=786432
# Adapter IDs translate actual published helper type to the frozen consumer ABI.
DEVICE={2:2,3:3,5:5,6:6,7:7,8:8,11:11,20:29,24:39,34:40,35:41,36:42,37:43,40:45,41:7,42:8,43:42,47:42,48:48}
def source():
 s=''' lea $dff000,a5
 move.w #$7fff,$9a(a5)
 move.w #$7fff,$96(a5)
 move.w #$7fff,$9c(a5)
 move.w #$0200,$100(a5)
 lea report(pc),a6
 lea stack_end(pc),sp
'''
 for i,label in enumerate(('ram','context','journal','runtime','resource','stack','stack_end','snapshots','snapshots_end')):
  s+=f' lea {label}(pc),a3\n move.l a3,{24+4*i}(a6)\n'
 s+=''' lea snapshots(pc),a3
 move.l a3,60(a6)
 lea snapshots_end(pc),a3
 moveq #15,d0
.guard:
 move.b #$5a,(a3)+
 dbra d0,.guard
 bsr.l llb_amiga_clock_start
.loop:
 cmpi.l #4096,12(a6)
 bhs.w failed
 lea ram(pc),a0
 lea context(pc),a1
 lea journal(pc),a2
 lea runtime(pc),a4
 lea resource(pc),a5
 move.l #$baddf00d,6(a4)
 move.l a2,a3
 move.l #67319,d0
.clear:
 clr.w (a3)+
 subq.l #1,d0
 bne.s .clear
 moveq #0,d0
 cmpi.w #$a025,(a1)
 bne.s .pad_ready
 lea pad_value(pc),a3
 move.b #16,(a3)
.pad_ready:
 move.b pad_value(pc),d0
 moveq #0,d1
 move.l 20(a6),d2
 move.l #$33445566,d3
 move.l #$44556677,d4
 move.l #$55667788,d5
 move.l #$66778899,d6
 move.l #$778899aa,d7
 movem.l d1-d7/a0-a6,-(sp)
 bsr.l recovery_state_dispatch_menu
 move.l d0,64(a6)
 movem.l d1-d7/a0-a6,-(sp)
 move.l sp,a2
 lea 56(sp),a3
 moveq #13,d0
.abi:
 move.l (a2)+,d1
 cmp.l (a3)+,d1
 bne.w abi_failed
 dbra d0,.abi
 movem.l (sp)+,d1-d7/a0-a6
 lea 56(sp),sp
 lea stack_end(pc),a3
 cmpa.l sp,a3
 bne.w stack_failed
 move.l 64(a6),d0
 cmpi.l #1,d0
 beq.s .advanced
 tst.l d0
 bne.w .terminal
 tst.l 20(a6)
 bne.w failed
 move.l #1,20(a6)
 addq.l #1,16(a6)
 bra.w .loop
.advanced:
 clr.l 20(a6)
 ; Bounded dynamic captures: context/runtime/journal every completion,
 ; RAM at the first 64 boundaries. No record feeds helper selection.
 move.l 60(a6),a3
 moveq #0,d0
 move.w 8(a4),d0
 cmpi.w #48,6(a4)
 bne.s .size_ready
 cmpi.w #$ffff,d0
 bne.w failed
 move.l #134638,d0
.size_ready:
 move.l a3,d1
 add.l d0,d1
 addi.l #2080,d1
 lea snapshots_end(pc),a2
 cmp.l a2,d1
 bhs.w failed
 move.l #1,(a3)+
 move.l (a1),(a3)+
 move.l 4(a1),(a3)+
 move.l (a4),(a3)+
 move.l 4(a4),(a3)+
 move.l 8(a4),(a3)+
 move.l d0,(a3)+
 moveq #0,d1
 cmpi.l #64,12(a6)
 bhs.s .no_ram
 move.l #2048,d1
.no_ram:
 move.l d1,(a3)+
 tst.l d1
 beq.s .journal
 move.l a0,a2
 move.w #511,d1
.copy_ram:
 move.l (a2)+,(a3)+
 dbra d1,.copy_ram
.journal:
 lea journal(pc),a2
 tst.l d0
 beq.s .captured
 .copy_journal:
 move.b (a2)+,(a3)+
 subq.l #1,d0
 bne.s .copy_journal
.captured:
 move.l a3,60(a6)
 addq.l #1,12(a6)
 moveq #0,d0
 move.w 6(a4),d0
 lea device_ids(pc),a3
 move.b (a3,d0.w),d0
 cmpi.b #$ff,d0
 beq.s .next
 lea journal(pc),a2
 bsr.l startup_consume
.next:
 cmpi.w #$a06c,(a1)
 beq.s .render
 bra.w .loop
.terminal:
 cmpi.l #-1,d0
 bne.s failed
 bra.s failed
.render:
 move.l sp,68(a6)
 clr.l 8(a6)
 bsr.l startup_display
stop:
 bra.s stop
abi_failed:
 moveq #-2,d0
 bra.s failed
stack_failed:
 moveq #-3,d0
failed:
 move.l d0,8(a6)
 move.l sp,68(a6)
 move.w #$f00,$dff180
 bra.s stop
'''
 s+='\n'.join(f' include "{n}.s"' for n in SOURCES)+'\n'
 s+=' include "recovery_state_menu_display_device.s"\n cnop 0,4\nreport:\n dc.b "CDRMEN01"\n dc.l -99\n dcb.l 15,0\npad_value:\n dc.b 0\ndevice_ids:\n dc.b '+','.join(str(DEVICE.get(i,255)) for i in range(56))+'\n cnop 0,4\n'
 for label,body in [('ram','dcb.b 2048,$a5'),('context','dc.b $fe,$24,$17,$33,0,$24,$fd,$a7'),('journal','dcb.b 134638,0'),('runtime','dc.b $0c,0,0,3,0,0,$ff,$ff,0,0,$d5,1'),('resource','incbin "private-prg.bin"'),('stack','dcb.b 4096,0\nstack_end:')]:
  s+=f' dcb.b 16,$5a\n{label}:\n {body}\n dcb.b 16,$5a\n'
 s+=f' dcb.b 16,$5a\nsnapshots:\nsnapshots_end equ snapshots+{WORKSPACE}\n'
 return s

def main():
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
 (OUT/'recovery_state_menu_display.s').write_text(source())
 def asm(src,dst,*flags):subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(PORT/'src'),'-I'+str(OUT),*flags,'-o',str(dst),str(src)],check=True)
 asm(OUT/'recovery_state_menu_display.s',OUT/'recovery_state_menu_display.bin')
 data=(OUT/'recovery_state_menu_display.bin').read_bytes();rounded=(len(data)+511)//512*512;allocation=(len(data)+WORKSPACE+16+511)//512*512
 assert allocation<1536*1024
 (OUT/'boot.s').write_text((PORT/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'))
 asm(OUT/'boot.s',OUT/'boot.bin',f'-DPAYLOAD_BYTES={rounded}')
 boot=(OUT/'boot.bin').read_bytes();disk=bytearray(901120);assert len(boot)<=1024 and rounded<=900096
 disk[:len(boot)]=boot;disk[1024:1024+len(data)]=data
 checksum=0
 for off in range(0,1024,4):checksum+=struct.unpack_from('>I',disk,off)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
 struct.pack_into('>I',disk,4,(~checksum)&0xffffffff);(OUT/'recovery_state_menu_display.adf').write_bytes(disk)
 report=dict(payload_bytes=len(data),workspace_bytes=WORKSPACE,allocation_bytes=allocation,adf_sha256=hashlib.sha256(disk).hexdigest(),source_sha256=hashlib.sha256(source().encode()).hexdigest())
 (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
