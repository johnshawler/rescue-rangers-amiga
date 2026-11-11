; Pair two rows to retain a small loop and avoid a large instruction footprint.
; Callable dirty NES background renderer. See NATIVE_BACKGROUND.md.
        xdef nes_draw_background
nes_draw_background:
        movem.l d0-d7/a0-a6,-(sp)
        moveq #0,d6
nb_row:
        moveq #0,d7
nb_column:
        move.w d6,d0
        lsl.w #5,d0
        add.w d7,d0
        moveq #0,d1
        move.b (a0,d0.w),d1
        move.w d1,d2
        lsl.w #4,d1
        lea (a1,d1.w),a5
; Attribute quadrant shift = ((tileY & 2) << 1) | (tileX & 2).
        move.w d6,d0
        lsr.w #2,d0
        lsl.w #3,d0
        move.w d7,d1
        lsr.w #2,d1
        add.w d1,d0
        moveq #0,d5
        move.b 960(a0,d0.w),d5
        move.w d6,d0
        and.w #2,d0
        add.w d0,d0
        move.w d7,d1
        and.w #2,d1
        or.w d1,d0
        lsr.w d0,d5
        and.w #3,d5
        move.w d5,d0
        lsl.w #8,d0
        or.w d0,d2
        cmp.w (a4),d2
        beq nb_skip
        move.w d2,(a4)
; Framebuffer origin x32,y8; opacity origin x0,y0.
        move.w d6,d0
        lsl.w #3,d0
        addq.w #8,d0
        mulu #40,d0
        add.w d7,d0
        addq.w #4,d0
        lea (a2,d0.l),a6
        move.w d6,d3
        lsl.w #8,d3
        add.w d7,d3
; Constant palette bitplanes for this tile.
        moveq #0,d1
        btst #0,d5
        beq nb_palette3
        moveq #-1,d1
nb_palette3:
        moveq #0,d2
        btst #1,d5
        beq nb_scan_start
        moveq #-1,d2
nb_scan_start:
        moveq #3,d4
nb_scan:
        move.b (a5),d0
        move.b d0,(a6)
        or.b 8(a5),d0
        move.b d0,(a3,d3.w)
        move.b 8(a5),10240(a6)
        move.b d1,20480(a6)
        move.b d2,30720(a6)
        clr.b 40960.l(a6)
        move.b 1(a5),d0
        move.b d0,40(a6)
        or.b 9(a5),d0
        move.b d0,32(a3,d3.w)
        move.b 9(a5),10280(a6)
        move.b d1,20520(a6)
        move.b d2,30760(a6)
        clr.b 41000.l(a6)
        addq.l #2,a5
        lea 80(a6),a6
        add.w #64,d3
        dbra d4,nb_scan
nb_skip:
        addq.l #2,a4
        addq.w #1,d7
        cmp.w #32,d7
        bne nb_column
        addq.w #1,d6
        cmp.w #30,d6
        bne nb_row
        movem.l (sp)+,d0-d7/a0-a6
        rts
