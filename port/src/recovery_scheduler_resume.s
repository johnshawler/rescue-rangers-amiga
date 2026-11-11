; New bounded FE8D -> C584 recovery. A0 RAM, A1 context, A2 controller journal.
; D0.b/D1.b decoded pads, A/B/Select/Start/U/D/L/R = bits 7..0.
; Journal 74 bytes: count.w then {address.w,data.b,kind.b}; read=0/write=1.
; Standard pads only: serial bus values 0/1, expansion bit zero.
; D0=1 success/-1 inert rejection; D1-D7/A0-A6 preserved; CCR scratch.
recovery_scheduler_resume:
        cmpi.w #$fe8d,(a1)
        bne.w .invalid
        tst.b 2(a1)
        bne.w .invalid
        cmpi.b #$bb,3(a1)
        bne.w .invalid
        tst.b 4(a1)
        bne.w .invalid
        cmpi.b #$bb,6(a1)
        bne.w .invalid
        movem.l d2-d7/a3,-(sp)
        move.b 5(a1),d2
        andi.b #$f3,d2
        cmpi.b #$a0,d2
        bne.w .bad
        cmpi.b #4,$80(a0)
        bne.w .bad
        cmpi.b #$bb,$82(a0)
        bne.w .bad
        cmpi.l #$08bf83c5,$1bc(a0)
        bne.w .bad
; Scheduler stores and original JSR C162 ($FECF) with restored SP=$BB.
        move.b #0,$90(a0)
        move.b #0,$91(a0)
        move.b #2,$80(a0)
        move.b #$fe,$1bb(a0)
        move.b #$cf,$1ba(a0)
        clr.w (a2)
        lea 2(a2),a3
        move.w #$4016,(a3)+
        move.b #1,(a3)+
        move.b #1,(a3)+
        addq.w #1,(a2)
        move.w #$4016,(a3)+
        move.b #0,(a3)+
        move.b #1,(a3)+
        addq.w #1,(a2)
        move.b d0,d2
        move.b d1,d3
        moveq #7,d7
.serial:
        moveq #0,d4
        add.b d2,d2
        addx.b d4,d4
        move.w #$4016,(a3)+
        move.b d4,(a3)+
        move.b #0,(a3)+
        addq.w #1,(a2)
        move.b $14(a0),d5
        add.b d5,d5
        or.b d4,d5
        move.b d5,$14(a0)
        move.b $00(a0),d5
        add.b d5,d5
        move.b d5,$00(a0)
        moveq #0,d4
        add.b d3,d3
        addx.b d4,d4
        move.w #$4017,(a3)+
        move.b d4,(a3)+
        move.b #0,(a3)+
        addq.w #1,(a2)
        move.b $15(a0),d5
        add.b d5,d5
        or.b d4,d5
        move.b d5,$15(a0)
        move.b $01(a0),d5
        add.b d5,d5
        move.b d5,$01(a0)
        dbra d7,.serial
; Expansion registers are now zero; retain both original ORA/STA stores.
        move.b $14(a0),d5
        move.b d5,$14(a0)
        move.b $15(a0),d5
        move.b d5,$15(a0)
        moveq #1,d7
.edge:
        move.b $14(a0,d7.w),d4
        move.b $16(a0,d7.w),d5
        eor.b d4,d5
        and.b d4,d5
        move.b d5,$14(a0,d7.w)
        move.b d4,$16(a0,d7.w)
        dbra d7,.edge
        moveq #3,d7
.sanitize:
        moveq #0,d6
        move.b $14(a0,d7.w),d4
        move.b d4,d5
        andi.b #$0c,d5
        cmpi.b #$0c,d5
        beq.s .clear
        move.b d4,d5
        andi.b #3,d5
        cmpi.b #3,d5
        bne.s .next
.clear:
        moveq #1,d6
        andi.b #$f0,d4
        move.b d4,$14(a0,d7.w)
.next:
        dbra d7,.sanitize
; Last CMP carry survives DEX, RTS, PLA/TAY and PLA/TAX. Final A/X=$BF.
        move.w #$c584,(a1)
        move.b #$bf,2(a1)
        move.b #$bf,3(a1)
        move.b #8,4(a1)
        andi.b #$4c,5(a1)
        ori.b #$a0,5(a1)
        or.b d6,5(a1)
        move.b #$bf,6(a1)
        movem.l (sp)+,d2-d7/a3
        moveq #1,d0
        rts
.bad:
        movem.l (sp)+,d2-d7/a3
.invalid:
        moveq #-1,d0
        rts
