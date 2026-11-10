; Chip 'n Dale: Rescue Rangers PAL, native A1200 first milestone.
; The static title fixture is not a playable game. No 6502 interpreter.
        move.l 4.w,a6
        move.l #58880,d0
        move.l #$10002,d1
        jsr -198(a6)
        tst.l d0
        beq fail
        lea report(pc),a0
        move.l d0,24(a0)
        move.l #2,d1
        jsr -216(a6)
        lea report(pc),a0
        move.l d0,28(a0)
        lea $dff000,a5
        move.w #$7fff,$9a(a5)
        move.w #$7fff,$96(a5)
        move.w #$7fff,$9c(a5)
        move.w #$0200,$100(a5)
        lea game_ram(pc),a0
        bsr rescue_game_selftest
        lea game_report(pc),a1
        move.l d0,8(a1)
        move.l a0,16(a1)
        lea title_context(pc),a2
        move.l a2,24(a1)
        lea initial_game_ram(pc),a1
        move.w #511,d0
.restore_ram:
        move.l (a1)+,(a0)+
        dbra d0,.restore_ram
        bsr timer_start
        lea nametable(pc),a0
        lea chrall+4096(pc),a1
        lea report(pc),a2
        move.l 24(a2),a2
        lea 51200(a2),a3
        lea tile_cache(pc),a4
        bsr nes_draw_background
        bsr timer_stop
        lea report(pc),a0
        move.l d0,16(a0)
        bsr timer_start
        lea oamdata(pc),a0
        lea chrall(pc),a1
        lea report(pc),a2
        move.l 24(a2),a2
        lea 51200(a2),a3
        lea sprite_scratch(pc),a4
        move.w #$90,d0
        move.w #$1e,d1
        bsr nes_draw_sprites_8x8
        lea report(pc),a0
        move.l d0,12(a0)
        bsr timer_stop
        lea report(pc),a0
        move.l d0,20(a0)
        move.l 24(a0),d0
        lea planes(pc),a0
        moveq #4,d1
ptrs:   move.w d0,6(a0)
        swap d0
        move.w d0,2(a0)
        swap d0
        add.l #10240,d0
        addq.l #8,a0
        dbra d1,ptrs
        lea $dff000,a5
        lea copper(pc),a0
        move.l a0,$80(a5)
        move.w #0,$88(a5)
        move.w #$8380,$96(a5)
        lea report(pc),a0
        clr.l 8(a0)
        bsr llb_amiga_clock_start
loop:
        move.l $dff004,d0
        andi.l #$1ff00,d0
        cmpi.l #$12c00,d0
        beq loop
.wait_line:
        move.l $dff004,d0
        andi.l #$1ff00,d0
        cmpi.l #$12c00,d0
        bne .wait_line
        bsr llb_read_amiga_inputs
        lea game_report(pc),a1
        move.b d0,20(a1)
        move.b d1,21(a1)
        lea game_ram(pc),a0
        bsr rescue_update_controllers
        move.b $14(a0),d0
        or.b d0,22(a1)
        move.b $15(a0),d0
        or.b d0,23(a1)
        bsr rescue_nmi_timers
        bsr rescue_random_step
        addq.l #1,12(a1)
        moveq #0,d6
        move.b $203(a0),d6
        lea title_context(pc),a1
        bsr rescue_title_step
        cmpi.b #3,(a1)
        beq loop
        moveq #0,d5
        cmp.b $203(a0),d6
        beq .check_text
        lea tile_cache(pc),a1
        lsr.w #3,d6
        add.w #544,d6
        add.w d6,d6
        move.w #$ffff,(a1,d6.w)
        moveq #1,d5
.check_text:
        tst.b $19(a0)
        beq .check_redraw
        lea nametable(pc),a1
        bsr rescue_title_apply_queue
        moveq #1,d5
.check_redraw:
        tst.b d5
        beq loop
        bsr redraw_title
        bra loop
fail:   bra.s fail

; Dirty background restores the old cursor tile; full original OAM is redrawn.
; On-demand title changes only. No real-time gameplay claim.
redraw_title:
        movem.l d0-d7/a0-a6,-(sp)
        lea nametable(pc),a0
        lea chrall+4096(pc),a1
        lea report(pc),a2
        move.l 24(a2),a2
        lea 51200(a2),a3
        lea tile_cache(pc),a4
        bsr nes_draw_background
        lea game_ram+$200(pc),a0
        lea chrall(pc),a1
        lea report(pc),a2
        move.l 24(a2),a2
        lea 51200(a2),a3
        lea sprite_scratch(pc),a4
        move.w #$90,d0
        move.w #$1e,d1
        bsr nes_draw_sprites_8x8
        movem.l (sp)+,d0-d7/a0-a6
        rts

timer_start:
        move.b #$7f,$bfdd00
        move.b #0,$bfde00
        move.b #0,$bfdf00
        move.b #$ff,$bfd400
        move.b #$ff,$bfd500
        move.b #$ff,$bfd600
        move.b #$ff,$bfd700
        move.b #$51,$bfdf00
        move.b #$11,$bfde00
        rts
timer_stop:
        move.b #0,$bfde00
        move.b #0,$bfdf00
        moveq #0,d0
        move.b $bfd700,d0
        lsl.l #8,d0
        move.b $bfd600,d0
        lsl.l #8,d0
        move.b $bfd500,d0
        lsl.l #8,d0
        move.b $bfd400,d0
        not.l d0
        rts

        cnop 0,4
report: dc.b "CDRPORT1"
        dc.l $ffffffff,$ffffffff,0,0,0,0
copper:
        dc.w $100,$5200,$102,0,$104,0,$106,0
        dc.w $10c,$11,$1fc,0
        dc.w $8e,$2c81,$90,$2cc1,$92,$38,$94,$d0
        dc.w $108,0,$10a,0
planes: dc.w $e0,0,$e2,0,$e4,0,$e6,0,$e8,0,$ea,0
        dc.w $ec,0,$ee,0,$f0,0,$f2,0
        include "palette.s"
        dc.w $ffff,$fffe
        include "native_rescue_game.s"
        include "native_rescue_title.s"
        include "native_rescue_title_queue.s"
        include "amiga_joystick.s"
        include "amiga_keyboard.s"
        include "amiga_clock.s"
        include "native_background.s"
        include "native_sprite_blitter.s"
        even
nametable: incbin "title-nametable.bin"
chrall: incbin "title-chr.bin"
oamdata: incbin "title-oam.bin"
        cnop 0,4
sprite_scratch: dcb.b 2196,0
tile_cache: dcb.w 960,$ffff

        cnop 0,4
game_report: dc.b "CDRGAME1"
        dc.l $ffffffff,0,0,0,0
initial_game_ram: incbin "title-ram.bin"
game_ram: dcb.b 2048,0

        even
title_context: dc.b 1,$ff
