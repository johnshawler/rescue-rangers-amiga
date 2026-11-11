; Additive first-stage prefix and bank-aware fixed-bank interrupt machinery.
; IDs110 stage pointers70,111 players0,112 fade entry0,113 fade continue0,
; 114 scheduler74,115 fixed game region60002. Existing33/41/42/70/79/98 reused.
; Mapper input is actual live A, never synthetic F1/runtime; nonzeroF6 rejects.
recovery_bank_loader_stage_dispatch:
 cmpi.w #$c6b5,(a1)
 beq.w .stage_init
 cmpi.w #$c6bd,(a1)
 beq.w .players
 cmpi.w #$c700,(a1)
 beq.w .fade_entry
 cmpi.w #$c115,(a1)
 beq.w .fixed
 cmpi.w #$c14e,(a1)
 beq.w .fixed
 cmpi.w #$c158,(a1)
 beq.w .fixed
 cmpi.w #$c24a,(a1)
 beq.w .fixed
 cmpi.w #$e099,(a1)
 beq.w .fixed
 cmpi.w #$ff53,(a1)
 beq.w .restore
 cmpi.w #$c0f9,(a1)
 bne.s .bank
 cmpi.b #4,$f1(a0)
 beq.w .rti
 tst.b $f1(a0)
 beq.w .rti
.bank:
 cmpi.b #4,3(a4)
 beq.s .stage_bank
 tst.b 3(a4)
 bne.w recovery_bank_loader_dialogue_dispatch
.stage_bank:
 cmpi.w #$ff04,(a1)
 beq.w .yield
 cmpi.w #$c2a5,(a1)
 beq.w .yield
 cmpi.w #$c2a8,(a1)
 beq.w .fade_continue
 cmpi.w #$fe8d,(a1)
 beq.w .scheduler
 cmpi.w #$c0bf,(a1)
 beq.w .queue
 bra.w recovery_bank_loader_dialogue_dispatch
.stage_init:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #110,d6
 moveq #70,d7
 movea.l a5,a3
 adda.l #$10193,a3
 lea recovery_bank_loader_stage_init(pc),a6
 bra.w .task
.players:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #111,d6
 lea recovery_gameplay_player_init(pc),a6
 bra.s .scratch_task
.fade_entry:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #112,d6
 lea recovery_gameplay_fade_entry(pc),a6
 bra.s .scratch_task
.fade_continue:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #113,d6
 lea recovery_startup_fade_continue(pc),a6
.scratch_task:
 moveq #0,d7
 bra.w .task
.fixed:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #115,d6
 move.w #60002,d7
 lea recovery_bank_loader_stage_fixed(pc),a6
 bra.w .task
.restore:
 movem.l d1-d7/a2-a6,-(sp)
 cmpi.b #8,2(a1)
 bhs.w .invalid
 moveq #79,d6
 moveq #22,d7
 lea recovery_bank_loader_restore(pc),a6
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
 move.b $100(a0,d3.w),d4
 addq.b #1,d3
 cmpi.b #$c2,$100(a0,d3.w)
 bne.s .enclosing
 cmpi.b #$a7,d4
 bne.w .invalid
 bra.s .resume_stage
.enclosing:
 cmpi.b #$e0,$100(a0,d3.w)
 bne.w .invalid
 cmpi.b #$98,d4
 bne.w .invalid
.resume_stage:
 moveq #114,d6
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
 tst.l d2
 beq.w .wait
 moveq #98,d6
 move.w #$ffff,d7
 lea recovery_bank_loader_dialogue_nmi(pc),a6
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
 bne.s .pending
 moveq #41,d6
 moveq #22,d7
 lea recovery_music_empty_queue_entry(pc),a6
 bra.w .invoke
.pending:
 moveq #70,d6
 moveq #22,d7
 lea recovery_nmi_audio_entry(pc),a6
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
 cmpi.b #8,3(a4)
 bhs.s .common_done
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
 cmpi.w #70,d6
 beq.s .mapper
 cmpi.w #98,d6
 beq.s .mapper
 cmpi.w #110,d6
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
 cmpi.w #110,d6
 bne.s .mapper_address
 cmpi.w #$fff0,d3
 bne.s .next
.mapper_address:
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
