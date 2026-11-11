; Static A07B cursor read/JSR, F379 sound ring request/RTS, A086 yield JSR.
; A0 RAM2048; A1 raw context8; A2 resource journal6; A3 immutable bank2[16384].
; Journal count.word/address.word/value.byte/zero.byte, untouched tail.
; D0=1 or -1 inert invalid PC. D1-D7/A0-A6 preserved. CCR scratch.
; Valid disjoint buffers/native stack and live bank2 mapping required for A07B.
; F379 accepts all DA byte values, including zero-page aliases, as original does.
recovery_character_cursor_sound_request:
 cmpi.w #$a07b,(a1)
 beq.s .accept
 cmpi.w #$f379,(a1)
 beq.s .accept
 cmpi.w #$a086,(a1)
 bne.w .invalid
.accept:
 movem.l d1-d7,-(sp)
 clr.w (a2)
 moveq #0,d7
 move.b 6(a1),d7
 moveq #0,d6
 move.b 5(a1),d6
 move.b 2(a1),d3
 cmpi.w #$f379,(a1)
 beq.w .queue
 cmpi.w #$a086,(a1)
 beq.w .yield
 moveq #0,d1
 move.b 4(a1),d1
 move.b $20e1(a3,d1.w),d3
 addi.w #$a0e1,d1
 move.w d1,2(a2)
 move.b d3,4(a2)
 clr.b 5(a2)
 move.w #1,(a2)
 move.b d3,$203(a0)
 moveq #$27,d3
 bsr.w .nz
 move.b #$a0,d2
 bsr.w .push
 move.b #$85,d2
 bsr.w .push
 move.w #$f379,(a1)
 bra.w .done
.yield:
 move.b #$a0,d2
 bsr.w .push
 move.b #$88,d2
 bsr.w .push
 move.w #$ff04,(a1)
 bra.w .done
.queue:
 move.b 3(a1),(a0)
 moveq #0,d1
 move.b $da(a0),d1
 move.b d3,1(a0)
 move.w d1,d4
 addi.b #$dc,d4
 andi.w #$ff,d4
 move.b (a0,d4.w),d3
 andi.b #$7c,d6
 cmpi.b #$88,d3
 bcs.s .nocarry
 ori.b #1,d6
.nocarry:
 move.b d3,d2
 subi.b #$88,d3
 bsr.s .nz
 move.b d2,d3
 btst #1,d6
 beq.s .restorex
 move.b 1(a0),d3
 move.b d3,(a0,d4.w)
 addq.b #1,d1
 move.b d1,d3
 andi.b #7,d3
 move.b d3,$da(a0)
 ; AND supplies NZ but LDX below supplies final NZ.
.restorex:
 move.b (a0),d3
 move.b d3,3(a1)
 bsr.s .nz
 ; LDX does not change A. Reload actual accumulator from branch outcome.
 ; Original saved comparison value distinguishes the enqueue branch.
 cmpi.b #$88,d2
 beq.s .accepted
 move.b d2,d3
 bra.s .return
.accepted:
 move.b d1,d3
 andi.b #7,d3
.return:
 addq.b #1,d7
 moveq #0,d4
 move.b $100(a0,d7.w),d4
 addq.b #1,d7
 moveq #0,d5
 move.b $100(a0,d7.w),d5
 lsl.w #8,d5
 or.w d4,d5
 addq.w #1,d5
 move.w d5,(a1)
.done:
 move.b d3,2(a1)
 move.b d6,5(a1)
 move.b d7,6(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d7
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
 move.b d2,$100(a0,d7.w)
 subq.b #1,d7
 rts
.invalid:
 moveq #-1,d0
 rts
