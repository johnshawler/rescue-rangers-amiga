; Original PRG bank 2 $A000-$A0C8, fixed-bank sound queue $F379-$F391.
; A0=2KiB game RAM, A1=two-byte host continuation {phase,original_X}.
; phase 0: initial A000; 1: resume A025; 2: resume A06C; 3: completed.
; Set context to zero initially. Call once each original frame yield.
; All D/A registers preserved. CCR scratch. No CPU emulation.
        xdef rescue_title_step
rescue_title_step:
        movem.l d0-d4/a2,-(sp)
        moveq #0,d2
        move.b 1(a1),d2
        move.b (a1),d0
        beq .menu
        cmpi.b #1,d0
        beq .countdown
        cmpi.b #2,d0
        beq .character
        bra .return
.countdown:
        subq.b #1,$be(a0)
        bcc .timer_high
        subq.b #1,$bf(a0)
.timer_high:
        move.b $be(a0),d0
        or.b $bf(a0),d0
        bne .menu
        move.b #1,$50(a0)
        move.b #1,$b8(a0)
        bra .finish
.menu:
        btst #4,$14(a0)
        bne .start
        btst #5,$14(a0)
        bne .toggle
        move.b $14(a0),d0
        andi.b #3,d0
        beq .yield_main
        btst #1,d0
        bne .one
        move.b #1,$50(a0)
        bra .cursor
.one:
        clr.b $50(a0)
        bra .cursor
.toggle:
        eori.b #1,$50(a0)
.cursor:
        moveq #$28,d2
        tst.b $50(a0)
        beq .set_cursor
        move.w #$88,d2
.set_cursor:
        move.b d2,$203(a0)
        bsr .sound
.yield_main:
        move.b #1,(a1)
        bra .return
.start:
        tst.b $50(a0)
        bne .finish
        lea .character_text(pc),a2
        moveq #23,d2
.copy_text:
        move.b (a2,d2.w),$360(a0,d2.w)
        dbra d2,.copy_text
        move.b #$ff,$19(a0)
        bra .yield_character
.character:
        btst #4,$14(a0)
        bne .confirm_character
        move.b $14(a0),d0
        andi.b #3,d0
        beq .yield_character
        andi.b #1,d0
        beq .chip
        move.b #$88,$203(a0)
        bra .character_sound
.chip:
        move.b #$28,$203(a0)
.character_sound:
        bsr .sound
.yield_character:
        move.b #2,(a1)
        bra .return
.confirm_character:
        cmpi.b #$28,$203(a0)
        beq .finish
        moveq #$1c,d2
.swap:
        move.b $340(a0,d2.w),d0
        move.b $341(a0,d2.w),$340(a0,d2.w)
        move.b d0,$341(a0,d2.w)
        subq.w #2,d2
        bpl .swap
        move.b #$8d,$5a2(a0)
        move.b #$8a,$5a4(a0)
        move.b #$95,$5a6(a0)
        move.b #$8e,$5a8(a0)
.finish:
        moveq #0,d2
.hide:
        move.b #$f8,$200(a0,d2.w)
        addq.b #4,d2
        bne .hide
        move.b #3,(a1)
.return:
        move.b d2,1(a1)
        movem.l (sp)+,d0-d4/a2
        rts
; Queue original menu SFX $27, retaining original scratch and full-ring policy.
.sound:
        move.b d2,$00(a0)
        moveq #0,d3
        move.b $da(a0),d3
        move.b #$27,$01(a0)
        cmpi.b #$88,$dc(a0,d3.w)
        bne .sound_done
        move.b #$27,$dc(a0,d3.w)
        addq.b #1,d3
        andi.b #7,d3
        move.b d3,$da(a0)
.sound_done:
        rts
.character_text:
        dc.b $22,$26,$07,$8c,$91,$92,$99,$a4,$a4,$a4,$a4,$22,$32,$08,$8d,$8a,$95,$8e,$a4,$a4,$a4,$a4,$a4,$ff
        even
