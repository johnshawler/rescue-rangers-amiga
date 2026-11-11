; Static bank3 $8003/$80E1/$80E9 through pointer setup, before $810D header.
; A0 RAM2048,A1 raw context8,A2 resource journal14,A3 immutable bank3[16384].
; PC8003,A27,resource[0A00]>27 required, otherwise inert rejection.
; Accept every raw P/SP/C0 and pointer, including zero or outside bank3: no
; pointer dereference occurs. Zero pointer stops8151; nonzero stops810D.
; D0=1/-1; D1-D7/A0-A6 preserved; CCR scratch. Valid disjoint buffers required.
recovery_sfx27_table_dispatch:
 cmpi.w #$8003,(a1)
 bne.w .invalid
 cmpi.b #$27,2(a1)
 bne.w .invalid
 cmpi.b #$28,$a00(a3)
 bcs.w .invalid
 movem.l d1-d7/a4,-(sp)
 clr.w (a2)
 lea 2(a2),a4
 addq.b #1,$c0(a0)
 moveq #0,d7
 move.b 6(a1),d7
 move.b #$80,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$e5,$100(a0,d7.w)
 subq.b #1,d7
 move.w #$8a00,d1
 move.b $a00(a3),d2
 bsr.s .publish
 move.w #$8a52,d1
 move.b $a52(a3),d2
 bsr.s .publish
 move.b d2,$c1(a0)
 move.b d2,d3
 move.w #$8a51,d1
 move.b $a51(a3),d2
 bsr.s .publish
 move.b d2,$c2(a0)
 or.b d2,d3
 move.b d3,2(a1)
 move.b #$4e,3(a1)
 move.b d7,6(a1)
 andi.b #$7c,5(a1)
 ori.b #2,5(a1)
 tst.b d3
 beq.s .zero
 move.b #0,4(a1)
 move.w #$810d,(a1)
 bra.s .done
.zero:
 move.w #$8151,(a1)
.done:
 movem.l (sp)+,d1-d7/a4
 moveq #1,d0
 rts
.publish:
 move.w d1,(a4)+
 move.b d2,(a4)+
 clr.b (a4)+
 addq.w #1,(a2)
 rts
.invalid:
 moveq #-1,d0
 rts
