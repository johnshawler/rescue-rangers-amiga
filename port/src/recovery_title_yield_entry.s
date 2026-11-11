; Static C5CB JSR FF04 -> FF04, retaining the original return frame.
; A0 RAM[2048], A1 context[8], A2 journal[8] of address.w/value.b/zero.b.
; D0=2 stores, -1 inert invalid PC; D1-D7/A0-A6 and host SP preserved.
recovery_title_yield_entry:
        cmpi.w #$c5cb,(a1)
        bne.s .invalid
        movem.l d1/a3,-(sp)
        moveq #0,d1
        move.b 6(a1),d1
        lea (a2),a3
        move.b #$c5,$100(a0,d1.w)
        ori.w #$100,d1
        move.w d1,(a3)+
        move.b #$c5,(a3)+
        clr.b (a3)+
        subq.b #1,d1
        move.b #$cd,(a0,d1.w)
        move.w d1,(a3)+
        move.b #$cd,(a3)+
        clr.b (a3)+
        subq.b #1,d1
        move.b d1,6(a1)
        move.w #$ff04,(a1)
        movem.l (sp)+,d1/a3
        moveq #2,d0
        rts
.invalid:
        moveq #-1,d0
        rts
