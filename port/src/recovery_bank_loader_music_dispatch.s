; Genuine stage music command0 at the original NMI queue call frame.
; ID134 journal60002; copied native preflight, no skipped/muted original action.
recovery_bank_loader_music_dispatch:
 cmpi.w #$8003,(a1)
 bne.w recovery_bank_loader_finish_dispatch
 tst.b 2(a1)
 bne.w recovery_bank_loader_finish_dispatch
 cmpi.b #3,3(a4)
 bne.w recovery_bank_loader_finish_dispatch
 movem.l d1-d7/a2-a6,-(sp)
 tst.l d2
 bne.w .invalid
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.w .invalid
 moveq #0,d3
 move.b 6(a1),d3
 addq.b #1,d3
 cmpi.b #$f2,$100(a0,d3.w)
 bne.w .invalid
 addq.b #1,d3
 cmpi.b #$c0,$100(a0,d3.w)
 bne.w .invalid
 lea recovery_bank_loader_stage_music(pc),a6
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
 move.w #134,6(a4)
 move.w #60002,8(a4)
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
