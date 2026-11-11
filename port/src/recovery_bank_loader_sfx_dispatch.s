; Ordinary live command entry, preserving existing special-command decoders.
recovery_bank_loader_sfx_dispatch:
 cmpi.w #$8003,(a1)
 bne.w recovery_bank_loader_queue5_dispatch
 cmpi.b #3,3(a4)
 bne.w recovery_bank_loader_queue5_dispatch
 cmpi.b #$f0,2(a1)
 bhs.w recovery_bank_loader_queue5_dispatch
 cmpi.b #$00,2(a1)
 beq.w recovery_bank_loader_queue5_dispatch
 cmpi.b #$07,2(a1)
 beq.w recovery_bank_loader_queue5_dispatch
 cmpi.b #$0e,2(a1)
 beq.w recovery_bank_loader_queue5_dispatch
 cmpi.b #$27,2(a1)
 beq.w recovery_bank_loader_queue5_dispatch
 movem.l d1-d7/a2-a6,-(sp)
 tst.l d2
 bne.s .invalid
 cmpi.w #$d501,10(a4)
 bne.s .invalid
 tst.w 4(a4)
 bne.s .invalid
 cmpi.b #$1e,(a4)
 bne.s .invalid
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.s .invalid
 movea.l a5,a3
 adda.l #49152,a3
 lea recovery_bank_loader_sfx_entry(pc),a6
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
 move.w #139,6(a4)
 move.w #1926,8(a4)
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
