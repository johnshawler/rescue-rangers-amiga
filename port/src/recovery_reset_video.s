; Original $FE67..$FE7B: sprite hide plus two $C1BA PPU clears.
; A0=2048-byte RAM, A1=8-byte boundary context, A2=8754-byte PPU journal.
; Journal BE count.w then {address.w, data.b, kind.b}; kind 0=read, 1=write.
; Read $2002 is a latch-reset event, data byte zero (result unused by source).
; Require PC=$FE67, RAM[$97] divisible by 4, RAM[$FF] bit 2 clear.
; D0=1 completed $FE7C; -1 invalid with no buffer changes.
; D1-D7/A0-A6 preserved; CCR scratch. No hardware MMIO or interpreter.
recovery_reset_video:
        cmpi.w  #$fe67,(a1)
        bne.w   .invalid
        move.l  d1,-(sp)
        move.b  $97(a0),d1
        andi.b  #3,d1
        bne.w   .invalid_pop
        btst    #2,$ff(a0)
        bne.w   .invalid_pop
        movem.l d2-d6/a3,-(sp)
        lea     2(a2),a3
        clr.w   (a2)
        moveq   #0,d4
        move.b  6(a1),d4
; Original JSR $C21E pushes $FE69.
        move.b  #$fe,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$69,$100(a0,d4.w)
        moveq   #0,d1
        move.b  $97(a0),d1
        cmpi.b  #4,d1
        bne.s   .hide
        move.b  #$f8,$200(a0)
.hide:
        move.b  #$f8,$200(a0,d1.w)
        addq.b  #4,d1
        bne.s   .hide
        moveq   #$20,d6
; First original JSR $C1BA pushes $FE72.
        addq.b  #1,d4
        move.b  #$fe,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$72,$100(a0,d4.w)
        bsr.w   .clear_table
; Second original JSR $C1BA pushes $FE7B.
        addq.b  #1,d4
        move.b  #$fe,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$7b,$100(a0,d4.w)
        moveq   #$24,d6
        bsr.w   .clear_table
        move.w  #$fe7c,(a1)
        move.b  #$c0,2(a1)
        move.b  #0,3(a1)
        move.b  #0,4(a1)
        andi.b  #$3c,5(a1)
        ori.b   #2,5(a1)
        movem.l (sp)+,d2-d6/a3
        move.l  (sp)+,d1
        moveq   #1,d0
        rts
.invalid_pop:
        move.l  (sp)+,d1
.invalid:
        moveq   #-1,d0
        rts
.clear_table:
        move.b  d6,(a0)
        move.b  #0,1(a0)
        move.b  #0,2(a0)
; Original LDA $2002: explicit latch-reset read, result intentionally unused.
        move.w  #$2002,(a3)+
        move.b  #0,(a3)+
        move.b  #0,(a3)+
        addq.w  #1,(a2)
        move.b  $ff(a0),d1
        andi.b  #$fe,d1
        move.w  #$2000,d2
        bsr.s   .publish
        move.b  d6,d1
        move.w  #$2006,d2
        bsr.s   .publish
        moveq   #0,d1
        bsr.s   .publish
        move.w  #$2007,d2
        move.w  #1023,d3
.tiles:
        bsr.s   .publish
        dbra    d3,.tiles
; CMP #$20 sets carry; ADC #2 therefore adds THREE, not two.
        move.b  d6,d1
        addq.b  #3,d1
        move.w  #$2006,d2
        bsr.s   .publish
        move.b  #$c0,d1
        bsr.s   .publish
        moveq   #0,d1
        move.w  #$2007,d2
        moveq   #63,d3
.attributes:
        bsr.s   .publish
        dbra    d3,.attributes
        rts
.publish:
        move.w  d2,(a3)+
        move.b  d1,(a3)+
        move.b  #1,(a3)+
        addq.w  #1,(a2)
        rts
