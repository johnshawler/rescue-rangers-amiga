; Standalone source-only synthetic C6BD fixtures, not stage boot integration.
        lea $dff000,a5
        move.w #$7fff,$9a(a5)
        move.w #$7fff,$96(a5)
        move.w #$7fff,$9c(a5)
        move.w #$0200,$100(a5)
        lea probe_stack_end(pc),sp
        include "gameplay-player-calls.inc"
        lea probe_report(pc),a6
        clr.l 8(a6)
        move.l #6,12(a6)
.halt:  bra.s .halt
        include "recovery_gameplay_player_init.s"
        include "gameplay-player-data.inc"
