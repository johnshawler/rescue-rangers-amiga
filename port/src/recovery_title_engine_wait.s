; Live bank2 A000 -> FF04 through A022 JSR for no menu-edge input.
; Only RAM14 & $33 == 0 supported; all other input or PC rejects inertly.
; A0 RAM2048,A1 context8,A2 journal8; wrapped page-one stack preserved.
; Journal address.word/value.byte/zero.byte, no header. D0=2/-1.
; No arithmetic, callback, queue consumption, or scheduling is synthesized.
recovery_title_engine_wait:
 cmpi.w #$a000,(a1)
 bne.s .invalid
 movem.l d1-d2,-(sp)
 move.b $14(a0),d1
 andi.b #$33,d1
 bne.s .unsupported
 moveq #0,d1
 move.b 6(a1),d1
 move.w d1,d2
 addi.w #$100,d2
 move.b #$a0,(a0,d2.w)
 move.w d2,(a2)
 move.b #$a0,2(a2)
 clr.b 3(a2)
 subq.b #1,d1
 move.w d1,d2
 addi.w #$100,d2
 move.b #$24,(a0,d2.w)
 move.w d2,4(a2)
 move.b #$24,6(a2)
 clr.b 7(a2)
 subq.b #1,d1
 move.b d1,6(a1)
 move.w #$ff04,(a1)
 clr.b 2(a1)
 andi.b #$7d,5(a1)
 ori.b #2,5(a1)
 moveq #2,d0
 movem.l (sp)+,d1-d2
 rts
.unsupported:
 movem.l (sp)+,d1-d2
.invalid:
 moveq #-1,d0
 rts
