; Chip 'n Dale Rescue Rangers (Europe): native game-state primitives.
; A0 = 2048-byte NES-layout game RAM. All D/A registers preserved, CCR scratch.
; No 6502 interpreter or opcode dispatcher. See analysis/NATIVE_GAME.md.
        xdef rescue_update_controllers
        xdef rescue_nmi_timers
        xdef rescue_hide_sprites
        xdef rescue_initialize_objects
        xdef rescue_random_step

; $C162-$C1B9. D0.b/D1.b = serially decoded controller 1/2 bytes.
; Bits: A B Select Start Up Down Left Right, bit 7 -> bit 0.
; Original $4016/$4017 hardware reads replaced by host input, expansion bits 0.
rescue_update_controllers:
        movem.l d0-d4,-(sp)
        clr.b $00(a0)
        clr.b $01(a0)
        move.b d0,$14(a0)
        move.b d1,$15(a0)
        moveq #1,d2
.rc_edge:
        move.b $14(a0,d2.w),d3
        move.b $16(a0,d2.w),d4
        eor.b d3,d4
        and.b d3,d4
        move.b d4,$14(a0,d2.w)
        move.b d3,$16(a0,d2.w)
        dbra d2,.rc_edge
        moveq #3,d2
.rc_sanitize:
        move.b $14(a0,d2.w),d3
        move.b d3,d4
        andi.b #$0c,d4
        cmpi.b #$0c,d4
        beq .rc_clear
        move.b d3,d4
        andi.b #$03,d4
        cmpi.b #$03,d4
        bne .rc_next
.rc_clear:
        andi.b #$f0,d3
        move.b d3,$14(a0,d2.w)
.rc_next:
        dbra d2,.rc_sanitize
        movem.l (sp)+,d0-d4
        rts

; $C0A1-$C0BE only: NMI counter, ready marker, four timer slots.
; Audio/bank switching and PPU portions of NMI are explicitly separate.
rescue_nmi_timers:
        movem.l d0-d1,-(sp)
        addq.b #1,$92(a0)
        move.b #$ff,$90(a0)
        moveq #0,d0
        moveq #3,d1
.rt_loop:
        cmpi.b #1,$80(a0,d0.w)
        bne .rt_next
        subq.b #1,$81(a0,d0.w)
        bne .rt_next
        move.b #4,$80(a0,d0.w)
.rt_next:
        addq.w #4,d0
        dbra d1,.rt_loop
        movem.l (sp)+,d0-d1
        rts

; $C21E-$C234: hide unused OAM sprites. $97 must be multiple of four.
rescue_hide_sprites:
        move.l d0,-(sp)
        moveq #0,d0
        move.b $97(a0),d0
        cmpi.b #4,d0
        bne .rh_loop
        move.b #$f8,$200(a0)
.rh_loop:
        move.b #$f8,$200(a0,d0.w)
        addq.b #4,d0
        bne .rh_loop
        move.l (sp)+,d0
        rts

; $C235-$C246: reset object slots 2..15, preserving players 0 and 1.
rescue_initialize_objects:
        move.l d0,-(sp)
        moveq #15,d0
.ri_loop:
        clr.b $4d0(a0,d0.w)
        move.b #$ff,$590(a0,d0.w)
        subq.w #1,d0
        cmpi.w #1,d0
        bne .ri_loop
        move.l (sp)+,d0
        rts

; $C2DC-$C2F6: four-byte shift-register random-state update.
rescue_random_step:
        movem.l d0-d2,-(sp)
        move.b $e4(a0),d0
        move.b d0,d1
        andi.b #2,d1
        move.b d1,$00(a0)
        move.b $e5(a0),d2
        eor.b d2,d0
        andi.b #2,d0
        lsr.b #2,d0
        ; LSR transfers feedback bit 1 to X, then ROXR chains all four bytes.
        move.b $e4(a0),d0
        roxr.b #1,d0
        move.b d0,$e4(a0)
        move.b $e5(a0),d0
        roxr.b #1,d0
        move.b d0,$e5(a0)
        move.b $e6(a0),d0
        roxr.b #1,d0
        move.b d0,$e6(a0)
        move.b $e7(a0),d0
        roxr.b #1,d0
        move.b d0,$e7(a0)
        movem.l (sp)+,d0-d2
        rts

; Destructive deterministic boot self-test. A0=2KiB RAM; D0=0 pass, -1 fail.
; Preserves all registers except D0 and CCR. Writes only primitive test state.
        xdef rescue_game_selftest
rescue_game_selftest:
        move.l d1,-(sp)
        clr.b $16(a0)
        clr.b $17(a0)
        moveq #$41,d0
        moveq #$22,d1
        bsr rescue_update_controllers
        cmpi.b #$41,$14(a0)
        bne .rs_fail
        cmpi.b #$22,$15(a0)
        bne .rs_fail
        bsr rescue_update_controllers
        tst.b $14(a0)
        bne .rs_fail
        tst.b $15(a0)
        bne .rs_fail
        move.b #1,$80(a0)
        move.b #1,$81(a0)
        clr.b $84(a0)
        clr.b $88(a0)
        clr.b $8c(a0)
        move.b #$ff,$92(a0)
        bsr rescue_nmi_timers
        cmpi.b #4,$80(a0)
        bne .rs_fail
        tst.b $92(a0)
        bne .rs_fail
        move.b #4,$97(a0)
        bsr rescue_hide_sprites
        cmpi.b #$f8,$200(a0)
        bne .rs_fail
        cmpi.b #$f8,$2fc(a0)
        bne .rs_fail
        bsr rescue_initialize_objects
        tst.b $4d2(a0)
        bne .rs_fail
        cmpi.b #$ff,$59f(a0)
        bne .rs_fail
        move.b #2,$e4(a0)
        clr.b $e5(a0)
        move.b #1,$e6(a0)
        clr.b $e7(a0)
        bsr rescue_random_step
        cmpi.b #$81,$e4(a0)
        bne .rs_fail
        cmpi.b #$80,$e7(a0)
        bne .rs_fail
        moveq #0,d0
        bra .rs_done
.rs_fail:
        moveq #-1,d0
.rs_done:
        move.l (sp)+,d1
        rts
