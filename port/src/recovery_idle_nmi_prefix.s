; Explicit logical hardware NMI from any original PC/SP to C0BF.
; A0=2048 RAM; A1=8 context PC.w,A,X,Y,raw P,S,reserved; A2=454 output.
; Count.w, capacity 49 records {address.w,value.b,kind.b}, DMA at fixed +198.
; Inactive records and DMA on video-skip remain untouched. Read value is unused.
; F0|9A != 0 executes genuine video-skip, retaining ALL pending requests.
; Otherwise nonzero 19..1D reject inertly; palette 18 may be zero or nonzero.
; All PC/SP/P values accepted. NMI frame B=0/U=1, PHP B/U/I=1.
; Raw context U stays raw (unused status bit); B clears like reference NMI.
; D0=1 at C0BF, -1 unsupported inert. D1-D7/A0-A6 preserved.
; No instruction decoder, mapper/audio/RTI, automatic timing or interrupt source.
recovery_idle_nmi_prefix:
        movem.l d1-d6/a3-a4,-(sp)
        move.b  $f0(a0),d1
        or.b    $9a(a0),d1
        bne.s   .accepted
        move.b  $19(a0),d1
        or.b    $1a(a0),d1
        or.b    $1b(a0),d1
        or.b    $1c(a0),d1
        or.b    $1d(a0),d1
        bne.w   .invalid
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
        lea     198(a2),a4
        moveq   #0,d3
.dma:
        move.b  $200(a0,d3.w),(a4)+
        addq.w  #1,d3
        cmpi.w  #256,d3
        bne.s   .dma
        moveq   #2,d1
        move.w  #$4014,d2
        bsr.w   .write
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
