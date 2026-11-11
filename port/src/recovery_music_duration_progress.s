; Static bank3 nonzero-duration path PC837F, after envelope-update branch.
; A0=owned 2048-byte RAM, A1=owned disjoint eight-byte canonical context.
; Accept X28..2B and canonical binary P. No resources/I/O.
; D0=1 success/-1 inert rejection; D1-D7/A0-A6 preserved; CCR scratch.
; Natural exit839D (fetch), otherwise actual stack-based RTS at839C.
recovery_music_duration_progress:
        movem.l d1-d7,-(sp)
        cmpi.w #$837f,(a1)
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
        moveq #0,d4
        move.b 6(a1),d4
        move.b 4(a1),d3
        move.b $740(a0,d2.w),d1
        bsr.w .subtract
        move.b d1,$740(a0,d2.w)
        tst.b d1
        beq.s .expire
        btst #0,d5
        bne.s .duration
.expire:
; Original JSR859B: retain both dead original stack stores and wrapping.
        move.b #$83,$100(a0,d4.w)
        subq.b #1,d4
        move.b #$8e,$100(a0,d4.w)
        subq.b #1,d4
        move.b $704(a0,d2.w),d1
        andi.b #$f8,d1
        ori.b #3,d1
        move.b d1,$704(a0,d2.w)
        addq.b #2,d4
.duration:
        move.b $738(a0,d2.w),d1
        bsr.w .subtract
        move.b d1,$738(a0,d2.w)
        move.w #$839d,(a1)
        tst.b d1
        beq.s .publish
        btst #0,d5
        beq.s .publish
; RTS, including original SP wrap and 16-bit return increment.
        addq.b #1,d4
        moveq #0,d6
        move.b $100(a0,d4.w),d6
        addq.b #1,d4
        moveq #0,d7
        move.b $100(a0,d4.w),d7
        lsl.w #8,d7
        or.w d7,d6
        addq.w #1,d6
        move.w d6,(a1)
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
.subtract:
; Binary SEC/SBC C7: carry=no borrow; V=(lhs^rhs)&(lhs^result)&80.
        andi.w #$ff,d1
        moveq #0,d6
        move.b $c7(a0),d6
        move.w d1,d7
        sub.w d6,d7
        eor.b d1,d6
        eor.b d7,d1
        and.b d1,d6
        andi.b #$80,d6
        lsr.b #1,d6
        andi.b #$3c,d5
        or.b d6,d5
        btst #8,d7
        bne.s .borrow
        ori.b #1,d5
.borrow:
        move.b d7,d1
        bne.s .nonzero
        ori.b #2,d5
.nonzero:
        btst #7,d1
        beq.s .done
        ori.b #$80,d5
.done:
        rts
