; Original fixed-bank $C115-$C139 PPU queue consumer, title nametable adapter.
; A0=2KiB RAM; A1=1024-byte nametable. All D/A preserved; CCR scratch.
; Only nametable-address commands ($2000-$2FFF), PPU increment=1 supported.
; Title's genuine character-choice commands address $2226 and $2232.
; $19 cleared as original. Caller invokes only when queue pending.
        xdef rescue_title_apply_queue
rescue_title_apply_queue:
        movem.l d0-d4,-(sp)
        moveq #0,d0
        clr.b $19(a0)
.rq_command:
        moveq #0,d1
        move.b $360(a0,d0.w),d1
        bmi .rq_done
        lsl.w #8,d1
        move.b $361(a0,d0.w),d1
        andi.w #$3ff,d1
        move.b $362(a0,d0.w),d2
.rq_copy:
        move.b $363(a0,d0.w),(a1,d1.w)
        addq.w #1,d1
        andi.w #$3ff,d1
        addq.b #1,d0
        subq.b #1,d2
        bpl .rq_copy
        addq.b #3,d0
        bne .rq_command
.rq_done:
        movem.l (sp)+,d0-d4
        rts
