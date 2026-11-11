; Static original bank2 $A025 translation. No runtime instruction decoding.
; A0 RAM2048, A1 context8 (PC.w,A,X,Y,rawP,SP,reserved), A2 journal16.
; Journal ordered address.word/value.byte/zero.byte, no header; untouched tail.
; D0 store count or -1 inert wrong-PC rejection. Other registers preserved.
; Valid disjoint buffers/code/native stack, live bank2 mapping required.
recovery_title_menu_countdown:
 cmpi.w #$a025,(a1)
 bne.w .invalid
 movem.l d1-d7/a3,-(sp)
 movea.l a2,a3
 moveq #0,d5
 moveq #0,d7
 move.b 6(a1),d7
 moveq #0,d6
 move.b 5(a1),d6
; SEC / SBC #1 low byte, then SBC #0 with propagated borrow.
 moveq #0,d3
 move.b $be(a0),d3
 moveq #1,d1
 bsr.w .subtract
 move.w #$be,d2
 andi.w #$ff,d2
 bsr.w .write
 moveq #0,d1
 btst #0,d6
 bne.s .no_borrow
 moveq #1,d1
.no_borrow:
 moveq #0,d3
 move.b $bf(a0),d3
 bsr.w .subtract
 move.w #$bf,d2
 bsr.w .write
 or.b $be(a0),d3
 bsr.w .nz
 move.w #$a000,(a1)
 tst.b d3
 bne.w .done
 moveq #1,d3
 bsr.w .nz
 moveq #$50,d2
 bsr.w .write
 move.w #$b8,d2
 bsr.w .write
 move.w #$a0bb,(a1)
 bra.w .done
; Binary SBC: D is preserved but never interpreted as BCD.
.subtract:
 andi.b #$3c,d6
 cmp.b d1,d3
 bcs.s .no_carry
 ori.b #1,d6
.no_carry:
 move.b d3,d0
 sub.b d1,d3
 eor.b d0,d1
 eor.b d3,d0
 and.b d0,d1
 andi.b #$80,d1
 beq.w .nz
 ori.b #$40,d6
 bra.w .nz

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
.write:
 move.b d3,(a0,d2.w)
 move.w d2,(a3)+
 move.b d3,(a3)+
 clr.b (a3)+
 addq.w #1,d5
 rts
.push:
 move.w d7,d2
 ori.w #$100,d2
 bsr.s .write
 subq.b #1,d7
 rts
.done:
 move.b d3,2(a1)
 move.b d6,5(a1)
 move.b d7,6(a1)
 move.l d5,d0
 movem.l (sp)+,d1-d7/a3
 rts
.invalid:
 moveq #-1,d0
 rts
