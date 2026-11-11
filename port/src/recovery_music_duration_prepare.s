; Static PC8374 instrument setup: zero instrument ->837F; otherwise86B2.
; A0=2KiB RAM,A1=8-byte context,A2=10-byte read journal,A3=16KiB bank3.
; Buffers owned/disjoint. Canonical binary P and X28..2B required.
; D0=1/-1 inert rejection; D1-D7/A0-A6 preserved; CCR scratch.
recovery_music_duration_prepare:
        movem.l d1-d7,-(sp)
        cmpi.w #$8374,(a1)
        bne.w .invalid
        move.b 5(a1),d5
        andi.b #$38,d5
        cmpi.b #$20,d5
        bne.w .invalid
        moveq #0,d2
        move.b 3(a1),d2
        cmpi.b #$28,d2
        bcs.w .invalid
        cmpi.b #$2b,d2
        bhi.w .invalid
        move.b 5(a1),d5
        move.b 2(a1),d1
        moveq #0,d4
        move.b 6(a1),d4
        clr.w (a2)
        clr.l 2(a2)
        clr.l 6(a2)
        moveq #0,d3
        move.b $700(a0,d2.w),d3
        move.b d1,d7
        move.b d3,d1
        bsr.w .nz
        move.b d7,d1
        tst.b d3
        bne.s .instrument
        move.w #$837f,(a1)
        bra.w .publish
.instrument:
        move.b #$83,$100(a0,d4.w)
        subq.b #1,d4
        move.b #$7b,$100(a0,d4.w)
        subq.b #1,d4
        subq.b #1,d3
        clr.b $c3(a0)
; Original three ROL stores: upper bits of (instrument-1)*8.
        move.w d3,d6
        lsr.w #7,d6
        move.b d6,$c3(a0)
        move.w d3,d6
        lsr.w #6,d6
        move.b d6,$c3(a0)
        move.w d3,d6
        lsr.w #5,d6
        move.b d6,$c3(a0)
        move.b d3,d1
        lsl.b #3,d1
        andi.b #$fe,d5
        moveq #0,d6
        move.b $a02(a3),d6
        move.w #$8a02,2(a2)
        move.b d6,4(a2)
        move.w #1,(a2)
        bsr.w .adc
        move.b d1,$c5(a0)
        move.b $c3(a0),d1
        moveq #0,d6
        move.b $a01(a3),d6
        move.w #$8a01,6(a2)
        move.b d6,8(a2)
        move.w #2,(a2)
        bsr.w .adc
        move.b d1,$c6(a0)
        addq.b #2,d4
; JSR86B2 retains real return frame837E.
        move.b #$83,$100(a0,d4.w)
        subq.b #1,d4
        move.b #$7e,$100(a0,d4.w)
        subq.b #1,d4
        move.w #$86b2,(a1)
.publish:
        move.b d1,2(a1)
        move.b d2,3(a1)
        move.b d3,4(a1)
        move.b d5,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d7
        moveq #-1,d0
        rts
.nz:
        andi.b #$7d,d5
        tst.b d1
        bne.s .nonzero
        ori.b #2,d5
.nonzero:
        btst #7,d1
        beq.s .done
        ori.b #$80,d5
.done:
        rts
.adc:
        andi.w #$ff,d1
        move.w d1,d7
        add.w d6,d7
        btst #0,d5
        beq.s .sum
        addq.w #1,d7
.sum:
        eor.b d1,d6
        not.b d6
        eor.b d7,d1
        and.b d1,d6
        andi.b #$80,d6
        lsr.b #1,d6
        andi.b #$3c,d5
        or.b d6,d5
        btst #8,d7
        beq.s .carry
        ori.b #1,d5
.carry:
        move.b d7,d1
        bra.s .nz
