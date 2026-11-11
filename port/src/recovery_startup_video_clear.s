; Static C597 through C5BB. A0 RAM2048,A1 context8,A2 PPU journal4382.
; D0=1 success,-1 inert unsupported PC. Other registers preserved.
; No resource view, no mapper action, no pending-queue mutation or NMI service.
; Journal: count word followed by address.word,value.byte,write-kind.byte.
; PPU status read has value zero (comparison view; returned value is discarded).
recovery_startup_video_clear:
 movem.l d1-d5/a3,-(sp)
 cmpi.w #$c597,(a1)
 bne.w .reject
 clr.w (a2)
 lea 2(a2),a3
 moveq #0,d5
 move.b 6(a1),d5
 move.l #$99,d1
 bsr.w .push_call
 addq.b #1,$f0(a0)
 clr.b $fe(a0)
 move.w #$2001,d2
 moveq #0,d1
 bsr.w .ppu
 move.b #4,$97(a0)
 move.l #$a0,d1
 bsr.w .push_call
 move.b #$f8,$200(a0)
 moveq #4,d3
.hide:
 move.b #$f8,$200(a0,d3.w)
 addq.b #4,d3
 bne.s .hide
 move.l #$a3,d1
 bsr.w .push_call
 moveq #31,d3
.zero_zp:
 clr.b $50(a0,d3.w)
 dbra d3,.zero_zp
 clr.b (a0)
 move.b #4,1(a0)
 moveq #0,d3
.page:
 moveq #0,d4
 move.b 1(a0),d4
 lsl.w #8,d4
.page_byte:
 clr.b (a0,d4.w)
 addq.w #1,d4
 addq.b #1,d3
 bne.s .page_byte
 addq.b #1,1(a0)
 cmpi.b #6,1(a0)
 bne.s .page
 clr.b $fc(a0)
 clr.b $fa(a0)
 clr.b $fd(a0)
 clr.b $fb(a0)
 clr.b $31(a0)
 clr.b $95(a0)
 move.l #$ba,d1
 bsr.w .push_call
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
 move.l #$c0,d1
 bsr.s .ppu
 move.w #$2007,d2
 moveq #0,d1
 moveq #63,d3
.attributes:
 bsr.s .ppu
 dbra d3,.attributes
 move.w #$c5bb,(a1)
 move.b #$c0,2(a1)
 clr.b 3(a1)
 clr.b 4(a1)
 andi.b #$3c,5(a1)
 ori.b #2,5(a1)
 moveq #1,d0
 bra.s .done
.reject:
 moveq #-1,d0
.done:
 movem.l (sp)+,d1-d5/a3
 rts
; Original JSR high then low writes; each fully completes RTS before next call.
; Offset wraps within page one even for incoming SP=00.
.push_call:
 move.b #$c5,$100(a0,d5.w)
 subq.b #1,d5
 move.b d1,$100(a0,d5.w)
 addq.b #1,d5
 rts
.ppu:
 move.w d2,(a3)+
 move.b d1,(a3)+
 move.b #1,(a3)+
 addq.w #1,(a2)
 rts
