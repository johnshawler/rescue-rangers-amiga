; Input-only stock target, no game/ROM data, no gameplay or speed claim.
        lea recovery_zx_stack_end(pc),sp
        move.w #$7fff,$dff09a
        move.w #$7fff,$dff096
        move.b #$7f,$bfed01
        bclr #6,$bfee01
        bsr llb_amiga_clock_start
        lea recovery_zx_state(pc),a0
        lea recovery_zx_report(pc),a2
        move.l a0,20(a2)
        lea recovery_zx_records(pc),a3
        move.l a3,24(a2)
        move.l #$00010000,8(a2)
        move.l d0,d6
        moveq #0,d7
recovery_zx_loop:
        bsr recovery_zx_poll
        cmp.l 8(a0),d7
        beq.s recovery_zx_time
        move.l 8(a0),d7
        cmpi.l #128,d7
        bhi.s recovery_zx_overflow
        move.l 16(a2),(a3)+
        move.l (a0),(a3)+
        move.l 4(a0),(a3)+
        move.l 8(a0),(a3)+
        move.l d7,28(a2)
        bra.s recovery_zx_time
recovery_zx_overflow:
        move.l #1,12(a2)
recovery_zx_time:
        bsr llb_amiga_clock_read
        sub.l d6,d0
        cmpi.l #14188,d0
        bcs.s recovery_zx_loop
        addi.l #14188,d6
        addq.l #1,16(a2)
        bra.s recovery_zx_loop
        include "recovery_zx_keyboard.s"
        include "amiga_clock.s"
        cnop 0,4
recovery_zx_report:
        dc.b 'CDRCLIV1'
        dcb.l 8,0
recovery_zx_state: dcb.b 12,0
recovery_zx_records: dcb.b 2048,0
recovery_zx_stack: dcb.b 1024,0
recovery_zx_stack_end:
