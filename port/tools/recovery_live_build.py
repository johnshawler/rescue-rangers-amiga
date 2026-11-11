#!/usr/bin/env python3
"""Source/approved-ROM-only live native audio diagnostic; output is PRIVATE."""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess,sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'tools'))
import build_recovery_menu_sfx_target as base
from recovery_live_source import transform
from experimental_direct_paula_build import noise

def build(out,history,display,stop_rti=0,full_redraw=False,scene=False):
 out.mkdir(parents=True,exist_ok=False)
 if scene:
  manifest=P/'analysis/recovery_scene_continue_manifest.json'
  assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='38099031ad4eb1961b8997ff1d1c7ae759adc0929c7e14a28c7da0cee0ff89be'
  m=json.loads(manifest.read_text())
  for path,digest in {**m['source_hashes'],**m['frozen_dependencies']}.items():assert hashlib.sha256((P.parent/path).read_bytes()).hexdigest()==digest,path
 for manifest in ('recovery_state_menu_sfx_manifest.json','recovery_menu_sfx_target_dependencies.json'):
  m=json.loads((P/'analysis'/manifest).read_text())
  for item in m.get('files',[])+m.get('frozen_dependencies',[]):
   assert hashlib.sha256((P.parent/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 rom=(P.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 assert hashlib.sha256((P/'src/experimental_direct_paula.c').read_bytes()).hexdigest()=='5c5be6ac34df5fc7d9b72a081343abc262c762d8b67b142c9e585e6a24080420'
 (out/'private-prg.bin').write_bytes(rom[16:131088]);(out/'startup-display-private-chr.bin').write_bytes(rom[131088:262160])
 (out/'recovery_menu_paula_waves.h').write_text('static const signed char dp_noise[3][2048] __attribute__((aligned(2)))={'+','.join('{'+','.join(map(str,noise(p,s)))+'}' for p,s in [(148,0),(944,0),(8,1)])+'};\n')
 cc=os.getenv('PAULA_CC','m68k-linux-gnu-gcc');ld=out/'adapter.ld'
 ld.write_text('SECTIONS { . = 0; .text : { *(.entry) *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }')
 subprocess.run([cc,'-I'+str(out),'-m68020','-mpcrel','-O2','-ffreestanding','-fno-builtin','-nostdlib','-fno-pie','-Wl,--build-id=none','-Wl,-T,'+str(ld),*[str(P/'src'/n) for n in ('recovery_menu_paula_entry.s','recovery_live_paula_adapter.c','experimental_direct_paula.c')],'-o',str(out/'adapter.elf')],check=True)
 subprocess.run([cc.replace('gcc','objcopy'),'-O','binary',str(out/'adapter.elf'),str(out/'adapter.bin')],check=True)
 syms=subprocess.check_output([cc.replace('gcc','nm'),'-S',str(out/'adapter.elf')],text=True);(out/'adapter.symbols').write_text(syms)
 extent=max(int(a.split()[0],16)+int(a.split()[1],16) for a in syms.splitlines() if len(a.split())==4)
 b=(out/'adapter.bin').read_bytes()
 planner=next(x.split() for x in syms.splitlines() if x.split()[-1]=='experimental_direct_paula_plan')
 a,n=int(planner[0],16),int(planner[1],16)
 assert n==470 and hashlib.sha256(b[a:a+n]).hexdigest()=='33eaebe81eb97ba518ce3def0ae33bb5db1201745018e4c4c77d5f01a5a64996'
 (out/'adapter.bin').write_bytes(b+bytes(extent-len(b)))
 s=base.source(history)
 s=s.replace(' bsr.l llb_amiga_clock_start',' bsr.l llb_amiga_clock_start\n bsr.l paula_adapter\n bsr.l paula_display_init',1)
 s=s.replace(' bsr.w capture_journal',' bsr.w capture_journal\n bsr.l paula_consume',1)
 s=s.replace(' bsr.l startup_display\nstop:', ' bsr.l paula_render\nstop:',1)
 # Save the originating failure BEFORE C may clobber caller-saved D0.
 s=s.replace('failed:\n move.l d0,8(a6)', 'failed:\n move.l d0,8(a6)\n bsr.l paula_adapter+8',1)
 # The predecessor capture guard stopped directly. Route the integrated copy
 # through permanent muted failure, preserving its20-byte span/alignment.
 old=' move.l #-3,8(a6)\n move.w #$f00,$dff180\n bra.w stop'
 assert s.count(old)==1
 # Reuse the14-byte unreachable padding for explicit guard diagnostics.
 # Three branch operands change, but all successful-path instruction addresses
 # and all dispatcher/device/data/adapter bytes retain their v6 layout.
 guards=[(' cmpi.l #12000,12(a6)\n bhs.w failed',' cmpi.l #12000,12(a6)\n bhs.w paula_loop_limit'),
         (' cmpi.l #127,d3\n bhi.w failed',' cmpi.l #127,d3\n bhi.w paula_history_limit'),
         (' tst.l 20(a6)\n bne.w failed',' tst.l 20(a6)\n bne.w paula_repeated_event')]
 for before,after in guards:
  assert s.count(before)==1
  s=s.replace(before,after,1)
 stubs='paula_loop_limit:\n moveq #-6,d0\n bra.s paula_guard_failed\npaula_history_limit:\n moveq #-7,d0\n bra.s paula_guard_failed\npaula_repeated_event:\n moveq #-8,d0\npaula_guard_failed:\n bra.w failed\n'
 s=s.replace(old,' moveq #-3,d0\n bra.w failed\n'+stubs,1)
 s+='\n cnop 0,4\npaula_adapter:\n incbin "adapter.bin"\n'
 s+=(P/'src/recovery_menu_paula_bridge.s').read_text().replace('DISPLAY_DMA',str(int(display)))
 s=transform(s,stop_rti,full_redraw,scene)
 (out/'recovery_live_target.s').write_text(s)
 def asm(src,dst,*flags):subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(P/'src'),'-I'+str(out),*flags,'-o',str(dst),str(src)],check=True)
 asm(out/'recovery_live_target.s',out/'target.bin','-L',str(out/'target.list'))
 symbols={name:int(addr,16) for addr,name in re.findall(r'^([0-9A-Fa-f]{8}) ([A-Za-z_][A-Za-z_0-9]*)$',(out/'target.list').read_text(),re.M)}
 (out/'target.symbols.json').write_text(json.dumps(symbols,indent=2)+'\n')
 data=(out/'target.bin').read_bytes()
 # Freeze the exact original-derived code and device bytes, independent of relocation.
 from recovery_state_menu_sfx_harness import assemble
 native=assemble();assert len(native)==46492 and hashlib.sha256(native).hexdigest()=='a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e'
 pos=data.index(native)+len(native);device=data[pos:data.index(b'CDRDIS01')]
 assert len(device)==1750 and hashlib.sha256(device).hexdigest()=='85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad'
 rounded=(len(data)+511)//512*512;allocation=(len(data)+16+511)//512*512
 assert allocation<1536*1024 and rounded<=900096
 (out/'boot.s').write_text((P/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'))
 asm(out/'boot.s',out/'boot.bin',f'-DPAYLOAD_BYTES={rounded}')
 disk=bytearray(901120);boot=(out/'boot.bin').read_bytes();disk[:len(boot)]=boot;disk[1024:1024+len(data)]=data;c=0
 for off in range(0,1024,4):c+=struct.unpack_from('>I',disk,off)[0];c=(c&0xffffffff)+(c>>32)
 struct.pack_into('>I',disk,4,(~c)&0xffffffff);(out/'target.adf').write_bytes(disk)
 report=dict(history="live-bounded",display_dma=display,helper_limit=1000000,rti_limit=4096,audio_ring_slots=256,journal_mode="last-completion",input_change_limit=128,diagnostic_stop_rti=stop_rti,full_redraw=full_redraw,scene=scene,payload_bytes=len(data),allocation_bytes=allocation,adapter_extent=extent,adf_sha256=hashlib.sha256(disk).hexdigest())
 report['sources']={str(p.relative_to(P.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted([*P.glob('src/recovery_live_*'),*P.glob('tools/recovery_live_*'),*P.glob('tests/recovery_live_*'),P/'src/recovery_redraw_invalidate.s',P/'src/recovery_zx_keyboard.s']) if p.is_file()}
 if scene:
  for n in ('recovery_scene_continue_dispatch','recovery_post_confirmation_entry','recovery_scene_palette_entry','recovery_scene_sprite_hide','recovery_scene_continue_prepare'):
   p=P/'src'/(n+'.s');report['sources'][str(p.relative_to(P.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
  report['scene_manifest_sha256']=hashlib.sha256((P/'analysis/recovery_scene_continue_manifest.json').read_bytes()).hexdigest()
 (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--history',choices=base.HISTORIES,default='default');a.add_argument('--display',type=int,choices=(0,1),default=1);a.add_argument('--stop-rti',type=int,default=0);a.add_argument('--full-redraw',action='store_true');a.add_argument('--scene',action='store_true');v=a.parse_args();assert 0<=v.stop_rti<=4096;build(v.output.resolve(),v.history,v.display,v.stop_rti,v.full_redraw,v.scene)
