; Conservative post-composition invalidation for persistent dirty backgrounds.
; Call AFTER sprites, before OAM can change. A0=256-byte OAM, A4=1920-byte
; background cache. All D/A registers preserved, CCR clobbered, 60 stack bytes.
; Invalidates at most four tiles per 8x8 sprite, clipped to 256x240.
; Includes transparent/disabled/overflow/behind-background sprites deliberately.
        xdef recovery_redraw_invalidate_oam
        xdef recovery_redraw_invalidate_all
recovery_redraw_invalidate_oam:
        movem.l d0-d7/a0-a6,-(sp)
        moveq #63,d7
rrdi_sprite:
        moveq #0,d0
        move.b (a0),d0
        addq.w #1,d0
        cmp.w #240,d0
        bcc rrdi_next
        move.w d0,d1
        addq.w #7,d1
        cmp.w #240,d1
        bcs rrdi_y_ok
        move.w #239,d1
rrdi_y_ok:
        lsr.w #3,d0
        lsr.w #3,d1
        moveq #0,d2
        move.b 3(a0),d2
        move.w d2,d3
        addq.w #7,d3
        cmp.w #256,d3
        bcs rrdi_x_ok
        move.w #255,d3
rrdi_x_ok:
        lsr.w #3,d2
        lsr.w #3,d3
rrdi_row:
        move.w d0,d4
        lsl.w #5,d4
        add.w d2,d4
        add.w d4,d4
        move.w #-1,(a4,d4.w)
        cmp.w d2,d3
        beq rrdi_one_column
        move.w #-1,2(a4,d4.w)
rrdi_one_column:
        addq.w #1,d0
        cmp.w d1,d0
        bls rrdi_row
rrdi_next:
        addq.l #4,a0
        dbra d7,rrdi_sprite
        movem.l (sp)+,d0-d7/a0-a6
        rts
; No OAM or other input read. Call before first background or any context change
; that cache keys do not encode. 12 stack bytes; all D/A registers preserved.
recovery_redraw_invalidate_all:
        movem.l d0-d1/a4,-(sp)
        moveq #-1,d0
        move.w #479,d1
rrdi_all:
        move.l d0,(a4)+
        dbra d1,rrdi_all
        movem.l (sp)+,d0-d1/a4
        rts
