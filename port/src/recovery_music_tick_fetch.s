; Static first active-channel music fetch, C0F3 -> 83A0 (not full tick).
; A0=2KiB RAM,A1=8-byte context,A2=6-byte resource-read journal,
; A3=read-only private 16KiB bank3 view. Buffers valid/disjoint/owned.
; Require canonical D=0 P, C0 in {0,4,8}, D0/D1/CF=0, empty queue,
; first channel duration zero and stream pointer within8000..BFFF.
; Journal count.w, original address.w, value.b, kind.b=0 (resource read).
; D0=1 success,-1 inert; D1-D7/A0-A6 preserved, CCR scratch.
recovery_music_tick_fetch:
        movem.l d1-d7,-(sp)
        cmpi.w #$c0f3,(a1)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #$38,d1
        cmpi.b #$20,d1
        bne.w .invalid
        moveq #0,d1
        move.b $db(a0),d1
        cmpi.b #7,d1
        bhi.w .invalid
        cmpi.b #$88,$dc(a0,d1.w)
        bne.w .invalid
        move.b $c0(a0),d1
        cmpi.b #8,d1
        bhi.w .invalid
        andi.b #3,d1
        bne.w .invalid
        move.b $d0(a0),d1
        or.b $d1(a0),d1
        or.b $cf(a0),d1
        or.b $763(a0),d1
        bne.w .invalid
        moveq #0,d6
        move.b $757(a0),d6
        lsl.w #8,d6
        move.b $753(a0),d6
        cmpi.w #$8000,d6
        bcs.w .invalid
        cmpi.w #$bfff,d6
        bhi.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        clr.w (a2)
; C0F6 JSR8000; bank3 phase and tempo accumulation.
        move.b #$c0,d1
        bsr.w .push
        move.b #$f8,d1
        bsr.w .push
        move.b $c0(a0),d1
        move.b #0,$c3(a0)
        addq.b #4,d1
        move.b d1,$c0(a0)
        moveq #0,d2
        move.b $ca(a0),d2
        moveq #0,d3
        move.b $c8(a0),d3
        add.w d3,d2
        move.b d2,$c8(a0)
        lsr.w #8,d2
        moveq #0,d3
        move.b $c9(a0),d3
        move.b d3,d5
        add.b d2,d3
        move.b d3,$c7(a0)
; ADC C9 + carry determines V; later CF LSR forces C=0.
        eor.b d3,d5
        not.b d2
        move.b $c9(a0),d1
        eor.b d1,d2
        and.b d2,d5
        andi.b #$80,d5
        lsr.b #1,d5
        moveq #0,d1
        bsr.w .push
        moveq #3,d1
        bsr.w .push
        move.b #$80,d1
        bsr.w .push
        move.b #$84,d1
        bsr.w .push
; Channel3 -> X2B, active pointer and duration zero lead to JSR856E.
        move.b #$83,d1
        bsr.w .push
        move.b #$9f,d1
        bsr.w .push
        move.b $753(a0),$c1(a0)
        move.b $757(a0),$c2(a0)
        move.w d6,2(a2)
        subi.w #$8000,d6
        move.b (a3,d6.w),d7
        move.b d7,4(a2)
        move.b #0,5(a2)
        move.w #1,(a2)
        addq.b #1,$753(a0)
        move.b $753(a0),d1
        bne.s .pointer_ready
        addq.b #1,$757(a0)
        move.b $757(a0),d1
.pointer_ready:
        move.b 5(a1),d2
        andi.b #$2c,d2
        or.b d5,d2
        tst.b d1
        bne.s .nonzero
        ori.b #2,d2
.nonzero:
        andi.b #$80,d1
        or.b d1,d2
        move.w #$83a0,(a1)
        move.b d7,2(a1)
        move.b #$2b,3(a1)
        move.b #0,4(a1)
        move.b d2,5(a1)
        addq.b #2,d4
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
