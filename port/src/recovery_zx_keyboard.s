; Independent native adapter. No aliases. Requires exclusive CIAA serial/ICR
; ownership after takeover, serial INPUT mode (CRA bit 6 clear), CIAB clock.
; A0: 12-byte zeroed state: held, raw, serial, saved CRA, ack elapsed.l,
; serial event count.l. D0 returns held; D1-D7/A0-A6 and SP preserved.
; Reading ICR clears ALL CIAA pending flags: not an OS-safe polling API.
        xdef recovery_zx_decode
        xdef recovery_zx_serial_decode
        xdef recovery_zx_poll
recovery_zx_serial_decode:
        not.b d0
        ror.b #1,d0
recovery_zx_decode:
        movem.l d1-d3/a1,-(sp)
        move.b d0,d1
        andi.w #$7f,d1
        lea recovery_zx_map(pc),a1
        moveq #7,d2
recovery_zx_find:
        cmp.b (a1),d1
        beq.s recovery_zx_found
        addq.l #2,a1
        dbra d2,recovery_zx_find
        bra.s recovery_zx_result
recovery_zx_found:
        move.b 1(a1),d3
        btst #7,d0
        bne.s recovery_zx_release
        or.b d3,(a0)
        bra.s recovery_zx_result
recovery_zx_release:
        not.b d3
        and.b d3,(a0)
recovery_zx_result:
        moveq #0,d0
        move.b (a0),d0
        movem.l (sp)+,d1-d3/a1
        rts
recovery_zx_poll:
        movem.l d1-d5,-(sp)
        move.b $bfed01,d0
        btst #3,d0
        beq.s recovery_zx_current
        moveq #0,d4
        move.b $bfec01,d4
        move.b d4,2(a0)
        not.b d4
        ror.b #1,d4
        move.b d4,1(a0)
        move.b $bfee01,d5
        move.b d5,3(a0)
        ori.b #$40,d5
        move.b d5,$bfee01
        bsr llb_amiga_clock_read
        move.l d0,d1
recovery_zx_ack:
        bsr llb_amiga_clock_read
        sub.l d1,d0
        cmpi.l #64,d0
        bcs.s recovery_zx_ack
        move.l d0,4(a0)
        move.b 3(a0),$bfee01
        move.l d4,d0
        bsr recovery_zx_decode
        addq.l #1,8(a0)
recovery_zx_current:
        moveq #0,d0
        move.b (a0),d0
        movem.l (sp)+,d1-d5
        rts
recovery_zx_map:
        dc.b $31,$40,$32,$80,$44,$10,$42,$20,$4e,1,$4f,2,$4d,4,$4c,8
        even
