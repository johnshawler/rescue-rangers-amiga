; Additive state-selected cursor/SFX composition. Frozen menu ABI and journal134638.
; Uses only live PC/RAM/mapper. No trial helper calls, schedules or oracle state.
; New helpers accept raw P/SP as qualified; frozen fallback retains its guards.
; All buffers disjoint and exclusively owned. Native scratch stack >= 1KiB.
recovery_state_menu_sfx:
 cmpi.w #$c0bf,(a1)
 bne.s .not_pending
 cmpi.b #2,3(a4)
 bne.s .not_pending
 movem.l d3,-(sp)
 moveq #0,d3
 move.b $db(a0),d3
 cmpi.b #8,d3
 bcc.s .queue_new
 cmpi.b #$88,$dc(a0,d3.w)
 beq.s .queue_old
.queue_new:
 movem.l (sp)+,d3
 bra.w .select14
.queue_old:
 movem.l (sp)+,d3
.not_pending:
 cmpi.w #$a07b,(a1)
 beq.w .select0
 cmpi.w #$f379,(a1)
 beq.w .select0
 cmpi.w #$a086,(a1)
 beq.w .select0
 cmpi.w #$8003,(a1)
 bne.s .not_queue
 cmpi.b #$27,2(a1)
 beq.w .select1
.not_queue:
 cmpi.w #$810d,(a1)
 beq.w .select2
 cmpi.w #$8151,(a1)
 beq.w .select3
 cmpi.w #$8224,(a1)
 beq.w .select4
 cmpi.w #$8006,(a1)
 beq.w .select5
 cmpi.w #$8298,(a1)
 beq.w .select5
 cmpi.w #$81a3,(a1)
 beq.w .select6
 cmpi.w #$8060,(a1)
 beq.w .select7
 cmpi.w #$807a,(a1)
 beq.w .select7
 cmpi.w #$82b0,(a1)
 beq.w .select8
 cmpi.w #$82c0,(a1)
 beq.w .select8
 cmpi.w #$82dc,(a1)
 beq.w .select9
 cmpi.w #$830b,(a1)
 beq.w .select10
 cmpi.w #$831b,(a1)
 beq.w .select10
 cmpi.w #$8052,(a1)
 beq.w .select11
 cmpi.w #$8235,(a1)
 beq.w .select13
 cmpi.w #$86b2,(a1)
 bne.s .shared
 cmpi.b #4,3(a1)
 bcs.w .select12
.shared:
 cmpi.w #$8085,(a1)
 beq.s .phase
 cmpi.w #$c0f6,(a1)
 bne.w recovery_state_dispatch_menu
 movem.l d3,-(sp)
 move.b $cf(a0),d3
 or.b $d0(a0),d3
 or.b $d1(a0),d3
 movem.l (sp)+,d3
 bne.w .select11
 bra.w recovery_state_dispatch_menu
.phase:
 movem.l d3,-(sp)
 move.b $cf(a0),d3
 or.b $d0(a0),d3
 or.b $d1(a0),d3
 movem.l (sp)+,d3
 bne.w .select7
 bra.w recovery_state_dispatch_menu
.select0:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #56,d6
 move.w #6,d7
 lea recovery_character_cursor_sound_request(pc),a6
 bra.w .enter
.select1:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #57,d6
 move.w #14,d7
 lea recovery_sfx27_table_dispatch(pc),a6
 bra.w .enter
.select2:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #58,d6
 move.w #6,d7
 lea recovery_sfx_header_initialize(pc),a6
 bra.w .enter
.select3:
 cmpi.b #1,$c0(a0)
 bne.w .select15
 movem.l d1-d7/a3-a6,-(sp)
 moveq #59,d6
 move.w #2,d7
 lea recovery_sfx_initialized_tail(pc),a6
 bra.w .enter
.select4:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #60,d6
 move.w #18,d7
 lea recovery_sfx_stream_entry(pc),a6
 bra.w .enter
.select5:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #61,d6
 move.w #6,d7
 lea recovery_sfx_duration_math(pc),a6
 bra.w .enter
.select6:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #62,d6
 move.w #30,d7
 lea recovery_sfx_channel_reconfigure(pc),a6
 bra.w .enter
.select7:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #63,d6
 move.w #30,d7
 lea recovery_sfx_phase_dispatch(pc),a6
 bra.w .enter
.select8:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #64,d6
 move.w #30,d7
 lea recovery_sfx_tick_entry(pc),a6
 bra.w .enter
.select9:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #65,d6
 move.w #78,d7
 lea recovery_sfx_command_mask(pc),a6
 bra.w .enter
.select10:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #66,d6
 move.w #14,d7
 lea recovery_sfx_event_action(pc),a6
 bra.w .enter
.select11:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #67,d6
 move.w #2,d7
 lea recovery_sfx_active_control(pc),a6
 bra.w .enter
.select12:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #68,d6
 move.w #514,d7
 lea recovery_sfx_envelope(pc),a6
 bra.w .enter
.select13:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #69,d6
 move.w #30,d7
 lea recovery_sfx_stream_control(pc),a6
 bra.w .enter
.select15:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #71,d6
 moveq #2,d7
 lea recovery_state_menu_sfx_tail(pc),a6
 bra.w .enter
.select14:
 movem.l d1-d7/a3-a6,-(sp)
 moveq #70,d6
 moveq #22,d7
 lea recovery_nmi_audio_entry(pc),a6
 bra.w .enter
.enter:
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 tst.l d2
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 cmpi.w #70,d6
 beq.s .pending_bank
 cmpi.w #56,d6
 beq.s .cursor
 cmpi.b #3,3(a4)
 bne.w .invalid
 bra.s .bank
.cursor:
 cmpi.b #2,3(a4)
 bne.w .invalid
 tst.b $91(a0)
 bne.w .invalid
 cmpi.b #2,$80(a0)
 bne.w .invalid
 bra.s .bank
.pending_bank:
 cmpi.b #2,3(a4)
 bne.w .invalid
.bank:
 moveq #0,d3
 move.b 3(a4),d3
 lsl.l #7,d3
 lsl.l #7,d3
 lea (a5,d3.l),a3
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
 move.w d6,6(a4)
 move.w d7,8(a4)
 cmpi.w #70,d6
 bne.s .done
 ; Replay the actual five serial writes, using live latch/register state.
 move.w (a2),d7
 beq.s .done
 subq.w #1,d7
 lea 2(a2),a3
.mapper:
 move.w (a3)+,d3
 moveq #0,d4
 move.b (a3)+,d4
 addq.l #1,a3
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
 dbra d7,.mapper
.done:
 movem.l (sp)+,d1-d7/a3-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
