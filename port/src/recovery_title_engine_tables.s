; C5D1 -> A000. Static native title table setup and original JSR.
; A0 RAM2048, A1 context8, A2 journal362, A3 fixed PRG bank7[16384].
; Journal count.word then address.word/value.byte/zero.byte resource reads.
; D0=1/-1; D1-D7/A0-A6 preserved. Buffers disjoint/exclusive. No interleave.
recovery_title_engine_tables:
 cmpi.w #$c5d1,(a1)
 bne.w .invalid
 movem.l d1-d4/a4,-(sp)
 clr.w (a2)
 lea 2(a2),a4
 moveq #29,d4
.first:
 move.w #$d657,d1
 add.w d4,d1
 bsr.s .read
 move.b d2,$340(a0,d4.w)
 subq.b #1,d4
 bpl.s .first
 moveq #29,d4
.second:
 move.w #$c73f,d1
 add.w d4,d1
 bsr.s .read
 move.b d2,$5a0(a0,d4.w)
 move.w #$c75d,d1
 add.w d4,d1
 bsr.s .read
 move.b d2,$5d0(a0,d4.w)
 subq.b #1,d4
 bpl.s .second
 move.b #$84,$be(a0)
 move.b #3,$bf(a0)
 moveq #0,d3
 move.b 6(a1),d3
 move.b #$c5,$100(a0,d3.w)
 subq.b #1,d3
 move.b #$f7,$100(a0,d3.w)
 subq.b #1,d3
 move.b d3,6(a1)
 move.w #$a000,(a1)
 move.b #3,2(a1)
 move.b #$ff,3(a1)
 move.b #$ff,4(a1)
 andi.b #$7d,5(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d4/a4
 rts
.invalid:
 moveq #-1,d0
 rts
.read:
 move.w d1,d3
 subi.w #$c000,d3
 moveq #0,d2
 move.b (a3,d3.w),d2
 move.w d1,(a4)+
 move.b d2,(a4)+
 clr.b (a4)+
 addq.w #1,(a2)
 rts
