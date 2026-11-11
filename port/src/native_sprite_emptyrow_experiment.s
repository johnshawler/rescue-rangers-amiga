; Additive experiment: do not clear unused ownership mask on empty rows.
; NES 8x8 sprites -> five contiguous Amiga 320x256 bitplanes.
; See ../NATIVE_SPRITES.md for ABI, integration and accuracy limits.
        xdef nes_draw_sprites_8x8
nes_draw_sprites_8x8:
        movem.l d1-d7/a0-a6,-(sp)
        btst #5,d0
        bne ns_unsupported
        move.b d1,32(a4)
        btst #4,d1
        beq ns_done
        btst #3,d0
        beq ns_table_ready
        lea 4096(a1),a1
ns_table_ready:
; Build first-eight OAM offsets for each row in OAM order: <=64*8
; row visits instead of 64*240 range checks in the drawing loop.
        lea 36(a4),a5
        moveq #59,d0
ns_clear_counts:
        clr.l (a5)+
        dbra d0,ns_clear_counts
        movea.l a0,a5
        moveq #0,d1
        moveq #63,d7
ns_evaluate_sprite:
        moveq #0,d0
        move.b (a5),d0
        addq.w #1,d0
        moveq #7,d4
ns_evaluate_row:
        cmp.w #240,d0
        bcc ns_evaluate_next
        moveq #0,d2
        move.b 36(a4,d0.w),d2
        cmp.w #8,d2
        bcc ns_evaluate_row_next
        move.w d0,d3
        lsl.w #3,d3
        add.w d2,d3
        move.b d1,276(a4,d3.w)
        addq.b #1,36(a4,d0.w)
ns_evaluate_row_next:
        addq.w #1,d0
        dbra d4,ns_evaluate_row
ns_evaluate_next:
        addq.l #4,a5
        addq.w #4,d1
        dbra d7,ns_evaluate_sprite
        lea 320(a2),a6
        moveq #0,d7
ns_row:
        moveq #0,d6
        move.b 36(a4,d7.w),d6
        beq ns_next_row
        clr.l (a4)
        clr.l 4(a4)
        clr.l 8(a4)
        clr.l 12(a4)
        clr.l 16(a4)
        clr.l 20(a4)
        clr.l 24(a4)
        clr.l 28(a4)
        move.w d7,d5
        lsl.w #3,d5
        add.w #276,d5
ns_sprite:
        moveq #0,d0
        move.b (a4,d5.w),d0
        lea (a0,d0.w),a5
; OAM Y is top minus one. Do NOT wrap FF to zero (hidden sprites).
        moveq #0,d0
        move.b (a5),d0
        addq.w #1,d0
        neg.w d0
        add.w d7,d0
        moveq #0,d3
        move.b 2(a5),d3
        btst #7,d3
        beq ns_y_ready
        eori.w #7,d0
ns_y_ready:
        moveq #0,d2
        move.b 1(a5),d2
        lsl.w #4,d2
        add.w d2,d0
        moveq #0,d2
        moveq #0,d1
        move.b (a1,d0.w),d2
        move.b 8(a1,d0.w),d1
        moveq #0,d4
        move.b 3(a5),d4
        movem.l d5-d6/a5,-(sp)
        moveq #7,d5
ns_pixel:
        cmp.w #256,d4
        bcc ns_pixel_next
        cmp.w #8,d4
        bcc ns_left_ok
        btst #2,32(a4)
        beq ns_pixel_next
ns_left_ok:
        move.w d5,d0
        btst #6,d3
        beq ns_x_ready
        eori.w #7,d0
ns_x_ready:
        moveq #0,d6
        btst d0,d2
        beq ns_low_zero
        moveq #1,d6
ns_low_zero:
        btst d0,d1
        beq ns_high_zero
        addq.w #2,d6
ns_high_zero:
        tst.w d6
        beq ns_pixel_next
; Claim each nontransparent sprite pixel before testing BG priority.
; A lower-index sprite hidden by BG must still hide later sprites.
        move.w d4,d0
        lsr.w #3,d0
        lea (a4,d0.w),a5
        move.w d4,d0
        not.w d0
        and.w #7,d0
        bset d0,(a5)
        bne ns_pixel_next
        btst #5,d3
        beq ns_visible
        move.w d4,d0
        lsr.w #3,d0
        lea (a3,d0.w),a5
        move.w d4,d0
        not.w d0
        and.w #7,d0
        btst d0,(a5)
        bne ns_pixel_next
ns_visible:
        move.w d3,d0
        and.w #3,d0
        lsl.w #2,d0
        or.w d0,d6
        ori.w #16,d6
        move.w d4,d0
        lsr.w #3,d0
        lea 4(a6,d0.w),a5
        move.w d4,d0
        not.w d0
        and.w #7,d0
        bclr d0,(a5)
        btst #0,d6
        beq ns_plane1
        bset d0,(a5)
ns_plane1:
        bclr d0,10240(a5)
        btst #1,d6
        beq ns_plane2
        bset d0,10240(a5)
ns_plane2:
        bclr d0,20480(a5)
        btst #2,d6
        beq ns_plane3
        bset d0,20480(a5)
ns_plane3:
        bclr d0,30720(a5)
        btst #3,d6
        beq ns_plane4
        bset d0,30720(a5)
ns_plane4:
; 40960 exceeds signed 16-bit displacement: full 68020 extension.
        bset d0,40960.l(a5)
ns_pixel_next:
        addq.w #1,d4
        dbra d5,ns_pixel
        movem.l (sp)+,d5-d6/a5
ns_next_sprite:
        addq.w #1,d5
        subq.w #1,d6
        bne ns_sprite
ns_next_row:
        lea 32(a3),a3
        lea 40(a6),a6
        addq.w #1,d7
        cmp.w #240,d7
        bne ns_row
ns_done:
        moveq #0,d0
        bra ns_return
ns_unsupported:
        moveq #-1,d0
ns_return:
        movem.l (sp)+,d1-d7/a0-a6
        rts
