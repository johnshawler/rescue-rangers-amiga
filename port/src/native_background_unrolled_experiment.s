; Additive unrolled experiment; exact native_background.s ABI and cache semantics.
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
; Fixed eight-row tile: remove three pointer updates and DBRA per row.
        move.b 0(a5),d0
        move.b d0,0(a6)
        or.b 8(a5),d0
        move.b d0,0(a3,d3.w)
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
        move.b 2(a5),d0
        move.b d0,80(a6)
        or.b 10(a5),d0
        move.b d0,64(a3,d3.w)
        move.b 10(a5),10320(a6)
        move.b d1,20560(a6)
        move.b d2,30800(a6)
        clr.b 41040.l(a6)
        move.b 3(a5),d0
        move.b d0,120(a6)
        or.b 11(a5),d0
        move.b d0,96(a3,d3.w)
        move.b 11(a5),10360(a6)
        move.b d1,20600(a6)
        move.b d2,30840(a6)
        clr.b 41080.l(a6)
        move.b 4(a5),d0
        move.b d0,160(a6)
        or.b 12(a5),d0
        move.b d0,128(a3,d3.w)
        move.b 12(a5),10400(a6)
        move.b d1,20640(a6)
        move.b d2,30880(a6)
        clr.b 41120.l(a6)
        move.b 5(a5),d0
        move.b d0,200(a6)
        or.b 13(a5),d0
        move.b d0,160(a3,d3.w)
        move.b 13(a5),10440(a6)
        move.b d1,20680(a6)
        move.b d2,30920(a6)
        clr.b 41160.l(a6)
        move.b 6(a5),d0
        move.b d0,240(a6)
        or.b 14(a5),d0
        move.b d0,192(a3,d3.w)
        move.b 14(a5),10480(a6)
        move.b d1,20720(a6)
        move.b d2,30960(a6)
        clr.b 41200.l(a6)
        move.b 7(a5),d0
        move.b d0,280(a6)
        or.b 15(a5),d0
        move.b d0,224(a3,d3.w)
        move.b 15(a5),10520(a6)
        move.b d1,20760(a6)
        move.b d2,31000(a6)
        clr.b 41240.l(a6)
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
