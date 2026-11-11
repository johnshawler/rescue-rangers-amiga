; Genuine fixed-bank F392 sprite caller, no fabricated bank or return frames.
; RAM/context ABI, RAM-only journal. IDs91 entry,92 JSR,93 yield,95 PLA.
; SP wraps; 97 must be divisible by4 for original C21E to terminate.
recovery_bank_loader_object_bridge:
 cmpi.w #$f392,(a1)
 beq.s .entry
 cmpi.w #$f39f,(a1)
 beq.w .call
 cmpi.w #$f3a2,(a1)
 beq.w .yield
 cmpi.w #$f3a9,(a1)
 beq.w .pop
 bra.w .invalid
.entry:
 move.b $97(a0),d0
 andi.b #3,d0
 bne.w .invalid
 movem.l d1-d2,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 move.b $f1(a0),$100(a0,d1.w)
 subq.b #1,d1
 addq.b #1,$9a(a0)
 move.b #$f3,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$99,$100(a0,d1.w)
 moveq #0,d2
 move.b $97(a0),d2
 cmpi.b #4,d2
 bne.s .hide
 move.b #$f8,$200(a0)
.hide:
 move.b #$f8,$200(a0,d2.w)
 addq.b #4,d2
 bne.s .hide
 addq.b #1,d1
 move.b #$f3,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$9e,$100(a0,d1.w)
 subq.b #1,d1
 move.b d1,6(a1)
 move.b #5,2(a1)
 clr.b 3(a1)
 andi.b #$7c,5(a1)
 ; CPX #4 determines carry; subsequent INX/LDA preserve it.
 cmpi.b #4,$97(a0)
 blo.s .no_c
 ori.b #1,5(a1)
.no_c:
 move.w #$ff53,(a1)
 bra.w .done
.call:
 movem.l d1-d2,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 move.b #$f3,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$a1,$100(a0,d1.w)
 subq.b #1,d1
 move.b d1,6(a1)
 move.w #$8000,(a1)
 bra.s .done
.yield:
 movem.l d1-d2,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 clr.b $9a(a0)
 move.b #$f3,$100(a0,d1.w)
 subq.b #1,d1
 move.b #$a8,$100(a0,d1.w)
 subq.b #1,d1
 move.b d1,6(a1)
 clr.b 2(a1)
 andi.b #$7d,5(a1)
 ori.b #2,5(a1)
 move.w #$ff04,(a1)
 bra.s .done
.pop:
 movem.l d1-d2,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 addq.b #1,d1
 move.b $100(a0,d1.w),d2
 move.b d2,2(a1)
 move.b d1,6(a1)
 andi.b #$7d,5(a1)
 tst.b d2
 bne.s .nonzero
 ori.b #2,5(a1)
.nonzero:
 andi.b #$80,d2
 or.b d2,5(a1)
 move.w #$ff53,(a1)
.done:
 moveq #1,d0
 movem.l (sp)+,d1-d2
 rts
.invalid:
 moveq #-1,d0
 rts
