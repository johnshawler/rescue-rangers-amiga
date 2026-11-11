; Additive bank2 dialogue and real interstitial return through stage entryC6B5.
; IDs96 dialogue60002,97 scheduler74,98 combined-queue134638 sentinelFFFF,
; 99 caller/return60002. >=4096 native stack recommended for copied preflight.
recovery_bank_loader_dialogue_dispatch:
 cmpi.b #2,3(a4)
 bne.w recovery_bank_loader_object_dispatch
 cmpi.w #$911c,(a1)
 beq.w .bridge
 cmpi.w #$911f,(a1)
 beq.w .bridge
 cmpi.w #$c60a,(a1)
 beq.w .bridge
 cmpi.w #$92ac,(a1)
 beq.w .dialogue
 cmpi.w #$9475,(a1)
 beq.w .dialogue
 cmpi.w #$9478,(a1)
 beq.w .dialogue
 cmpi.w #$947b,(a1)
 beq.w .dialogue
 cmpi.w #$947e,(a1)
 beq.w .dialogue
 cmpi.w #$fe8d,(a1)
 bne.w recovery_bank_loader_object_dispatch
 cmpi.b #4,$80(a0)
 bne.s .queue_check
 movem.l d3,-(sp)
 moveq #0,d3
 move.b $82(a0),d3
 addq.b #4,d3
 cmpi.b #$94,$100(a0,d3.w)
 bne.s .delegate
 subq.b #1,d3
 cmpi.b #$77,$100(a0,d3.w)
 beq.s .resume
 cmpi.b #$7a,$100(a0,d3.w)
 beq.s .resume
 cmpi.b #$7d,$100(a0,d3.w)
 bne.s .delegate
.resume:
 movem.l (sp)+,d3
 movem.l d1-d7/a2-a6,-(sp)
 move.l d0,d5
 bsr.w .common
 tst.l d0
 bmi.w .done
 tst.l d2
 bne.w .invalid
 move.l d5,d0
 moveq #97,d6
 moveq #74,d7
 lea recovery_general_task_scheduler(pc),a6
 bra.w .invoke
.delegate:
 movem.l (sp)+,d3
 bra.w recovery_bank_loader_object_dispatch
.queue_check:
 move.b $1c(a0),d0
 or.b $1d(a0),d0
 beq.w recovery_bank_loader_object_dispatch
 movem.l d1-d7/a2-a6,-(sp)
 bsr.w .common
 tst.l d0
 bmi.w .done
 cmpi.b #1,$80(a0)
 bne.w .invalid
 cmpi.l #1,d2
 bhi.w .invalid
 btst #7,$ff(a0)
 beq.w .invalid
 move.b $f0(a0),d3
 or.b $9a(a0),d3
 bne.w .invalid
 tst.l d2
 beq.w .wait
 moveq #98,d6
 move.w #$ffff,d7
 lea recovery_bank_loader_dialogue_nmi(pc),a6
 bra.w .invoke
.bridge:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #99,d6
 lea recovery_bank_loader_dialogue_bridge(pc),a6
 bra.s .task
.dialogue:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #96,d6
 lea recovery_bank_loader_dialogue_region(pc),a6
.task:
 move.w #60002,d7
 bsr.s .common
 tst.l d0
 bmi.w .done
 tst.l d2
 bne.w .invalid
 tst.b $91(a0)
 bne.w .invalid
 cmpi.b #2,$80(a0)
 bne.w .invalid
 bra.s .invoke
.common:
 moveq #-1,d0
 cmpi.w #$d501,10(a4)
 bne.s .common_done
 tst.w 4(a4)
 bne.s .common_done
 cmpi.b #$1e,(a4)
 bne.s .common_done
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.s .common_done
 moveq #1,d0
.common_done:
 rts
.invoke:
 jsr (a6)
 cmpi.l #1,d0
 bne.w .done
 move.w d6,6(a4)
 move.w d7,8(a4)
 cmpi.w #98,d6
 bne.w .done
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
