; Complete first-channel rest event,83A0 through original channel RTS.
; A0=2KiB RAM,A1=8-byte canonical context,A2=10-byte resource journal,
; A3=16KiB read-only bank3. Buffers valid/disjoint/owned. No interpreter.
; Supports X2B and rest encodings20,40,60,80,A0,C0,E0; D clear.
; D0=1 success,-1 inert. D1-D7/A0-A6 preserved. Native CCR scratch.
recovery_music_event_rest:
        movem.l d1-d7,-(sp)
        cmpi.w #$83a0,(a1)
        bne.w .invalid
        cmpi.b #$2b,3(a1)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #$38,d1
        cmpi.b #$20,d1
        bne.w .invalid
        moveq #0,d7
        move.b 2(a1),d7
        beq.w .invalid
        move.b d7,d1
        andi.b #$1f,d1
        bne.w .invalid
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
        move.b $75b(a0),d6
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
        andi.b #$ef,$75b(a0)
        move.b d3,d1
        lsr.b #1,d1
        add.b d1,d3
.duration:
        moveq #0,d7
        move.b $763(a0),d7
        move.b d3,d5
        andi.w #255,d3
        add.w d7,d3
        move.b d3,$763(a0)
        move.b d3,4(a1)
; Preserve binary ADC C/V, then rest path ends with LDA FF (N=1,Z=0).
        move.b 5(a1),d2
        andi.b #$2c,d2
        ori.b #$80,d2
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
; PLA; AND1F; JSR859B; original envelope release and RTS; JMP846D.
        addq.b #1,d4
        move.b $100(a0,d4.w),d1
        move.b #$83,$100(a0,d4.w)
        subq.b #1,d4
        move.b #$e5,$100(a0,d4.w)
        subq.b #1,d4
        move.b $72f(a0),d1
        andi.b #$f8,d1
        ori.b #3,d1
        move.b d1,$72f(a0)
        addq.b #2,d4
        move.b #$ff,$76b(a0)
; Actual original channel RTS, including 8-bit SP wrap and 16-bit PC wrap.
        addq.b #1,d4
        moveq #0,d7
        move.b $100(a0,d4.w),d7
        addq.b #1,d4
        moveq #0,d1
        move.b $100(a0,d4.w),d1
        lsl.w #8,d1
        or.w d1,d7
        addq.w #1,d7
        move.w d7,(a1)
        move.b #$ff,2(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d7
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
