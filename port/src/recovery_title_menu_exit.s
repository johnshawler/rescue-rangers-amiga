; Static original bank2 $A0BB translation. No runtime instruction decoding.
; A0 RAM2048, A1 context8 (PC.w,A,X,Y,rawP,SP,reserved), A2 journal256.
; Journal ordered address.word/value.byte/zero.byte, no header; untouched tail.
; D0 store count or -1 inert wrong-PC rejection. Other registers preserved.
; Valid disjoint buffers/code/native stack, live bank2 mapping required.
recovery_title_menu_exit:
 cmpi.w #$a0bb,(a1)
 bne.w .invalid
 movem.l d1-d7/a3,-(sp)
 movea.l a2,a3
 moveq #0,d5
 moveq #0,d7
 move.b 6(a1),d7
 moveq #0,d6
 move.b 5(a1),d6
 moveq #0,d4
 move.b #$f8,d3
.hide:
 move.w d4,d2
 addi.w #$200,d2
 bsr.w .write
 addq.b #4,d4
 bne.s .hide
; Last INX wraps X to zero, leaving N=0,Z=1 and A=F8.
 clr.b 3(a1)
 andi.b #$7d,d6
 ori.b #2,d6
 addq.b #1,d7
 move.w d7,d2
 ori.w #$100,d2
 moveq #0,d4
 move.b (a0,d2.w),d4
 addq.b #1,d7
 move.w d7,d2
 ori.w #$100,d2
 moveq #0,d1
 move.b (a0,d2.w),d1
 lsl.w #8,d1
 or.w d1,d4
 addq.w #1,d4
 move.w d4,(a1)
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
