#!/usr/bin/env python3
"""PRIVATE diagnostic: embeds locally supplied cartridge resource bytes."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'tests'))
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
# Verify authorized input BEFORE creating directories or writing any output.
rom=(P.parent/'input/rescue-rangers-europe.nes').read_bytes()
if hashlib.sha256(rom).hexdigest()!=SHA:raise ValueError('wrong Europe cartridge SHA-256')
from recovery_stage_resource_target_fixtures import CASES,fixture
resource=rom[16+4*16384+0x193:16+4*16384+0x338];assert len(resource)==421
B=P/'build';B.mkdir(exist_ok=True);name='recovery-stage-resource-probe'
def blob(label,data):
    return '\n even\n dcb.b 16,$5a\n'+label+':\n'+''.join(' dc.b '+','.join(str(v) for v in data[i:i+32])+'\n' for i in range(0,len(data),32))+' dcb.b 16,$5a\n'
def address(label,reg):return f' lea probe_origin(pc),{reg}\n adda.l #{label}-probe_origin,{reg}\n'
def seeds():
    s=' move.l #$10203040,d0\n'
    for r in range(1,8):s+=f' move.l #${0x11223300+r:08x},d{r}\n'
    for r in range(4,6):s+=f' movea.l #${0x22334400+r:08x},a{r}\n'
    return s+address('resource','a3')
calls='';data='\n even\nprobe_report:\n dc.b "CDRSR001"\n dc.l -1,0\n dcb.l 6,0\n'
data+=blob('resource',resource)
for i,case in enumerate(CASES):
    state,ctx=fixture(case)
    calls+=address(f'record{i}','a6')+address(f'ram{i}','a0')+address(f'ctx{i}','a1')
    calls+=' move.l a0,0(a6)\n move.l a1,4(a6)\n'
    for off,label in ((8,f'j0_{i}'),(12,f'j1_{i}'),(16,f'j2_{i}'),(20,f'mid0ram{i}'),(24,f'mid0ctx{i}'),(28,f'mid1ram{i}'),(32,f'mid1ctx{i}'),(36,'resource'),(40,'probe_stack')):
        calls+=address(label,'a3')+f' move.l a3,{off}(a6)\n'
    calls+=' move.l sp,44(a6)\n move.l sp,48(a6)\n'
    calls+=address('probe_report','a3')+f' move.l a6,{16+i*4}(a3)\n'
    for n,helper in enumerate(('recovery_stage_resource_init','recovery_gameplay_player_init','recovery_gameplay_fade_entry')):
        calls+=f' movea.l {8+4*n}(a6),a2\n'+seeds()+f' movem.l d0-d7/a0-a6,{64+120*n}(a6)\n bsr.w {helper}\n movem.l d0-d7/a0-a6,{124+120*n}(a6)\n move.l sp,{52+4*n}(a6)\n'
        if n<2:
            calls+=f''' movea.l a0,a3
 movea.l {20+8*n}(a6),a4
 move.w #511,d0
.copy{n}_{i}:
 move.l (a3)+,(a4)+
 dbra d0,.copy{n}_{i}
 movea.l {24+8*n}(a6),a4
 move.l (a1),(a4)
 move.l 4(a1),4(a4)
'''
    contents=[(f'record{i}',bytes(424)),(f'ram{i}',state),(f'ctx{i}',ctx)]
    contents += [(f'j{n}_{i}',b'\xb6'*size) for n,size in enumerate((256,256,512))]
    contents += [(f'mid{n}ram{i}',b'\xcc'*2048) for n in range(2)]+[(f'mid{n}ctx{i}',b'\xcc'*8) for n in range(2)]
    for label,content in contents:data+=blob(label,content)
data+='\n even\n dcb.b 16,$5a\nprobe_stack:\n dcb.b 4096,$ee\nprobe_stack_end:\n dcb.b 16,$5a\n'
(B/'stage-resource-calls.inc').write_text(calls);(B/'stage-resource-data.inc').write_text(data)
vasm=os.environ['VASM'];payload_file=B/(name+'.bin')
subprocess.run([vasm,'-quiet','-m68020','-Fbin','-I'+str(P/'src'),'-I'+str(B),'-o',str(payload_file),str(P/'src/recovery_stage_resource_probe.s')],check=True)
payload=payload_file.read_bytes();rounded=(len(payload)+511)//512*512
boot_file=B/(name+'-boot.bin')
subprocess.run([vasm,'-quiet','-m68020','-Fbin',f'-DPAYLOAD_BYTES={rounded}','-o',str(boot_file),str(P/'src/boot.s')],check=True)
boot=boot_file.read_bytes();assert len(boot)<=1024 and rounded<=900096
disk=bytearray(901120);disk[:len(boot)]=boot;disk[1024:1024+len(payload)]=payload
checksum=0
for off in range(0,1024,4):
    checksum+=struct.unpack_from('>I',disk,off)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
struct.pack_into('>I',disk,4,(~checksum)&0xffffffff)
(B/(name+'.adf')).write_bytes(disk)
report=dict(payload_bytes=len(payload),allocation_bytes=rounded,proprietary_inputs=True,cases=6,sha256=hashlib.sha256(disk).hexdigest(),rom_sha256=SHA)
(B/(name+'-build.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
