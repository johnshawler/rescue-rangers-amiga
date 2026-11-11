; Additive state-selected menu/character adapter. Frozen startup remains unchanged.
; Startup ABI, but journal134638, disjoint runtime and resources, native stack1KiB.
; Diagnostic size FFFF means134638 only for helper48. No diagnostic selects code.
recovery_state_dispatch_menu:
        cmpi.w #$83a0,(a1)
        bne.s .not_music
        cmpi.b #$0e,2(a1)
        beq.w .enter
        cmpi.b #1,2(a1)
        beq.w .enter
        cmpi.b #$12,2(a1)
        beq.w .enter
        cmpi.b #$13,2(a1)
        beq.w .enter
        cmpi.b #$0f,2(a1)
        beq.w .enter
.not_music:
        cmpi.w #$fe8d,(a1)
        bne.s .pcs
        cmpi.b #2,3(a4)
        bne.w recovery_state_dispatch_startup
        cmpi.b #4,$80(a0)
        beq.w .resume_check
        tst.b $19(a0)
        bne.w .enter
        bra.w recovery_state_dispatch_startup
.pcs:
        cmpi.w #$c5d1,(a1)
        beq.w .enter
        cmpi.w #$a025,(a1)
        beq.w .enter
        cmpi.w #$a000,(a1)
        beq.w .enter
        cmpi.w #$a0bb,(a1)
        beq.w .enter
        cmpi.w #$a05c,(a1)
        beq.w .enter
        cmpi.w #$a06c,(a1)
        beq.w .enter
        cmpi.w #$a089,(a1)
        beq.w .enter
        bra.w recovery_state_dispatch_startup
.resume_check:
        movem.l d3-d4,-(sp)
        moveq #0,d3
        move.b $82(a0),d3
        addq.b #3,d3
        move.b $100(a0,d3.w),d4
        addq.b #1,d3
        cmpi.b #$a0,$100(a0,d3.w)
        bne.s .resume_old
        cmpi.b #$24,d4
        beq.s .resume_new
        cmpi.b #$6b,d4
        beq.s .resume_new
        cmpi.b #$88,d4
        beq.s .resume_new
.resume_old:
        movem.l (sp)+,d3-d4
        bra.w recovery_state_dispatch_startup
.resume_new:
        movem.l (sp)+,d3-d4
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
        cmpi.w #$83a0,(a1)
        beq.w .music
        cmpi.b #2,3(a4)
        bne.w .invalid
        cmpi.w #$fe8d,(a1)
        beq.w .scheduler
        tst.l d2
        bne.w .invalid
        tst.b $91(a0)
        bne.w .invalid
        cmpi.b #2,$80(a0)
        bne.w .invalid
        moveq #0,d3
        move.b 3(a4),d3
        lsl.l #7,d3
        lsl.l #7,d3
        lea (a5,d3.l),a3
        cmpi.w #$c5d1,(a1)
        beq.w .tables
        cmpi.w #$a05c,(a1)
        beq.w .setup
        cmpi.w #$a025,(a1)
        beq.w .countdown
        cmpi.w #$a000,(a1)
        beq.w .menu
        cmpi.w #$a0bb,(a1)
        beq.w .exit
        moveq #49,d6
        lea recovery_character_selection_dispatch(pc),a6
        bra.w .scratch
.music:
        tst.l d2
        bne.w .invalid
        cmpi.b #3,3(a4)
        bne.w .invalid
        moveq #0,d3
        move.b 3(a4),d3
        lsl.l #7,d3
        lsl.l #7,d3
        lea (a5,d3.l),a3
        moveq #22,d7
        moveq #51,d6
        lea recovery_music_active_command0e(pc),a6
        cmpi.b #$0e,2(a1)
        beq.w .invoke
        moveq #52,d6
        lea recovery_music_active_command01(pc),a6
        cmpi.b #1,2(a1)
        bne.s .music12
        moveq #10,d7
        bra.w .invoke
.music12:
        moveq #53,d6
        lea recovery_music_active_command12(pc),a6
        cmpi.b #$12,2(a1)
        beq.w .invoke
        moveq #54,d6
        lea recovery_music_active_command13(pc),a6
        cmpi.b #$13,2(a1)
        beq.w .invoke
        moveq #55,d6
        lea recovery_music_active_command0f(pc),a6
        bra.w .invoke
.tables:
        lea 114688(a5),a3
        moveq #43,d6
        move.w #362,d7
        lea recovery_title_engine_tables(pc),a6
        bra.w .invoke
.setup:
        moveq #47,d6
        moveq #106,d7
        lea recovery_character_menu_setup(pc),a6
        bra.w .invoke
.countdown:
        moveq #44,d6
        lea recovery_title_menu_countdown(pc),a6
        bra.w .scratch
.menu:
        moveq #45,d6
        lea recovery_title_menu_dispatch(pc),a6
        bra.w .scratch
.exit:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #1,d3
        cmpi.b #$f7,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$c5,$100(a0,d3.w)
        bne.w .invalid
        moveq #46,d6
        lea recovery_title_menu_exit(pc),a6
        bra.w .scratch
.scheduler:
        cmpi.b #4,$80(a0)
        bne.s .nmi
        tst.l d2
        bne.w .invalid
        moveq #50,d6
        moveq #74,d7
        lea recovery_general_task_scheduler(pc),a6
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
        or.b $1c(a0),d3
        or.b $1d(a0),d3
        bne.w .invalid
        tst.l d2
        beq.w .wait
        moveq #48,d6
        moveq #-1,d7
        lea recovery_queued_video_nmi_prefix(pc),a6
        bra.s .invoke
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
.invoke:
        jsr (a6)
        cmpi.l #1,d0
        bne.w .done
        move.w d6,6(a4)
        move.w d7,8(a4)
        cmpi.w #48,d6
        bne.w .done
; Consume actual published mapper records in order. Count.w is unsigned.
; Test zero before decrement; counts above $8000 must still reach DBRA.
        moveq #0,d7
        move.w (a2),d7
        tst.w d7
        beq.s .done
        subq.w #1,d7
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
