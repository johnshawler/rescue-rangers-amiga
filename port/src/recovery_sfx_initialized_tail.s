; Static 8151 RTS through nested return, empty queue, tick phase, JSR8224.
; Require PC8151,C0=1,nonzero D0/D1,DB<8,empty queue and original two
; wrapped frames 80E5/C0F2. Otherwise inert. A0 RAM,A1 context,A2 journal2.
; No resource access. Every P/SP accepted. D1-D7/A0-A6 preserved.
recovery_sfx_initialized_tail:
 movem.l d1-d5,-(sp)
 cmpi.w #$8151,(a1)
 bne.w .invalid
 cmpi.b #1,$c0(a0)
 bne.w .invalid
 move.b $d0(a0),d1
 or.b $d1(a0),d1
 beq.w .invalid
 moveq #0,d2
 move.b $db(a0),d2
 cmpi.b #8,d2
 bcc.w .invalid
 cmpi.b #$88,$dc(a0,d2.w)
 bne.w .invalid
 moveq #0,d3
 move.b 6(a1),d3
 addq.b #1,d3
 cmpi.b #$e5,$100(a0,d3.w)
 bne.w .invalid
 addq.b #1,d3
 cmpi.b #$80,$100(a0,d3.w)
 bne.w .invalid
 addq.b #1,d3
 cmpi.b #$f2,$100(a0,d3.w)
 bne.w .invalid
 addq.b #1,d3
 cmpi.b #$c0,$100(a0,d3.w)
 bne.w .invalid
 clr.w (a2)
 clr.b $c0(a0)
 move.b #$c0,$100(a0,d3.w)
 subq.b #1,d3
 move.b #$f8,$100(a0,d3.w)
 subq.b #1,d3
 clr.b $c3(a0)
 move.b #4,$c0(a0)
 move.b #$80,$100(a0,d3.w)
 subq.b #1,d3
 move.b #$5f,$100(a0,d3.w)
 subq.b #1,d3
 move.w #$8224,(a1)
 move.b d1,2(a1)
 move.b d2,3(a1)
 move.b #4,4(a1)
 andi.b #$3c,5(a1)
 andi.b #$80,d1
 or.b d1,5(a1)
 move.b d3,6(a1)
 movem.l (sp)+,d1-d5
 moveq #1,d0
 rts
.invalid:
 movem.l (sp)+,d1-d5
 moveq #-1,d0
 rts
