; Indexed pitched-event duration and gate, $83A0 to $83FD before note PLA.
; A0=2048-byte RAM,A1=8-byte context,A2=10-byte journal,A3=16KiB bank3.
; Disjoint valid owned buffers; resource immutable. X28..2B, event21..FF
; excluding rests; canonical P with D clear. No hardware effects.
; D0=1 success,-1 inert rejection; D1-D7/A0-A6 preserved, CCR scratch.
recovery_music_pitched_gate:
        movem.l d1-d7/a4,-(sp)
        cmpi.w #$83a0,(a1)
        bne.w .invalid
        moveq #0,d0
        move.b 3(a1),d0
        cmpi.b #$28,d0
        bcs.w .invalid
        cmpi.b #$2b,d0
        bhi.w .invalid
        lea (a0,d0.w),a4
        move.b 5(a1),d1
        andi.b #$38,d1
        cmpi.b #$20,d1
        bne.w .invalid
        moveq #0,d7
        move.b 2(a1),d7
        cmpi.b #$21,d7
        bcs.w .invalid
        move.b d7,d1
        andi.b #$1f,d1
        beq.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        clr.w (a2)
        clr.l 2(a2)
        clr.l 6(a2)
; CMP20 sets C; PHA and four ROL then AND7, TAY, DEY.
        move.b d7,$100(a0,d4.w)
        subq.b #1,d4
        lsr.w #5,d7
        subq.w #1,d7
        moveq #0,d6
        move.b $730(a4),d6
        btst #5,d6
        beq.s .normal_table
        move.w d7,d1
        addi.w #$8585,d1
        move.b $585(a3,d7.w),d3
        bsr.w .record
        tst.b d3
        bne.s .duration
; Zero special-table value follows original fallback with A=0: no dotted flag.
        moveq #0,d6
.normal_table:
        move.w d7,d1
        addi.w #$858c,d1
        move.b $58c(a3,d7.w),d3
        bsr.w .record
        btst #4,d6
        beq.s .duration
        move.b d3,$c3(a0)
        andi.b #$ef,$730(a4)
        move.b d3,d1
        lsr.b #1,d1
        add.b d1,d3
.duration:
        moveq #0,d7
        move.b $738(a4),d7
        move.b d3,d5
        andi.w #255,d3
        add.w d7,d3
        move.b d3,$738(a4)
        move.b d3,4(a1)
; Preserve binary ADC C/V for the following pitched multiply.
        move.b 5(a1),d2
        andi.b #$2c,d2
        cmpi.w #255,d3
        bls.s .no_carry
        ori.b #1,d2
.no_carry:
        move.b d5,d1
        eor.b d7,d1
        not.b d1
        eor.b d3,d5
        and.b d1,d5
        andi.b #$80,d5
        lsr.b #1,d5
        or.b d5,d2
 ; PLA/AND1F/PHA leave a note operand pending on the original stack.
        addq.b #1,d4
        move.b $100(a0,d4.w),d1
        andi.b #$1f,d1
        move.b d1,$100(a0,d4.w)
        subq.b #1,d4
        move.b d3,$c4(a0)
        move.b $73c(a4),d1
        move.b d1,$c1(a0)
; Original JSR8006, multiplying C1*C4 into C1:C2 with eight rounds.
        move.b #$83,$100(a0,d4.w)
        subq.b #1,d4
        move.b #$f3,$100(a0,d4.w)
        subq.b #1,d4
        clr.b $c2(a0)
        moveq #7,d7
.multiply:
        moveq #0,d3
        move.b $c2(a0),d3
        add.w d3,d3
        move.b d3,$c2(a0)
        lsr.w #8,d3
        moveq #0,d5
        move.b $c1(a0),d5
        add.w d5,d5
        or.w d3,d5
        move.b d5,$c1(a0)
        andi.b #$fe,d2
        btst #8,d5
        beq.s .next_round
        moveq #0,d5
        move.b $c2(a0),d5
        moveq #0,d6
        move.b $c4(a0),d6
        move.w d5,d3
        add.w d6,d3
        bsr.w .adc_flags
        move.b d3,$c2(a0)
        moveq #0,d5
        move.b $c1(a0),d5
        moveq #0,d6
        move.w d5,d3
        btst #0,d2
        beq.s .high_no_carry
        addq.w #1,d3
.high_no_carry:
        bsr.w .adc_flags
        move.b d3,$c1(a0)
.next_round:
        dbra d7,.multiply
        addq.b #2,d4
; LDA C1/BNE/LDA01/STA0740,X: no zero outcome.
        move.b $c1(a0),d3
        bne.s .gate
        moveq #1,d3
.gate:
        move.b d3,$740(a4)
        move.w #$83fd,(a1)
        move.b d3,2(a1)
        clr.b 4(a1)
        andi.b #$6d,d2
        andi.b #$80,d3
        or.b d3,d2
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4
        moveq #1,d0
        rts
; Binary ADC flags C/V only; NZ are superseded at the public boundary.
.adc_flags:
        andi.b #$be,d2
        cmpi.w #255,d3
        bls.s .adc_no_carry
        ori.b #1,d2
.adc_no_carry:
        move.b d5,d1
        eor.b d6,d1
        not.b d1
        move.b d5,d0
        eor.b d3,d0
        and.b d1,d0
        andi.b #$80,d0
        lsr.b #1,d0
        or.b d0,d2
        rts
.invalid:
        movem.l (sp)+,d1-d7/a4
        moveq #-1,d0
        rts
.record:
        moveq #0,d0
        move.w (a2),d0
        lsl.w #2,d0
        move.w d1,2(a2,d0.w)
        move.b d3,4(a2,d0.w)
        clr.b 5(a2,d0.w)
        addq.w #1,(a2)
        rts
