; Static 8151 RTS, 80E6 DEC/RTS, C0F3 empty queue through C0F6.
; Separate bridge, not a change to the frozen C0=01 combined tail.
; A0 RAM2048 A1 raw context8 A2 journal2. No resource reads.
; Require genuine 80E5/C0F2 wrapped frames, DB<8, empty queue.
; Every C0/raw P/SP accepted. Original stack reads and C0 write retained.
recovery_state_menu_sfx_tail:
 movem.l d1-d4,-(sp)
 cmpi.w #$8151,(a1)
 bne.w .invalid
 moveq #0,d1
 move.b $db(a0),d1
 cmpi.b #8,d1
 bcc.w .invalid
 cmpi.b #$88,$dc(a0,d1.w)
 bne.w .invalid
 moveq #0,d2
 move.b 6(a1),d2
 addq.b #1,d2
 cmpi.b #$e5,$100(a0,d2.w)
 bne.w .invalid
 addq.b #1,d2
 cmpi.b #$80,$100(a0,d2.w)
 bne.w .invalid
 addq.b #1,d2
 cmpi.b #$f2,$100(a0,d2.w)
 bne.w .invalid
 addq.b #1,d2
 cmpi.b #$c0,$100(a0,d2.w)
 bne.w .invalid
 clr.w (a2)
 subq.b #1,$c0(a0)
 move.b d2,6(a1)
 move.b d1,3(a1)
 move.b #$88,2(a1)
 andi.b #$7c,5(a1)
 ori.b #3,5(a1)
 move.w #$c0f6,(a1)
 moveq #1,d0
.done:
 movem.l (sp)+,d1-d4
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
