#!/usr/bin/env python3
"""Source-only six-fixture continuous native player/fade-entry target."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'tests'))
from recovery_gameplay_fade_target_fixtures import CASES,fixture
B=P/'build';B.mkdir(exist_ok=True);name='recovery-gameplay-fade-entry-probe'
def blob(label,data):
    return '\n dcb.b 16,$5a\n'+label+':\n'+''.join(' dc.b '+','.join(str(v) for v in data[i:i+32])+'\n' for i in range(0,len(data),32))+' dcb.b 16,$5a\n'
def address(label,reg):
    return f' lea probe_origin(pc),{reg}\n adda.l #{label}-probe_origin,{reg}\n'
def seeds():
    s=' move.l #$10203040,d0\n'
    for r in range(1,8):s+=f' move.l #${0x11223300+r:08x},d{r}\n'
    for r in range(3,6):s+=f' movea.l #${0x22334400+r:08x},a{r}\n'
    return s
calls='';data='\n even\nprobe_report:\n dc.b "CDRGF001"\n dc.l -1,0\n dcb.l 6,0\n'
for i,case in enumerate(CASES):
    state,ctx=fixture(case)
    calls+=address(f'record{i}','a6')+address(f'ram{i}','a0')+address(f'ctx{i}','a1')+address(f'journal1_{i}','a2')
    calls+=' move.l a0,0(a6)\n move.l a1,4(a6)\n move.l a2,8(a6)\n'
    for offset,label in ((12,f'journal2_{i}'),(16,f'midram{i}'),(20,f'midctx{i}'),(24,'probe_stack')):
        calls+=address(label,'a3')+f' move.l a3,{offset}(a6)\n'
    calls+=' move.l sp,28(a6)\n move.l sp,32(a6)\n'
    calls+=address('probe_report','a3')+f' move.l a6,{16+i*4}(a3)\n'+seeds()
    calls+=' movem.l d0-d7/a0-a6,44(a6)\n bsr.w recovery_gameplay_player_init\n movem.l d0-d7/a0-a6,104(a6)\n move.l sp,36(a6)\n'
    calls+=f''' movea.l a0,a3
 movea.l 16(a6),a4
 move.w #511,d0
.copy{i}:
 move.l (a3)+,(a4)+
 dbra d0,.copy{i}
 movea.l 20(a6),a4
 move.l (a1),(a4)
 move.l 4(a1),4(a4)
 movea.l 12(a6),a2
'''+seeds()
    calls+=' movem.l d0-d7/a0-a6,164(a6)\n bsr.w recovery_gameplay_fade_entry\n movem.l d0-d7/a0-a6,224(a6)\n move.l sp,40(a6)\n'
    for label,content in ((f'record{i}',bytes(284)),(f'ram{i}',state),(f'ctx{i}',ctx),(f'journal1_{i}',b'\xb6'*256),(f'journal2_{i}',b'\xb6'*512),(f'midram{i}',b'\xcc'*2048),(f'midctx{i}',b'\xcc'*8)):
        data+=blob(label,content)
data+='\n dcb.b 16,$5a\nprobe_stack:\n dcb.b 4096,$ee\nprobe_stack_end:\n dcb.b 16,$5a\n'
(B/'gameplay-fade-calls.inc').write_text(calls);(B/'gameplay-fade-data.inc').write_text(data)
vasm=os.environ['VASM'];payload_file=B/(name+'.bin')
subprocess.run([vasm,'-quiet','-m68020','-Fbin','-I'+str(P/'src'),'-I'+str(B),'-o',str(payload_file),str(P/'src/recovery_gameplay_fade_entry_probe.s')],check=True)
payload=payload_file.read_bytes();rounded=(len(payload)+511)//512*512
boot_file=B/(name+'-boot.bin')
subprocess.run([vasm,'-quiet','-m68020','-Fbin',f'-DPAYLOAD_BYTES={rounded}','-o',str(boot_file),str(P/'src/boot.s')],check=True)
boot=boot_file.read_bytes();assert len(boot)<=1024 and rounded<=900096
disk=bytearray(901120);disk[:len(boot)]=boot;disk[1024:1024+len(payload)]=payload
checksum=0
for offset in range(0,1024,4):
    checksum+=struct.unpack_from('>I',disk,offset)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
struct.pack_into('>I',disk,4,(~checksum)&0xffffffff)
(B/(name+'.adf')).write_bytes(disk)
report=dict(payload_bytes=len(payload),allocation_bytes=rounded,proprietary_inputs=False,cases=len(CASES),sha256=hashlib.sha256(disk).hexdigest())
(B/(name+'-build.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
