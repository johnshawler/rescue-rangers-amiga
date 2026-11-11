; Static bank3 810D..8151, Y=0. Zero header stops8152 before music init.
; A0 RAM2048,A1 raw context8,A2 journal6,A3 immutable bank3[16384].
; Valid disjoint buffers/live bank3 preconditions. Pointer8000..BFFF only.
; D0=1/-1; D1-D7/A0-A6 preserved; CCR scratch; rejection fully inert.
recovery_sfx_header_initialize:
 cmpi.w #$810d,(a1)
 bne.w .invalid
 tst.b 4(a1)
 bne.w .invalid
 cmpi.b #$80,$c2(a0)
 bcs.w .invalid
 cmpi.b #$c0,$c2(a0)
 bcc.w .invalid
 movem.l d1-d7,-(sp)
 moveq #0,d1
 move.b $c2(a0),d1
 lsl.w #8,d1
 move.b $c1(a0),d1
 move.w d1,2(a2)
 subi.w #$8000,d1
 move.b (a3,d1.w),d2
 move.b d2,4(a2)
 clr.b 5(a2)
 move.w #1,(a2)
 move.b 5(a1),d3
 andi.b #$7d,d3
 tst.b d2
 beq.w .zero
 addq.b #1,3(a1)
 move.b d2,$c4(a0)
 andi.b #$7f,d2
 andi.b #$fe,d3
 cmp.b $ce(a0),d2
 bcs.w .priority
 ori.b #1,d3
 move.b d2,d6
 sub.b $ce(a0),d6
 move.b d2,$ce(a0)
 tst.b d6
 bne.s .init
 tst.b $d6(a0)
 bpl.s .init
 tst.b $c4(a0)
 bmi.s .init
 clr.b $d7(a0)
.init:
 clr.b $d6(a0)
 move.b $c4(a0),d5
 move.b d5,d4
 add.b d4,d4
 move.b d4,$c4(a0)
 moveq #0,d4
 btst #7,d5
 beq.s .rotate
 move.b #$80,d4
.rotate:
 move.b d4,$d6(a0)
 beq.s .pointer
 move.b 3(a1),$d7(a0)
.pointer:
 addq.b #1,$c1(a0)
 move.b $c1(a0),d4
 move.b d4,$d0(a0)
 bne.s .high
 addq.b #1,$c2(a0)
.high:
 move.b $c2(a0),$d1(a0)
 clr.b $d2(a0)
 clr.b $d3(a0)
 clr.b $d4(a0)
 clr.b $d5(a0)
 moveq #$27,d4
.clear:
 clr.b $700(a0,d4.w)
 dbra d4,.clear
 move.b #$ff,4(a1)
 andi.b #$7c,d3
 ori.b #$80,d3
 clr.b 2(a1)
 move.b d3,5(a1)
 move.w #$8151,(a1)
 bra.s .done
.priority:
 move.b d2,2(a1)
 sub.b $ce(a0),d2
 andi.b #$7c,d3
 andi.b #$80,d2
 or.b d2,d3
 move.b d3,5(a1)
 move.w #$8151,(a1)
 bra.s .done
.zero:
 ori.b #2,d3
 clr.b 2(a1)
 move.b d3,5(a1)
 move.w #$8152,(a1)
.done:
 movem.l (sp)+,d1-d7
 moveq #1,d0
 rts
.invalid:
 moveq #-1,d0
 rts
