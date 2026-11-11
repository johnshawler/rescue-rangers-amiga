; Static bank3 81A3 ->81C0/80BB ->82AC/82AF ->8060.
; A0 RAM2048,A1 context8,A2 journal30,A3 immutable bank (not read).
; Requires genuine82AB and805F frames separated by saved mask.
; D0=1/-1; D1-D7/A0-A6 preserved; native SP balanced; CCR scratch.
recovery_sfx_channel_reconfigure:
 movem.l d1-d7/a4,-(sp)
 cmpi.w #$81a3,(a1)
 bne.w .invalid
 moveq #0,d4
 move.b 6(a1),d4
 addq.b #1,d4
 cmpi.b #$ab,$100(a0,d4.w)
 bne.w .invalid
 addq.b #1,d4
 cmpi.b #$82,$100(a0,d4.w)
 bne.w .invalid
 addq.b #2,d4
 cmpi.b #$5f,$100(a0,d4.w)
 bne.w .invalid
 addq.b #1,d4
 cmpi.b #$80,$100(a0,d4.w)
 bne.w .invalid
 subq.b #5,d4
 move.b 5(a1),d3
 moveq #0,d6
 lea 2(a2),a4
 clr.w (a2)
 move.b $cf(a0),d2
 bsr.w .nz
 tst.b d2
 beq.w .outerreturn
 eori.b #15,d2
 move.b d2,$cf(a0)
 ; JSR81C0 then PHA.
 move.b #$81,d1
 bsr.w .push
 move.b #$ad,d1
 bsr.w .push
 move.b d2,d1
 bsr.w .push
 moveq #3,d7
.channel:
 move.b $cf(a0),d2
 lsr.b #1,d2
 bcs.s .skip
 ; JSR80BB, TXA/AND3/EOR3/ASL/ASL/TAY.
 move.b #$81,d1
 bsr.w .push
 move.b #$cc,d1
 bsr.w .push
 moveq #3,d5
 sub.w d7,d5
 lsl.w #2,d5
 move.b d5,4(a1)
 moveq #$30,d2
 ; CPY8 sets C, then conditional LDA0. NZ overwritten later.
 andi.b #$fe,d3
 cmpi.b #8,d5
 bcs.s .volume
 ori.b #1,d3
 cmpi.b #8,d5
 bne.s .volume
 moveq #0,d2
.volume:
 move.w d5,d1
 addi.w #$4000,d1
 bsr.w .apu
 addq.b #2,d4
 move.b $754(a0,d7.w),d2
 or.b $750(a0,d7.w),d2
 beq.s .skip
 move.b #$ff,$77c(a0,d7.w)
.skip:
 ; LSR CF leaves carry; DEX supplies final NZ.
 move.b $cf(a0),d2
 andi.b #$fe,d3
 btst #0,d2
 beq.s .nocarry
 ori.b #1,d3
.nocarry:
 lsr.b #1,d2
 move.b d2,$cf(a0)
 subq.w #1,d7
 bpl.w .channel
 move.b #$ff,3(a1)
 addq.b #1,d4
 move.b $100(a0,d4.w),d2
 move.b d2,$cf(a0)
 moveq #8,d2
 move.w #$4001,d1
 bsr.s .apu
 move.w #$4005,d1
 bsr.s .apu
 moveq #15,d2
 move.w #$4015,d1
 bsr.s .apu
 ; RTS81EF; LDA0/STA CF; RTS81B2.
 addq.b #2,d4
 clr.b $cf(a0)
.outerreturn:
 addq.b #2,d4
 ; PLA82AC, STA CF, RTS82AF consumes actual805F.
 addq.b #1,d4
 move.b $100(a0,d4.w),d2
 bsr.s .nz
 move.b d2,$cf(a0)
 addq.b #2,d4
 move.w #$8060,(a1)
 move.b d2,2(a1)
 move.b d3,5(a1)
 move.b d4,6(a1)
 movem.l (sp)+,d1-d7/a4
 moveq #1,d0
 rts
.invalid:
 movem.l (sp)+,d1-d7/a4
 moveq #-1,d0
 rts
.push:
 move.b d1,$100(a0,d4.w)
 subq.b #1,d4
 rts
.apu:
 move.w d1,(a4)+
 move.b d2,(a4)+
 move.b #1,(a4)+
 addq.w #1,d6
 move.w d6,(a2)
 rts
.nz:
 andi.b #$7d,d3
 tst.b d2
 bne.s .nonzero
 ori.b #2,d3
 rts
.nonzero:
 bpl.s .done
 ori.b #$80,d3
.done:
 rts
