; Newly authored static music-event handler; no runtime CPU interpreter.
; A0=2048-byte RAM,A1=8-byte context,A2=22-byte journal,A3=16KiB bank3.
; Valid disjoint owned buffers; D0=1/-1, other registers preserved.
recovery_music_event_instrument08:
        movem.l d1-d7,-(sp)
        cmpi.w #$83a0,(a1)
        bne.w .invalid
        cmpi.b #8,2(a1)
        bne.w .invalid
        cmpi.b #$2b,3(a1)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #$38,d1
        cmpi.b #$20,d1
        bne.w .invalid
        moveq #0,d6
        move.b $757(a0),d6
        lsl.w #8,d6
        move.b $753(a0),d6
        cmpi.w #$8000,d6
        bcs.w .invalid
        cmpi.w #$bfff,d6
        bhi.w .invalid
        cmpi.b #$67,$493(a3)
        bne.w .invalid
        cmpi.b #$86,$494(a3)
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
        move.b #8,$c4(a0)
        move.b #$84,d1
        bsr.w .push
        move.b #$7b,d1
        bsr.w .push
        move.b $753(a0),$c1(a0)
        move.b $757(a0),$c2(a0)
        move.w d6,2(a2)
        subi.w #$8000,d6
        move.b (a3,d6.w),d7
        move.b d7,4(a2)
        clr.b 5(a2)
        move.w #1,(a2)
        addq.b #1,$753(a0)
        bne.s .incremented
        addq.b #1,$757(a0)
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
        move.b $493(a3),d1
        move.w #$8493,6(a2)
        move.b d1,8(a2)
        clr.b 9(a2)
        move.w #2,(a2)
        bsr.w .push
        move.b $494(a3),d2
        move.w #$8494,10(a2)
        move.b d2,12(a2)
        clr.b 13(a2)
        move.w #3,(a2)
        move.b d2,$c2(a0)
        addq.b #1,d4
        move.b $100(a0,d4.w),$c1(a0)

        addq.b #1,$c3(a0)
        moveq #0,d7
        move.b $c3(a0),d7
        cmp.b $72b(a0),d7
        bne.s .changed
        move.b 5(a1),d2
        andi.b #$6c,d2
        ori.b #3,d2
        move.b #18,4(a1)
        bra.w .finished
.changed:
        move.b d7,$72b(a0)
        move.b $72f(a0),d1
        ori.b #8,d1
        move.b d1,$72f(a0)
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
        bls.s .no_carry
        ori.b #1,d2
.no_carry:
        eor.b d3,d5
        not.b d5
        eor.b d7,d3
        and.b d5,d3
        andi.b #$80,d3
        lsr.b #1,d3
        or.b d3,d2
        tst.b d7
        bne.s .nonzero
        ori.b #2,d2
.nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
.finished:
        addq.b #2,d4
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b d2,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d7
        moveq #-1,d0
        rts
.push:
        move.b d1,$100(a0,d4.w)
        subq.b #1,d4
        rts
