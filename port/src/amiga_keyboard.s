; Keyboard adapter after custom-hardware takeover. Poll CIAA serial pending;
; handshake preserves CIAA timer settings and uses the existing CIAB clock.
; Return=Start, Tab=Select, Space=A, left Alt=B, cursor keys=directions.
; One held byte supports independent simultaneous presses/releases.
        xdef llb_keyboard_decode
; A0 one-byte held state,D0 decoded Amiga raw key (bit7=release).
; D0 returns complete NES held byte; other registers preserved.
llb_keyboard_decode:
        movem.l d1-d3/a1,-(sp)
        move.b d0,d1
        andi.w #$7f,d1
        lea llb_keyboard_map(pc),a1
        moveq #7,d2
llb_key_find:
        cmp.b (a1),d1
        beq llb_key_found
        addq.l #2,a1
        dbra d2,llb_key_find
        bra llb_key_result
llb_key_found:
        move.b 1(a1),d3
        btst #7,d0
        bne llb_key_release
        or.b d3,(a0)
        bra llb_key_result
llb_key_release:
        not.b d3
        and.b d3,(a0)
llb_key_result:
        moveq #0,d0
        move.b (a0),d0
        movem.l (sp)+,d1-d3/a1
        rts
llb_keyboard_poll:
        movem.l d1-d4/a0,-(sp)
        move.b $bfed01,d0
        btst #3,d0
        beq llb_keyboard_current
        moveq #0,d4
        move.b $bfec01,d4
        not.b d4
        ror.b #1,d4
        bset #6,$bfee01
        bsr llb_amiga_clock_read
        move.l d0,d1
llb_keyboard_ack:
        bsr llb_amiga_clock_read
        sub.l d1,d0
        cmpi.l #64,d0
        bcs llb_keyboard_ack
        bclr #6,$bfee01
        lea llb_keyboard_held(pc),a0
        move.l d4,d0
        bsr llb_keyboard_decode
llb_keyboard_current:
        moveq #0,d0
        move.b llb_keyboard_held(pc),d0
        movem.l (sp)+,d1-d4/a0
        rts
        xdef llb_read_amiga_inputs
llb_read_amiga_inputs:
        bsr llb_read_amiga_joysticks
        move.l d0,-(sp)
        bsr llb_keyboard_poll
        or.l (sp)+,d0
        rts
        xdef llb_read_amiga_primary_input
llb_read_amiga_primary_input:
        bsr llb_read_amiga_joystick
        move.l d0,-(sp)
        bsr llb_keyboard_poll
        or.l (sp)+,d0
        rts
        even
llb_keyboard_map:
        dc.b $40,$80,$64,$40,$42,$20,$44,$10,$4c,8,$4d,4,$4f,2,$4e,1
llb_keyboard_held: dc.b 0
        even
