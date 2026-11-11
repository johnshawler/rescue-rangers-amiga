; C5BB -> C5C0 through original FF53 zero-deferred branch.
; A0 RAM2048, A1 context8, A2 journal22. No resource read.
; Caller requires empty MMC1 latch and PRG mode3. Does not service interrupts.
; PC C5BB and F6=0 required; other entries inert. F6 is never changed.
; D0=1 success/-1 unsupported; D1-D7/A0-A6 preserved, CCR scratch.
; Journal count.word then address.word/value.byte/kind.byte (mapper kind=live F5).
recovery_startup_bank_select:
 cmpi.w #$c5bb,(a1)
 bne.s .reject
 tst.b $f6(a0)
 bne.s .reject
 movem.l d1-d3/a4,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 move.b #$c5,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$bf,$100(a0,d1.w)
 move.b #2,$f1(a0)
 move.b #2,$f4(a0)
 addq.b #1,$f5(a0)
 clr.w (a2)
 lea 2(a2),a4
 moveq #2,d2
 moveq #4,d3
.loop:
 move.w #$fff0,(a4)+
 move.b d2,(a4)+
 move.b $f5(a0),(a4)+
 addq.w #1,(a2)
 lsr.b #1,d2
 dbra d3,.loop
 clr.b $f5(a0)
 move.w #$c5c0,(a1)
 clr.b 2(a1)
 andi.b #$7c,5(a1)
 ori.b #2,5(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d3/a4
 rts
.reject:
 moveq #-1,d0
 rts
