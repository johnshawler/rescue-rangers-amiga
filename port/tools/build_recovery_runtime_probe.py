#!/usr/bin/env python3
"""Build a private cartridge-bearing 68-call diagnostic, never a source-only disk."""
from pathlib import Path
import argparse, hashlib, json, os, struct, subprocess
PORT=Path(__file__).resolve().parents[1]
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
STRIDE=11000
NAMES=('recovery_audio_reset_command', 'recovery_reset_ram', 'recovery_reset_mapper', 'recovery_reset_video', 'recovery_reset_dispatch', 'recovery_first_yield', 'recovery_first_nmi_prefix', 'recovery_nmi_audio_entry', 'recovery_silent_tick_rti', 'recovery_scheduler_resume', 'recovery_resumed_task_setup', 'recovery_palette_nmi_prefix', 'recovery_music07_command', 'recovery_music_tick_fetch', 'recovery_music_command04', 'recovery_music_stream_fetch', 'recovery_music_command05', 'recovery_music_command06', 'recovery_music_stream_command07_volume', 'recovery_music_event_instrument08', 'recovery_music_event_command18', 'recovery_music_event_command09', 'recovery_music_event_rest', 'recovery_music_channel_iteration', 'recovery_music_indexed_fetch', 'recovery_music_indexed_commands', 'recovery_music_indexed_rest', 'recovery_music_pitched_gate', 'recovery_music_pitched_note', 'recovery_active_nmi_return', 'recovery_general_task_scheduler', 'recovery_idle_nmi_prefix')
SIZES={0: 30, 1: 0, 2: 82, 3: 8754, 4: 0, 5: 6, 6: 298, 7: 22, 8: 22, 9: 74, 10: 0, 11: 454, 12: 30, 13: 6, 14: 14, 15: 6, 16: 18, 17: 14, 18: 14, 19: 22, 20: 14, 21: 14, 22: 10, 23: 0, 24: 6, 25: 22, 26: 10, 27: 10, 28: 18, 29: 22, 30: 74, 31: 454}
SEQUENCE=[1, 2, 3, 4, 5, 6, 7, 0, 8, 9, 10, 30, 31, 7, 12, 13, 14, 15, 16, 15, 17, 15, 18, 15, 19, 15, 20, 15, 21, 15, 22, 23, 24, 25, 24, 25, 24, 25, 24, 25, 24, 26, 23, 24, 25, 24, 25, 24, 25, 24, 25, 24, 26, 23, 24, 25, 24, 25, 24, 25, 24, 25, 24, 27, 28, 23, 29, 30]
def source():
    lines=[''' lea $dff000,a5
 move.w #$7fff,$9a(a5)
 move.w #$7fff,$96(a5)
 move.w #$7fff,$9c(a5)
 move.w #$0200,$100(a5)
 lea report(pc),a6
 lea stack_end(pc),sp
 lea ram(pc),a0
 lea context(pc),a1
 move.l a0,16(a6)
 move.l a1,20(a6)
 lea snapshots(pc),a4
 move.l a4,24(a6)
 move.l #$5a5a5a5a,748000(a4)
 move.l #$5a5a5a5a,748004(a4)
 move.l #$5a5a5a5a,748008(a4)
 move.l #$5a5a5a5a,748012(a4)
 lea resource(pc),a3
 move.l a3,28(a6)
 lea stack(pc),a4
 move.l a4,32(a6)
 move.l sp,36(a6)
''']
    for call,index in enumerate(SEQUENCE):
        status=0 if call==11 else 1
        lines.append(f''' lea snapshots+{call*STRIDE}(pc),a4
 move.l #{index},(a4)
 move.l #{status},4(a4)
 move.l #{SIZES[index]},8(a4)
 lea 2068(a4),a2
 lea resource(pc),a3
 moveq #0,d0
 moveq #0,d1
 move.l #$22334455,d2
 move.l #$33445566,d3
 move.l #$44556677,d4
 move.l #$55667788,d5
 move.l #$66778899,d6
 move.l #$778899aa,d7
 movem.l d1-d7/a0-a6,-(sp)
 bsr.w {NAMES[index]}
 cmpi.l #{status},d0
 bne.w failed
 movem.l d1-d7/a0-a6,-(sp)
 move.l sp,a3
 lea 56(sp),a4
 moveq #13,d0
abi_{call}:
 move.l (a3)+,d1
 cmp.l (a4)+,d1
 bne.w abi_failed
 dbra d0,abi_{call}
 movem.l (sp)+,d1-d7/a0-a6
 lea 56(sp),sp
 lea stack_end(pc),a4
 cmpa.l sp,a4
 bne.w stack_failed
 lea snapshots+{call*STRIDE+12}(pc),a4
 move.l (a1),(a4)+
 move.l 4(a1),(a4)+
 move.l a0,a3
 move.w #511,d0
copy_{call}:
 move.l (a3)+,(a4)+
 dbra d0,copy_{call}
 addq.l #1,12(a6)
''')
    lines.append(''' move.l sp,40(a6)
 clr.l 8(a6)
 move.w #$0070,$180(a5)
stop:
 bra.s stop
abi_failed:
 moveq #-2,d0
 bra.s failed
stack_failed:
 moveq #-3,d0
failed:
 move.l d0,8(a6)
 move.l sp,40(a6)
 move.w #$0700,$180(a5)
 bra.s stop
''')
    lines += [f' include "{name}.s"\n' for name in NAMES]
    lines += [''' even
report:
 dc.b 'CDRRUN01'
 dc.l -99,0,0,0,0,0,0,0,0
 dcb.b 16,$5a
ram:
 dcb.b 2048,$a5
 dcb.b 32,$5a
context:
 dc.b $fe,$24,$17,$33,0,$24,$fd,$a7
 dcb.b 32,$5a
stack:
 dcb.b 4096,0
stack_end:
 dcb.b 32,$5a
resource:
 incbin "recovery-runtime-private-bank3.bin"
 dcb.b 32,$5a
snapshots:
; The boot loader allocates and clears this private snapshot workspace.
; Do not waste disk reads on 748016 bytes of initially zero workspace.
''']
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=PORT.parent/'input/rescue-rangers-europe.nes')
    parser.add_argument('--output-dir',type=Path,default=PORT/'build')
    args=parser.parse_args()
    # Fail closed before mkdir, extracts, assembler outputs, or reports.
    rom=args.rom.read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA,'Private cartridge hash mismatch'
    resources=rom[16+3*16384:16+4*16384]
    assert len(resources)==16384
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    resource=out/'recovery-runtime-private-bank3.bin'
    resource.write_bytes(resources)
    src=out/'recovery-runtime-private-driver.s';src.write_text(source())
    name='recovery-runtime-probe'
    payload=out/(name+'.bin');vasm=os.environ['VASM']
    subprocess.run([vasm,'-m68020','-Fbin','-quiet','-I'+str(PORT/'src'),'-I'+str(out),'-o',str(payload),str(src)],check=True)
    data=payload.read_bytes();rounded=(len(data)+511)//512*512
    allocation=(len(data)+748016+511)//512*512
    boot_source=out/'recovery-runtime-private-boot.s'
    boot_source.write_text((PORT/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'))
    boot=out/(name+'-boot.bin')
    subprocess.run([vasm,'-m68020','-Fbin','-quiet',f'-DPAYLOAD_BYTES={rounded}','-o',str(boot),str(boot_source)],check=True)
    assert len(boot.read_bytes())<=1024 and rounded<=901120-1024
    disk=bytearray(901120);disk[:len(boot.read_bytes())]=boot.read_bytes();disk[1024:1024+len(data)]=data
    checksum=0
    for off in range(0,1024,4):
        checksum+=struct.unpack_from('>I',disk,off)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
    struct.pack_into('>I',disk,4,(~checksum)&0xffffffff)
    adf=out/(name+'.adf');adf.write_bytes(disk)
    report=dict(artifact=adf.name,proprietary_inputs=True,distribution='PRIVATE cartridge-bearing diagnostic, never source-only',native_helper_calls=68,native_helper_count=len(set(SEQUENCE)),payload_bytes=len(data),allocation_bytes=allocation,payload_sha256=hashlib.sha256(data).hexdigest(),sha256=hashlib.sha256(disk).hexdigest(),resource_sha256=hashlib.sha256(resources).hexdigest(),boundary='C2A8; next countdown instruction untranslated')
    (out/(name+'-build.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
