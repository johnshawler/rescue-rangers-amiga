; F3E5 render-enable/yield preparation; F3F1 genuine PLA/bank restore;
; 910C index0B interstitial continuation to original sprite update F392.
; A0 RAM2048,A1 ctx8,A2 journal6 (only F3E5 publishes a PPU event).
; D0=1/-1; all other registers preserved, wrapped original page-one stack.
recovery_bank_loader_fade:
 cmpi.w #$f3e5,(a1)
 beq.s .enable
 cmpi.w #$f3f1,(a1)
 beq.w .restore
 cmpi.w #$910c,(a1)
 bne.w .invalid
 cmpi.b #$0b,$31(a0)
 bne.w .invalid
 movem.l d1,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 move.b #8,$97(a0)
 move.b #$91,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$1b,$100(a0,d1.w)
 subq.b #1,d1
 move.b d1,6(a1)
 move.b #8,2(a1)
 andi.b #$7c,5(a1)
 ori.b #1,5(a1)
 move.w #$f392,(a1)
 bra.w .done
.enable:
 movem.l d1,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 move.b $f1(a0),$100(a0,d1.w)
 subq.b #1,d1
 move.b #$f3,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$ea,$100(a0,d1.w)
 subq.b #1,$f0(a0)
 move.b #$1e,$fe(a0)
 move.w #$2001,2(a2)
 move.b #$1e,4(a2)
 move.b #1,5(a2)
 move.w #1,(a2)
 addq.b #1,d1
 move.b #$f3,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$ed,$100(a0,d1.w)
 subq.b #1,d1
 move.b d1,6(a1)
 move.w #$ff04,(a1)
 move.b #$1e,2(a1)
 andi.b #$7d,5(a1)
 bra.s .done
.restore:
 movem.l d1-d2,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 addq.b #1,d1
 move.b $100(a0,d1.w),d2
 move.b d2,2(a1)
 move.b d1,6(a1)
 andi.b #$7d,5(a1)
 tst.b d2
 bne.s .nonzero
 ori.b #2,5(a1)
.nonzero:
 andi.b #$80,d2
 or.b d2,5(a1)
 move.w #$ff53,(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d2
 rts
.done:
 moveq #1,d0
 movem.l (sp)+,d1
 rts
.invalid:
 moveq #-1,d0
 rts
