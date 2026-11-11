; Static original A06C-A07B/A08C-A0BB and A089 continuation.
; A0 RAM2048, A1 raw context8, A2 ordered store journal196 (no header).
; D0 store count; -1 inert unsupported PC. D1-D7/A0-A6 preserved.
; Direction ends BEFORE bank2 resource A07B; no fabricated cursor/audio.
; Disjoint valid buffers/native stack and authentic bank2 mapping required.
recovery_character_selection_dispatch:
 cmpi.w #$a089,(a1)
 beq.w .resume
 cmpi.w #$a06c,(a1)
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
 andi.b #3,d3
 beq.w .wait
 andi.b #1,d3
 bsr.w .nz
 move.b d3,4(a1)
 move.w #$a07b,(a1)
 bra.w .done
.wait:
 bsr.w .nz
 move.b #$a0,d3
 bsr.w .push
 move.b #$88,d3
 bsr.w .push
 moveq #0,d3
 move.w #$ff04,(a1)
 bra.w .done
.confirm:
 move.b $203(a0),d3
 bsr.w .nz
 andi.b #$7c,d6
 cmpi.b #$28,d3
 bcs.s .cmp_nc
 ori.b #1,d6
.cmp_nc:
 move.b d3,d4
 subi.b #$28,d3
 bsr.w .nz
 move.b d4,d3
 move.w #$a0bb,(a1)
 btst #1,d6
 bne.w .done
 moveq #$1c,d4
.swap:
 move.b $340(a0,d4.w),d3
 bsr.w .push
 move.b $341(a0,d4.w),d3
 move.w d4,d2
 addi.w #$340,d2
 bsr.w .write
 addq.b #1,d7
 move.w d7,d2
 ori.w #$100,d2
 move.b (a0,d2.w),d3
 move.w d4,d2
 addi.w #$341,d2
 bsr.w .write
 subq.b #2,d4
 bpl.s .swap
 move.b d4,3(a1)
 move.w #$5a2,d2
 move.b #$8d,d3
 bsr.w .write
 addq.w #2,d2
 move.b #$8a,d3
 bsr.w .write
 addq.w #2,d2
 move.b #$95,d3
 bsr.w .write
 addq.w #2,d2
 move.b #$8e,d3
 bsr.w .write
 bsr.w .nz
 bra.w .done
.resume:
 move.w #$a06c,(a1)
 moveq #0,d0
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
