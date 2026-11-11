#!/usr/bin/env python3
"""Source/approved-ROM-only live native audio diagnostic; output is PRIVATE."""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess,sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'tools'))
import build_recovery_menu_sfx_target as base
from recovery_play_target_source import integrated_source
from experimental_direct_paula_build import noise

def build(out,history,display,stop_rti=0):
 out.mkdir(parents=True,exist_ok=False)
 frozen=P/'analysis/recovery_bank_loader_play_manifest.json'
 assert hashlib.sha256(frozen.read_bytes()).hexdigest()=='428fc25ff5de74f2bcd64bbb6213207c1b7c0cdc500cfe2df4cd287da9743ba2'
 # Check only the reviewed flat source closure. Do not recursively expand
 # historical research manifests into private disassembly/old experiments.
 from recovery_play_target_source import source_files
 for name,digest in source_files().items():
  assert hashlib.sha256((P.parent/name).read_bytes()).hexdigest()==digest,name
 rom=(P.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 assert hashlib.sha256((P/'src/experimental_direct_paula.c').read_bytes()).hexdigest()=='5c5be6ac34df5fc7d9b72a081343abc262c762d8b67b142c9e585e6a24080420'
 (out/'private-prg.bin').write_bytes(rom[16:131088]);(out/'startup-display-private-chr.bin').write_bytes(rom[131088:262160])
 (out/'recovery_menu_paula_waves.h').write_text('static const signed char dp_noise[4][2048] __attribute__((aligned(2)))={'+','.join('{'+','.join(map(str,noise(p,s)))+'}' for p,s in [(148,0),(944,0),(8,1),(188,0)])+'};\n')
 cc=os.getenv('PAULA_CC','m68k-linux-gnu-gcc');ld=out/'adapter.ld'
 ld.write_text('SECTIONS { . = 0; .text : { *(.entry) *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }')
 subprocess.run([cc,'-I'+str(out),'-m68020','-mpcrel','-O2','-ffreestanding','-fno-builtin','-nostdlib','-fno-pie','-Wl,--build-id=none','-Wl,-T,'+str(ld),*[str(P/'src'/n) for n in ('recovery_menu_paula_entry.s','recovery_stage_target_paula_adapter.c','experimental_direct_paula.c','recovery_stage_target_plan.c')],'-o',str(out/'adapter.elf')],check=True)
 subprocess.run([cc.replace('gcc','objcopy'),'-O','binary',str(out/'adapter.elf'),str(out/'adapter.bin')],check=True)
 syms=subprocess.check_output([cc.replace('gcc','nm'),'-S',str(out/'adapter.elf')],text=True);(out/'adapter.symbols').write_text(syms)
 extent=max(int(a.split()[0],16)+int(a.split()[1],16) for a in syms.splitlines() if len(a.split())==4)
 b=(out/'adapter.bin').read_bytes()
 planner=next(x.split() for x in syms.splitlines() if x.split()[-1]=='experimental_direct_paula_plan')
 a,n=int(planner[0],16),int(planner[1],16)
 assert n==470 and hashlib.sha256(b[a:a+n]).hexdigest()=='33eaebe81eb97ba518ce3def0ae33bb5db1201745018e4c4c77d5f01a5a64996'
 (out/'adapter.bin').write_bytes(b+bytes(extent-len(b)))
 s=integrated_source(history,display,stop_rti)
 (out/'recovery_stage_target.s').write_text(s)
 def asm(src,dst,*flags):subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(P/'src'),'-I'+str(out),*flags,'-o',str(dst),str(src)],check=True)
 asm(out/'recovery_stage_target.s',out/'target.bin','-L',str(out/'target.list'))
 symbols={name:int(addr,16) for addr,name in re.findall(r'^([0-9A-Fa-f]{8}) ([A-Za-z_][A-Za-z_0-9]*)$',(out/'target.list').read_text(),re.M)}
 (out/'target.symbols.json').write_text(json.dumps(symbols,indent=2)+'\n')
 data=(out/'target.bin').read_bytes()
 # Freeze the exact original-derived composite, independent of relocation.
 from recovery_bank_loader_play_harness import assemble
 native=assemble();assert len(native)==216616 and hashlib.sha256(native).hexdigest()=='5a3ab5ff5204b73dd1223291f42f826f634ff43eaee725c7a503684f80e317f4'
 assert data.count(native)==1
 report_native_sha=hashlib.sha256(native).hexdigest()
 rounded=(len(data)+511)//512*512;allocation=(len(data)+16+511)//512*512
 assert allocation<1536*1024 and rounded<=900096
 (out/'boot.s').write_text((P/'src/boot.s').read_text().replace('move.l #PAYLOAD_BYTES,d0',f'move.l #{allocation},d0'))
 asm(out/'boot.s',out/'boot.bin',f'-DPAYLOAD_BYTES={rounded}')
 disk=bytearray(901120);boot=(out/'boot.bin').read_bytes();disk[:len(boot)]=boot;disk[1024:1024+len(data)]=data;c=0
 for off in range(0,1024,4):c+=struct.unpack_from('>I',disk,off)[0];c=(c&0xffffffff)+(c>>32)
 struct.pack_into('>I',disk,4,(~c)&0xffffffff);(out/'target.adf').write_bytes(disk)
 report=dict(history="live-bounded",display_dma=display,helper_limit=1000000,rti_limit=4096,audio_ring_slots=256,journal_mode="last-completion",input_change_limit=128,diagnostic_stop_rti=stop_rti,full_redraw=True,stage=True,play=True,journal_capture_capacity=135168,goal_game_frames=5,native_sha256=report_native_sha,payload_bytes=len(data),allocation_bytes=allocation,adapter_extent=extent,adf_sha256=hashlib.sha256(disk).hexdigest())
 report['sources']={str(p.relative_to(P.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted([*P.glob('src/recovery_stage_target_*'),*P.glob('tools/recovery_stage_target_*'),*P.glob('tests/recovery_stage_target_*'),*P.glob('src/recovery_live_*'),*P.glob('tools/recovery_live_*'),P/'src/recovery_redraw_invalidate.s',P/'src/recovery_zx_keyboard.s']) if p.is_file()}
 from recovery_play_target_source import SOURCES
 report['sources'].update({str((P/'src'/(n+'.s')).relative_to(P.parent)):hashlib.sha256((P/'src'/(n+'.s')).read_bytes()).hexdigest() for n in SOURCES})
 report['noise_extension']=dict(register_value=8,PAL_period=188,short_mode=False,wave=8,samples=2048,Paula_period=160,loop_words=1024,approximation=True)
 report['sources'].update({str(p.relative_to(P.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted([*P.glob('tools/recovery_play_target_*'),*P.glob('tests/recovery_play_target_*')]) if p.is_file()})
 report['stage_manifest_sha256']=hashlib.sha256(frozen.read_bytes()).hexdigest()
 (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--history',choices=base.HISTORIES,default='default');a.add_argument('--display',type=int,choices=(0,1),default=1);a.add_argument('--stop-rti',type=int,default=0);v=a.parse_args();assert 0<=v.stop_rti<=4096;build(v.output.resolve(),v.history,v.display,v.stop_rti)
