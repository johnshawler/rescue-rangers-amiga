; Apply original blanking with its current universal RGB4 backdrop.
; Gray/emphasis/partial rendering/scroll/8x16 modes are not implemented.
; Unsupported modes may occur during startup before the first accepted frame;
; blank them. After any accepted frame they fail closed rather than freeze it.
recovery_live_scanout:
 movem.l d0-d2/a0-a2,-(sp)
 lea startup_device(pc),a0
 tst.l 16(a0)
 bne.w .bad
 tst.b 1(a0)
 beq.s .blank
 cmpi.b #$1e,1(a0)
 bne.s .unsupported
 cmpi.b #$90,(a0)
 bne.s .unsupported
 tst.b 3(a0)
 bne.s .unsupported
 tst.b 4(a0)
 bne.s .unsupported
 cmpi.b #$1e,10(a0)
 bne.s .unsupported
 tst.b 15(a0)
 bne.s .unsupported
 bra.s .done
.unsupported:
 lea recovery_live_report(pc),a1
 tst.l 36(a1)
 bne.s .bad
.blank:
 move.w #$0100,$dff096
 lea startup_palette(pc),a1
 moveq #0,d0
 move.b (a1),d0
 andi.w #63,d0
 add.w d0,d0
 lea startup_rgb12(pc),a1
 move.w (a1,d0.w),d1
 lea startup_colors(pc),a2
 move.w d1,2(a2)
 move.w d1,$dff180
.done:
 movem.l (sp)+,d0-d2/a0-a2
 rts
.bad:
 movem.l (sp)+,d0-d2/a0-a2
 lea startup_display_report(pc),a0
 move.l #-1,8(a0)
 moveq #-5,d0
 bra.l failed
