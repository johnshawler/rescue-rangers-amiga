; Static four-task scheduler. A0=RAM[2048], A1=raw context[8],
; A2=journal[74], D0.b/D1.b=standard pads. Journal count + addr/value/kind.
; Returns 0 idle at FE90, 1 resumed, 2 fresh dispatch, -1 invalid PC.
; Accept FE8D or FE90; one scan only, no asynchronous interrupt inside call.
; All registers except D0 preserved. No instruction decoding or ROM access.
        xdef recovery_general_task_scheduler
recovery_general_task_scheduler:
        cmpi.w #$fe8d,(a1)
        beq.s .start
        cmpi.w #$fe90,(a1)
        bne.w .invalid
.start:
        movem.l d1-d7/a3,-(sp)
        moveq #0,d7
        move.b 6(a1),d7
        cmpi.w #$fe8d,(a1)
        bne.s .scan_entry
        move.w #255,d7
.scan_entry:
        clr.w (a2)
        move.b #0,$90(a0)
        moveq #0,d4
.scan:
        moveq #0,d3
        move.b $80(a0,d4.w),d3
        cmpi.b #4,d3
        bhs.s .ready
        addq.w #4,d4
        cmpi.w #16,d4
        bne.s .scan
        move.w #$fe90,(a1)
        move.b d3,2(a1)
        move.b #16,3(a1)
        clr.b 4(a1)
        andi.b #$7c,5(a1)
        ori.b #2,5(a1)
        move.b d7,6(a1)
        moveq #0,d0
        bra.w .done
.ready:
        move.w d4,d2
        lsr.w #2,d2
        move.b d2,$91(a0)
        move.b #2,$80(a0,d4.w)
        moveq #0,d6
        cmpi.b #8,d3
        blo.s .carry_ready
        moveq #1,d6
.carry_ready:
        cmpi.b #8,d3
        bne.s .saved
        move.b $82(a0,d4.w),d5
        move.b d5,$93(a0)
        move.b $83(a0,d4.w),d5
        move.b d5,$94(a0)
        move.b d5,(a1)
        move.b $93(a0),1(a1)
        move.b d5,2(a1)
        move.b d4,3(a1)
        move.b d3,4(a1)
        bsr.w .flags
        move.b d7,6(a1)
        moveq #2,d0
        bra.w .done
.saved:
        moveq #0,d7
        move.b $82(a0,d4.w),d7
        tst.b d2
        bne.w .restore
        move.b #$fe,d5
        bsr.w .push
        move.b #$cf,d5
        bsr.w .push
        move.l d7,-(sp)
        clr.w (a2)
        lea 2(a2),a3
        move.w #$4016,(a3)+
        move.b #1,(a3)+
        move.b #1,(a3)+
        addq.w #1,(a2)
        move.w #$4016,(a3)+
        move.b #0,(a3)+
        move.b #1,(a3)+
        addq.w #1,(a2)
        move.b d0,d2
        move.b d1,d3
        moveq #7,d7
.serial:
        moveq #0,d4
        add.b d2,d2
        addx.b d4,d4
        move.w #$4016,(a3)+
        move.b d4,(a3)+
        move.b #0,(a3)+
        addq.w #1,(a2)
        move.b $14(a0),d5
        add.b d5,d5
        or.b d4,d5
        move.b d5,$14(a0)
        move.b $00(a0),d5
        add.b d5,d5
        move.b d5,$00(a0)
        moveq #0,d4
        add.b d3,d3
        addx.b d4,d4
        move.w #$4017,(a3)+
        move.b d4,(a3)+
        move.b #0,(a3)+
        addq.w #1,(a2)
        move.b $15(a0),d5
        add.b d5,d5
        or.b d4,d5
        move.b d5,$15(a0)
        move.b $01(a0),d5
        add.b d5,d5
        move.b d5,$01(a0)
        dbra d7,.serial
; Expansion registers are now zero; retain both original ORA/STA stores.
        move.b $14(a0),d5
        move.b d5,$14(a0)
        move.b $15(a0),d5
        move.b d5,$15(a0)
        moveq #1,d7
.edge:
        move.b $14(a0,d7.w),d4
        move.b $16(a0,d7.w),d5
        eor.b d4,d5
        and.b d4,d5
        move.b d5,$14(a0,d7.w)
        move.b d4,$16(a0,d7.w)
        dbra d7,.edge
        moveq #3,d7
.sanitize:
        moveq #0,d6
        move.b $14(a0,d7.w),d4
        move.b d4,d5
        andi.b #$0c,d5
        cmpi.b #$0c,d5
        beq.s .clear
        move.b d4,d5
        andi.b #3,d5
        cmpi.b #3,d5
        bne.s .next
.clear:
        moveq #1,d6
        andi.b #$f0,d4
        move.b d4,$14(a0,d7.w)
.next:
        dbra d7,.sanitize
        move.l (sp)+,d7
; Consume the original C162 RTS frame, retaining the reads and wrapped S.
        bsr.s .pop
        bsr.s .pop
.restore:
        bsr.s .pop
        move.b d5,4(a1)
        bsr.s .pop
        move.b d5,2(a1)
        move.b d5,3(a1)
        bsr.s .flags
        bsr.s .pop
        move.b d5,d4
        bsr.s .pop
        lsl.w #8,d5
        move.b d4,d5
        addq.w #1,d5
        move.w d5,(a1)
        move.b d7,6(a1)
        moveq #1,d0
.done:
        movem.l (sp)+,d1-d7/a3
        rts
.flags:
        andi.b #$7c,5(a1)
        or.b d6,5(a1)
        tst.b d5
        bne.s .nz
        ori.b #2,5(a1)
.nz:
        btst #7,d5
        beq.s .flagdone
        ori.b #$80,5(a1)
.flagdone:
        rts
.push:
        move.w d7,d2
        ori.w #256,d2
        move.b d5,(a0,d2.w)
        subq.b #1,d7
        rts
.pop:
        addq.b #1,d7
        move.w d7,d2
        ori.w #256,d2
        moveq #0,d5
        move.b (a0,d2.w),d5
        rts
.invalid:
        moveq #-1,d0
        rts
