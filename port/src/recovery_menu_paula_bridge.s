; C ABI bridge. Preserve native runner registers and source state exactly.
paula_consume:
 movem.l d0-d7/a0-a6,-(sp)
 moveq #0,d0
 move.w 6(a4),d0
 move.l d0,-(sp)
 moveq #0,d0
 move.w 8(a4),d0
 move.l d0,-(sp)
 move.l a2,-(sp)
 bsr.l paula_adapter+4
 lea 12(sp),sp
 tst.l d0
 beq.s .bad
 movem.l (sp)+,d0-d7/a0-a6
 rts
.bad:
 movem.l (sp)+,d0-d7/a0-a6
 move.l #-4,d0
 bra.l failed
paula_render:
 movem.l d0-d7/a0-a6,-(sp)
 bsr.l paula_adapter+12
 bsr.l startup_display
 bsr.l paula_adapter+16
 tst.l 8(a6)
 bne.s .display_failed
 bsr.l paula_adapter+8
 movem.l (sp)+,d0-d7/a0-a6
 rts
.display_failed:
 movem.l (sp)+,d0-d7/a0-a6
 moveq #-5,d0
 bra.l failed
; Display scanout contention is active from initialization. Initial planes are
; cleared diagnostic storage, not a fabricated game screen. One final render.
paula_display_init:
 movem.l d0-d7/a0-a6,-(sp)
 ifne DISPLAY_DMA
 lea startup_frame(pc),a0
 move.l a0,d0
 lea startup_planes(pc),a0
 moveq #4,d1
.ptr:
 move.w d0,6(a0)
 swap d0
 move.w d0,2(a0)
 swap d0
 addi.l #10240,d0
 addq.l #8,a0
 dbra d1,.ptr
 lea startup_copper(pc),a0
 move.l a0,$dff080
 move.w #0,$dff088
 move.w #$8380,$dff096
 endif
 movem.l (sp)+,d0-d7/a0-a6
 rts
