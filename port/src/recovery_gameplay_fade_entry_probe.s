; Synthetic C6BD -> C700 -> C2A5 only. No bank-4 initialization/frame sync.
probe_origin:
        lea $dff000,a5
        move.w #$7fff,$9a(a5)
        move.w #$7fff,$96(a5)
        move.w #$7fff,$9c(a5)
        move.w #$0200,$100(a5)
        lea probe_origin(pc),sp
        adda.l #probe_stack_end-probe_origin,sp
        include "gameplay-fade-calls.inc"
        lea probe_origin(pc),a6
        adda.l #probe_report-probe_origin,a6
        clr.l 8(a6)
        move.l #6,12(a6)
.halt:  bra.s .halt
        include "recovery_gameplay_player_init.s"
        include "recovery_gameplay_fade_entry.s"
        include "gameplay-fade-data.inc"
