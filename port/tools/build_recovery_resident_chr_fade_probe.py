#!/usr/bin/env python3
"""Private stock-Chip reset-to-C5D1 diagnostics with four bounded RAM capture windows."""
from pathlib import Path
import argparse,hashlib,json,os,struct,subprocess,sys
PORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PORT/'tests'))
from recovery_resident_chr_fade_target_oracle import NAMES,SIZES,SHA,oracle
MARKER=b'CDRCHR01'
def layout(results,window):
 offsets=[];total=0
 for call,r in enumerate(results):
  offsets.append(total);total+=52+len(r[4])+(2048 if window*256<=call<(window+1)*256 else 0)
 return offsets,total

def source(results,window):
 offsets,total=layout(results,window)
 lines=[f''' lea $dff000,a5
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
''']
 for delta in range(0,16,4):lines.append(f' move.l #$5a5a5a5a,{total+delta}(a4)')
 for label,off in [('resource',28),('stack',32),('resource2',48)]:lines.append(f' lea {label}(pc),a4\n move.l a4,{off}(a6)')
 lines.append(' move.l sp,36(a6)')
 for call,(index,status,context,ram,journal,raw) in enumerate(results):
  captured=window*256<=call<(window+1)*256
  end=20+(2048 if captured else 0); jo=end+16
  lines.append(f''' lea snapshots+{offsets[call]}(pc),a4
 move.l #{index},(a4)
 move.l #{status},4(a4)
 move.l #{SIZES[index]},8(a4)''')
  for base in (end,jo+SIZES[index]):
   for delta in range(0,16,4):lines.append(f' move.l #$5a5a5a5a,{base+delta}(a4)')
  lines.append(f''' lea {jo}(a4),a2
 lea {'resource2' if index in (42,43) else 'resource'}(pc),a3
 moveq #0,d0
 moveq #0,d1
 move.l #$22334455,d2
 move.l #$33445566,d3
 move.l #$44556677,d4
 move.l #$55667788,d5
 move.l #$66778899,d6
 move.l #$778899aa,d7
 movem.l d1-d7/a0-a6,-(sp)
 bsr.l {NAMES[index]}
 cmpi.l #{status},d0
 bne.l failed
 movem.l d1-d7/a0-a6,-(sp)
 move.l sp,a3
 lea 56(sp),a4
 moveq #13,d0
abi_{call}:
 move.l (a3)+,d1
 cmp.l (a4)+,d1
 bne.l abi_failed
 dbra d0,abi_{call}
 movem.l (sp)+,d1-d7/a0-a6
 lea 56(sp),sp
 lea stack_end(pc),a4
 cmpa.l sp,a4
 bne.l stack_failed
 lea snapshots+{offsets[call]+12}(pc),a4
 move.l (a1),(a4)+
 move.l 4(a1),(a4)+''')
  if captured:lines.append(f''' move.l a0,a3
 move.w #511,d0
copy_{call}:
 move.l (a3)+,(a4)+
 dbra d0,copy_{call}''')
  lines.append(' addq.l #1,12(a6)')
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
 bra.s stop''')
 lines += [f' include "{name}.s"' for name in NAMES]
 lines.append(f''' even
report:
 dc.b 'CDRCHR01'
 dc.l -99,0,0,0,0,0,0,0,0,{window},0
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
 incbin "recovery-resident-chr-fade-private-bank3.bin"
 dcb.b 32,$5a
resource2:
 incbin "recovery-resident-chr-fade-private-bank2.bin"
 dcb.b 32,$5a
snapshots:
; Allocated and cleared by boot loader, not loaded from reference snapshots.
''')
 return '\n'.join(lines)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,default=PORT.parent/'input/rescue-rangers-europe.nes');p.add_argument('--output-dir',type=Path,default=PORT/'build/chr-fade-stock');args=p.parse_args()
 rom=args.rom.read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA,'Private cartridge hash mismatch'
 results,bus,instructions=oracle(rom);assert len(results)==1024
 out=args.output_dir.resolve();assert (PORT/'build').resolve() in out.parents
 out.mkdir(parents=True,exist_ok=True)
 for bank in (2,3):(out/f'recovery-resident-chr-fade-private-bank{bank}.bin').write_bytes(rom[16+bank*16384:16+(bank+1)*16384])
 reports=[]
 for window in range(4):
  name=f'recovery-resident-chr-fade-w{window}';src=out/(name+'.s');src.write_text(source(results,window));payload=out/(name+'.bin')
  def assemble(source,output,*flags):subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(PORT/'src'),'-I'+str(out),*flags,'-o',str(output),str(source)],check=True)
  assemble(src,payload);data=payload.read_bytes();rounded=(len(data)+511)//512*512;_,workspace=layout(results,window);allocation=(len(data)+workspace+16+511)//512*512
  assert allocation<1536*1024,'Reserve at least 512 KiB stock Chip for firmware/system'
  boot_source=out/(name+'-boot.s');boot_source.write_text((PORT/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'));boot=out/(name+'-boot.bin');assemble(boot_source,boot,f'-DPAYLOAD_BYTES={rounded}')
  assert len(boot.read_bytes())<=1024 and rounded<=901120-1024
  disk=bytearray(901120);disk[:len(boot.read_bytes())]=boot.read_bytes();disk[1024:1024+len(data)]=data
  checksum=0
  for off in range(0,1024,4):checksum+=struct.unpack_from('>I',disk,off)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
  struct.pack_into('>I',disk,4,(~checksum)&0xffffffff);(out/(name+'.adf')).write_bytes(disk)
  reports.append(dict(window=window,captured_calls=[window*256,(window+1)*256],executed_calls=1024,payload_bytes=len(data),snapshot_bytes=workspace,allocation_bytes=allocation,payload_sha256=hashlib.sha256(data).hexdigest(),adf_sha256=hashlib.sha256(disk).hexdigest()))
 paths=[Path(__file__),PORT/'tests/recovery_resident_chr_fade_target_oracle.py',PORT/'src/boot.s']+[PORT/'src'/(n+'.s') for n in NAMES]
 report=dict(private_cartridge_bearing=True,distribution='PRIVATE diagnostic only',no_reference_state_in_target=True,logical_NMIs=35,physical_hardware=False,source_sha256={str(p.relative_to(PORT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},windows=reports,maximum_allocation_bytes=max(r['allocation_bytes'] for r in reports))
 (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
