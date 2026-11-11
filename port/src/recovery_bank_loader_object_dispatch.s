; Additive bank5 sprite-caller and logical-NMI extension over frozen F392 chain.
; IDs90 object60002,91/92/93/95 RAM-only,94 scheduler74.
; Reuses unchanged IDs33/40/41/42/79 with exact existing effects/metadata.
; No deferred audio or queue bypass: unsupported entries fail explicitly.
recovery_bank_loader_object_dispatch:
 cmpi.w #$f392,(a1)
 beq.w .entry
 cmpi.w #$ff53,(a1)
 beq.w .restore
 cmpi.w #$c0f9,(a1)
 bne.s .bank
 cmpi.b #5,$f1(a0)
 beq.w .rti
.bank:
 cmpi.b #5,3(a4)
 bne.w recovery_bank_loader_dispatch
 cmpi.w #$f39f,(a1)
 beq.w .call
 cmpi.w #$8000,(a1)
 beq.w .object
 cmpi.w #$f3a2,(a1)
 beq.w .yield_setup
 cmpi.w #$ff04,(a1)
 beq.w .yield
 cmpi.w #$fe8d,(a1)
 beq.w .scheduler
 cmpi.w #$c0bf,(a1)
 beq.w .queue
 cmpi.w #$f3a9,(a1)
 beq.w .pop
 bra.w recovery_bank_loader_dispatch
.entry:
 movem.l d1-d7/a2-a6,-(sp)
 cmpi.b #2,3(a4)
 bne.w .invalid
 moveq #91,d6
 bra.w .bridge
.restore:
 ; Preserve the bank2 baseline's deliberately narrow restore qualification.
 cmpi.b #2,3(a4)
 bne.s .restore5
 cmpi.b #5,2(a1)
 bne.w recovery_bank_loader_dispatch
 bra.s .restore_enter
.restore5:
 cmpi.b #5,3(a4)
 bne.w recovery_bank_loader_dispatch
 cmpi.b #2,2(a1)
 bne.w recovery_bank_loader_dispatch
.restore_enter:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #79,d6
 moveq #22,d7
 lea recovery_bank_loader_restore(pc),a6
 bra.w .task
.call:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #92,d6
 bra.w .bridge
.object:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #90,d6
 move.w #60002,d7
 lea recovery_object_region(pc),a6
 bra.w .task
.yield_setup:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #93,d6
 bra.w .bridge
.pop:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #95,d6
.bridge:
 moveq #0,d7
 lea recovery_bank_loader_object_bridge(pc),a6
 bra.w .task
.yield:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #33,d6
 moveq #0,d7
 lea recovery_gameplay_frame_yield(pc),a6
 bra.w .task
.scheduler:
 movem.l d1-d7/a2-a6,-(sp)
 move.l d0,d5
 bsr.w .common
 tst.l d0
 bmi.w .done
 cmpi.b #4,$80(a0)
 bne.w .nmi
 tst.l d2
 bne.w .invalid
 moveq #0,d3
 move.b $82(a0),d3
 addq.b #3,d3
 cmpi.b #$a8,$100(a0,d3.w)
 bne.w .invalid
 addq.b #1,d3
 cmpi.b #$f3,$100(a0,d3.w)
 bne.w .invalid
 moveq #94,d6
 moveq #74,d7
 lea recovery_general_task_scheduler(pc),a6
 move.l d5,d0
 bra.w .invoke
.nmi:
 cmpi.b #1,$80(a0)
 bne.w .invalid
 cmpi.l #1,d2
 bhi.w .invalid
 btst #7,$ff(a0)
 beq.w .invalid
 move.b $f0(a0),d3
 or.b $9a(a0),d3
 or.b $19(a0),d3
 or.b $1c(a0),d3
 or.b $1d(a0),d3
 bne.w .invalid
 tst.l d2
 beq.w .wait
 moveq #40,d6
 move.w #494,d7
 lea recovery_chr_nmi_prefix(pc),a6
 bra.w .invoke
.queue:
 movem.l d1-d7/a2-a6,-(sp)
 bsr.w .common
 tst.l d0
 bmi.w .done
 tst.l d2
 bne.w .invalid
 moveq #0,d3
 move.b $db(a0),d3
 cmpi.b #8,d3
 bhs.w .invalid
 cmpi.b #$88,$dc(a0,d3.w)
 bne.w .invalid
 moveq #41,d6
 moveq #22,d7
 lea recovery_music_empty_queue_entry(pc),a6
 bra.w .invoke
.rti:
 movem.l d1-d7/a2-a6,-(sp)
 bsr.w .common
 tst.l d0
 bmi.w .done
 tst.l d2
 bne.w .invalid
 cmpi.b #3,3(a4)
 bne.w .invalid
 cmpi.b #4,$80(a0)
 bne.w .invalid
 moveq #0,d3
 move.b 6(a1),d3
 addq.b #6,d3
 cmpi.b #$8d,$100(a0,d3.w)
 bne.w .invalid
 addq.b #1,d3
 cmpi.b #$fe,$100(a0,d3.w)
 bne.w .invalid
 moveq #42,d6
 moveq #22,d7
 lea recovery_active_nmi_return(pc),a6
 bra.w .invoke
.task:
 bsr.s .common
 tst.l d0
 bmi.w .done
 tst.l d2
 bne.w .invalid
 tst.b $91(a0)
 bne.w .invalid
 cmpi.b #2,$80(a0)
 bne.w .invalid
 tst.w d7
 bne.w .invoke
 suba.w #512,sp
 movea.l sp,a2
 jsr (a6)
 adda.w #512,sp
 cmpi.l #-1,d0
 beq.w .done
 moveq #1,d0
 bra.s .publish
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
.publish:
 move.w d6,6(a4)
 move.w d7,8(a4)
 cmpi.w #79,d6
 beq.s .mapper
 cmpi.w #40,d6
 blo.s .done
 cmpi.w #42,d6
 bhi.s .done
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
