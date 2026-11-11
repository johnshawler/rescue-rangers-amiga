; Static F3CF JSR C21E / F3D2 JSR FF04. No 6502 decoder.
; A0 RAM2048, A1 context8 PC.w/A/X/Y/rawP/SP/reserved, A2 journal264.
; D0 store count or -1 inert rejection; D1-D7/A0-A6 preserved.
; Reject F3CF if RAM97 & 3 (original sprite loop cannot terminate).
; Ordered address.w/value.b/zero stores, max66. Valid disjoint buffers required.
recovery_scene_sprite_hide:
 cmpi.w #$f3d2,(a1)
 beq.s .valid
 cmpi.w #$f3cf,(a1)
 bne.w .invalid
 moveq #3,d0
 and.b $97(a0),d0
 bne.w .invalid
.valid:
 movem.l d1-d7/a3,-(sp)
 movea.l a2,a3
 moveq #0,d5
 moveq #0,d7
 move.b 6(a1),d7
 move.b #$f3,d3
 bsr.w .push
 cmpi.w #$f3d2,(a1)
 beq.w .yield
 move.b #$d1,d3
 bsr.w .push
 moveq #0,d4
 move.b $97(a0),d4
 move.b 5(a1),d6
 andi.b #$7c,d6
 cmpi.b #4,d4
 bcs.s .carrydone
 ori.b #1,d6
.carrydone:
 move.b #$f8,d3
 cmpi.b #4,d4
 bne.s .loop
 move.w #$200,d2
 bsr.w .write
.loop:
 move.w d4,d2
 addi.w #$200,d2
 bsr.w .write
 addq.b #4,d4
 bne.s .loop
; Read the genuine JSR frame with wrapped 6502 SP, then increment RTS PC.
 bsr.w .pop
 moveq #0,d1
 move.b d3,d1
 bsr.w .pop
 lsl.w #8,d3
 or.w d3,d1
 addq.w #1,d1
 move.w d1,(a1)
 move.b #$f8,2(a1)
 clr.b 3(a1)
 ori.b #2,d6
 move.b d6,5(a1)
 bra.s .done
.yield:
 move.b #$d4,d3
 bsr.s .push
 move.w #$ff04,(a1)
.done:
 move.b d7,6(a1)
 move.l d5,d0
 movem.l (sp)+,d1-d7/a3
 rts
.pop:
 addq.b #1,d7
 move.w d7,d2
 ori.w #$100,d2
 moveq #0,d3
 move.b (a0,d2.w),d3
 rts
.push:
 move.w d7,d2
 ori.w #$100,d2
 bsr.s .write
 subq.b #1,d7
 rts
.write:
 move.b d3,(a0,d2.w)
 move.w d2,(a3)+
 move.b d3,(a3)+
 clr.b (a3)+
 addq.w #1,d5
 rts
.invalid:
 moveq #-1,d0
 rts
