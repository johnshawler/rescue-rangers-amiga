; Newly authored static 68020 stage resource initialization C6B5 -> C6BD.
; A0 RAM[2048], A1 context[8], A2 journal[70], A3 immutable resource[421].
; Resource view bank4 CPU 8193..8337 inclusive. No proprietary bytes embedded.
; Entry PC C6B5, RAM F6=0; mapper serial latch empty and PRG mode 3 required.
; Counted journal70: semantic resource kind0, mapper kindliveF5.
; RAM writes remain ordered actual stores, not duplicated in external journal.
; D0=1 success/-1 invalid; other registers preserved; CCR scratch.
        xdef recovery_bank_loader_stage_init
recovery_bank_loader_stage_init:
        cmpi.w #$c6b5,(a1)
        bne.w .invalid
        tst.b $f6(a0)
        bne.w .invalid
        movem.l d1-d7/a4,-(sp)
        clr.w (a2)
        lea 2(a2),a4
        moveq #0,d5
        moveq #0,d7
        move.b 6(a1),d7
        move.b #$c6,d3
        bsr.w .push
        move.b #$b9,d3
        bsr.w .push
        move.w #$f1,d2
        moveq #4,d3
        bsr.w .write
        move.w #$f4,d2
        bsr.w .write
        move.w #$f5,d2
        move.b $f5(a0),d3
        addq.b #1,d3
        bsr.w .write
        moveq #4,d3
        bsr.w .mapper
        moveq #2,d3
        bsr.w .mapper
        moveq #1,d3
        bsr.w .mapper
        moveq #0,d3
        bsr.w .mapper
        bsr.w .mapper
        move.w #$f5,d2
        bsr.w .write
; FF74 RTS consumes the first original call frame; C6BA pushes C6BC.
        addq.b #2,d7
        move.b #$c6,d3
        bsr.w .push
        move.b #$bc,d3
        bsr.w .push
        moveq #0,d4
        move.b $31(a0),d4
        move.b $0(a3,d4.w),d3
        move.w #$8193,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$74,d2
        bsr.w .write
        move.b $f(a3,d4.w),d3
        move.w #$81a2,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$75,d2
        bsr.w .write
        move.b $1e(a3,d4.w),d3
        move.w #$81b1,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$72,d2
        bsr.w .write
        move.b $2d(a3,d4.w),d3
        move.w #$81c0,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$73,d2
        bsr.w .write
        move.b $3c(a3,d4.w),d3
        move.w #$81cf,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$78,d2
        bsr.w .write
        move.b $4b(a3,d4.w),d3
        move.w #$81de,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$79,d2
        bsr.w .write
        move.b $5a(a3,d4.w),d3
        move.w #$81ed,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$76,d2
        bsr.w .write
        move.b $69(a3,d4.w),d3
        move.w #$81fc,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$77,d2
        bsr.w .write
        move.b $78(a3,d4.w),d3
        move.w #$820b,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$7a,d2
        bsr.w .write
        move.b $87(a3,d4.w),d3
        move.w #$821a,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$7b,d2
        bsr.w .write
        move.b $96(a3,d4.w),d3
        move.w #$8229,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$7c,d2
        bsr.w .write
        move.b $a5(a3,d4.w),d3
        move.w #$8238,d2
        add.w d4,d2
        moveq #1,d6
        bsr.w .event
        move.w #$7d,d2
        bsr.w .write
        addq.b #2,d7
        move.w #$c6bd,(a1)
        move.b d3,2(a1)
        move.b d4,3(a1)
        andi.b #$7c,5(a1)
        tst.b d3
        bne.s .nonzero
        ori.b #2,5(a1)
.nonzero:
        andi.b #$80,d3
        or.b d3,5(a1)
        move.b d7,6(a1)
        moveq #1,d0
        movem.l (sp)+,d1-d7/a4
        rts
.push:
        move.w d7,d2
        ori.w #$100,d2
        bsr.s .write
        subq.b #1,d7
        rts
.mapper:
        move.w #$fff0,d2
        moveq #2,d6
        bra.s .event
.write:
        move.b d3,(a0,d2.w)
        moveq #0,d6
.event:
        tst.b d6
        beq.s .ram_only
        move.w d2,(a4)+
        move.b d3,(a4)+
        cmpi.b #2,d6
        beq.s .mapper_kind
        clr.b (a4)+
        bra.s .publish
.mapper_kind:
        move.b $f5(a0),(a4)+
.publish:
        addq.w #1,(a2)
.ram_only:
        addq.w #1,d5
        rts
.invalid:
        moveq #-1,d0
        rts
