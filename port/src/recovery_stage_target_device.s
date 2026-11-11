; Bounded startup device consumer, not a CPU/PPU emulator.
; D0=helper index, A2=authentic journal. All registers preserved.
; Only admitted startup PPU registers; unknown writes latch an error.
; Mapper latch persists across calls; NT writes resolve current mirroring.
; PPUADDR latch, increment, palette mirrors, DMA OAM rotation retained.
startup_consume:
 movem.l d0-d7/a0-a6,-(sp)
 lea startup_device(pc),a0
 move.l d0,d7
 moveq #0,d6
 move.w (a2),d6
 lea 2(a2),a1
 tst.w d6
 beq.w .done
 subq.w #1,d6
.next:
 moveq #0,d1
 move.w (a1)+,d1
 moveq #0,d2
 move.b (a1)+,d2
 moveq #0,d3
 move.b (a1)+,d3
 cmpi.w #42,d7
 beq.s .resource
 cmpi.w #43,d7
 bne.s .dispatch
.resource:
 tst.b d3
 beq.w .skip
.dispatch:
 cmpi.w #$8000,d1
 bhs.w .mapper
 addq.l #1,20(a0)
 cmpi.w #$2002,d1
 beq.w .status
 cmpi.w #$2000,d1
 beq.w .ctrl
 cmpi.w #$2001,d1
 beq.w .mask
 cmpi.w #$2003,d1
 beq.w .oamaddr
 cmpi.w #$2005,d1
 beq.w .scroll
 cmpi.w #$2006,d1
 beq.w .address
 cmpi.w #$2007,d1
 beq.w .data
 cmpi.w #$4014,d1
 beq.w .dma
.error:
 addq.l #1,16(a0)
 bra.w .skip
.status:
 clr.b 2(a0)
 bra.w .skip
.ctrl:
 move.b d2,(a0)
 bra.w .skip
.mask:
 move.b d2,1(a0)
 bra.w .skip
.oamaddr:
 move.b d2,5(a0)
 bra.w .skip
.scroll:
 tst.b 2(a0)
 bne.s .scroll_y
 move.b d2,3(a0)
 bra.s .toggle
.scroll_y:
 move.b d2,4(a0)
.toggle:
 eori.b #1,2(a0)
 bra.w .skip
.address:
 tst.b 2(a0)
 bne.s .address_low
 andi.b #$3f,d2
 move.b d2,8(a0)
 bra.s .toggle
.address_low:
 move.b d2,9(a0)
 move.w 8(a0),6(a0)
 bra.s .toggle
.data:
 moveq #0,d4
 move.w 6(a0),d4
 andi.w #$3fff,d4
 cmpi.w #$2000,d4
 blo.w .error
 cmpi.w #$3f00,d4
 bhs.s .palette
 andi.w #$fff,d4
 move.w d4,d5
 lsr.w #8,d5
 lsr.w #2,d5
 andi.w #$3ff,d4
 moveq #0,d3
 move.b 10(a0),d3
 andi.w #3,d3
 beq.s .nt_ready
 cmpi.w #1,d3
 beq.s .nt_upper
 cmpi.w #2,d3
 beq.s .vertical
 lsr.w #1,d5
.vertical:
 btst #0,d5
 beq.s .nt_ready
.nt_upper:
 addi.w #1024,d4
.nt_ready:
 lea startup_nt(pc),a3
 move.b d2,(a3,d4.w)
 bra.s .increment
.palette:
 andi.w #31,d4
 move.w d4,d5
 andi.w #$13,d5
 cmpi.w #$10,d5
 bne.s .pal_ready
 andi.w #15,d4
.pal_ready:
 andi.b #$3f,d2
 lea startup_palette(pc),a3
 move.b d2,(a3,d4.w)
.increment:
 moveq #1,d4
 btst #2,(a0)
 beq.s .inc_ready
 moveq #32,d4
.inc_ready:
 add.w d4,6(a0)
 andi.w #$7fff,6(a0)
 bra.w .skip
.dma:
 cmpi.b #2,d2
 bne.w .error
 cmpi.w #48,d7
 bne.s .old_dma
 lea 134382(a2),a3
 bra.s .dma_ready
.old_dma:
 lea 42(a2),a3
 cmpi.w #6,d7
 beq.s .dma_ready
 lea 198(a2),a3
 cmpi.w #45,d7
 bne.s .dma_ready
 lea 238(a2),a3
.dma_ready:
 lea startup_oam(pc),a4
 moveq #0,d4
 move.b 5(a0),d4
 move.w #255,d5
.dma_copy:
 move.b (a3)+,(a4,d4.w)
 addq.b #1,d4
 dbra d5,.dma_copy
 bra.s .skip
.mapper:
 addq.l #1,24(a0)
 btst #7,d2
 beq.s .serial
 clr.b 14(a0)
 clr.b 15(a0)
 ori.b #12,10(a0)
 bra.s .skip
.serial:
 andi.w #1,d2
 moveq #0,d4
 move.b 15(a0),d4
 lsl.w d4,d2
 or.b d2,14(a0)
 addq.b #1,15(a0)
 cmpi.b #5,15(a0)
 bne.s .skip
 lsr.w #8,d1
 lsr.w #5,d1
 andi.w #3,d1
 move.b 14(a0),10(a0,d1.w)
 clr.b 14(a0)
 clr.b 15(a0)
.skip:
 dbra d6,.next
.done:
 movem.l (sp)+,d0-d7/a0-a6
 rts

; Stage target: horizontal full redraw; selected BG bank is CHR+4096.
startup_display:
 lea startup_display_report(pc),a6
 lea startup_device(pc),a0
 move.l a0,12(a6)
 lea startup_nt(pc),a1
 move.l a1,16(a6)
 lea startup_palette(pc),a1
 move.l a1,20(a6)
 lea startup_oam(pc),a1
 move.l a1,24(a6)
 lea startup_chr(pc),a1
 move.l a1,28(a6)
 lea startup_frame(pc),a1
 move.l a1,32(a6)
 lea startup_copper(pc),a1
 move.l a1,36(a6)
 bsr llb_amiga_clock_read
 move.l d0,40(a6)
 tst.l 16(a0)
 bne.w .unsupported
 move.b (a0),d0
 andi.b #$fe,d0
 cmpi.b #$90,d0
 bne.w .unsupported
 cmpi.b #$1e,1(a0)
 bne.w .unsupported
 tst.b 4(a0)
 bne.w .unsupported
 cmpi.b #$1e,10(a0)
 bne.w .unsupported
 tst.b 15(a0)
 bne.w .unsupported
 ; Select both immutable CHR banks from live mapper registers.
 lea startup_chr(pc),a2
 moveq #0,d3
.copy_bank:
 moveq #0,d0
 move.b 11(a0,d3.w),d0
 andi.l #31,d0
 lsl.l #8,d0
 lsl.l #4,d0
 lea startup_cartridge_chr(pc),a1
 adda.l d0,a1
 move.w #1023,d1
.copy_chr:
 move.l (a1)+,(a2)+
 dbra d1,.copy_chr
 addq.w #1,d3
 cmpi.w #2,d3
 bne.s .copy_bank
 lea startup_nt(pc),a0
 lea startup_chr+4096(pc),a1
 lea startup_frame(pc),a2
 lea startup_opacity(pc),a3
 lea startup_scratch(pc),a4
 lea startup_device(pc),a5
 moveq #0,d0
 moveq #0,d1
 moveq #0,d2
 moveq #0,d3
 moveq #0,d4
 move.b (a5),d0
 move.b 1(a5),d1
 move.b 3(a5),d2
 move.b 4(a5),d3
 move.b 10(a5),d4
 bsr recovery_scroll_view_draw
 tst.l d0
 bne.w .unsupported
 lea startup_oam(pc),a0
 lea startup_chr(pc),a1
 lea startup_scratch(pc),a4
 lea startup_device(pc),a5
 moveq #0,d0
 moveq #0,d1
 move.b (a5),d0
 move.b 1(a5),d1
 bsr nes_draw_sprites_8x8
 tst.l d0
 bne.w .unsupported
 bsr llb_amiga_clock_read
 move.l d0,44(a6)
 ; Convert generated logical palette through fixed, declared DAC approximation.
 lea startup_palette(pc),a0
 lea startup_rgb12(pc),a1
 lea startup_colors+2(pc),a2
 moveq #0,d2
.colors:
 move.w d2,d1
 andi.w #3,d1
 bne.s .nonzero
 moveq #0,d1
 bra.s .color_index
.nonzero:
 move.w d2,d1
.color_index:
 moveq #0,d0
 move.b (a0,d1.w),d0
 andi.w #63,d0
 add.w d0,d0
 move.w (a1,d0.w),(a2)
 addq.l #4,a2
 addq.w #1,d2
 cmpi.w #32,d2
 bne.s .colors
 lea startup_frame(pc),a0
 move.l a0,d0
 lea startup_planes(pc),a0
 moveq #4,d1
.ptrs:
 move.w d0,6(a0)
 swap d0
 move.w d0,2(a0)
 swap d0
 addi.l #10240,d0
 addq.l #8,a0
 dbra d1,.ptrs
 lea $dff000,a5
 lea startup_copper(pc),a0
 move.l a0,$80(a5)
 move.w #0,$88(a5)
 move.w #$8380,$96(a5)
 clr.l 8(a6)
 rts
.unsupported:
 move.l #-1,8(a6)
 move.w #$f00,$dff180
 rts
 include "recovery_scroll_view_draw.s"
 include "native_sprite_blitter.s"
 include "amiga_clock.s"
 cnop 0,4
startup_display_report:
 dc.b 'CDRDIS01'
 dc.l -99,0,0,0,0,0,0,0,0,0
startup_device:
 dc.b 0,0,0,0,0,0
 dc.w 0,0
 dc.b 12,0,0,3,0,0
 dc.l 0,0,0
startup_copper:
 dc.w $100,$5200,$102,0,$104,0,$106,0
 dc.w $10c,$11,$1fc,0
 dc.w $8e,$2c81,$90,$2cc1,$92,$38,$94,$d0
 dc.w $108,0,$10a,0
startup_planes:
 dc.w $e0,0,$e2,0,$e4,0,$e6,0,$e8,0,$ea,0
 dc.w $ec,0,$ee,0,$f0,0,$f2,0
startup_colors:
 rept 32
 dc.w $180+REPTN*2,0
 endr
 dc.w $ffff,$fffe
; Conventional 2C02 RGB approximation, rounded down to Amiga RGB4.
; This is a declared display conversion, not reference screenshot pixels.
startup_rgb12:
 dc.w $666,$028,$21a,$40a,$607,$700,$600,$540,$330,$040,$050,$040,$044,$000,$000,$000
 dc.w $aaa,$16c,$44f,$83f,$b2c,$d25,$c40,$a60,$880,$590,$2a0,$0a3,$099,$000,$000,$000
 dc.w $fff,$6bf,$99f,$c8f,$f7f,$f7b,$f96,$db2,$bc0,$8d1,$5e5,$4e9,$4dd,$444,$000,$000
 dc.w $fff,$bef,$ddf,$edf,$fdf,$fde,$fdc,$eea,$dea,$cea,$beb,$bed,$bee,$bbb,$000,$000
 cnop 0,4
startup_nt: dcb.b 2048,0
startup_palette: dcb.b 32,0
startup_oam: dcb.b 256,0
startup_chr: dcb.b 8192,0
startup_frame: dcb.b 51200,0
startup_opacity: dcb.b 7680,0
startup_cache: dcb.w 960,$ffff
startup_scratch: dcb.b 2196,0
startup_cartridge_chr:
 incbin "startup-display-private-chr.bin"
