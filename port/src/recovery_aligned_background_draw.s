; Additive shift-zero fast path; generic shifts1-7 retain frozen merge loop.
; Additive visible-tile background renderer. Same pixel/index ABI as scroll_view.
; Cache 33 CHR offsets per eight scanlines; decode only visible pattern bytes.
; Scratch remains 256 bytes; maximum stack below return address is 128 bytes.
        xdef recovery_aligned_background_draw
recovery_aligned_background_draw:
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
 ; Locals: origin tile, fine shift, y (6), 33 CHR offset words (66).
        and.w #1,d0
        lsl.w #8,d0
        add.w d2,d0
        and.w #7,d2
        lsr.w #3,d0
        lea -66(sp),sp
        move.w #0,-(sp)
        move.w d2,-(sp)
        move.w d0,-(sp)
        lea 324(a2),a2
.group:
        lea 6(sp),a6
        moveq #0,d7
.tile:
; Resolve just the 33 visible tiles, wrapping the physical NT seam.
        move.w (sp),d1
        add.w d7,d1
        and.w #63,d1
        move.w d1,d0
        and.w #32,d0
        lsl.w #5,d0
        lea (a0,d0.w),a5
        move.w 4(sp),d6
        move.w d6,d0
        lsr.w #3,d0
        lsl.w #5,d0
        and.w #31,d1
        add.w d1,d0
        moveq #0,d2
        move.b (a5,d0.w),d2
        lsl.w #4,d2
        move.w d2,(a6)+
; Attributes are invariant over the following eight output scanlines.
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
        cmp.w #33,d7
        bne.w .tile
.row:
        move.w 4(sp),d6
        and.w #7,d6
        lea 6(sp),a5
        moveq #0,d7
.pattern:
        move.w (a5)+,d2
        add.w d6,d2
        move.b (a1,d2.w),(a4,d7.w)
        move.b 8(a1,d2.w),64(a4,d7.w)
        addq.w #1,d7
        cmp.w #33,d7
        bne.s .pattern
; Packed adjacent-byte merges. The last viewport byte uses scratch tile 32.
        move.w 2(sp),d5
        moveq #0,d7
        tst.w d5
        beq.w .aligned_byte
.byte:
        moveq #0,d0
        move.b (a4,d7.w),d0
        lsl.w #8,d0
        move.b 1(a4,d7.w),d0
        lsl.w d5,d0
        lsr.w #8,d0
        move.b d0,(a2,d7.w)
        move.b d0,d4
        move.b 64(a4,d7.w),d0
        lsl.w #8,d0
        move.b 65(a4,d7.w),d0
        lsl.w d5,d0
        lsr.w #8,d0
        move.b d0,10240(a2,d7.w)
        or.b d0,d4
        move.b d4,(a3)+
        move.b 128(a4,d7.w),d0
        lsl.w #8,d0
        move.b 129(a4,d7.w),d0
        lsl.w d5,d0
        lsr.w #8,d0
        move.b d0,20480(a2,d7.w)
        move.b 192(a4,d7.w),d0
        lsl.w #8,d0
        move.b 193(a4,d7.w),d0
        lsl.w d5,d0
        lsr.w #8,d0
        move.b d0,30720(a2,d7.w)
        clr.b 40960.l(a2,d7.w)
        addq.w #1,d7
        cmp.w #32,d7
        bne.w .byte
        bra.s .row_finished
.aligned_byte:
        move.b (a4,d7.w),d0
        move.b d0,(a2,d7.w)
        move.b d0,d4
        move.b 64(a4,d7.w),d0
        move.b d0,10240(a2,d7.w)
        or.b d0,d4
        move.b d4,(a3)+
        move.b 128(a4,d7.w),20480(a2,d7.w)
        move.b 192(a4,d7.w),30720(a2,d7.w)
        clr.b 40960.l(a2,d7.w)
        addq.w #1,d7
        cmp.w #32,d7
        bne.s .aligned_byte
.row_finished:
        lea 40(a2),a2
        addq.w #1,4(sp)
        cmpi.w #240,4(sp)
        beq.s .finished
        move.w 4(sp),d0
        and.w #7,d0
        bne.w .row
        bra.w .group
.finished:
        lea 72(sp),sp
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
