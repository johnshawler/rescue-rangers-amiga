; Static original bank2 $A000 translation. No runtime instruction decoding.
; A0 RAM2048, A1 context8 (PC.w,A,X,Y,rawP,SP,reserved), A2 journal16.
; Journal ordered address.word/value.byte/zero.byte, no header; untouched tail.
; D0 store count or -1 inert wrong-PC rejection. Other registers preserved.
; Valid disjoint buffers/code/native stack, live bank2 mapping required.
recovery_title_menu_dispatch:
 cmpi.w #$a000,(a1)
 bne.w .invalid
 movem.l d1-d7/a3,-(sp)
 movea.l a2,a3
 moveq #0,d5
 moveq #0,d7
 move.b 6(a1),d7
 moveq #0,d6
 move.b 5(a1),d6
 move.b $14(a0),d3
 andi.b #$10,d3
 bne.w .confirm
 move.b $14(a0),d3
 andi.b #$20,d3
 bne.s .toggle
 move.b $14(a0),d3
 andi.b #3,d3
 beq.w .wait
 andi.b #2,d3
 beq.s .right
 moveq #0,d3
 bra.s .selection
.right:
 moveq #1,d3
 bra.s .selection
.toggle:
 move.b $50(a0),d3
 eori.b #1,d3
.selection:
 moveq #$50,d2
 bsr.w .write
 move.b #$28,3(a1)
 tst.b d3
 beq.s .cursor
 move.b #$88,3(a1)
.cursor:
 move.b 3(a1),d3
 move.w #$203,d2
 bsr.w .write
 moveq #$27,d3
 bsr.w .nz
 move.b #$a0,d3
 bsr.w .push
 move.b #$54,d3
 bsr.w .push
 moveq #$27,d3
 move.w #$f379,(a1)
 bra.w .done
.confirm:
 move.b $50(a0),d3
 bsr.w .nz
 move.w #$a0bb,(a1)
 tst.b d3
 bne.w .done
 move.w #$a05c,(a1)
 bra.w .done
.wait:
 moveq #0,d3
 bsr.w .nz
 move.b #$a0,d3
 bsr.w .push
 move.b #$24,d3
 bsr.w .push
 moveq #0,d3
 move.w #$ff04,(a1)
 bra.w .done

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
