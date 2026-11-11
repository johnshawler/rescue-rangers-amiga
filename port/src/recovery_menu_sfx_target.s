; Bounded scripted menu/SFX runner. Frozen dispatch/device/renderer code is linked unchanged.
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
 lea capture(pc),a3
 move.l a3,72(a6)
 bsr.l llb_amiga_clock_start
.loop:
 cmpi.l #12000,12(a6)
 bhs.w failed
 lea ram(pc),a0
 lea context(pc),a1
 lea journal(pc),a2
 lea runtime(pc),a4
 lea resource(pc),a5
 cmpi.w #$a025,(a1)
 bne.s .not_title
 move.l #1,80(a6)
.not_title:
 cmpi.w #$a06c,(a1)
 bne.s .not_character
 addq.l #1,84(a6)
.not_character:
 moveq #0,d0
 tst.l 80(a6)
 beq.s .pad_ready
 moveq #16,d0
.pad_ready:
 move.l 84(a6),d3
 beq.s .pad_done
 cmpi.l #127,d3
 bhi.w failed
 lea input_samples(pc),a3
 move.b (a3,d3.w),d0
.pad_done:
 lea pad_value(pc),a3
 move.b d0,(a3)
 moveq #0,d1
 move.l 20(a6),d2
 bsr.l recovery_state_menu_sfx
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
 bsr.w capture_journal
 moveq #0,d0
 move.w 6(a4),d0
 lea device_ids(pc),a3
 move.b (a3,d0.w),d0
 cmpi.b #$ff,d0
 beq.s .next
 lea journal(pc),a2
 bsr.l startup_consume
.next:
 cmpi.w #$c5f8,(a1)
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

; Copy only counted records and defined DMA, never stale padding.
; Header per completion: helper word, count word, records, optional DMA256.
; Runtime size zero forbids reading the stale journal header. FFFF is a sentinel.
capture_journal:
 movem.l d0-d7/a0-a5,-(sp)
 moveq #0,d0
 move.w 6(a4),d0
 cmpi.w #71,d0
 bhi.w .bad
 moveq #0,d1
 tst.w 8(a4)
 beq.s .no_records
 move.w (a2),d1
 cmpi.l #33595,d1
 bhi.w .bad
.no_records:
 move.l d1,d2
 lsl.l #2,d2
 addq.l #4,d2
 moveq #0,d3
 cmpi.w #6,d0
 bne.s .dma11
 moveq #42,d3
.dma11:
 cmpi.w #11,d0
 bne.s .dma40
 move.l #198,d3
.dma40:
 cmpi.w #40,d0
 bne.s .dma48
 move.l #238,d3
.dma48:
 cmpi.w #48,d0
 bne.s .length
 cmpi.w #$ffff,8(a4)
 bne.w .bad
 move.l #134382,d3
.length:
 tst.l d3
 beq.s .capacity
 addi.l #256,d2
.capacity:
 move.l 76(a6),d4
 add.l d2,d4
 cmpi.l #262144,d4
 bhi.s .bad
 movea.l 72(a6),a3
 adda.l 76(a6),a3
 move.l d4,76(a6)
 move.w d0,(a3)+
 move.w d1,(a3)+
 lea 2(a2),a0
 tst.w d1
 beq.s .dma
 subq.w #1,d1
.copy:
 move.l (a0)+,(a3)+
 dbra d1,.copy
.dma:
 tst.l d3
 beq.s .done
 movea.l a2,a0
 adda.l d3,a0
 moveq #63,d1
.copy_dma:
 move.l (a0)+,(a3)+
 dbra d1,.copy_dma
.done:
 movem.l (sp)+,d0-d7/a0-a5
 rts
.bad:
 move.l #-3,8(a6)
 move.w #$f00,$dff180
 bra.w stop

; Preserve the predecessor executable alignment and exact device bytes.
 nop
