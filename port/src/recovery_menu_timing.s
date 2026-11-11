; Minimal measurement runner. Frozen dispatch/device/renderer code is linked unchanged.
; Journal initialized once, then reused: only published records and DMA are consumed.
; No captured fixture, prescribed helper schedule, or live input.
 lea $dff000,a5
 move.w #$7fff,$9a(a5)
 move.w #$7fff,$96(a5)
 move.w #$7fff,$9c(a5)
 move.w #$0200,$100(a5)
 lea report(pc),a6
 lea stack_end(pc),sp
 lea ram(pc),a3
 move.l a3,24(a6)
 lea context(pc),a3
 move.l a3,28(a6)
 lea journal(pc),a3
 move.l a3,32(a6)
 lea runtime(pc),a3
 move.l a3,36(a6)
 lea resource(pc),a3
 move.l a3,40(a6)
 lea stack(pc),a3
 move.l a3,44(a6)
 lea stack_end(pc),a3
 move.l a3,48(a6)
 bsr.l llb_amiga_clock_start
.loop:
 cmpi.l #4096,12(a6)
 bhs.w failed
 lea ram(pc),a0
 lea context(pc),a1
 lea journal(pc),a2
 lea runtime(pc),a4
 lea resource(pc),a5
 moveq #0,d0
 cmpi.w #$a025,(a1)
 bne.s .pad_ready
 lea pad_value(pc),a3
 move.b #16,(a3)
.pad_ready:
 move.b pad_value(pc),d0
 moveq #0,d1
 move.l 20(a6),d2
 bsr.l recovery_state_dispatch_menu
 move.l d0,64(a6)
 cmpi.l #1,d0
 beq.s .advanced
 tst.l d0
 bne.w .terminal
 tst.l 20(a6)
 bne.w failed
 move.l #1,20(a6)
 addq.l #1,16(a6)
 bra.w .loop
.advanced:
 clr.l 20(a6)
 addq.l #1,12(a6)
 moveq #0,d0
 move.w 6(a4),d0
 lea device_ids(pc),a3
 move.b (a3,d0.w),d0
 cmpi.b #$ff,d0
 beq.s .next
 lea journal(pc),a2
 bsr.l startup_consume
.next:
 cmpi.w #$a06c,(a1)
 beq.s .render
 bra.w .loop
.terminal:
 cmpi.l #-1,d0
 bne.s failed
 bra.s failed
.render:
 move.l sp,68(a6)
 clr.l 8(a6)
 bsr.l startup_display
stop:
 bra.s stop
failed:
 move.l d0,8(a6)
 move.l sp,68(a6)
 move.w #$f00,$dff180
 bra.s stop
