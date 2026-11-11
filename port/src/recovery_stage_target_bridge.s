; Real CIA events feed original controller ABI. No writes into original game RAM.
; Output-only input changes retain dispatch position for independent replay.
recovery_live_init:
 movem.l d0-d7/a0-a6,-(sp)
 move.b #$7f,$bfed01
 bclr #6,$bfee01
 lea recovery_live_report(pc),a2
 lea recovery_live_state(pc),a0
 move.l a0,20(a2)
 lea recovery_live_changes(pc),a0
 move.l a0,24(a2)
 move.l #$10000,8(a2)
 movem.l (sp)+,d0-d7/a0-a6
 rts
recovery_live_poll:
 movem.l d0-d7/a0-a6,-(sp)
 lea recovery_live_state(pc),a0
 bsr.l recovery_zx_poll
 lea recovery_live_report(pc),a2
 cmp.b 32(a2),d0
 beq.s .done
 move.l 28(a2),d1
 cmpi.l #128,d1
 bhs.s .overflow
 move.b d0,32(a2)
 lsl.l #4,d1
 lea recovery_live_changes(pc),a3
 adda.l d1,a3
 move.l 12(a6),(a3)+
 move.l 20(a6),(a3)+
 move.l 16(a2),(a3)+
 move.l d0,(a3)+
 addq.l #1,28(a2)
.done:
 movem.l (sp)+,d0-d7/a0-a6
 rts
.overflow:
 move.l #1,12(a2)
 movem.l (sp)+,d0-d7/a0-a6
 moveq #-9,d0
 bra.l failed
recovery_live_render:
 movem.l d0-d7/a0-a6,-(sp)
 move.w 6(a4),d0
 cmpi.w #8,d0
 beq.s .rti
 cmpi.w #20,d0
 beq.s .rti
 cmpi.w #42,d0
 bne.w .done
.rti:
 lea recovery_live_report(pc),a3
 addq.l #1,16(a3)
 ; Only the existing renderer's admitted unscrolled 8x8 view is attempted.
 lea startup_device(pc),a0
 tst.l 16(a0)
 bne.s .render
 move.b (a0),d0
 andi.b #$fe,d0
 cmpi.b #$90,d0
 bne.w .done
 cmpi.b #$1e,1(a0)
 bne.w .done
 tst.b 4(a0)
 bne.w .done
 cmpi.b #$1e,10(a0)
 bne.w .done
 tst.b 15(a0)
 bne.w .done
.render:
 ; Full redraw on every admitted completion, no dirty cache.
 bsr.l paula_adapter+12
 bsr.l startup_display
 bsr.l paula_adapter+16
 tst.l 8(a6)
 bne.s .bad
 lea recovery_live_report(pc),a3
 addq.l #1,36(a3)
 move.l 16(a3),40(a3)
.done:
 movem.l (sp)+,d0-d7/a0-a6
 rts
.bad:
 movem.l (sp)+,d0-d7/a0-a6
 moveq #-5,d0
 bra.l failed
 include "recovery_zx_keyboard.s"
 cnop 0,4
recovery_live_report:
 dc.b 'CDRCLIV1'
 dcb.l 9,0
recovery_live_state: dcb.b 12,0
recovery_live_changes: dcb.b 2048,0

 include "recovery_redraw_invalidate.s"
recovery_live_banks: dc.w $ffff

; Optional source-built phase stop, never original game state fabrication.
recovery_live_diagnostic_stop:
 movem.l a0,-(sp)
 lea recovery_live_report(pc),a0
 cmpi.l #recovery_live_stop_rti,16(a0)
 movem.l (sp)+,a0
 beq.s .stop
 rts
.stop:
 addq.l #4,sp
 move.l #1,8(a6)
 move.l sp,68(a6)
 bsr.l paula_adapter+8
 bra.l stop
