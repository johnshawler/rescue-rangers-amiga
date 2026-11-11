#!/usr/bin/env python3
"""Build six synthetic player-init fixtures; no cartridge/firmware input."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'tests'))
from test_recovery_gameplay_player_init_contract import CASES,fixture
B=P/'build';B.mkdir(exist_ok=True);name='recovery-gameplay-player-init-probe'
def blob(label,data):
    return '\n dcb.b 16,$5a\n'+label+':\n'+''.join(' dc.b '+','.join(str(v) for v in data[i:i+32])+'\n' for i in range(0,len(data),32))+' dcb.b 16,$5a\n'
calls='';data='\n even\nprobe_report:\n dc.b "CDRGP001"\n dc.l -1,0\n dcb.l 6,0\n'
for i,case in enumerate(CASES):
    state,ctx=fixture(case)
    calls+=f''' lea record{i}(pc),a6
 lea ram{i}(pc),a0
 lea ctx{i}(pc),a1
 lea journal{i}(pc),a2
 move.l a0,0(a6)
 move.l a1,4(a6)
 move.l a2,8(a6)
 lea probe_stack(pc),a3
 move.l a3,12(a6)
 move.l sp,16(a6)
 move.l sp,20(a6)
 lea probe_report(pc),a3
 move.l a6,{16+i*4}(a3)
 move.l #$10203040,d0
'''
    for r in range(1,8):calls+=f' move.l #${0x11223300+r:08x},d{r}\n'
    for r in range(3,6):calls+=f' movea.l #${0x22334400+r:08x},a{r}\n'
    calls+=f''' movem.l d0-d7/a0-a6,28(a6)
 bsr.w recovery_gameplay_player_init
 movem.l d0-d7/a0-a6,88(a6)
 move.l sp,24(a6)
'''
    data+=blob(f'record{i}',bytes(148))+blob(f'ram{i}',state)+blob(f'ctx{i}',ctx)+blob(f'journal{i}',b'\xb6'*256)
data+='\n dcb.b 16,$5a\nprobe_stack:\n dcb.b 4096,$ee\nprobe_stack_end:\n dcb.b 16,$5a\n'
(B/'gameplay-player-calls.inc').write_text(calls);(B/'gameplay-player-data.inc').write_text(data)
vasm=os.environ['VASM'];payload_file=B/(name+'.bin')
subprocess.run([vasm,'-quiet','-m68020','-Fbin','-I'+str(P/'src'),'-I'+str(B),'-o',str(payload_file),str(P/'src/recovery_gameplay_player_init_probe.s')],check=True)
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
