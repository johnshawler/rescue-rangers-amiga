; Static original title cursor-sound continuation: A055 JMP A022; JSR FF04.
; Original A/P/X/Y untouched; push original return A024 then enter FF04.
; New helper72 has no device journal. Rejects before writes on bad state.
recovery_live_dispatch:
 cmpi.w #$a055,(a1)
 bne.l recovery_state_menu_sfx
 tst.l d2
 bne.s .bad
 cmpi.w #$d501,10(a4)
 bne.s .bad
 tst.w 4(a4)
 bne.s .bad
 cmpi.b #$1e,(a4)
 bne.s .bad
 cmpi.b #2,3(a4)
 bne.s .bad
 tst.b $91(a0)
 bne.s .bad
 cmpi.b #2,$80(a0)
 bne.s .bad
 movem.l d3-d4,-(sp)
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.s .restore_bad
 moveq #0,d3
 move.b 6(a1),d3
 move.w d3,d4
 ori.w #$100,d4
 move.b #$a0,(a0,d4.w)
 subq.b #1,d3
 move.w d3,d4
 ori.w #$100,d4
 move.b #$24,(a0,d4.w)
 subq.b #1,d3
 move.b d3,6(a1)
 move.w #$ff04,(a1)
 move.w #72,6(a4)
 clr.w 8(a4)
 movem.l (sp)+,d3-d4
 moveq #1,d0
 rts
.restore_bad:
 movem.l (sp)+,d3-d4
.bad:
 moveq #-1,d0
 rts
