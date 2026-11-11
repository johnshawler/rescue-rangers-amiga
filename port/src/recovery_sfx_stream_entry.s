; Static SFX entry8224 through parameter/duration setup and JSR8006.
; Signed commands stop8235, loop commands8249; no opcode interpreter.
; A0 RAM2048 A1 rawcontext8 A2 journal18 A3 bank3[16384].
; Pointer8000..BFFC for zero duration (four-read maximum); live bank3.
; Nonzero duration requires wrapped805F frame and consumes RTS to8060.
; Disjoint valid buffers; D0=1/-1; D1-D7/A0-A6 preserved, CCR scratch.
recovery_sfx_stream_entry:
 movem.l d1-d7,-(sp)
 cmpi.w #$8224,(a1)
 bne.w .invalid
 moveq #0,d4
 move.b 6(a1),d4
 tst.b $d3(a0)
 bne.w .checkreturn
 cmpi.b #$80,$d1(a0)
 bcs.w .invalid
 cmpi.b #$c0,$d1(a0)
 bcc.w .invalid
 cmpi.b #$bf,$d1(a0)
 bne.s .accepted
 cmpi.b #$fd,$d0(a0)
 bcc.w .invalid
.accepted:
 clr.w (a2)
 move.b 5(a1),d3
 moveq #0,d6
 moveq #2,d7
 move.b #$2f,d5
 bsr.w .fetch
 move.b d2,$c4(a0)
 ; ASL A
 andi.b #$7c,d3
 btst #7,d2
 beq.s .positive
 ori.b #1,d3
.positive:
 add.b d2,d2
 bsr.w .nz
 move.w #$8235,d1
 btst #0,d3
 bne.w .finish
 ; LSR C4
 bsr.w .shiftc4
 move.w #$8249,d1
 btst #0,d3
 bne.w .finish
 ; parameter bit1
 bsr.w .shiftc4
 btst #0,d3
 beq.s .bit2
 move.b #$7e,d5
 bsr.w .fetch
 move.b d2,$d4(a0)
.bit2:
 bsr.w .shiftc4
 btst #0,d3
 beq.s .duration
 move.b #$87,d5
 bsr.w .fetch
 move.b d2,$d2(a0)
.duration:
 move.b #$8c,d5
 bsr.w .fetch
 move.b d2,$d3(a0)
 move.b d2,$c1(a0)
 move.b $d4(a0),d2
 bsr.w .nz
 move.b d2,$c4(a0)
 move.b #$82,$100(a0,d4.w)
 subq.b #1,d4
 move.b #$97,$100(a0,d4.w)
 subq.b #1,d4
 move.w #$8006,d1
 bra.w .finish
.checkreturn:
 addq.b #1,d4
 cmpi.b #$5f,$100(a0,d4.w)
 bne.w .invalid
 addq.b #1,d4
 cmpi.b #$80,$100(a0,d4.w)
 bne.w .invalid
 clr.w (a2)
 move.b 5(a1),d3
 move.b $d3(a0),d2
 subq.b #1,$d3(a0)
 subq.b #1,$d5(a0)
 move.b d2,d5
 move.b $d5(a0),d2
 bsr.w .nz
 move.b d5,d2
 move.w #$8060,d1
.finish:
 move.w d1,(a1)
 move.b d2,2(a1)
 move.b d3,5(a1)
 move.b d4,6(a1)
 movem.l (sp)+,d1-d7
 moveq #1,d0
 rts
.invalid:
 movem.l (sp)+,d1-d7
 moveq #-1,d0
 rts
.nz:
 andi.b #$7d,d3
 tst.b d2
 bne.s .nonzero
 ori.b #2,d3
 rts
.nonzero:
 bpl.s .nzdone
 ori.b #$80,d3
.nzdone:
 rts
.shiftc4:
 andi.b #$7c,d3
 move.b $c4(a0),d1
 lsr.b #1,d1
 bcc.s .nocarry
 ori.b #1,d3
.nocarry:
 move.b d1,$c4(a0)
 bne.s .shiftdone
 ori.b #2,d3
.shiftdone:
 rts
.fetch:
 ; authentic JSR8358, LDY0, resource read, pointer INC, RTS
 move.b #$82,$100(a0,d4.w)
 subq.b #1,d4
 move.b d5,$100(a0,d4.w)
 subq.b #1,d4
 clr.b 4(a1)
 moveq #0,d1
 move.b $d1(a0),d1
 lsl.w #8,d1
 move.b $d0(a0),d1
 move.w d1,(a2,d7.w)
 subi.w #$8000,d1
 move.b (a3,d1.w),d2
 move.b d2,2(a2,d7.w)
 clr.b 3(a2,d7.w)
 addq.w #1,d6
 move.w d6,(a2)
 addq.w #4,d7
 addq.b #1,$d0(a0)
 bne.s .fetchlow
 addq.b #1,$d1(a0)
 move.b d2,d1
 move.b $d1(a0),d2
 bra.s .fetchflags
.fetchlow:
 move.b d2,d1
 move.b $d0(a0),d2
.fetchflags:
 bsr.w .nz
 move.b d1,d2
 addq.b #2,d4
 rts
