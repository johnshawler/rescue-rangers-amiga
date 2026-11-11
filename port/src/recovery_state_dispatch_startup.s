; State-driven startup/title extension. No schedules or CPU interpreter.
; ABI as scheduler, except journal capacity 32770 bytes (disjoint runtime).
recovery_state_dispatch_startup:
        cmpi.w #$83a0,(a1)
        bne.s .noncommand
        cmpi.b #3,2(a1)
        beq.w .enter
        cmpi.b #2,2(a1)
        beq.w .enter
.noncommand:
        cmpi.w #$c2a8,(a1)
        beq.w .enter
        cmpi.w #$c594,(a1)
        beq.w .enter
        cmpi.w #$c597,(a1)
        beq.w .enter
        cmpi.w #$c5bb,(a1)
        beq.w .enter
        cmpi.w #$c5c0,(a1)
        beq.w .enter
        cmpi.w #$c5c5,(a1)
        beq.w .enter
        cmpi.w #$c5cb,(a1)
        beq.w .enter
        cmpi.w #$c5ce,(a1)
        beq.w .enter
        cmpi.w #$ff04,(a1)
        beq.w .enter
        cmpi.b #2,3(a4)
        bne.s .check_scheduler
        cmpi.w #$c2a5,(a1)
        beq.w .enter
        cmpi.w #$fe8d,(a1)
        beq.w .enter
        cmpi.w #$c0bf,(a1)
        beq.w .enter
.check_scheduler:
        cmpi.w #$fe8d,(a1)
        bne.s .check_return
        cmpi.b #4,$80(a0)
        beq.w .enter
.check_return:
        cmpi.w #$c0f9,(a1)
        bne.s .old
        cmpi.b #2,$f1(a0)
        beq.w .enter
.old:
        bra.w recovery_state_dispatch_scheduler
.enter:
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
        cmpi.w #$fe8d,(a1)
        beq.w .scheduler
        tst.l d2
        bne.w .invalid
        cmpi.w #$83a0,(a1)
        beq.w .command
        cmpi.w #$c0f9,(a1)
        beq.w .rti
        cmpi.w #$c0bf,(a1)
        beq.w .queue
        cmpi.b #6,3(a4)
        beq.s .task
        cmpi.b #2,3(a4)
        bne.w .invalid
.task:
        tst.b $91(a0)
        bne.w .invalid
        cmpi.b #2,$80(a0)
        bne.w .invalid
        cmpi.w #$c2a8,(a1)
        beq.w .fade
        cmpi.w #$c2a5,(a1)
        beq.w .yield
        cmpi.w #$ff04,(a1)
        beq.w .yield
        cmpi.w #$c594,(a1)
        beq.w .outer_yield
        cmpi.w #$c597,(a1)
        beq.w .video
        cmpi.w #$c5bb,(a1)
        beq.w .bank
        cmpi.b #2,3(a4)
        bne.w .invalid
        bsr.w .resource_pointer
        cmpi.w #$c5c0,(a1)
        beq.w .load
        cmpi.w #$c5c5,(a1)
        beq.w .title
        cmpi.w #$c5cb,(a1)
        beq.w .title_yield
        cmpi.w #$c5ce,(a1)
        beq.w .title_fade
        bra.w .invalid
.command:
        cmpi.b #3,3(a4)
        bne.w .invalid
        bsr.w .resource_pointer
        moveq #29,d6
        lea recovery_music_active_command03(pc),a6
        cmpi.b #3,2(a1)
        beq.s .command_ready
        moveq #30,d6
        lea recovery_music_active_command02(pc),a6
.command_ready:
        moveq #10,d7
        bra.w .invoke
.scheduler:
        cmpi.b #6,3(a4)
        beq.s .scheduler_bank
        cmpi.b #2,3(a4)
        bne.w .invalid
.scheduler_bank:
        cmpi.b #4,$80(a0)
        bne.w .nmi
        tst.l d2
        bne.w .invalid
        moveq #0,d3
        move.b $82(a0),d3
        addq.b #3,d3
        moveq #0,d4
        move.b $100(a0,d3.w),d4
        addq.b #1,d3
        cmpi.b #$c2,$100(a0,d3.w)
        bne.s .saved_c5
        cmpi.b #$a7,d4
        bne.w .invalid
        bra.s .resume
.saved_c5:
        cmpi.b #$c5,$100(a0,d3.w)
        bne.w .delegate
        cmpi.b #6,3(a4)
        bne.s .saved_title
        cmpi.b #$96,d4
        bne.w .delegate
        bra.s .resume
.saved_title:
        cmpi.b #$cd,d4
        bne.w .invalid
.resume:
        moveq #31,d6
        moveq #74,d7
        lea recovery_general_task_scheduler(pc),a6
        bra.w .invoke
.nmi:
        cmpi.b #2,3(a4)
        bne.w .invalid
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
        cmpi.b #2,3(a4)
        bne.w .invalid
        moveq #0,d3
        move.b $db(a0),d3
        cmpi.b #8,d3
        bcc.w .invalid
        cmpi.b #$88,$dc(a0,d3.w)
        bne.w .invalid
        moveq #41,d6
        moveq #22,d7
        lea recovery_music_empty_queue_entry(pc),a6
        bra.w .invoke
.rti:
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
.fade:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #1,d3
        cmpi.b #1,$100(a0,d3.w)
        bne.s .fade_ready
        move.b $0f(a0),d4
        add.b $0d(a0),d4
        bmi.s .fade_return
        cmpi.b #$50,d4
        bne.s .fade_ready
.fade_return:
        addq.b #1,d3
        moveq #-109,d4
        cmpi.b #6,3(a4)
        beq.s .fade_frame
        move.b #$d0,d4
.fade_frame:
        cmp.b $100(a0,d3.w),d4
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$c5,$100(a0,d3.w)
        bne.w .invalid
.fade_ready:
        moveq #32,d6
        lea recovery_startup_fade_continue(pc),a6
        bra.w .scratch
.outer_yield:
        cmpi.b #6,3(a4)
        bne.w .invalid
        bra.s .fade_ready
.yield:
        moveq #33,d6
        lea recovery_gameplay_frame_yield(pc),a6
        bra.w .scratch
.video:
        cmpi.b #6,3(a4)
        bne.w .invalid
        moveq #34,d6
        move.w #4382,d7
        lea recovery_startup_video_clear(pc),a6
        bra.w .invoke
.bank:
        cmpi.b #6,3(a4)
        bne.w .invalid
        tst.b $f5(a0)
        bne.w .invalid
        moveq #35,d6
        moveq #22,d7
        lea recovery_startup_bank_select(pc),a6
        bra.w .invoke
.load:
        moveq #36,d6
        move.l #32770,d7
        lea recovery_startup_resource_load(pc),a6
        bra.w .invoke
.title:
        moveq #37,d6
        move.w #566,d7
        lea recovery_startup_title_setup(pc),a6
        bra.w .invoke
.title_yield:
        moveq #38,d6
        lea recovery_title_yield_entry(pc),a6
        bra.w .scratch
.title_fade:
        moveq #39,d6
        lea recovery_title_fade_entry(pc),a6
.scratch:
        suba.w #512,sp
        movea.l sp,a2
        jsr (a6)
        adda.w #512,sp
        cmpi.l #-1,d0
        beq.w .done
        moveq #1,d0
        move.w d6,6(a4)
        clr.w 8(a4)
        bra.w .done
.resource_pointer:
        moveq #0,d3
        move.b 3(a4),d3
        andi.l #7,d3
        lsl.l #7,d3
        lsl.l #7,d3
        lea (a5,d3.l),a3
        rts
.invoke:
        jsr (a6)
        cmpi.l #1,d0
        bne.w .done
        move.w d6,6(a4)
        move.w d7,8(a4)
        cmpi.w #35,d6
        beq.s .mapper
        cmpi.w #40,d6
        bcc.s .mapper
        bra.w .done
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

.delegate:
        movem.l (sp)+,d1-d7/a2-a6
        bra.w recovery_state_dispatch_scheduler
