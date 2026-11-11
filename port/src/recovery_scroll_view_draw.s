; Source-only horizontal 512x240 background viewport. See recovery_scroll_view.md.
        xdef recovery_scroll_view_draw
recovery_scroll_view_draw:
        movem.l d1-d7/a0-a6,-(sp)
        cmp.l #255,d2
        bhi.w .reject
        tst.l d3
        bne.w .reject
        cmp.l #$1e,d4
        bne.w .reject
        cmp.l #$90,d0
        beq.s .ctrl_ok
        cmp.l #$91,d0
        bne.w .reject
.ctrl_ok:
        tst.l d1
        beq.w .blank
        cmp.l #$1e,d1
        bne.w .reject
; Stack locals: world byte origin, fine shift, y. Extra six bytes.
        and.w #1,d0
        lsl.w #8,d0
        add.w d2,d0
        and.w #7,d2
        lsr.w #3,d0
        move.w #0,-(sp)
        move.w d2,-(sp)
        move.w d0,-(sp)
        lea 324(a2),a2
.row:
        moveq #0,d7
.tile:
; d7 is world tile x 0..63. Resolve physical NT before tile/attribute.
        move.w d7,d0
        and.w #32,d0
        lsl.w #5,d0
        lea (a0,d0.w),a5
        move.w 4(sp),d6
        move.w d6,d0
        lsr.w #3,d0
        lsl.w #5,d0
        move.w d7,d1
        and.w #31,d1
        add.w d1,d0
        moveq #0,d2
        move.b (a5,d0.w),d2
        lsl.w #4,d2
        move.w d6,d0
        and.w #7,d0
        add.w d0,d2
        move.b (a1,d2.w),(a4,d7.w)
        move.b 8(a1,d2.w),64(a4,d7.w)
; Attribute byte and quadrant independently selected for each world tile.
        move.w d6,d0
        lsr.w #5,d0
        lsl.w #3,d0
        move.w d1,d2
        lsr.w #2,d2
        add.w d2,d0
        moveq #0,d3
        move.b 960(a5,d0.w),d3
        and.w #16,d6
        lsr.w #2,d6
        and.w #2,d1
        or.w d1,d6
        lsr.w d6,d3
        moveq #0,d0
        btst #0,d3
        beq.s .pal_high
        moveq #-1,d0
.pal_high:
        move.b d0,128(a4,d7.w)
        moveq #0,d0
        btst #1,d3
        beq.s .pal_done
        moveq #-1,d0
.pal_done:
        move.b d0,192(a4,d7.w)
        addq.w #1,d7
        cmp.w #64,d7
        bne.w .tile
; Merge neighbouring tile bytes with native word shifts. No source overread at wrap.
        move.w (sp),d6
        move.w 2(sp),d5
        moveq #0,d7
.byte:
        move.w d6,d1
        addq.w #1,d1
        and.w #63,d1
        movea.l a4,a5
        lea (a2,d7.w),a6
        moveq #0,d4
        moveq #3,d3
.plane:
        moveq #0,d0
        move.b (a5,d6.w),d0
        lsl.w #8,d0
        move.b (a5,d1.w),d0
        lsl.w d5,d0
        lsr.w #8,d0
        move.b d0,(a6)
        cmp.w #2,d3
        blo.s .not_opacity
        or.b d0,d4
.not_opacity:
        lea 64(a5),a5
        lea 10240(a6),a6
        dbra d3,.plane
        clr.b (a6)
        move.b d4,(a3)+
        addq.w #1,d6
        and.w #63,d6
        addq.w #1,d7
        cmp.w #32,d7
        bne.s .byte
        lea 40(a2),a2
        addq.w #1,4(sp)
        cmpi.w #240,4(sp)
        bne.w .row
        addq.l #6,sp
        bra.s .done
.blank:
        lea 324(a2),a2
        move.w #239,d7
.blank_row:
        moveq #31,d6
.blank_byte:
        clr.b (a2)
        clr.b 10240(a2)
        clr.b 20480(a2)
        clr.b 30720(a2)
        clr.b 40960.l(a2)
        clr.b (a3)+
        addq.l #1,a2
        dbra d6,.blank_byte
        addq.l #8,a2
        dbra d7,.blank_row
.done:
        moveq #0,d0
        bra.s .return
.reject:
        moveq #-1,d0
.return:
        movem.l (sp)+,d1-d7/a0-a6
        rts
