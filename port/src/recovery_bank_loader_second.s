; Bank2 9034 -> 8000, genuine second loader JSR with X=8.
; RAM/context ABI, no external journal or resources. All raw P supported.
recovery_bank_loader_second:
 cmpi.w #$9034,(a1)
 bne.s .invalid
 movem.l d1,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 move.b #$90,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$38,$100(a0,d1.w)
 subq.b #1,d1
 move.b d1,6(a1)
 move.b #8,3(a1)
 andi.b #$7d,5(a1)
 move.w #$8000,(a1)
 moveq #1,d0
 movem.l (sp)+,d1
 rts
.invalid:
 moveq #-1,d0
 rts
