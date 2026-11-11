; Static C5C5 -> C5CB: bank2 setup8820 then rendering enable C158.
; A0 RAM2048,A1 context8,A2 journal566,A3 immutable bank2[16384].
; Caller requires bank2 mapping and exclusive buffers; no IRQ/NMI interleave.
; Journal count.word then address.word/value.byte/kind.byte:
; kind0 resource, kind1 PPU write. Every semantic read is published in order.
; PC mismatch inertly rejects. D0=1 success/-1 rejection, other regs preserved.
; CHR requests 1B/1A=9F remain live; no queue is drained or bypassed.
recovery_startup_title_setup:
 cmpi.w #$c5c5,(a1)
 bne.w .invalid
 movem.l d1-d7/a4,-(sp)
 clr.w (a2)
 lea 2(a2),a4
 moveq #0,d7
 move.b 6(a1),d7
 move.b #$c5,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$c7,$100(a0,d7.w)
 moveq #15,d4
.palette:
 move.w #$8861,d1
 add.w d4,d1
 bsr.w .resource
 move.b d2,$300(a0,d4.w)
 move.b d2,$310(a0,d4.w)
 move.b d2,$320(a0,d4.w)
 move.b d2,$330(a0,d4.w)
 subq.b #1,d4
 bpl.s .palette
 moveq #120,d4
 moveq #0,d5
.sprites:
 moveq #0,d6
.sprite_byte:
 move.w #$8871,d1
 add.w d4,d1
 add.w d6,d1
 bsr.s .resource
 move.w d5,d3
 add.w d6,d3
 move.b d2,$200(a0,d3.w)
 addq.w #1,d6
 cmpi.w #4,d6
 bne.s .sprite_byte
 addq.b #4,d5
 subq.b #4,d4
 bpl.s .sprites
 move.b #$9f,$1b(a0)
 move.b #$9f,$1a(a0)
 ; RTS then caller's JSR C158 reuses the same real page-one frame.
 addq.b #1,d7
 move.b #$c5,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$ca,$100(a0,d7.w)
 subq.b #1,$f0(a0)
 move.b #$1e,$fe(a0)
 move.w #$2001,d1
 moveq #$1e,d2
 moveq #1,d3
 bsr.s .event
 move.w #$c5cb,(a1)
 move.b d2,2(a1)
 move.b d5,3(a1)
 move.b d4,4(a1)
 andi.b #$7d,5(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d7/a4
 rts
.invalid:
 moveq #-1,d0
 rts
.resource:
 move.w d1,d3
 subi.w #$8000,d3
 moveq #0,d2
 move.b (a3,d3.w),d2
 moveq #0,d3
.event:
 move.w d1,(a4)+
 move.b d2,(a4)+
 move.b d3,(a4)+
 addq.w #1,(a2)
 rts
