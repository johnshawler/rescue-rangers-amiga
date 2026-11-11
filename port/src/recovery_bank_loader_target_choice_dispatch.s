; Fixed F328 targeting, preserving real mapper bank and original return frame.
recovery_bank_loader_target_choice_dispatch:
 cmpi.w #$f328,(a1)
 bne.w recovery_bank_loader_video5_dispatch
 movem.l d1-d7/a2-a6,-(sp)
 tst.l d2
 bne.s .invalid
 cmpi.w #$d501,10(a4)
 bne.s .invalid
 tst.w 4(a4)
 bne.s .invalid
 cmpi.b #$1e,(a4)
 bne.s .invalid
 cmpi.b #8,3(a4)
 bhs.s .invalid
 tst.b $91(a0)
 bne.s .invalid
 cmpi.b #2,$80(a0)
 bne.s .invalid
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.s .invalid
 lea recovery_bank_loader_target_choice_region(pc),a6
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
 move.w #152,6(a4)
 move.w #2,8(a4)
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
