; Shared four-channel music data dispatch and static setup handlers.
; A0 RAM, A1 context, A2 22-byte journal, A3 immutable 16KiB bank3.
; D0=1/-1; D1-D7/A0-A6 preserved; buffers valid/disjoint/exclusive.
; No runtime CPU opcode decode. Commands 04/05/06/07/08/09/18 only.
recovery_music_indexed_commands:
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
        andi.b #$30,d1
        cmpi.b #$20,d1
        bne.w .invalid
        moveq #0,d5
        move.b 2(a1),d5
        cmpi.b #4,d5
        beq.w .select4
        cmpi.b #5,d5
        beq.w .select5
        cmpi.b #6,d5
        beq.w .select6
        cmpi.b #7,d5
        beq.w .select7
        cmpi.b #8,d5
        beq.w .select8
        cmpi.b #9,d5
        beq.w .select9
        cmpi.b #24,d5
        beq.w .select24
        bra.w .invalid
.select4:
        move.w #$8551,d3
        bra.w .selected
.select5:
        move.w #$84cd,d3
        bra.w .selected
.select6:
        move.w #$84db,d3
        bra.w .selected
.select7:
        move.w #$8652,d3
        bra.w .selected
.select8:
        btst #3,5(a1)
        bne.w .invalid
        move.w #$8667,d3
        bra.w .selected
.select9:
        move.w #$84e1,d3
        bra.w .selected
.select24:
        move.w #$86a5,d3
        bra.w .selected
.selected:
        add.w d5,d5
        addi.w #$483,d5
        moveq #0,d6
        move.b $72c(a4),d6
        lsl.w #8,d6
        move.b $728(a4),d6
        cmpi.w #$8000,d6
        bcs.w .invalid
        cmpi.w #$bfff,d6
        bhi.w .invalid
        cmpi.b #5,2(a1)
        bne.s .bounds_ok
        cmpi.w #$bfff,d6
        beq.w .invalid
.bounds_ok:
        cmp.b (a3,d5.w),d3
        bne.w .invalid
        lsr.w #8,d3
        cmp.b 1(a3,d5.w),d3
        bne.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        clr.w (a2)
        clr.l 14(a2)
        clr.l 18(a2)
; JSR8473; STA C4; JSR856E; fetch operand and increment original pointer.
        move.b #$83,d1
        bsr.w .push
        move.b #$a6,d1
        bsr.w .push
        move.b 2(a1),$c4(a0)
        move.b #$84,d1
        bsr.w .push
        move.b #$7b,d1
        bsr.w .push
        move.b $728(a4),$c1(a0)
        move.b $72c(a4),$c2(a0)
        move.w d6,2(a2)
        subi.w #$8000,d6
        move.b (a3,d6.w),d7
        move.b d7,4(a2)
        clr.b 5(a2)
        move.w #1,(a2)
        addq.b #1,$728(a4)
        bne.s .incremented
        addq.b #1,$72c(a4)
.incremented:
        addq.b #2,d4
        move.b d7,$c3(a0)
; JSR8023 and inline data dispatch retain original push/pop writes.
        move.b #$84,d1
        bsr.w .push
        move.b #$82,d1
        bsr.w .push
        addq.b #1,d4
        move.b $100(a0,d4.w),$c1(a0)
        addq.b #1,d4
        move.b $100(a0,d4.w),$c2(a0)
        move.b (a3,d5.w),d1
        move.w d5,d0
        addi.w #$8000,d0
        move.w d0,6(a2)
        move.b d1,8(a2)
        clr.b 9(a2)
        move.w #2,(a2)
        bsr.w .push
        move.b 1(a3,d5.w),d2
        addq.w #1,d0
        move.w d0,10(a2)
        move.b d2,12(a2)
        clr.b 13(a2)
        move.w #3,(a2)
        move.b d2,$c2(a0)
        addq.b #1,d4
        move.b $100(a0,d4.w),$c1(a0)
        cmpi.b #4,2(a1)
        beq.w .handler4
        cmpi.b #5,2(a1)
        beq.w .handler5
        cmpi.b #6,2(a1)
        beq.w .handler6
        cmpi.b #7,2(a1)
        beq.w .handler7
        cmpi.b #8,2(a1)
        beq.w .handler8
        cmpi.b #9,2(a1)
        beq.w .handler9
        cmpi.b #24,2(a1)
        beq.w .handler24
        bra.w .invalid
.handler4:
; Static8551 semantic handler, RTS and JMP839D.
        move.b $730(a4),d7
        andi.b #$97,d7
        or.b $c3(a0),d7
        move.b d7,$730(a4)
        addq.b #2,d4
        move.b 5(a1),d2
        andi.b #$6c,d2
        tst.b d7
        bne.s .h4_nonzero
        ori.b #2,d2
.h4_nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b #10,4(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4
        moveq #1,d0
        rts
.handler5:
; Static84CD handler: reset fractional tempo and fetch tempo low byte.
        move.b #0,$c8(a0)
        move.b #$84,d1
        bsr.w .push
        move.b #$d3,d1
        bsr.w .push
        moveq #0,d6
        move.b $72c(a4),d6
        lsl.w #8,d6
        move.b $728(a4),d6
        move.b $728(a4),$c1(a0)
        move.b $72c(a4),$c2(a0)
        move.w d6,14(a2)
        subi.w #$8000,d6
        move.b (a3,d6.w),d7
        move.b d7,16(a2)
        clr.b 17(a2)
        move.w #4,(a2)
        addq.b #1,$728(a4)
        bne.s .h5_second_incremented
        addq.b #1,$72c(a4)
.h5_second_incremented:
        addq.b #2,d4
        move.b $c3(a0),d3
        move.b d7,$ca(a0)
        move.b d3,$c9(a0)
        addq.b #2,d4
        move.b 5(a1),d2
        andi.b #$6c,d2
        tst.b d3
        bne.s .h5_nonzero
        ori.b #2,d2
.h5_nonzero:
        move.b d3,d1
        andi.b #$80,d1
        or.b d1,d2
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b d3,4(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4
        moveq #1,d0
        rts
.handler6:
; Static84DB channel setup, RTS and JMP839D.
        move.b $c3(a0),d7
        move.b d7,$73c(a4)
        addq.b #2,d4
        move.b 5(a1),d2
        andi.b #$6c,d2
        tst.b d7
        bne.s .h6_nonzero
        ori.b #2,d2
.h6_nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b #14,4(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4
        moveq #1,d0
        rts
.handler7:
; Static8652 channel setup, RTS and JMP839D.
        move.b $70c(a4),d7
        andi.b #$c0,d7
        or.b $c3(a0),d7
        ori.b #$30,d7
        move.b d7,$70c(a4)
        addq.b #2,d4
        move.b 5(a1),d2
        andi.b #$6c,d2
        ori.b #1,d2
        tst.b d7
        bne.s .h7_nonzero
        ori.b #2,d2
.h7_nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b #16,4(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4
        moveq #1,d0
        rts
.handler8:

        addq.b #1,$c3(a0)
        moveq #0,d7
        move.b $c3(a0),d7
        cmp.b $700(a4),d7
        bne.s .h8_changed
        move.b 5(a1),d2
        andi.b #$6c,d2
        ori.b #3,d2
        move.b #18,4(a1)
        bra.w .h8_finished
.h8_changed:
        move.b d7,$700(a4)
        move.b $704(a4),d1
        ori.b #8,d1
        move.b d1,$704(a4)
        subq.b #1,d7
        move.b d7,4(a1)
        clr.b $c3(a0)
; Three ASL A / ROL C3 pairs, preserving every original C3 write.
        add.w d7,d7
        move.w d7,d1
        lsr.w #8,d1
        move.b d1,$c3(a0)
        add.w d7,d7
        move.w d7,d1
        lsr.w #8,d1
        move.b d1,$c3(a0)
        add.w d7,d7
        move.w d7,d1
        lsr.w #8,d1
        move.b d1,$c3(a0)
; Resource base address low, then high. Journal extends to five records.
        moveq #0,d3
        move.b $a02(a3),d3
        move.w #$8a02,14(a2)
        move.b d3,16(a2)
        clr.b 17(a2)
        move.w #4,(a2)
        andi.w #255,d7
        add.w d3,d7
        move.b d7,$c5(a0)
        lsr.w #8,d7
        moveq #0,d3
        move.b $c3(a0),d3
        moveq #0,d5
        move.b $a01(a3),d5
        move.w #$8a01,18(a2)
        move.b d5,20(a2)
        clr.b 21(a2)
        move.w #5,(a2)
        add.w d3,d7
        add.w d5,d7
        move.b d7,$c6(a0)
; Binary ADC's C,V,N,Z; retain I,D,U (D is guarded clear).
        move.b 5(a1),d2
        andi.b #$2c,d2
        cmpi.w #255,d7
        bls.s .h8_no_carry
        ori.b #1,d2
.h8_no_carry:
        eor.b d3,d5
        not.b d5
        eor.b d7,d3
        and.b d5,d3
        andi.b #$80,d3
        lsr.b #1,d3
        or.b d3,d2
        tst.b d7
        bne.s .h8_nonzero
        ori.b #2,d2
.h8_nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
.h8_finished:
        addq.b #2,d4
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4
        moveq #1,d0
        rts
.handler9:
        move.b $730(a4),d7
        andi.b #$f8,d7
        or.b $c3(a0),d7
        move.b d7,$730(a4)
        addq.b #2,d4
        move.b 5(a1),d2
        andi.b #$6c,d2
        tst.b d7
        bne.s .h9_nonzero
        ori.b #2,d2
.h9_nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b #20,4(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4
        moveq #1,d0
        rts
.handler24:
        move.b $70c(a4),d7
        andi.b #$0f,d7
        or.b $c3(a0),d7
        ori.b #$30,d7
        move.b d7,$70c(a4)
        addq.b #2,d4
        move.b 5(a1),d2
        andi.b #$6c,d2
        tst.b d7
        bne.s .h24_nonzero
        ori.b #2,d2
.h24_nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b #50,4(a1)
        move.b d2,5(a1)
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
