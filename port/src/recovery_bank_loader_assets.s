; Bank2 9039/9041 -> F3E5, authentic index0B palette/CHR/OAM preparation.
; A0 RAM2048,A1 ctx8,A2 journal154,A3 immutable bank2[16384].
; Resource values come from live bank view; no captured data is installed.
; Other stage indices reject inertly. D0=1/-1; other registers preserved.
recovery_bank_loader_assets:
 cmpi.b #$0b,$31(a0)
 bne.w .invalid
 cmpi.w #$9039,(a1)
 beq.s .accepted
 cmpi.w #$9041,(a1)
 bne.w .invalid
.accepted:
 movem.l d1-d7/a4,-(sp)
 clr.w (a2)
 lea 2(a2),a4
 moveq #0,d7
 move.b 6(a1),d7
 addq.b #1,d7
 moveq #0,d4
 move.b $100(a0,d7.w),d4
 move.w d4,d1
 addi.w #$91f4,d1
 bsr.w .resource
 ori.b #$80,d2
 move.b d2,$1b(a0)
 move.w d4,d1
 addi.w #$91f3,d1
 bsr.w .resource
 move.b 5(a1),d6
 andi.b #$7c,d6
 tst.b d2
 beq.s .index
 ; SEC/SBC #4 overflow, the only V-writing instruction in this span.
 move.b d2,d3
 move.b d2,d1
 subq.b #4,d2
 eor.b d2,d3
 and.b d1,d3
 andi.b #$80,d3
 andi.b #$bf,d6
 lsr.b #1,d3
 or.b d3,d6
.index:
 lsl.b #4,d2
 moveq #0,d4
 move.b d2,d4
 moveq #0,d5
.background:
 move.w d4,d1
 addi.w #$922f,d1
 bsr.w .resource
 move.b d2,$320(a0,d5.w)
 addq.b #1,d4
 addq.w #1,d5
 cmpi.w #16,d5
 bne.s .background
 moveq #3,d5
.oam:
 move.w d5,d1
 addi.w #$922b,d1
 bsr.w .resource
 move.b d2,$200(a0,d5.w)
 dbra d5,.oam
 move.b #$8d,$1a(a0)
 moveq #$60,d4
 moveq #0,d5
.sprite:
 move.w d4,d1
 addi.w #$922f,d1
 bsr.w .resource
 move.b d2,$330(a0,d5.w)
 addq.b #1,d4
 addq.w #1,d5
 cmpi.w #16,d5
 bne.s .sprite
 move.b #$91,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$0b,$100(a0,d7.w)
 subq.b #1,d7
 move.b d7,6(a1)
 move.w #$f3e5,(a1)
 move.b #$0b,2(a1)
 move.b #$10,3(a1)
 move.b #$70,4(a1)
 ori.b #1,d6
 move.b d6,5(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d7/a4
 rts
.resource:
 move.w d1,(a4)+
 subi.w #$8000,d1
 moveq #0,d2
 move.b (a3,d1.w),d2
 move.b d2,(a4)+
 clr.b (a4)+
 addq.w #1,(a2)
 rts
.invalid:
 moveq #-1,d0
 rts
