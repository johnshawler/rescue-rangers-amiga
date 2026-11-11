"""Offline bounded static translation. Never linked into target; no runtime decoder.
Requires approved private reference ROM. Emits native logic, never game tables.
"""
import hashlib,re
from pathlib import Path
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
ROOT=Path(__file__).resolve().parents[2]
SHA='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'

RANGES=((0xea8f,0xebfa),(0xed3a,0xeeab),(0xf000,0xf328),(0xf5a6,0xf7fe))
BASE_ENTRIES=(0xeb10,0xf62c,0xea8f,0xeb3b,0xed3a,0xed5b,0xed7a,0xed99,0xedf5,0xee23,0xf000,0xf03f,0xf066,0xf0ac,0xf0d3,0xf0e7,0xf0fb,0xf1ae,0xf1f1,0xf217,0xf21e,0xf23c,0xf25a,0xf27f,0xf2a2,0xf2c5,0xf2ea,0xf2fb,0xf31d,0xf5a6,0xf62d,0xf696,0xf6dc,0xf721,0xf74c,0xf782,0xf7c8)
ENTRIES=()

def generate():
 rom=(ROOT/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 m=MPU();m.memory[0x8000:0xc000]=rom[16+6*16384:16+7*16384];m.memory[0xc000:]=rom[16+7*16384:16+8*16384];dis=Disassembler(m)
 global ENTRIES
 pcs=[]
 for lo,hi in RANGES:
  pc=lo
  while pc<hi:
   pcs.append(pc);pc+=dis.instruction_at(pc)[0]
  assert pc==hi
 ENTRIES=tuple(sorted(set(BASE_ENTRIES)|{pc+3 for pc in pcs if dis.instruction_at(pc)[1].startswith('JSR')}))
 out=[]
 def emit(*s):out.extend(s)
 emit('; Static native translation of fixed-bank movement, tile collision, slopes and object collision.',
 '; No instruction bytes, runtime decoder, proprietary tables, or captured effects.',
 '; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.',
 '; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.',
 '; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.',
 '; One committed ordered RAM/resource journal after scratch validation pass.',
 '; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.',
 'recovery_player_collision_region:\n ; Transaction preflight uses temporary RAM/context and publishes no effects.\n ; The external resource must remain immutable between both passes.\n movem.l d1-d7/a0-a6,-(sp)\n suba.w #2060,sp\n movea.l a0,a3\n movea.l sp,a0\n movea.l a0,a6\n move.w #511,d0\n.copy_ram:\n move.l (a3)+,(a6)+\n dbra d0,.copy_ram\n move.l (a1),(a6)+\n move.l 4(a1),(a6)+\n lea 2048(sp),a1\n lea 2056(sp),a2\n movea.w #1,a6\n bsr.w recovery_player_collision_region_core\n cmpi.l #1,d0\n bne.s .rejected\n movea.l 2088(sp),a0\n movea.l 2092(sp),a1\n movea.l 2096(sp),a2\n suba.l a6,a6\n bsr.w recovery_player_collision_region_core\n bra.s .return\n.rejected:\n moveq #-1,d0\n.return:\n adda.w #2060,sp\n movem.l (sp)+,d1-d7/a0-a6\n rts\nrecovery_player_collision_region_core:',
 ' cmpi.b #7,3(a4)',' bhi.w .invalid',
 ' cmpi.b #$1e,(a4)',' bne.w .invalid',' tst.w 4(a4)',' bne.w .invalid',
 ' cmpi.w #$d501,10(a4)',' bne.w .invalid',
 ' movem.l d1-d7/a3-a4/a6,-(sp)',
 ' lea 2(a2),a3',' clr.w (a2)',
 ' moveq #0,d4',' moveq #0,d5',' moveq #0,d6',' moveq #0,d7',
 ' move.b 2(a1),d4',' move.b 3(a1),d5',' move.b 4(a1),d6',' move.b 5(a1),d7',' movea.l #20000,a4', *[line for entry in ENTRIES for line in (f' cmpi.w #${entry:04x},(a1)',f' beq.w .p{entry:04x}')], ' bra.w .budget_failure')
 regs={'A':'d4','X':'d5','Y':'d6'}
 def addr(arg):
  if arg.startswith('($'):
   n=int(arg[2:4],16)
   emit(' moveq #0,d1',f' move.b ${(n+1)&255:02x}(a0),d1',' lsl.w #8,d1',f' move.b ${n:02x}(a0),d1',' add.w d6,d1')
  else:
   a=arg.split(',')[0];emit(f' move.w #{a},d1')
   if ',' in arg:emit(f' add.w {regs[arg[-1]]},d1')
   if len(a)==3:emit(' andi.w #$ff,d1')
 def read(arg):
  if arg.startswith('#'):emit(f' move.w {arg},d0')
  elif arg=='A':emit(' move.b d4,d0')
  else:addr(arg);emit(' bsr.w .read')
 ranges=RANGES
 pcs=[]
 for lo,hi in ranges:
  pc=lo
  while pc<hi:
   pcs.append(pc);pc+=dis.instruction_at(pc)[0]
 returns=[pc+3 for pc in pcs if dis.instruction_at(pc)[1].startswith('JSR')]
 external_branches=set()
 for pc in pcs:
  n,s=dis.instruction_at(pc);op,*rest=s.split(' ',1);arg=rest[0] if rest else '';nextpc=pc+n
  emit(f'.p{pc:04x}: ; {op} {arg}',' subq.l #1,a4',' cmpa.l #0,a4',' beq.w .budget_failure')
  if op in ('LDA','LDX','LDY'):
   read(arg);emit(f' move.b d0,{regs[op[-1]]}',' bsr.w .nz')
  elif op in ('STA','STX','STY'):
   addr(arg);emit(f' move.b {regs[op[-1]]},d0',' bsr.w .write')
  elif op in ('AND','ORA','EOR'):
   read(arg);emit(f' {dict(AND="and",ORA="or",EOR="eor")[op]}.b d0,d4',' move.b d4,d0',' bsr.w .nz')
  elif op in ('INC','DEC'):
   addr(arg);emit(' bsr.w .read',f' {"addq" if op=="INC" else "subq"}.b #1,d0',' bsr.w .write',' bsr.w .nz')
  elif op in ('INX','DEX','INY','DEY'):
   r=regs[op[-1]];emit(f' {"addq" if op.startswith("IN") else "subq"}.b #1,{r}',f' move.b {r},d0',' bsr.w .nz')
  elif op in ('TAX','TAY','TXA','TYA'):
   src=regs[op[1]];dst=regs[op[2]];emit(f' move.b {src},{dst}',f' move.b {dst},d0',' bsr.w .nz')
  elif op in ('CMP','CPX','CPY'):
   read(arg);r=regs['A' if op=='CMP' else op[-1]]
   emit(f' move.b {r},d2',' andi.b #$fe,d7',' cmp.b d0,d2',f' bcs.s .cmp{pc:04x}',' ori.b #1,d7',f'.cmp{pc:04x}:',' sub.b d0,d2',' move.b d2,d0',' bsr.w .nz')
  elif op in ('ADC','SBC'):read(arg);emit(f' bsr.w .{op.lower()}')
  elif op in ('LSR','ASL','ROR','ROL'):
   read(arg)
   emit(' move.b d7,d2',' andi.b #$fe,d7',f' btst #{0 if op in ("LSR","ROR") else 7},d0',f' beq.s .shift{pc:04x}',' ori.b #1,d7',f'.shift{pc:04x}:',f' {"lsr" if op in ("LSR","ROR") else "lsl"}.b #1,d0')
   if op in ('ROR','ROL'):
    emit(' btst #0,d2',f' beq.s .rotate{pc:04x}',f' ori.b #{128 if op=="ROR" else 1},d0',f'.rotate{pc:04x}:')
   emit(' move.b d0,d4' if arg=='A' else ' bsr.w .write',' bsr.w .nz')
  elif op in ('SEC','CLC'):emit(' ori.b #1,d7' if op=='SEC' else ' andi.b #$fe,d7')
  elif op in ('BEQ','BNE','BPL','BMI','BCS','BCC'):
   bit={'BEQ':1,'BNE':1,'BPL':7,'BMI':7,'BCS':0,'BCC':0}[op];cond='bne' if op in ('BEQ','BMI','BCS') else 'beq'
   if int(arg[1:],16) not in pcs:external_branches.add(int(arg[1:],16))
   emit(f' btst #{bit},d7',f' {cond}.w .p{int(arg[1:],16):04x}')
  elif op=='JMP':
   if arg.startswith('('):
    # Original indirect jump reads live pointer; no target opcode is read.
    ptr=int(arg[2:-1],16)
    emit(f' move.w #${ptr:04x},d1',' bsr.w .read',' move.b d0,d3',f' move.w #${(ptr&0xff00)|((ptr+1)&255):04x},d1',' bsr.w .read',' lsl.w #8,d0',' move.b d3,d0',' move.w d0,(a1)',' bra.w .success')
    continue
   target=int(arg[1:],16)
   if target in pcs:emit(f' bra.w .p{target:04x}')
   else:emit(f' move.w #${target:04x},(a1)',' bra.w .success')
  elif op=='JSR':
   target=int(arg[1:],16)
   emit(f' move.w #${(pc+2)>>8:02x},d0',' bsr.w .push',f' move.w #${(pc+2)&255:02x},d0',' bsr.w .push')
   if target in pcs:emit(f' bra.w .p{target:04x}')
   else:emit(f' move.w #${target:04x},(a1)',' bra.w .success')
  elif op=='RTS':
   emit(' bsr.w .pop',' move.b d0,d2',' bsr.w .pop',' lsl.w #8,d0',' move.b d2,d0',' addq.w #1,d0')
   # All original in-region JSR return sites, not a runtime opcode decoder.
   for ret in returns:
    emit(f' cmpi.w #${ret:04x},d0',f' beq.w .p{ret:04x}')
   emit(' move.w d0,(a1)',' bra.w .success')
  elif op=='PHA':emit(' move.b d4,d0',' bsr.w .push')
  elif op=='PLA':emit(' bsr.w .pop',' move.b d0,d4',' bsr.w .nz')
  elif op=='PHP':emit(' move.b d7,d0',' ori.b #$30,d0',' bsr.w .push')
  elif op=='PLP':emit(' bsr.w .pop',' ori.b #$30,d0',' move.b d0,d7')
  else:raise Exception(s)
  pc=nextpc
 for target in sorted(external_branches):
  emit(f'.p{target:04x}:',f' move.w #${target:04x},(a1)',' bra.w .success')
 emit('''; NZ preserves all other raw bits, including noncanonical B/U/D.
.nz:
 andi.b #$7d,d7
 tst.b d0
 bne.s .nonzero
 ori.b #2,d7
.nonzero:
 tst.b d0
 bpl.s .nzdone
 ori.b #$80,d7
.nzdone:
 rts
.push:
 moveq #0,d1
 move.b 6(a1),d1
 move.b d0,$100(a0,d1.w)
 subq.b #1,6(a1)
 rts
.pop:
 addq.b #1,6(a1)
 moveq #0,d1
 move.b 6(a1),d1
 moveq #0,d0
 move.b $100(a0,d1.w),d0
 rts
.write:
 andi.l #$ffff,d1
 cmpi.w #$2000,d1
 bhs.w .bad_read
 andi.w #$7ff,d1
 move.b d0,(a0,d1.w)
 rts
; Data read only, never instruction fetch. RAM mirrors and fixed/mapped PRG.
.read:
 andi.l #$ffff,d1
 cmpi.w #$2000,d1
 bhs.s .external
 andi.w #$7ff,d1
 moveq #0,d0
 move.b (a0,d1.w),d0
 rts
.external:
 cmpi.w #$8000,d1
 bcs.w .bad_read
 cmpi.w #15000,(a2)
 bhs.w .bad_read
 move.l d1,d2
 cmpi.w #$c000,d1
 bhs.s .fixed
 move.l a4,-(sp)
 movea.l 40(sp),a4
 moveq #0,d2
 move.b 3(a4),d2
 movea.l (sp)+,a4
 lsl.l #8,d2
 lsl.l #6,d2
 subi.w #$8000,d1
 add.l d1,d2
 addi.w #$8000,d1
 bra.s .resource
.fixed:
 addi.l #$10000,d2
.resource:
 moveq #0,d0
 move.b (a5,d2.l),d0
 cmpa.w #0,a6
 bne.s .validation_read
 move.w d1,(a3)+
 move.b d0,(a3)+
 clr.b (a3)+
.validation_read:
 addq.w #1,(a2)
 rts
; Binary 2A03 math: the raw decimal bit never changes arithmetic.
.adc:
 andi.l #255,d0
 move.l d4,d2
 andi.l #255,d2
 move.l d2,d3
 add.w d0,d3
 btst #0,d7
 beq.s .adc0
 addq.w #1,d3
.adc0:
 eor.b d2,d0
 not.b d0
 eor.b d3,d2
 and.b d2,d0
 andi.b #$3c,d7
 btst #7,d0
 beq.s .adcv
 ori.b #$40,d7
.adcv:
 cmpi.w #255,d3
 bls.s .adcc
 ori.b #1,d7
.adcc:
 move.b d3,d4
 move.b d4,d0
 bra.w .nz
.sbc:
 andi.l #255,d0
 move.l d4,d2
 andi.l #255,d2
 move.l d2,d3
 sub.w d0,d3
 btst #0,d7
 bne.s .sbc0
 subq.w #1,d3
.sbc0:
 eor.b d2,d0
 eor.b d3,d2
 and.b d2,d0
 andi.b #$3c,d7
 btst #7,d0
 beq.s .sbcv
 ori.b #$40,d7
.sbcv:
 tst.w d3
 bmi.s .sbcc
 ori.b #1,d7
.sbcc:
 move.b d3,d4
 move.b d4,d0
 bra.w .nz
.bad_read:
 addq.l #4,sp
.budget_failure:
 moveq #-2,d0
 bra.s .save
.success:
 moveq #1,d0
.save:
 move.b d4,2(a1)
 move.b d5,3(a1)
 move.b d6,4(a1)
 move.b d7,5(a1)
 movem.l (sp)+,d1-d7/a3-a4/a6
 rts
.invalid:
 moveq #-1,d0
 rts''')
 return re.sub(r'\b(bra|bsr|beq|bne|bhi|bls|bhs|bcs|bcc|bpl|bmi)\.w',r'\1.l','\n'.join(out)+'\n')
if __name__=='__main__':(ROOT/'port/src/recovery_player_collision_region.s').write_text(generate())
