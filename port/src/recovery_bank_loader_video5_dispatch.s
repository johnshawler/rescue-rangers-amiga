; Actual bank5/task1 queued video NMI; event0 waits only after admission.
recovery_bank_loader_video5_dispatch:
 cmpi.w #$fe8d,(a1)
 bne.w recovery_bank_loader_scroll_status_dispatch
 cmpi.b #5,3(a4)
 bne.w recovery_bank_loader_scroll_status_dispatch
 cmpi.b #1,$80(a0)
 bne.w recovery_bank_loader_scroll_status_dispatch
 tst.b $19(a0)
 beq.w recovery_bank_loader_scroll_status_dispatch
 movem.l d1-d7/a2-a6,-(sp)
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
 cmpi.l #1,d2
 bhi.w .invalid
 btst #7,$ff(a0)
 beq.w .invalid
 tst.b $f5(a0)
 bne.w .invalid
 tst.b $f6(a0)
 bne.w .invalid
 lea recovery_bank_loader_video5_preflight(pc),a6
 jsr (a6)
 cmpi.l #1,d0
 bne.w .done
 tst.l d2
 beq.w .wait
 lea recovery_bank_loader_dialogue_nmi(pc),a6
 jsr (a6)
 cmpi.l #1,d0
 bne.w .done
 move.w #98,6(a4)
 move.w #$ffff,8(a4)
.mapper:
 moveq #0,d7
 move.w (a2),d7
 subq.w #1,d7
 bmi.s .done
 lea 2(a2),a3
.record:
 moveq #0,d3
 move.w (a3)+,d3
 moveq #0,d4
 move.b (a3)+,d4
 addq.l #1,a3
 cmpi.w #$8000,d3
 bcs.s .next
 btst #7,d4
 beq.s .bit
 clr.w 4(a4)
 ori.b #12,(a4)
 bra.s .next
.bit:
 andi.l #1,d4
 moveq #0,d5
 move.b 5(a4),d5
 lsl.b d5,d4
 or.b d4,4(a4)
 addq.b #1,5(a4)
 cmpi.b #5,5(a4)
 bne.s .next
 lsr.w #8,d3
 lsr.w #5,d3
 andi.w #3,d3
 move.b 4(a4),(a4,d3.w)
 clr.w 4(a4)
.next:
 dbra d7,.record
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.wait:
 moveq #0,d0
 bra.s .done
.invalid:
 moveq #-1,d0
 bra.s .done
