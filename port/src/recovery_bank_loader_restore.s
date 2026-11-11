; Static FF53 zero-deferred bank publication and genuine wrapped RTS.
; A0 RAM2048,A1 context8,A2 journal22. F6!=0 rejects before any mutation.
; Caller owns mapper-mode/latch prerequisites and applies ordered mapper events.
; All raw status bits are preserved except N/Z/C set by original instructions.
; D0=1/-1; D1-D7/A0-A6 and native SP preserved. No resource access.
recovery_bank_loader_restore:
 cmpi.w #$ff53,(a1)
 bne.w .invalid
 tst.b $f6(a0)
 bne.w .invalid
 movem.l d1-d4/a3,-(sp)
 moveq #0,d1
 move.b 2(a1),d1
 move.b d1,$f1(a0)
 move.b d1,$f4(a0)
 addq.b #1,$f5(a0)
 clr.w (a2)
 lea 2(a2),a3
 moveq #4,d2
.loop:
 move.w #$fff0,(a3)+
 move.b d1,(a3)+
 move.b $f5(a0),(a3)+
 addq.w #1,(a2)
 subq.w #1,d2
 bmi.s .published
 lsr.b #1,d1
 bra.s .loop
.published:
 ; Fourth LSR leaves original bit3 in C; STA/LDA do not alter C.
 move.b 2(a1),d4
 lsr.b #3,d4
 andi.b #1,d4
 clr.b $f5(a0)
 moveq #0,d1
 move.b 6(a1),d1
 addq.b #1,d1
 moveq #0,d3
 move.b $100(a0,d1.w),d3
 addq.b #1,d1
 moveq #0,d2
 move.b $100(a0,d1.w),d2
 lsl.w #8,d2
 or.w d3,d2
 addq.w #1,d2
 move.w d2,(a1)
 move.b d1,6(a1)
 clr.b 2(a1)
 andi.b #$7c,5(a1)
 ori.b #2,d4
 or.b d4,5(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d4/a3
 rts
.invalid:
 moveq #-1,d0
 rts
