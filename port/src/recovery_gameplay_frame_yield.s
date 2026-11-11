; New static 68020 C2A5/FF04 -> FE8D, before scheduler execution.
; A0=2KiB RAM, A1=PC.w/A/X/Y/raw-P/S/reserved, A2=512-byte journal.
; Journal records address.w/value.b/zero.b. Disjoint buffers/code/native stack.
; D0=10 (C2A5) or 8 (FF04); invalid PC -1 inert. All other regs preserved.
; Direct FF04 entry retains whatever original caller frame already exists.
        xdef recovery_gameplay_frame_yield
recovery_gameplay_frame_yield:
        cmpi.w #$c2a5,(a1)
        beq.s .valid
        cmpi.w #$ff04,(a1)
        bne.w .invalid
.valid:
        movem.l d1-d7/a3,-(sp)
        movea.l a2,a3
        moveq #0,d5
        moveq #0,d7
        move.b 6(a1),d7
        cmpi.w #$c2a5,(a1)
        bne.s .body
        move.b #$c2,d3
        bsr.w .push
        move.b #$a7,d3
        bsr.w .push
.body:
        move.w #$93,d2
        moveq #1,d3
        bsr.w .write
        move.b 3(a1),d3
        bsr.w .push
        move.b 4(a1),d3
        bsr.w .push
        move.b #$ff,d3
        bsr.w .push
        move.b #$0e,d3
        bsr.w .push
; FEF7 LDA $91; ASL; ASL; TAX; RTS. Retain both original stack reads.
        moveq #0,d4
        move.b $91(a0),d4
        move.b d4,d6
        lsr.b #6,d6
        andi.b #1,d6
        lsl.b #2,d4
        addq.b #1,d7
        move.w d7,d2
        ori.w #$100,d2
        move.b (a0,d2.w),d1
        addq.b #1,d7
        move.w d7,d2
        ori.w #$100,d2
        move.b (a0,d2.w),d1
        move.w #$81,d2
        add.w d4,d2
        andi.w #$ff,d2
        move.b $93(a0),d3
        bsr.w .write
        subq.w #1,d2
        andi.w #$ff,d2
        moveq #1,d3
        bsr.w .write
        addq.w #2,d2
        andi.w #$ff,d2
        move.b d7,d3
        bsr.w .write
        move.w #$fe8d,(a1)
        move.b d4,2(a1)
        move.b d7,3(a1)
        move.b d4,4(a1)
        andi.b #$7c,5(a1)
        or.b d6,5(a1)
        tst.b d7
        bne.s .nonzero
        ori.b #2,5(a1)
.nonzero:
        andi.b #$80,d3
        or.b d3,5(a1)
        move.b d7,6(a1)
        move.l d5,d0
        movem.l (sp)+,d1-d7/a3
        rts
.push:
        move.w d7,d2
        ori.w #$100,d2
        bsr.s .write
        subq.b #1,d7
        rts
.write:
        move.b d3,(a0,d2.w)
        move.w d2,(a3)+
        move.b d3,(a3)+
        clr.b (a3)+
        addq.w #1,d5
        rts
.invalid:
        moveq #-1,d0
        rts
