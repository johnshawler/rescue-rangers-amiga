; Static complete command04,83A0 ->839D before next fetch. No CPU interpreter.
; A0=2KiB RAM,A1=8-byte canonical context,A2=14-byte resource journal,
; A3=authentic read-only 16KiB bank3 view. All buffers valid/disjoint/owned.
; Journal count.w then3 records(address.w,value.b,kind.b=0).
; Guards command04 dispatch target8551 at848B/C before any mutations.
; Resource preflight reads are not emulated game reads; no asset extract.
; D0=1 success,-1 inert; D1-D7/A0-A6 preserved, native stack balanced.
recovery_music_command04:
        movem.l d1-d7,-(sp)
        cmpi.w #$83a0,(a1)
        bne.w .invalid
        cmpi.b #4,2(a1)
        bne.w .invalid
        cmpi.b #$2b,3(a1)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #$30,d1
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
        cmpi.b #$51,$48b(a3)
        bne.w .invalid
        cmpi.b #$85,$48c(a3)
        bne.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        clr.w (a2)
; JSR8473; STA C4; JSR856E; fetch operand and increment original pointer.
        move.b #$83,d1
        bsr.w .push
        move.b #$a6,d1
        bsr.w .push
        move.b #4,$c4(a0)
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
        move.b $48b(a3),d1
        move.w #$848b,6(a2)
        move.b d1,8(a2)
        clr.b 9(a2)
        move.w #2,(a2)
        bsr.w .push
        move.b $48c(a3),d2
        move.w #$848c,10(a2)
        move.b d2,12(a2)
        clr.b 13(a2)
        move.w #3,(a2)
        move.b d2,$c2(a0)
        addq.b #1,d4
        move.b $100(a0,d4.w),$c1(a0)
; Static8551 semantic handler, RTS and JMP839D.
        move.b $75b(a0),d7
        andi.b #$97,d7
        or.b $c3(a0),d7
        move.b d7,$75b(a0)
        addq.b #2,d4
        move.b 5(a1),d2
        andi.b #$6c,d2
        tst.b d7
        bne.s .nonzero
        ori.b #2,d2
.nonzero:
        move.b d7,d1
        andi.b #$80,d1
        or.b d1,d2
        move.w #$839d,(a1)
        move.b d7,2(a1)
        move.b #10,4(a1)
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
