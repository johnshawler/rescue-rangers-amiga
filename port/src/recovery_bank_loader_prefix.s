; Bank2 9003 -> 8000. Save live OAM and object slots; issue first loader call.
; A0 RAM2048,A1 ctx8,A2 journal6,A3 immutable bank2[16384].
; SP>=2B prevents OAM backup from overwriting the actual 8D0A return frame.
; Other SP values reject inertly; no assumption about copied OAM contents.
; D0=1/-1, other registers preserved, native USER mode safe.
recovery_bank_loader_prefix:
 cmpi.w #$9003,(a1)
 bne.w .invalid
 cmpi.b #$2b,6(a1)
 blo.w .invalid
 movem.l d1-d7/a4,-(sp)
 moveq #0,d7
 move.b 6(a1),d7
 move.b $4d0(a0),$100(a0,d7.w)
 subq.b #1,d7
 move.b $4d1(a0),$100(a0,d7.w)
 subq.b #1,d7
 move.b #$90,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$0d,$100(a0,d7.w)
 ; Original 8D0A copies descending, including all original stores.
 moveq #$27,d1
.copy:
 move.b $200(a0,d1.w),$100(a0,d1.w)
 dbra d1,.copy
 addq.b #1,d7
 move.b #$f8,$200(a0)
 move.b #$f8,$204(a0)
 clr.b $4d0(a0)
 clr.b $4d1(a0)
 clr.b $fa(a0)
 clr.b $fc(a0)
 clr.b $fb(a0)
 clr.b $fd(a0)
 moveq #0,d1
 move.b $31(a0),d1
 move.b d1,d4
 lsr.b #6,d4
 andi.b #1,d4
 lsl.b #2,d1
 move.b d1,2(a1)
 move.b d1,4(a1)
 move.b d1,$100(a0,d7.w)
 subq.b #1,d7
 move.w d1,d2
 addi.w #$91f3,d2
 moveq #0,d3
 move.b $11f3(a3,d1.w),d3
 move.w d2,2(a2)
 move.b d3,4(a2)
 clr.b 5(a2)
 move.w #1,(a2)
 moveq #$33,d2
 tst.b d3
 bne.s .loaded
 moveq #9,d3
 moveq #$40,d2
.loaded:
 move.b d3,3(a1)
 andi.b #$7c,5(a1)
 or.b d4,5(a1)
 move.b d3,d4
 andi.b #$80,d4
 or.b d4,5(a1)
 move.b #$90,$100(a0,d7.w)
 subq.b #1,d7
 move.b d2,$100(a0,d7.w)
 subq.b #1,d7
 move.b d7,6(a1)
 move.w #$8000,(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d7/a4
 rts
.invalid:
 moveq #-1,d0
 rts
