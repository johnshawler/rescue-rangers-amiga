; Additive task-zero saved continuation to C2A8. Palette/active ABI unchanged.
; Selection depends on original PC/task RAM/saved frame, not diagnostics.
; Non-C2A8 saved frames retain the frozen dispatcher's existing behavior.
recovery_state_dispatch_scheduler:
        cmpi.w #$c0bf,(a1)
        bne.s .not_queue
        movem.l d3,-(sp)
        moveq #0,d3
        move.b $db(a0),d3
        cmpi.b #8,d3
        bcc.s .old_queue
        cmpi.b #$88,$dc(a0,d3.w)
        bne.s .old_queue
        movem.l (sp)+,d3
        bra.w .audio
.old_queue:
        movem.l (sp)+,d3
.not_queue:
        cmpi.w #$c0f6,(a1)
        beq.w .audio
        cmpi.w #$8085,(a1)
        beq.w .audio
        cmpi.w #$8374,(a1)
        beq.w .audio
        cmpi.w #$837f,(a1)
        beq.w .audio
        cmpi.w #$86b2,(a1)
        beq.w .audio
        cmpi.w #$c2a8,(a1)
        beq.w .continuation
        cmpi.w #$c2a5,(a1)
        beq.w .continuation
        cmpi.w #$fe8d,(a1)
        bne.w recovery_state_dispatch_active
        cmpi.b #4,$80(a0)
        bne.w recovery_state_dispatch_active
        movem.l d1-d7/a3-a6,-(sp)
        moveq #0,d3
        move.b $82(a0),d3
        addq.b #3,d3
        cmpi.b #$a7,$100(a0,d3.w)
        bne.w .delegate
        addq.b #1,d3
        cmpi.b #$c2,$100(a0,d3.w)
        bne.w .delegate
        cmpi.w #$d501,10(a4)
        bne.w .invalid
        tst.w 4(a4)
        bne.w .invalid
        tst.l d2
        bne.w .invalid
        cmpi.b #$1e,(a4)
        bne.w .invalid
        cmpi.b #6,3(a4)
        bne.w .invalid
        move.b 5(a1),d3
        andi.b #$30,d3
        cmpi.b #$20,d3
        bne.w .invalid
        jsr recovery_general_task_scheduler
        move.w #21,6(a4)
        move.w #74,8(a4)
        movem.l (sp)+,d1-d7/a3-a6
        rts
.delegate:
        movem.l (sp)+,d1-d7/a3-a6
        bra.w recovery_state_dispatch_active
.invalid:
        moveq #-1,d0
        movem.l (sp)+,d1-d7/a3-a6
        rts

; RAM-only helper journals are private scratch. Their RAM writes are already
; original effects; no hardware/resource journal records are published.
.continuation:
        movem.l d1-d7/a2-a6,-(sp)
        cmpi.w #$d501,10(a4)
        bne.w .bad_continue
        tst.w 4(a4)
        bne.w .bad_continue
        tst.l d2
        bne.w .bad_continue
        cmpi.b #$1e,(a4)
        bne.w .bad_continue
        cmpi.b #6,3(a4)
        bne.w .bad_continue
        move.b 5(a1),d3
        andi.b #$30,d3
        cmpi.b #$20,d3
        bne.w .bad_continue
        tst.b $91(a0)
        bne.w .bad_continue
        cmpi.b #2,$80(a0)
        bne.w .bad_continue
        cmpi.w #$c2a5,(a1)
        beq.w .yield
; Bound fade continuation to its next delay, not an arbitrary live RTS target.
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #1,d3
        cmpi.b #1,$100(a0,d3.w)
        bne.w .fade
        move.b $0f(a0),d3
        add.b $0d(a0),d3
        bmi.w .bad_continue
        cmpi.b #$50,d3
        beq.w .bad_continue
.fade:
        suba.w #272,sp
        movea.l sp,a2
        jsr recovery_startup_fade_continue
        adda.w #272,sp
        move.w #22,6(a4)
        bra.s .continued
.yield:
        suba.w #272,sp
        movea.l sp,a2
        jsr recovery_gameplay_frame_yield
        adda.w #272,sp
        move.w #23,6(a4)
.continued:
        clr.w 8(a4)
        moveq #1,d0
        movem.l (sp)+,d1-d7/a2-a6
        rts
.bad_continue:
        moveq #-1,d0
        movem.l (sp)+,d1-d7/a2-a6
        rts

.audio:
        movem.l d1-d7/a3-a6,-(sp)
        cmpi.w #$d501,10(a4)
        bne.w .invalid
        tst.w 4(a4)
        bne.w .invalid
        tst.l d2
        bne.w .invalid
        cmpi.b #$1e,(a4)
        bne.w .invalid
        cmpi.w #$c0bf,(a1)
        beq.w .empty_queue
        cmpi.b #3,3(a4)
        bne.w .invalid
        moveq #0,d3
        move.b 3(a4),d3
        andi.l #7,d3
        lsl.l #7,d3
        lsl.l #7,d3
        lea (a5,d3.l),a3
        cmpi.w #$8374,(a1)
        beq.w .prepare
        cmpi.w #$86b2,(a1)
        beq.w .envelope
        cmpi.w #$837f,(a1)
        beq.w .progress
        cmpi.w #$8085,(a1)
        bne.w .control
; Admit only genuine outer tick or bounded phase-wrapper frames.
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #2,d3
        tst.b $100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$f8,$100(a0,d3.w)
        bne.s .phase_frame
        addq.b #1,d3
        cmpi.b #$c0,$100(a0,d3.w)
        bne.w .invalid
        bra.s .control
.phase_frame:
        cmpi.b #$51,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$80,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$f8,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$c0,$100(a0,d3.w)
        bne.w .invalid
.control:
        moveq #25,d6
        moveq #0,d7
        lea recovery_music_active_control(pc),a6
        bra.w .audio_invoke
.prepare:
        moveq #26,d6
        moveq #10,d7
        lea recovery_music_duration_prepare(pc),a6
        bra.w .audio_invoke
.envelope:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #1,d3
        cmpi.b #$7e,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$83,$100(a0,d3.w)
        bne.w .invalid
        moveq #27,d6
        move.w #514,d7
        lea recovery_music_active_envelope(pc),a6
        bra.w .audio_invoke
.progress:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #1,d3
        cmpi.b #$84,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$80,$100(a0,d3.w)
        bne.w .invalid
        moveq #28,d6
        moveq #0,d7
        lea recovery_music_duration_progress(pc),a6
        bra.w .audio_invoke
.empty_queue:
        cmpi.b #6,3(a4)
        bne.w .invalid
        move.b 5(a1),d3
        andi.b #$30,d3
        cmpi.b #$20,d3
        bne.w .invalid
        moveq #24,d6
        moveq #22,d7
        lea recovery_music_empty_queue_entry(pc),a6
.audio_invoke:
        jsr (a6)
        cmpi.l #1,d0
        bne.w .audio_done
        move.w d6,6(a4)
        move.w d7,8(a4)
        cmpi.w #24,d6
        bne.w .audio_done
; Consume this helper's real five serial writes in their published order.
        moveq #0,d7
        move.w (a2),d7
        subq.w #1,d7
        lea 2(a2),a3
.serial_record:
        moveq #0,d3
        move.w (a3)+,d3
        moveq #0,d4
        move.b (a3)+,d4
        addq.l #1,a3
        btst #7,d4
        beq.s .serial_bit
        clr.b 4(a4)
        clr.b 5(a4)
        ori.b #12,(a4)
        bra.s .serial_next
.serial_bit:
        andi.l #1,d4
        moveq #0,d5
        move.b 5(a4),d5
        lsl.b d5,d4
        or.b d4,4(a4)
        addq.b #1,5(a4)
        cmpi.b #5,5(a4)
        bne.s .serial_next
        lsr.w #8,d3
        lsr.w #5,d3
        andi.w #3,d3
        move.b 4(a4),(a4,d3.w)
        clr.b 4(a4)
        clr.b 5(a4)
.serial_next:
        dbra d7,.serial_record
.audio_done:
        movem.l (sp)+,d1-d7/a3-a6
        rts
