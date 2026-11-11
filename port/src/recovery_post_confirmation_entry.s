; Newly derived static game control flow: C5F8 -> 9000 or C63B,
; bank-2 9000 -> F3C9, fixed F3C9 -> C274 (before palette fade).
; A0 RAM2048; A1 PC.word,A,X,Y,rawP,SP,reserved; A2 journal12.
; Ordered RAM stores: address.word,value.byte,zero, no header.
; D0 count, or -1 inert unsupported PC. D1-D7/A0-A6 preserved.
; Valid disjoint buffers/native stack required; 9000 requires bank2.
; No instruction decoding, fabricated returns, hardware effects or assets.
recovery_post_confirmation_entry:
 cmpi.w #$c5f8,(a1)
 beq.s .valid
 cmpi.w #$9000,(a1)
 beq.s .valid
 cmpi.w #$f3c9,(a1)
 bne.w .invalid
.valid:
 movem.l d1-d7/a3,-(sp)
 movea.l a2,a3
 moveq #0,d5
 moveq #0,d7
 move.b 6(a1),d7
 moveq #0,d6
 move.b 5(a1),d6
 cmpi.w #$9000,(a1)
 beq.w .scene
 cmpi.w #$f3c9,(a1)
 beq.w .fade
 move.b $b8(a0),d3
 bsr.w .nz
 tst.b d3
 beq.s .normal
 move.b $bd(a0),d3
 bsr.w .nz
 moveq #$31,d2
 bsr.w .write
 move.b d3,d4
 move.b #$c6,d3
 bsr.w .push
 move.b #$10,d3
 bsr.w .push
 move.w #$c63b,(a1)
 bra.w .done
.normal:
 moveq #$0b,d3
 bsr.w .nz
 moveq #$31,d2
 bsr.w .write
 move.b d3,d4
 move.b #$c6,d3
 bsr.w .push
 move.b #$09,d3
 bsr.w .push
 move.w #$9000,(a1)
 bra.w .done
.scene:
 move.b 2(a1),d4
 move.b #$90,d3
 bsr.w .push
 moveq #2,d3
 bsr.w .push
 move.w #$f3c9,(a1)
 bra.w .done
.fade:
 move.b $f1(a0),d3
 bsr.w .nz
 move.b d3,d4
 bsr.w .push
 move.b #$f3,d3
 bsr.w .push
 move.b #$ce,d3
 bsr.w .push
 move.w #$c274,(a1)
.done:
 move.b d4,2(a1)
 move.b d6,5(a1)
 move.b d7,6(a1)
 move.l d5,d0
 movem.l (sp)+,d1-d7/a3
 rts
.nz:
 andi.b #$7d,d6
 tst.b d3
 bne.s .nonzero
 ori.b #2,d6
.nonzero:
 move.b d3,d0
 andi.b #$80,d0
 or.b d0,d6
 rts
.push:
 move.w d7,d2
 ori.w #$100,d2
 bsr.s .write
 subq.b #1,d7
 rts
.write:
 move.b d3,(a0,d2.w)
 move.w d2,(a3)+
 move.b d3,(a3)+
 clr.b (a3)+
 addq.w #1,d5
 rts
.invalid:
 moveq #-1,d0
 rts
