; Hardware NMI at explicit pre-instruction boundary $FE8D, then $C000..$C0BE.
; A0=2048-byte RAM, A1=8-byte boundary context, A2=298-byte journal/resource.
; Journal: count.w, ten {address.w,data.b,kind.b} records, 256-byte OAM at +42.
; Require PC=$FE8D, canonical P bits B=0/U=1, FF bit7 set,
; and RAM F0,9A,18..1D all zero (startup no pending render/resource queues).
; D0=1 at untranslated $C0BF, -1 invalid/inert; other D/A preserved.
; Explicit synchronous NMI event only. No bank/audio/RTI or timing emulation.
recovery_first_nmi_prefix:
        movem.l d1-d6/a3-a4,-(sp)
        cmpi.w  #$fe8d,(a1)
        bne.w   .invalid
        move.b  5(a1),d1
        andi.b  #$30,d1
        cmpi.b  #$20,d1
        bne.w   .invalid
        btst    #7,$ff(a0)
        beq.w   .invalid
        move.b  $f0(a0),d1
        or.b    $9a(a0),d1
        or.b    $18(a0),d1
        or.b    $19(a0),d1
        or.b    $1a(a0),d1
        or.b    $1b(a0),d1
        or.b    $1c(a0),d1
        or.b    $1d(a0),d1
        bne.w   .invalid
        clr.w   (a2)
        lea     2(a2),a3
        moveq   #0,d4
        move.b  6(a1),d4
; Actual interrupt entry: PC high, PC low, status with B clear; then I is set.
        move.b  #$fe,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$8d,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  5(a1),$100(a0,d4.w)
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
        lea     42(a2),a4
        moveq   #0,d3
.dma:
        move.b  $200(a0,d3.w),(a4)+
        addq.w  #1,d3
        cmpi.w  #256,d3
        bne.s   .dma
        moveq   #2,d1
        move.w  #$4014,d2
        bsr.w   .write
; Guarded pending queues are zero; original reaches $C086 directly.
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
        andi.b  #$7c,5(a1)
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
