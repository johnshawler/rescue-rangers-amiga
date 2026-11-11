; Host proof: static original NMI including finite RAM19/C115 scripts.
; A0 RAM2048, A1 context8, A2 journal134638. Up to33595 four-byte
; PPU/mapper records, count.w; DMA at134382, 256 bytes. Tail untouched.
; 1C/1D and nonterminating scripts reject inertly on active-video path.
; F0|9A skips all video, retaining pending requests exactly as original.
; D0=1/-1; D1-D7/A0-A6 preserved, stack balanced, CCR scratch.
; Valid disjoint buffers/code/native stack required; no ROM resources.
recovery_queued_video_nmi_prefix:
        movem.l d1-d6/a3-a4,-(sp)
        move.b  $f0(a0),d1
        or.b    $9a(a0),d1
        bne.s   .accepted
        move.b  $1c(a0),d1
        or.b    $1d(a0),d1
        bne.w   .invalid
; Validate finite original X traversal before any observable write. Each command
; consumes 1..129 data bytes, X wraps as an 8-bit register. A repeated X can
; never terminate because this script RAM is not modified by the handler.
        tst.b   $19(a0)
        beq.w   .accepted
        moveq   #0,d3
        move.w  #255,d6
.validate:
        tst.b   $360(a0,d3.w)
        bmi.w   .accepted
        moveq   #0,d5
        move.b  $362(a0,d3.w),d5
        cmpi.w  #128,d5
        bls.s   .length
        moveq   #0,d5
.length:
        addq.w  #4,d5
        add.b   d5,d3
        beq.w   .accepted
        dbra    d6,.validate
        bra.w   .invalid
.accepted:
        clr.w   (a2)
        lea     2(a2),a3
        moveq   #0,d4
        move.b  6(a1),d4
; Actual interrupt entry: PC high, PC low, status with B clear; then I is set.
        move.b  (a1),$100(a0,d4.w)
        subq.b  #1,d4
        move.b  1(a1),$100(a0,d4.w)
        subq.b  #1,d4
        move.b  5(a1),d1
        andi.b  #$ef,d1
        ori.b   #$20,d1
        move.b  d1,$100(a0,d4.w)
        subq.b  #1,d4
; PHP saves post-interrupt status with B/U set; PHA/TXA/PHA/TYA/PHA.
        move.b  5(a1),d1
        ori.b   #$34,d1
        move.b  d1,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  2(a1),$100(a0,d4.w)
        subq.b  #1,d4
        move.b  3(a1),$100(a0,d4.w)
        subq.b  #1,d4
        move.b  4(a1),$100(a0,d4.w)
        subq.b  #1,d4
        move.b  $f0(a0),d1
        or.b    $9a(a0),d1
        bne.w   .timers
        move.w  #$2000,d2
        move.b  $ff(a0),d1
        andi.b  #$78,d1
        bsr.w   .write
        bsr.w   .status_read
        moveq   #0,d1
        move.w  #$2001,d2
        bsr.w   .write
        move.w  #$2003,d2
        bsr.w   .write
; Capture DMA's original page-two data in the same resource output.
        lea     134382(a2),a4
        moveq   #0,d3
.dma:
        move.b  $200(a0,d3.w),(a4)+
        addq.w  #1,d3
        cmpi.w  #256,d3
        bne.s   .dma
        moveq   #2,d1
        move.w  #$4014,d2
        bsr.w   .write
        tst.b   $19(a0)
        beq.s   .queued_done
; Original C044 JSR C115 and C115..C139, including wrapped stack writes.
        move.b  #$c0,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$46,$100(a0,d4.w)
        subq.b  #1,d4
        moveq   #0,d3
        move.b  #0,$19(a0)
.queued_command:
        move.b  $360(a0,d3.w),d1
        bmi.s   .queued_return
        move.w  #$2006,d2
        bsr.w   .write
        move.b  $361(a0,d3.w),d1
        bsr.w   .write
        move.b  $362(a0,d3.w),d5
        move.w  #$2007,d2
.queued_data:
        move.b  $363(a0,d3.w),d1
        bsr.w   .write
        addq.b  #1,d3
        subq.b  #1,d5
        bpl.s   .queued_data
        addq.b  #3,d3
        bne.s   .queued_command
.queued_return:
        addq.b  #2,d4
.queued_done:
; Original C047..C059, including wrapped JSR stack writes.
        move.b  $1a(a0),d1
        beq.s   .chr1
        move.b  #$c0,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$4f,$100(a0,d4.w)
        subq.b  #1,d4
        andi.b  #$1f,d1
        move.b  d1,$f2(a0)
        move.w  #$bfff,d2
        bsr.w   .serial
        move.b  #0,$1a(a0)
        addq.b  #2,d4
.chr1:
        move.b  $1b(a0),d1
        beq.s   .palette_entry
        move.b  #$c0,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$58,$100(a0,d4.w)
        subq.b  #1,d4
        andi.b  #$1f,d1
        move.b  d1,$f3(a0)
        move.w  #$dfff,d2
        bsr.w   .serial
        move.b  #0,$1b(a0)
        addq.b  #2,d4
.palette_entry:
; Optional palette path; an absent request skips every palette access.
        tst.b   $18(a0)
        beq.w   .scroll
        move.b  #0,$18(a0)
        bsr.w   .status_read
        move.w  #$2006,d2
        moveq   #$3f,d1
        bsr.w   .write
        moveq   #0,d1
        bsr.w   .write
        moveq   #0,d3
.palette:
        move.w  #$2007,d2
        move.b  $300(a0,d3.w),d1
        bsr.w   .write
        addq.w  #1,d3
        cmpi.w  #32,d3
        bne.s   .palette
        move.w  #$2006,d2
        moveq   #$3f,d1
        bsr.w   .write
        moveq   #0,d1
        bsr.w   .write
        bsr.w   .write
        bsr.w   .write
; Continue original scroll and timer suffix at $C086.
.scroll:
        bsr.w   .status_read
        move.w  #$2005,d2
        move.b  $fc(a0),d1
        bsr.w   .write
        move.b  $fa(a0),d1
        bsr.w   .write
        move.w  #$2001,d2
        move.b  $fe(a0),d1
        bsr.w   .write
        move.w  #$2000,d2
        move.b  $fd(a0),d1
        andi.b  #1,d1
        or.b    $ff(a0),d1
        bsr.w   .write
; Original timer slice, with its exact write ordering and terminal registers.
.timers:
        addq.b  #1,$92(a0)
        move.b  #$ff,$90(a0)
        moveq   #0,d3
.timer:
        moveq   #0,d1
        move.b  $80(a0,d3.w),d1
        moveq   #0,d5
        tst.b   d1
        beq.s   .next_timer
        moveq   #1,d5
        cmpi.b  #1,d1
        bne.s   .next_timer
        subq.b  #1,$81(a0,d3.w)
        bne.s   .next_timer
        moveq   #4,d1
        move.b  d1,$80(a0,d3.w)
.next_timer:
        addq.w  #4,d3
        cmpi.w  #16,d3
        bne.s   .timer
        move.w  #$c0bf,(a1)
        move.b  d1,2(a1)
        move.b  #$10,3(a1)
        move.b  #0,4(a1)
        andi.b  #$6c,5(a1)
        ori.b   #6,5(a1)
        or.b    d5,5(a1)
        move.b  d4,6(a1)
        movem.l (sp)+,d1-d6/a3-a4
        moveq   #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d6/a3-a4
        moveq   #-1,d0
        rts
.write:
        move.w  d2,(a3)+
        move.b  d1,(a3)+
        move.b  #1,(a3)+
        addq.w  #1,(a2)
        rts
.status_read:
        move.w  #$2002,(a3)+
        move.b  #0,(a3)+
        move.b  #0,(a3)+
        addq.w  #1,(a2)
        rts
.serial:
        moveq   #4,d6
.serial_loop:
        move.w  d2,(a3)+
        move.b  d1,(a3)+
        move.b  $f5(a0),(a3)+
        addq.w  #1,(a2)
        lsr.b   #1,d1
        dbra    d6,.serial_loop
        rts
