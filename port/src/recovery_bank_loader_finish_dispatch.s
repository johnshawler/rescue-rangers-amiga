; First-stage completion wrappers over reviewed map composition.
;116 bank4 object60002;130 stage0 finish60002;131 fade-in0;132 fade continue0;
;133 actual frame scheduler74. No mapper/audio suppression.
recovery_bank_loader_finish_dispatch:
 cmpi.b #4,3(a4)
 bne.s .fixed
 cmpi.w #$8040,(a1)
 beq.w .objects
 cmpi.w #$8090,(a1)
 beq.w .objects
.fixed:
 cmpi.w #$e106,(a1)
 beq.w .finish
 cmpi.w #$e10c,(a1)
 beq.w .finish
 cmpi.w #$e10f,(a1)
 beq.w .finish
 cmpi.w #$c262,(a1)
 beq.w .finish
 cmpi.w #$c265,(a1)
 beq.w .finish
 cmpi.w #$c703,(a1)
 beq.w .finish
 cmpi.w #$c617,(a1)
 beq.w .finish
 cmpi.w #$c26e,(a1)
 beq.w .fade_in
 cmpi.b #5,3(a4)
 bne.s .scheduler_check
 cmpi.w #$c2a5,(a1)
 beq.w .yield
 cmpi.w #$c2a8,(a1)
 beq.w .fade_continue
.scheduler_check:
 cmpi.w #$fe8d,(a1)
 bne.w recovery_bank_loader_map_dispatch
 cmpi.b #4,$80(a0)
 bne.w recovery_bank_loader_map_dispatch
 movem.l d3-d4,-(sp)
 moveq #0,d3
 move.b $82(a0),d3
 addq.b #3,d3
 move.b $100(a0,d3.w),d4
 addq.b #1,d3
 cmpi.b #4,3(a4)
 bne.s .bank5
 cmpi.b #$e1,$100(a0,d3.w)
 bne.s .delegate
 cmpi.b #$0e,d4
 bne.s .delegate
 bra.s .resume
.bank5:
 cmpi.b #5,3(a4)
 bne.s .delegate
 cmpi.b #$c2,$100(a0,d3.w)
 bne.s .delegate
 cmpi.b #$a7,d4
 bne.s .delegate
.resume:
 movem.l (sp)+,d3-d4
 movem.l d1-d7/a2-a6,-(sp)
 move.l d0,d5
 move.w #133,d6
 moveq #74,d7
 lea recovery_general_task_scheduler(pc),a6
 bra.w .validate
.delegate:
 movem.l (sp)+,d3-d4
 bra.w recovery_bank_loader_map_dispatch
.objects:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #116,d6
 move.w #60002,d7
 lea recovery_stage_object_region(pc),a6
 bra.w .validate
.finish:
 movem.l d1-d7/a2-a6,-(sp)
 move.w #130,d6
 move.w #60002,d7
 lea recovery_bank_loader_stage_finish(pc),a6
 bra.w .validate
.fade_in:
 movem.l d1-d7/a2-a6,-(sp)
 move.w #131,d6
 moveq #0,d7
 lea recovery_bank_loader_stage_fade_in(pc),a6
 bra.s .validate
.fade_continue:
 movem.l d1-d7/a2-a6,-(sp)
 move.w #132,d6
 moveq #0,d7
 lea recovery_startup_fade_continue(pc),a6
 bra.s .validate
.yield:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #33,d6
 moveq #0,d7
 lea recovery_gameplay_frame_yield(pc),a6
.validate:
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 tst.l d2
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 cmpi.b #8,3(a4)
 bhs.w .invalid
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.w .invalid
 cmpi.w #133,d6
 bne.s .task
 move.l d5,d0
 bra.s .invoke
.task:
 tst.b $91(a0)
 bne.w .invalid
 cmpi.b #2,$80(a0)
 bne.w .invalid
 tst.w d7
 bne.s .invoke
 suba.w #512,sp
 movea.l sp,a2
 jsr (a6)
 adda.w #512,sp
 cmpi.l #-1,d0
 beq.s .done
 moveq #1,d0
 bra.s .publish
.invoke:
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
.publish:
 move.w d6,6(a4)
 move.w d7,8(a4)
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
