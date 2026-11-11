; Add frozen map100 to the live stage composition; preserve genuine mapper exits.
; Same long-journal/runtime ABI; >=4096 native scratch recommended.
recovery_bank_loader_map_dispatch:
 cmpi.w #$e179,(a1)
 beq.w .enter
 cmpi.w #$e17c,(a1)
 beq.w .enter
 cmpi.w #$e1d3,(a1)
 beq.w .enter
 cmpi.w #$e1e4,(a1)
 beq.w .enter
 cmpi.w #$e1e7,(a1)
 beq.w .enter
 cmpi.w #$e1ea,(a1)
 beq.w .enter
 cmpi.w #$dbec,(a1)
 beq.w .enter
 cmpi.w #$dc5c,(a1)
 beq.w .enter
 cmpi.w #$dc5f,(a1)
 beq.w .enter
 cmpi.w #$df97,(a1)
 beq.w .enter
 cmpi.w #$e028,(a1)
 beq.w .enter
 bra.w recovery_bank_loader_stage_dispatch
.enter:
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
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.s .invalid
 tst.b $91(a0)
 bne.s .invalid
 cmpi.b #2,$80(a0)
 bne.s .invalid
 lea recovery_stage_map_region(pc),a6
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
 move.w #100,6(a4)
 move.w #60002,8(a4)
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
