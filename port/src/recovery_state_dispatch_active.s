; Additive PC/RAM music dispatcher. No schedule, interpreter or trial calls.
; Palette ABI unchanged; A5 immutable eight-bank PRG image, A4 live serial mapper.
; IDs13..20: tick fetch, indexed fetch/commands/rest, gate/note, iteration, RTI.
recovery_state_dispatch_active:
        cmpi.w #$c0f3,(a1)
        bne.s .more
        tst.b $c9(a0)
        bne.s .enter
        bra.w recovery_state_dispatch_palette
.more:
        cmpi.w #$839d,(a1)
        beq.s .enter
        cmpi.w #$83a0,(a1)
        beq.s .enter
        cmpi.w #$83fd,(a1)
        beq.s .enter
        cmpi.w #$8085,(a1)
        beq.s .enter
        cmpi.w #$c0f9,(a1)
        beq.s .enter
        bra.w recovery_state_dispatch_palette
.enter:
        movem.l d1-d7/a3-a6,-(sp)
        cmpi.w #$d501,10(a4)
        bne.w .invalid
        tst.w 4(a4)
        bne.w .invalid
        tst.l d2
        bne.w .invalid
        cmpi.b #$1e,(a4)
        bne.w .invalid
        cmpi.b #3,3(a4)
        bne.w .invalid
        moveq #0,d3
        move.b 3(a4),d3
        andi.l #7,d3
        lsl.l #7,d3
        lsl.l #7,d3
        lea (a5,d3.l),a3
        move.w (a1),d3
        cmpi.w #$c0f3,d3
        beq.w .tick
        cmpi.w #$839d,d3
        beq.w .fetch
        cmpi.w #$83fd,d3
        beq.w .note
        cmpi.w #$8085,d3
        beq.w .iteration
        cmpi.w #$c0f9,d3
        beq.w .rti
; Music data dispatch, not 6502 opcode decode.
        cmpi.b #$20,2(a1)
        bcs.w .command
        move.b 2(a1),d3
        andi.b #$1f,d3
        bne.w .gate
        bra.w .rest
.tick:
        moveq #13,d6
        move.w #6,d7
        lea recovery_music_tick_fetch(pc),a6
        bra.w .invoke
.fetch:
        moveq #14,d6
        move.w #6,d7
        lea recovery_music_indexed_fetch(pc),a6
        bra.w .invoke
.command:
        moveq #15,d6
        move.w #22,d7
        lea recovery_music_indexed_commands(pc),a6
        bra.w .invoke
.rest:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #1,d3
        cmpi.b #$84,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$80,$100(a0,d3.w)
        bne.w .invalid
        moveq #16,d6
        move.w #10,d7
        lea recovery_music_indexed_rest(pc),a6
        bra.w .invoke
.gate:
        moveq #17,d6
        move.w #10,d7
        lea recovery_music_pitched_gate(pc),a6
        bra.w .invoke
.note:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #2,d3
        cmpi.b #$84,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$80,$100(a0,d3.w)
        bne.w .invalid
        moveq #18,d6
        move.w #18,d7
        lea recovery_music_pitched_note(pc),a6
        bra.w .invoke
.iteration:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #3,d3
        cmpi.b #$f8,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$c0,$100(a0,d3.w)
        bne.w .invalid
        moveq #19,d6
        move.w #0,d7
        lea recovery_music_channel_iteration(pc),a6
        bra.w .invoke
.rti:
        moveq #0,d3
        move.b 6(a1),d3
        addq.b #6,d3
        cmpi.b #$8d,$100(a0,d3.w)
        bne.w .invalid
        addq.b #1,d3
        cmpi.b #$fe,$100(a0,d3.w)
        bne.w .invalid
        cmpi.b #6,$f1(a0)
        bne.w .invalid
        cmpi.b #4,$80(a0)
        bne.w .invalid
        moveq #20,d6
        move.w #22,d7
        lea recovery_active_nmi_return(pc),a6
        bra.w .invoke
.invoke:
        jsr (a6)
        cmpi.l #1,d0
        bne.w .done
        move.w d6,6(a4)
        move.w d7,8(a4)
        cmpi.w #20,d6
        bne.w .done
; Consume real serial writes, never assign an expected next bank.
.mapper:
        moveq #0,d7
        move.w (a2),d7
        subq.w #1,d7
        lea 2(a2),a3
.record:
        moveq #0,d3
        move.w (a3)+,d3
        moveq #0,d4
        move.b (a3)+,d4
        addq.l #1,a3
        btst #7,d4
        beq.s .bit
        clr.b 4(a4)
        clr.b 5(a4)
        ori.b #12,(a4)
        bra.s .next
.bit:
        andi.l #1,d4
        moveq #0,d5
        move.b 5(a4),d5
        lsl.b d5,d4
        or.b d4,4(a4)
        addq.b #1,5(a4)
        cmpi.b #5,5(a4)
        bne.s .next
        lsr.w #8,d3
        lsr.w #5,d3
        andi.w #3,d3
        move.b 4(a4),(a4,d3.w)
        clr.b 4(a4)
        clr.b 5(a4)
.next:
        dbra d7,.record
.done:
        movem.l (sp)+,d1-d7/a3-a6
        rts
.invalid:
        moveq #-1,d0
        bra.s .done
