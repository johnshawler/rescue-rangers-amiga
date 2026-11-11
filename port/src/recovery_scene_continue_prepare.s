; Static F3D5 -> FF53: render-disable, C1BA nametable clear, saved-bank PLA.
; A0 RAM2048, A1 context8, A2 journal4382 (count + PPU records).
; Returns 1 / -1 inert reject. D1-D7/A0-A6 preserved. User-mode safe.
; No mapper writes or F6 mutation: FF53/deferred audio remains caller work.
recovery_scene_continue_prepare:
 cmpi.w #$f3d5,(a1)
 bne.w .invalid
 movem.l d1-d7/a3,-(sp)
 movea.l a2,a3
 clr.w (a3)+
 moveq #0,d7
 move.b 6(a1),d7
 move.b #$f3,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$d7,$100(a0,d7.w)
 addq.b #1,d7
 addq.b #1,$f0(a0)
 clr.b $fe(a0)
 moveq #0,d1
 move.w #$2001,d2
 bsr.w .ppu
 move.b #$f3,$100(a0,d7.w)
 subq.b #1,d7
 move.b #$e0,$100(a0,d7.w)
 addq.b #1,d7
 move.b #$20,(a0)
 clr.b 1(a0)
 clr.b 2(a0)
 move.w #$2002,(a3)+
 clr.w (a3)+
 addq.w #1,(a2)
 moveq #0,d1
 move.b $ff(a0),d1
 andi.b #$fe,d1
 move.w #$2000,d2
 bsr.s .ppu
 moveq #$20,d1
 move.w #$2006,d2
 bsr.s .ppu
 moveq #0,d1
 bsr.s .ppu
 move.w #$2007,d2
 move.w #1023,d3
.tiles:
 bsr.s .ppu
 dbra d3,.tiles
 move.w #$2006,d2
 moveq #$23,d1
 bsr.s .ppu
 move.b #$c0,d1
 bsr.s .ppu
 move.w #$2007,d2
 moveq #0,d1
 moveq #63,d3
.attributes:
 bsr.s .ppu
 dbra d3,.attributes
 ; C1ED CMP and ADC leave C=0,V=0; LDX 01 then PLA set final N/Z.
 addq.b #1,d7
 move.b $100(a0,d7.w),d1
 move.b d1,2(a1)
 clr.b 3(a1)
 clr.b 4(a1)
 andi.b #$3c,5(a1)
 tst.b d1
 bne.s .nonzero
 ori.b #2,5(a1)
.nonzero:
 andi.b #$80,d1
 or.b d1,5(a1)
 move.b d7,6(a1)
 move.w #$ff53,(a1)
 moveq #1,d0
 movem.l (sp)+,d1-d7/a3
 rts
.ppu:
 move.w d2,(a3)+
 move.b d1,(a3)+
 move.b #1,(a3)+
 addq.w #1,(a2)
 rts
.invalid:
 moveq #-1,d0
 rts
