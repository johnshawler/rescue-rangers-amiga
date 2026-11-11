; Static C5C0 -> C5C5: bank-2 loader8000, fixed caller X=2.
; A0 RAM2048,A1 context8,A2 journal32770,A3 immutable bank2[16384].
; Requires live mapper bank2/mode3/empty latch. No interrupt interleaving.
; Preflight requires stream wholly within bank, <=4094 stream bytes including
; terminator; rejected PC/stream is inert. Resource must not change mid-call.
; Journal count.word, address.word/value.byte/kind.byte. Kind0 resource read,
; kind1 PPU write, kind2 discarded PPU status read (value normalized to zero).
; Preflight reads are validation only; semantic reads are explicitly journaled.
; D0=1 success/-1 unsupported; other registers preserved, native CCR scratch.
recovery_startup_resource_load:
 cmpi.w #$c5c0,(a1)
 bne.w .invalid_entry
 movem.l d1-d7/a4-a5,-(sp)
 moveq #0,d1
 move.b $49(a3),d1
 lsl.w #8,d1
 move.b $3f(a3),d1
 subi.l #$8000,d1
 moveq #0,d7
.validate:
 cmpi.l #$4000,d1
 bhs.w .invalid
 addq.w #1,d7
 cmpi.w #4094,d7
 bhi.w .invalid
 move.b (a3,d1.l),d2
 addq.l #1,d1
 tst.b d2
 beq.s .accepted
 ; Address-low plus count must remain inside view and stream budget.
 move.l d1,d3
 addq.l #1,d3
 cmpi.l #$4000,d3
 bhs.w .invalid
 moveq #0,d2
 move.b (a3,d3.l),d2
 cmpi.w #128,d2
 bls.s .count_valid
 moveq #0,d2
.count_valid:
 addq.w #1,d2
 addq.l #2,d1
 addq.w #2,d7
 add.w d2,d7
 cmpi.w #4094,d7
 bhi.w .invalid
 add.l d2,d1
 ; Next loop checks final data bound and terminator, before any mutation.
 bra.s .validate
.accepted:
 clr.w (a2)
 lea 2(a2),a4
 moveq #0,d7
 move.b 6(a1),d7
 move.b #$c5,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$c4,$100(a0,d7.w)
 subq.b #1,d7
 move.w #$803f,d1
 bsr.w .resource
 move.b d2,(a0)
 move.w #$8049,d1
 bsr.w .resource
 move.b d2,1(a0)
 moveq #0,d4
.header:
 move.w #$2002,d1
 moveq #0,d2
 moveq #2,d3
 bsr.w .event
 bsr.w .stream
 tst.b d2
 beq.w .finish
 move.w #$2006,d1
 bsr.w .ppu
 moveq #$18,d6
 bsr.w .advance
 bsr.w .stream
 move.w #$2006,d1
 bsr.w .ppu
 moveq #$20,d6
 bsr.w .advance
 bsr.w .stream
 move.b d2,2(a0)
 moveq #$27,d6
 bsr.w .advance
.data:
 bsr.w .stream
 move.w #$2007,d1
 bsr.w .ppu
 moveq #$2f,d6
 bsr.w .advance
 subq.b #1,2(a0)
 bpl.s .data
 bra.w .header
.finish:
 move.w #$c5c5,(a1)
 clr.b 2(a1)
 move.b #2,3(a1)
 move.b d4,4(a1)
 andi.b #$7d,5(a1)
 ori.b #2,5(a1)
 moveq #1,d0
 bra.s .done
.invalid:
 moveq #-1,d0
.done:
 movem.l (sp)+,d1-d7/a4-a5
 rts
.invalid_entry:
 moveq #-1,d0
 rts
.stream:
 moveq #0,d1
 move.b 1(a0),d1
 lsl.w #8,d1
 move.b (a0),d1
 add.w d4,d1
.resource:
 move.l d1,d5
 subi.l #$8000,d5
 moveq #0,d2
 move.b (a3,d5.l),d2
 moveq #0,d3
 bra.s .event
.advance:
 move.b #$80,$100(a0,d7.w)
 subq.b #1,d7
 move.b d6,$100(a0,d7.w)
 addq.b #1,d7
 addq.b #1,d4
 bne.s .advanced
 addq.b #1,1(a0)
.advanced:
 rts
.ppu:
 moveq #1,d3
.event:
 move.w d1,(a4)+
 move.b d2,(a4)+
 move.b d3,(a4)+
 addq.w #1,(a2)
 rts
