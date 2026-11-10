        dc.b 'DOS',0
        dc.l 0,880
        move.l a1,a5
        move.l #PAYLOAD_BYTES,d0
        move.l #$10002,d1
        jsr -198(a6)
        tst.l d0
        beq.s fail
        move.l d0,a4
        move.l a5,a1
        move.w #2,28(a1)
        move.l #PAYLOAD_BYTES,36(a1)
        move.l a4,40(a1)
        move.l #1024,44(a1)
        jsr -456(a6)
        tst.l d0
        bne.s fail
        jmp (a4)
fail:   moveq #-1,d0
        rts
