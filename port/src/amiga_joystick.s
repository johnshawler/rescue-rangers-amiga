; Standard Amiga port-2 digital joystick -> game's NES button byte.
; D0.b result: A=fire, B=second fire, directions; Start/Select unavailable.
; No keyboard adapter yet. D1-D3 preserved, CCR clobbered.
        xdef llb_read_amiga_joystick
llb_read_amiga_joystick:
        movem.l d1-d3,-(sp)
        moveq #0,d0
        move.w $dff00c,d1
        btst #1,d1
        beq joy_no_right
        bset #0,d0
joy_no_right:
        btst #9,d1
        beq joy_no_left
        bset #1,d0
joy_no_left:
        move.w d1,d2
        lsr.w #1,d2
        eor.w d1,d2
        btst #0,d2
        beq joy_no_down
        bset #2,d0
joy_no_down:
        btst #8,d2
        beq joy_no_up
        bset #3,d0
joy_no_up:
        btst #7,$bfe001
        bne joy_no_a
        bset #7,d0
joy_no_a:
        btst #6,$dff016
        bne joy_no_b
        bset #6,d0
joy_no_b:
        movem.l (sp)+,d1-d3
        rts

; Standard port1 adapter for the second player. Same individual ABI.
        xdef llb_read_amiga_joystick_one
llb_read_amiga_joystick_one:
        movem.l d1-d3,-(sp)
        moveq #0,d0
        move.w $dff00a,d1
        btst #1,d1
        beq joy1_no_right
        bset #0,d0
joy1_no_right:
        btst #9,d1
        beq joy1_no_left
        bset #1,d0
joy1_no_left:
        move.w d1,d2
        lsr.w #1,d2
        eor.w d1,d2
        btst #0,d2
        beq joy1_no_down
        bset #2,d0
joy1_no_down:
        btst #8,d2
        beq joy1_no_up
        bset #3,d0
joy1_no_up:
        btst #6,$bfe001
        bne joy1_no_a
        bset #7,d0
joy1_no_a:
        btst #2,$dff016
        bne joy1_no_b
        bset #6,d0
joy1_no_b:
        movem.l (sp)+,d1-d3
        rts

; Both physical ports: D0 player1 (port2), D1 player2 (port1).
; Other registers preserved. A second joystick replaces the port1 mouse.
        xdef llb_read_amiga_joysticks
llb_read_amiga_joysticks:
        bsr llb_read_amiga_joystick
        move.l d0,-(sp)
        bsr llb_read_amiga_joystick_one
        move.l d0,d1
        move.l (sp)+,d0
        rts
