; Static bank-3 command07 initialization; no instruction decoder.
; A0=2KiB RAM,A1=8-byte canonical context,A2=30-byte APU journal.
; A3=caller-owned read-only 16KiB bank3 resource view ($8000-$BFFF).
; Requires PC8003,A07,CF0, canonical P, original C0F2 return frame.
; Resource count>7, command07 pointer in8000..BFF7, header byte zero.
; D0=1 at C0F3,-1 inert. D1-D7/A0-A6 preserved. Buffers disjoint.
recovery_music07_command:
        movem.l d1-d7/a3-a5,-(sp)
        cmpi.w #$8003,(a1)
        bne.w .invalid
        cmpi.b #7,2(a1)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #$30,d1
        cmpi.b #$20,d1
        bne.w .invalid
        tst.b $cf(a0)
        bne.w .invalid
        cmpi.b #8,$a00(a3)
        bcs.w .invalid
        moveq #0,d6
        move.b $a11(a3),d6
        lsl.w #8,d6
        move.b $a12(a3),d6
        cmpi.w #$8000,d6
        bcs.w .invalid
        cmpi.w #$bff7,d6
        bhi.w .invalid
        move.w d6,d7
        subi.w #$8000,d7
        lea (a3,d7.w),a4
        tst.b (a4)
        bne.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        addq.b #1,d4
        cmpi.b #$f2,$100(a0,d4.w)
        bne.w .invalid
        addq.b #1,d4
        cmpi.b #$c0,$100(a0,d4.w)
        bne.w .invalid
        subq.b #2,d4
        clr.w (a2)
        lea 2(a2),a5
        addq.b #1,$c0(a0)
        move.b #$80,d1
        bsr.w .push
        move.b #$e5,d1
        bsr.w .push
        move.b d6,$c1(a0)
        lsr.w #8,d6
        move.b d6,$c2(a0)
        move.b #1,$c9(a0)
        move.b #$99,$ca(a0)
        move.b #0,$c8(a0)
        move.b #0,$cb(a0)
        move.b #0,$cc(a0)
        move.b #0,$cd(a0)
        moveq #$53,d3
.clear:
        move.b #0,$728(a0,d3.w)
        dbra d3,.clear
        moveq #3,d3
        addq.l #1,a4
.headers:
        move.b (a4)+,$754(a0,d3.w)
        move.b (a4)+,$750(a0,d3.w)
        dbra d3,.headers
        moveq #0,d1
        bsr.w .push
        moveq #3,d3
        moveq #0,d5
.mute:
        move.b #$81,d1
        bsr.w .push
        move.b #$cc,d1
        bsr.w .push
        move.w #$4000,d2
        add.w d5,d2
        moveq #$30,d1
        cmpi.w #8,d5
        bne.s .publish_mute
        moveq #0,d1
.publish_mute:
        bsr.w .publish
        addq.b #2,d4
        move.b $754(a0,d3.w),d1
        or.b $750(a0,d3.w),d1
        beq.s .empty
        move.b #$ff,$77c(a0,d3.w)
.empty:
        move.b #0,$cf(a0)
        addq.w #4,d5
        dbra d3,.mute
        addq.b #1,d4
        move.b #0,$cf(a0)
        moveq #8,d1
        move.w #$4001,d2
        bsr.w .publish
        move.w #$4005,d2
        bsr.w .publish
        moveq #$0f,d1
        move.w #$4015,d2
        bsr.w .publish
        addq.b #2,d4
        subq.b #1,$c0(a0)
        addq.b #2,d4
        move.w #$c0f3,(a1)
        move.b #$0f,2(a1)
        move.b #$ff,3(a1)
        move.b #$0c,4(a1)
        andi.b #$7c,5(a1)
        move.b $c0(a0),d1
        bne.s .nonzero
        ori.b #2,5(a1)
.nonzero:
        andi.b #$80,d1
        or.b d1,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a3-a5
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d7/a3-a5
        moveq #-1,d0
        rts
.push:
        move.b d1,$100(a0,d4.w)
        subq.b #1,d4
        rts
.publish:
        move.w d2,(a5)+
        move.b d1,(a5)+
        move.b #1,(a5)+
        addq.w #1,(a2)
        rts
