; Additive static main-frame dispatch. ID136 resource journal60002.
recovery_bank_loader_carry_dispatch:
 cmpi.w #$d3e7,(a1)
 beq.w .frame
 cmpi.w #$d40b,(a1)
 beq.w .frame
 cmpi.w #$d435,(a1)
 beq.w .frame
 cmpi.w #$d460,(a1)
 beq.w .frame
 bra.w recovery_bank_loader_collision_dispatch
.frame:
 movem.l d1-d7/a2-a6,-(sp)
 tst.l d2
 bne.w .invalid
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 cmpi.b #8,3(a4)
 bhs.w .invalid
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.w .invalid
 tst.b $91(a0)
 bne.w .invalid
 cmpi.b #2,$80(a0)
 bne.w .invalid
 lea recovery_bank_loader_carry_region(pc),a6
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
 move.w #136,6(a4)
 move.w #60002,8(a4)
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
