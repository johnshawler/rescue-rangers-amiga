; Additive 68020 state dispatcher, bounded reset/first-NMI prefix.
; A0 RAM[2048], A1 canonical context[8], A2 journal[8754], A4 runtime[12].
; D0.b/D1.b external pads; D2.l event: 0=advance, 1=logical NMI.
; Runtime bytes: control,CHR0,CHR1,PRG,latch value,latch count;
; then last helper ID.w, last journal size.w, ABI tag.w=$D501.
; Initial mapper obligation: 0C/00/00/03/00/00. Entry FE24/Y=0.
; Caller owns disjoint aligned buffers, exclusive access and valid stack.
; D0=1 advanced; 0 wait for NMI; -1 unsupported/invalid, inert.
; D1-D7/A0-A6 preserved; CCR scratch. No opcode decode, schedule, expected
; state, timing or physical backend. Mapper journals consumed before return.
recovery_state_dispatch_prefix:
        movem.l d1-d7/a3-a6,-(sp)
        cmpi.w #$d501,10(a4)
        bne.w .invalid
        tst.b 4(a4)
        bne.w .invalid
        tst.b 5(a4)
        bne.w .invalid
        cmpi.l #1,d2
        bhi.w .invalid
        move.w (a1),d3
        tst.l d2
        bne.w .nmi
        cmpi.w #$fe24,d3
        beq.w .reset_ram
        cmpi.w #$fe43,d3
        beq.w .reset_mapper
        cmpi.b #$1e,(a4)
        bne.w .invalid
        cmpi.b #3,3(a4)
        beq.w .audio_bank
        cmpi.b #6,3(a4)
        bne.w .invalid
        cmpi.w #$fe67,d3
        beq.w .reset_video
        cmpi.w #$fe7c,d3
        beq.w .reset_dispatch
        cmpi.w #$c574,d3
        beq.w .first_yield
        cmpi.w #$c0bf,d3
        beq.w .audio_entry
        cmpi.w #$c584,d3
        beq.w .setup
        cmpi.w #$fe8d,d3
        bne.w .invalid
        cmpi.b #4,$80(a0)
        beq.w .resume
        cmpi.b #1,$80(a0)
        bne.w .invalid
        tst.b $18(a0)
        bne.w .invalid
        moveq #0,d0
        bra.w .done
.audio_bank:
        cmpi.w #$8003,d3
        beq.w .audio_reset
        cmpi.w #$c0f3,d3
        beq.w .silent
        bra.w .invalid
.nmi:
        cmpi.w #$fe8d,d3
        bne.w .invalid
        cmpi.b #$1e,(a4)
        bne.w .invalid
        cmpi.b #6,3(a4)
        bne.w .invalid
        cmpi.b #1,$80(a0)
        bne.w .invalid
        bra.w .first_nmi
.reset_ram:
        cmpi.l #$0c000003,(a4)
        bne.w .invalid
        moveq #1,d6
        move.w #0,d7
        lea recovery_reset_ram(pc),a6
        bra.w .invoke
.reset_mapper:
        cmpi.l #$0c000003,(a4)
        bne.w .invalid
        moveq #2,d6
        move.w #82,d7
        lea recovery_reset_mapper(pc),a6
        bra.w .invoke
.reset_video:
        moveq #3,d6
        move.w #8754,d7
        lea recovery_reset_video(pc),a6
        bra.w .invoke
.reset_dispatch:
        moveq #4,d6
        move.w #0,d7
        lea recovery_reset_dispatch(pc),a6
        bra.w .invoke
.first_yield:
        moveq #5,d6
        move.w #6,d7
        lea recovery_first_yield(pc),a6
        bra.w .invoke
.first_nmi:
        moveq #6,d6
        move.w #298,d7
        lea recovery_first_nmi_prefix(pc),a6
        bra.w .invoke
.audio_entry:
        moveq #7,d6
        move.w #22,d7
        lea recovery_nmi_audio_entry(pc),a6
        bra.w .invoke
.audio_reset:
        moveq #0,d6
        move.w #30,d7
        lea recovery_audio_reset_command(pc),a6
        bra.w .invoke
.silent:
        moveq #8,d6
        move.w #22,d7
        lea recovery_silent_tick_rti(pc),a6
        bra.w .invoke
.resume:
        moveq #9,d6
        move.w #74,d7
        lea recovery_scheduler_resume(pc),a6
        bra.w .invoke
.setup:
        moveq #10,d6
        move.w #0,d7
        lea recovery_resumed_task_setup(pc),a6
        bra.w .invoke
.invoke:
        jsr (a6)
        cmpi.l #1,d0
        bne.w .done
        move.w d6,6(a4)
        move.w d7,8(a4)
        cmpi.w #2,d6
        beq.s .mapper
        cmpi.w #7,d6
        beq.s .mapper
        cmpi.w #8,d6
        bne.s .done
; Consume real serial writes, never assign an expected next bank.
.mapper:
        moveq #0,d7
        move.w (a2),d7
        subq.w #1,d7
        lea 2(a2),a3
.record:
        moveq #0,d3
        move.w (a3)+,d3
        moveq #0,d4
        move.b (a3)+,d4
        addq.l #1,a3
        btst #7,d4
        beq.s .bit
        clr.b 4(a4)
        clr.b 5(a4)
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
        clr.b 4(a4)
        clr.b 5(a4)
.next:
        dbra d7,.record
.done:
        movem.l (sp)+,d1-d7/a3-a6
        rts
.invalid:
        moveq #-1,d0
        bra.s .done
