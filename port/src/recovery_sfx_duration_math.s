; Static Ricoh duration multiply8006..8022 and SFX tick tail8298..82AF.
; A0 RAM2048 A1 rawcontext8 A2 journal6 A3 immutable bank3[16384].
; Entry8006 requires authentic8297 frame. Entry8298 requires pointer8000..BFFF
; and authentic805F frame (needed only on equal-mask RTS, checked in advance).
; D0=1 accepted/-1 inert rejected; D1-D7/A0-A6 and native SP preserved.
; Raw P (including D) preserved except original binary Ricoh flag effects.
recovery_sfx_duration_math:
 movem.l d1-d7,-(sp)
 moveq #0,d4
 move.b 6(a1),d4
 cmpi.w #$8006,(a1)
 beq.s .multiplycheck
 cmpi.w #$8298,(a1)
 bne.w .invalid
 cmpi.b #$80,$d1(a0)
 bcs.w .invalid
 cmpi.b #$c0,$d1(a0)
 bcc.w .invalid
 move.w #$805f,d1
 bra.s .check
.multiplycheck:
 move.w #$8297,d1
.check:
 addq.b #1,d4
 cmp.b $100(a0,d4.w),d1
 bne.w .invalid
 lsr.w #8,d1
 addq.b #1,d4
 cmp.b $100(a0,d4.w),d1
 bne.w .invalid
 subq.b #2,d4
 clr.w (a2)
 move.b 5(a1),d3
 cmpi.w #$8298,(a1)
 beq.w .tail
 moveq #0,d2
 clr.b $c2(a0)
 moveq #8,d7
.loop:
 ; ASL C2; ROL C1 (C from ASL), branch on C from ROL.
 move.b $c2(a0),d1
 move.b d1,d5
 add.b d1,d1
 move.b d1,$c2(a0)
 lsr.b #7,d5
 moveq #0,d6
 move.b $c1(a0),d6
 add.w d6,d6
 or.b d5,d6
 move.b d6,$c1(a0)
 andi.b #$7c,d3
 btst #8,d6
 beq.s .noadd
 ori.b #1,d3
 ; CLC, LDA C2, ADC C4: decimal flag deliberately does not change arithmetic.
 andi.b #$fe,d3
 move.b $c2(a0),d2
 moveq #0,d5
 move.b $c4(a0),d5
 bsr.w .adc
 move.b d2,$c2(a0)
 moveq #0,d5
 move.b $c1(a0),d2
 bsr.w .adc
 move.b d2,$c1(a0)
.noadd:
 ; DEY overrides NZ from prior shifts/ADC; C,V remain live.
 subq.b #1,d7
 move.b d2,d1
 move.b d7,d2
 bsr.w .nz
 move.b d1,d2
 tst.b d7
 bne.s .loop
 clr.b 4(a1)
 addq.b #2,d4
 move.w #$8298,d1
 bra.w .finish
.tail:
 move.b $c1(a0),d2
 addq.b #1,d2
 move.b d2,4(a1)
 move.b d2,$d5(a0)
 addq.b #1,$c0(a0)
 move.b $c0(a0),d2
 bsr.w .nz
 ; JSR8358 / LDY0 / LDA(D0),Y / INC pointer / RTS.
 move.b #$82,$100(a0,d4.w)
 subq.b #1,d4
 move.b #$a1,$100(a0,d4.w)
 subq.b #1,d4
 clr.b 4(a1)
 moveq #0,d1
 move.b $d1(a0),d1
 lsl.w #8,d1
 move.b $d0(a0),d1
 move.w d1,2(a2)
 subi.w #$8000,d1
 move.b (a3,d1.w),d2
 move.b d2,4(a2)
 clr.b 5(a2)
 move.w #1,(a2)
 addq.b #1,$d0(a0)
 bne.s .low
 addq.b #1,$d1(a0)
.low:
 addq.b #2,d4
 ; PHA; EOR CF; branch. EOR overrides fetch NZ, preserves C,V.
 move.b d2,$100(a0,d4.w)
 subq.b #1,d4
 move.b $cf(a0),d1
 eor.b d1,d2
 bsr.w .nz
 tst.b d2
 beq.s .equal
 move.b d2,$cf(a0)
 move.b #$82,$100(a0,d4.w)
 subq.b #1,d4
 move.b #$ab,$100(a0,d4.w)
 subq.b #1,d4
 move.w #$81a3,d1
 bra.s .finish
.equal:
 addq.b #1,d4
 move.b $100(a0,d4.w),d2
 bsr.w .nz
 move.b d2,$cf(a0)
 addq.b #2,d4
 move.w #$8060,d1
.finish:
 move.w d1,(a1)
 move.b d2,2(a1)
 move.b d3,5(a1)
 move.b d4,6(a1)
 movem.l (sp)+,d1-d7
 moveq #1,d0
 rts
.invalid:
 movem.l (sp)+,d1-d7
 moveq #-1,d0
 rts
.nz:
 andi.b #$7d,d3
 tst.b d2
 bne.s .nonzero
 ori.b #2,d3
 rts
.nonzero:
 bpl.s .nzdone
 ori.b #$80,d3
.nzdone:
 rts
.adc:
 ; D2 old accumulator byte; D5 unsigned operand; raw carry D3 bit0.
 moveq #0,d6
 move.b d2,d6
 add.w d5,d6
 btst #0,d3
 beq.s .carryin
 addq.w #1,d6
.carryin:
 ; V = ~(old xor operand) & (old xor result) & 80.
 eor.b d2,d5
 not.b d5
 eor.b d6,d2
 and.b d2,d5
 andi.b #$3c,d3
 btst #7,d5
 beq.s .nov
 ori.b #$40,d3
.nov:
 btst #8,d6
 beq.s .noc
 ori.b #1,d3
.noc:
 move.b d6,d2
 bra.s .nz
