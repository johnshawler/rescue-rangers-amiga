; Static original C274 palette fade-out entry -> C2A5.
; A0 RAM2048; A1 context8; A2 ordered store journal280.
; D0=70 stores or -1 inert unsupported PC; other registers preserved.
; Valid disjoint buffers, native stack and code required.
        xdef recovery_scene_palette_entry
recovery_scene_palette_entry:
        cmpi.w #$c274,(a1)
        bne.w .invalid
        movem.l d1-d7/a3,-(sp)
        movea.l a2,a3
        moveq #0,d5
        moveq #0,d7
        move.b 6(a1),d7
        moveq #$0f,d2
        moveq #$10,d3
        bsr.w .write
        moveq #$0d,d2
        move.b #$10,d3
        bsr.w .write
        move.w #$9a,d2
        moveq #0,d3
        bsr.w .write
        moveq #$0e,d2
        moveq #4,d3
        bsr.w .write
        moveq #31,d4
.copy:
        move.b $320(a0,d4.w),d3
        move.w #$300,d2
        add.w d4,d2
        bsr.w .write
        dbra d4,.copy
        moveq #31,d4
.attenuate:
        moveq #0,d3
        move.b $300(a0,d4.w),d3
; Record 6502 subtraction C/V independently from native flag changes.
        moveq #0,d6
        cmpi.b #$10,d3
        bcs.s .no_carry
        moveq #1,d6
.no_carry:
        move.b d3,d1
        subi.b #$10,d3
        eor.b d3,d1
        andi.b #$80,d1
        beq.s .no_overflow
; Subtrahend positive: overflow only if original operand negative.
        btst #7,$300(a0,d4.w)
        beq.s .no_overflow
        ori.b #$40,d6
.no_overflow:
        tst.b d3
        bpl.s .positive
        moveq #$0f,d3
.positive:
        move.w #$300,d2
        add.w d4,d2
        bsr.w .write
        dbra d4,.attenuate
        moveq #$18,d2
        move.b #$ff,d3
        bsr.w .write
        moveq #4,d3
        bsr.w .push
        move.w #$c2a5,(a1)
        move.b #4,2(a1)
        move.b #$10,3(a1)
        move.b #$ff,4(a1)
        andi.b #$3c,5(a1)
        or.b d6,5(a1)
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
