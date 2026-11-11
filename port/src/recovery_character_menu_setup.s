; Static bank2 A05C -> FF04 character-menu table copy and real yield JSR.
; A0 RAM2048, A1 context8, A2 journal106, A3 immutable bank2[16384].
; Journal count.word + resource address.word/value.byte/zero.byte. Tail untouched.
; D0=1 success/-1 inert wrong PC. D1-D7/A0-A6 preserved. Disjoint valid buffers.
; Caller supplies live bank2 mapping; no ROM instructions decoded or embedded.
recovery_character_menu_setup:
 cmpi.w #$a05c,(a1)
 bne.w .invalid
 movem.l d1-d4/a4,-(sp)
 lea 2(a2),a4
 clr.w (a2)
 moveq #23,d1
 moveq #0,d4
.copy:
 move.b $20c9(a3,d1.w),d2
 move.w d1,d3
 addi.w #$a0c9,d3
 move.w d3,(a4)+
 move.b d2,(a4)+
 clr.b (a4)+
 addq.w #1,d4
 move.w d4,(a2)
 move.b d2,$360(a0,d1.w)
 dbra d1,.copy
 move.b d2,2(a1)
 move.b #$ff,3(a1)
 andi.b #$7d,5(a1)
 ori.b #$80,5(a1)
 move.b #$ff,$19(a0)
 moveq #0,d1
 move.b 6(a1),d1
 move.b #$a0,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$6b,$100(a0,d1.w)
 subq.b #1,d1
 move.b d1,6(a1)
 move.w #$ff04,(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d4/a4
 rts
.invalid:
 moveq #-1,d0
 rts
