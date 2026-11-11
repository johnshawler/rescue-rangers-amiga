; New bounded C584 -> nested palette-delay yield at FE8D.
; A0=2KiB original RAM, A1=eight-byte canonical context. No external journal.
; Requires canonical C584 first-resume context, D=0, task zero and queue <8.
; D0=1 success/-1 inert; D1-D7/A0-A6 preserved; native CCR scratch.
recovery_resumed_task_setup:
        cmpi.w #$c584,(a1)
        bne.w .invalid
        cmpi.b #$bf,2(a1)
        bne.w .invalid
        cmpi.b #$bf,3(a1)
        bne.w .invalid
        cmpi.b #8,4(a1)
        bne.w .invalid
        cmpi.b #$bf,6(a1)
        bne.w .invalid
        tst.b $91(a0)
        bne.w .invalid
        cmpi.b #8,$da(a0)
        bcc.w .invalid
        movem.l d1-d2,-(sp)
        move.b 5(a1),d1
        andi.b #$fa,d1
        cmpi.b #$a0,d1
        bne.w .bad
; C584, JSR F377 with return C58C, sound queue command 07.
        move.b #$88,$e4(a0)
        move.b #$c5,$1bf(a0)
        move.b #$8c,$1be(a0)
        move.b #7,$d9(a0)
        move.b #$bf,(a0)
        moveq #0,d1
        move.b $da(a0),d1
        move.b #7,1(a0)
        cmpi.b #$88,$dc(a0,d1.w)
        bne.s .queued
        move.b #7,$dc(a0,d1.w)
        addq.b #1,d1
        andi.b #7,d1
        move.b d1,$da(a0)
.queued:
        move.b #2,$f8(a0)
; C591 JSR C274; C594 remains on original stack across nested yield.
        move.b #$c5,$1bf(a0)
        move.b #$93,$1be(a0)
        move.b #$10,$0f(a0)
        move.b #$10,$0d(a0)
        move.b #0,$9a(a0)
        move.b #4,$0e(a0)
        moveq #31,d1
.copy:
        move.b $320(a0,d1.w),d2
        move.b d2,$300(a0,d1.w)
        dbra d1,.copy
        moveq #31,d1
.dim:
        move.b $300(a0,d1.w),d2
        subi.b #$10,d2
        bpl.s .store
        moveq #$0f,d2
.store:
        move.b d2,$300(a0,d1.w)
        dbra d1,.dim
        move.b #$ff,$18(a0)
; PHA delay=4; JSR FF04 with return C2A7, save X=10/Y=FF.
        move.b #4,$1bd(a0)
        move.b #$c2,$1bc(a0)
        move.b #$a7,$1bb(a0)
        move.b #1,$93(a0)
        move.b #$10,$1ba(a0)
        move.b #$ff,$1b9(a0)
        move.b #$ff,$1b8(a0)
        move.b #$0e,$1b7(a0)
        move.b #1,$81(a0)
        move.b #1,$80(a0)
        move.b #$b8,$82(a0)
        move.w #$fe8d,(a1)
        move.b #0,2(a1)
        move.b #$b8,3(a1)
        move.b #0,4(a1)
        andi.b #4,5(a1)
        ori.b #$a0,5(a1)
; Last SBC is palette index zero. Overflow survives the nested yield.
        move.b $320(a0),d1
        andi.b #$f0,d1
        cmpi.b #$80,d1
        bne.s .no_overflow
        ori.b #$40,5(a1)
.no_overflow:
        move.b #$b8,6(a1)
        movem.l (sp)+,d1-d2
        moveq #1,d0
        rts
.bad:
        movem.l (sp)+,d1-d2
.invalid:
        moveq #-1,d0
        rts
