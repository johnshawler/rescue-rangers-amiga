; New bounded startup bank-3 silent tick, bank-6 restoration and first RTI.
; A0=2048-byte RAM; A1=8-byte context; A2=22-byte mapper journal.
; Caller has selected bank 3. Buffers valid, disjoint, exclusively owned.
; Exact startup entry/frame only, allowing D=0/1 and saved I=0/1.
; D0=1 at FE8D BEFORE scheduler execution; -1 inert rejection.
; Other D/A preserved, CCR scratch. Canonical output P: B=0,U=1.
recovery_silent_tick_rti:
        movem.l d1-d3/a3,-(sp)
        cmpi.w #$c0f3,(a1)
        bne.w .invalid
        tst.b 2(a1)
        bne.w .invalid
        cmpi.b #$ff,3(a1)
        bne.w .invalid
        cmpi.b #$0c,4(a1)
        bne.w .invalid
        cmpi.b #$b4,6(a1)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #$f7,d1
        cmpi.b #$26,d1
        bne.w .invalid
        cmpi.b #1,$db(a0)
        bne.w .invalid
        cmpi.b #$88,$dd(a0)
        bne.w .invalid
        cmpi.b #6,$f1(a0)
        bne.w .invalid
        move.b $f5(a0),d1
        or.b $c0(a0),d1
        or.b $cf(a0),d1
        or.b $d0(a0),d1
        or.b $d1(a0),d1
        or.b $c8(a0),d1
        or.b $c9(a0),d1
        or.b $ca(a0),d1
        or.b $cc(a0),d1
        bne.w .invalid
        moveq #7,d2
.guard_pointers:
        tst.b $750(a0,d2.w)
        bne.w .invalid
        dbra d2,.guard_pointers
        tst.b $1b5(a0)
        bne.w .invalid
        cmpi.b #$bb,$1b6(a0)
        bne.w .invalid
        tst.b $1b7(a0)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #8,d1
        ori.b #$a0,d1
        move.b $1b9(a0),d3
        andi.b #$fb,d3
        cmp.b d3,d1
        bne.w .invalid
        ori.b #$14,d1
        cmp.b $1b8(a0),d1
        bne.w .invalid
        cmpi.b #$8d,$1ba(a0)
        bne.w .invalid
        cmpi.b #$fe,$1bb(a0)
        bne.w .invalid
; Empty queue branches to JSR 8000 (return C0F8); all semantic stores.
        clr.w (a2)
        move.b #$c0,$1b4(a0)
        move.b #$f8,$1b3(a0)
        move.b #0,$c3(a0)
        move.b #4,$c0(a0)
        move.b #0,$c8(a0)
        move.b #0,$c7(a0)
        move.b #0,$1b2(a0)
        moveq #3,d2
.channels:
        move.b d2,$1b1(a0)
        move.b #$80,$1b0(a0)
        move.b #$84,$1af(a0)
; Cleared pointers make 8363 return immediately; LSR CF still stores.
        move.b #0,$cf(a0)
        dbra d2,.channels
        move.b #0,$cf(a0)
        move.b #2,$c0(a0)
        move.b #4,$c0(a0)
; Return from bank-3 update; serialize restore shadow 6 in exact order.
        lea 2(a2),a3
        moveq #6,d1
        moveq #4,d2
.publish:
        move.w #$fff0,(a3)+
        move.b d1,(a3)+
        move.b #0,(a3)+
        addq.w #1,(a2)
        lsr.b #1,d1
        dbra d2,.publish
; Restore saved registers and RTI architectural state. Saved RAM is untouched.
        move.w #$fe8d,(a1)
        move.b $1b7(a0),2(a1)
        move.b $1b6(a0),3(a1)
        move.b $1b5(a0),4(a1)
        move.b $1b9(a0),5(a1)
        move.b #$bb,6(a1)
        movem.l (sp)+,d1-d3/a3
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d3/a3
        moveq #-1,d0
        rts
