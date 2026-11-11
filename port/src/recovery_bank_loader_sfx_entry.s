; Static ordinary bank3 command entry8003/80E1/80E9 through810D or8151.
; A0 RAM2048,A1 raw context8,A2 counted journal1926,A3 bank3 view16384.
; Commands00-EF, nonzero table count. Repeated subtraction and all original
; header/table reads preserved; zero count and F0+ reject before mutation.
; D0=1/-1; all other D/A preserved; USER mode; immutable disjoint buffers.
recovery_bank_loader_sfx_entry:
 cmpi.w #$8003,(a1)
 bne.w .invalid
 cmpi.b #$f0,2(a1)
 bhs.w .invalid
 tst.b $a00(a3)
 beq.w .invalid
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
 moveq #0,d5
 move.b 2(a1),d5
 move.b 5(a1),d4
 andi.b #$40,d4
.modulo:
 move.w #$8a00,d1
 move.b $a00(a3),d2
 bsr.w .publish
 cmp.b d2,d5
 bcs.s .lookup
 ; Original SEC/SBC reads the immutable header a second time.
 move.b $a00(a3),d2
 bsr.w .publish
 move.b d5,d4
 sub.b d2,d5
 move.b d4,d1
 eor.b d5,d1
 eor.b d2,d4
 and.b d1,d4
 andi.b #$80,d4
 lsr.b #1,d4
 bra.s .modulo
.lookup:
 moveq #0,d6
 btst #7,d5
 beq.s .carry_clear
 moveq #1,d6
.carry_clear:
 add.b d5,d5
 move.w #$8a04,d1
 add.w d5,d1
 move.b $a04(a3,d5.w),d2
 bsr.w .publish
 move.b d2,$c1(a0)
 move.b d2,d3
 move.w #$8a03,d1
 add.w d5,d1
 move.b $a03(a3,d5.w),d2
 bsr.w .publish
 move.b d2,$c2(a0)
 or.b d2,d3
 move.b d3,2(a1)
 move.b d5,3(a1)
 move.b d7,6(a1)
 andi.b #$3c,5(a1)
 or.b d4,5(a1)
 or.b d6,5(a1)
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
