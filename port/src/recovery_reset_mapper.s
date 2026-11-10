; Bounded original fixed-bank $FE43..$FE66, no asynchronous interrupt injection.
; A0=2KiB RAM, A1=8-byte context as recovery_reset_ram.s.
; A2=82-byte journal: BE word count, then 20 {BE address.w,value.b,busy.b}.
; Require context PC=$FE43 and RAM[$F6]=0. Buffers disjoint and writable.
; D0=1 at untranslated $FE67; -1 invalid, all buffers unchanged.
; Preserve D1-D7/A0-A6; CCR scratch. Journal is data, never hardware MMIO.
recovery_reset_mapper:
        cmpi.w  #$fe43,(a1)
        bne.w   .invalid
        tst.b   $f6(a0)
        bne.w   .invalid
        movem.l d1-d4/a3,-(sp)
        moveq   #0,d4
        move.b  6(a1),d4
        lea     2(a2),a3
        clr.w   (a2)
; Original JSR $FF53 pushes $FE47, high then low, even when SP wraps.
        move.b  #$fe,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$47,$100(a0,d4.w)
        moveq   #6,d1
        move.b  d1,$f1(a0)
        move.b  d1,$f4(a0)
        addq.b  #1,$f5(a0)
        move.w  #$fff0,d2
        bsr.s   .serial
        move.b  #0,$f5(a0)
; $F6 was validated zero; interrupt-free execution does not enter audio.
        moveq   #$1e,d1
        move.w  #$9fff,d2
        bsr.s   .serial
; Original JSR $FF1F pushes $FE61.
        addq.b  #1,d4
        move.b  #$fe,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$61,$100(a0,d4.w)
        moveq   #0,d1
        move.b  d1,$f2(a0)
        move.w  #$bfff,d2
        bsr.s   .serial
        move.b  #0,$1a(a0)
; Original JSR $FF39 pushes $FE66.
        addq.b  #1,d4
        move.b  #$fe,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$66,$100(a0,d4.w)
        moveq   #$10,d1
        move.b  d1,$f3(a0)
        move.w  #$dfff,d2
        bsr.s   .serial
        move.b  #0,$1b(a0)
        move.w  #$fe67,(a1)
        move.b  #0,2(a1)
        andi.b  #$7c,5(a1)
        ori.b   #2,5(a1)
        movem.l (sp)+,d1-d4/a3
        moveq   #1,d0
        rts
; Publish original full shifted A bytes, not only MMC1 bit 0.
; Commit count AFTER record is populated; preserve contemporaneous busy byte.
.serial:
        moveq   #4,d3
.next:
        move.w  d2,(a3)+
        move.b  d1,(a3)+
        move.b  $f5(a0),(a3)+
        addq.w  #1,(a2)
        lsr.b   #1,d1
        dbra    d3,.next
        rts
.invalid:
        moveq   #-1,d0
        rts
