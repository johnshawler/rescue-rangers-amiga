; Free-running32-bit PAL CIA-B E-clock timestamp for game scheduling.
; Owns both CIAB timers after OS/custom takeover; does not install an IRQ.
; D0=current increasing unsigned tick count, other registers preserved.
        xdef llb_amiga_clock_start
        xdef llb_amiga_clock_read
llb_amiga_clock_start:
        move.b #0,$bfde00
        move.b #0,$bfdf00
        move.b #$7f,$bfdd00
        move.b #$ff,$bfd400
        move.b #$ff,$bfd500
        move.b #$ff,$bfd600
        move.b #$ff,$bfd700
        move.b #$51,$bfdf00
        move.b #$11,$bfde00
llb_amiga_clock_read:
        movem.l d1-d4,-(sp)
llb_clock_retry:
        moveq #0,d0
        moveq #0,d1
        moveq #0,d2
        moveq #0,d3
        move.b $bfd700,d0
        move.b $bfd600,d1
        move.b $bfd500,d2
        move.b $bfd400,d3
; Reject rollover while reading, without stopping either timer.
        move.b $bfd500,d4
        cmp.b d2,d4
        bne llb_clock_retry
        move.b $bfd600,d4
        cmp.b d1,d4
        bne llb_clock_retry
        move.b $bfd700,d4
        cmp.b d0,d4
        bne llb_clock_retry
        lsl.l #8,d0
        or.l d1,d0
        lsl.l #8,d0
        or.l d2,d0
        lsl.l #8,d0
        or.l d3,d0
        not.l d0
        movem.l (sp)+,d1-d4
        rts
