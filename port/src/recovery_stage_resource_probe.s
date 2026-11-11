; PRIVATE synthetic C6B5 -> C6BD -> C700 -> C2A5, F6=0. No frame sync.
probe_origin:
        lea $dff000,a5
        move.w #$7fff,$9a(a5)
        move.w #$7fff,$96(a5)
        move.w #$7fff,$9c(a5)
        move.w #$0200,$100(a5)
        lea probe_origin(pc),sp
        adda.l #probe_stack_end-probe_origin,sp
        include "stage-resource-calls.inc"
        lea probe_origin(pc),a6
        adda.l #probe_report-probe_origin,a6
        clr.l 8(a6)
        move.l #6,12(a6)
.halt:  bra.s .halt
        include "recovery_stage_resource_init.s"
        include "recovery_gameplay_player_init.s"
        include "recovery_gameplay_fade_entry.s"
        include "stage-resource-data.inc"
