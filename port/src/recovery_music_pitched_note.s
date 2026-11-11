; Indexed pitched note $83FD through natural channel RTS. No CPU interpreter.
; A0=2048-byte RAM,A1=8-byte context,A2=18-byte resource journal,
; A3=immutable 16KiB bank3. Valid disjoint owned buffers required.
; X28..2B, stacked note1..31, canonical binary P. D0=1/-1 inert.
; D1-D7/A0-A6 preserved, native CCR scratch. Byte RAM/resource effects.
recovery_music_pitched_note:
        movem.l d1-d7/a4-a5,-(sp)
        cmpi.w #$83fd,(a1)
        bne.w .invalid
        moveq #0,d0
        move.b 3(a1),d0
        cmpi.b #$28,d0
        bcs.w .invalid
        cmpi.b #$2b,d0
        bhi.w .invalid
        lea (a0,d0.w),a4
        move.b 5(a1),d2
        move.b d2,d1
        andi.b #$38,d1
        cmpi.b #$20,d1
        bne.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        addq.b #1,d4
        moveq #0,d6
        move.b $100(a0,d4.w),d6
        beq.w .invalid
        cmpi.b #31,d6
        bhi.w .invalid
        subq.b #1,d6
; Read-only preflight: determine whether the instrument byte is reached.
        tst.b $730(a4)
        bpl.s .pre_pitch
        tst.b $718(a4)
        beq.s .pre_done
.pre_pitch:
        cmpi.b #$28,3(a1)
        beq.s .pre_instrument
        moveq #0,d7
        move.b $730(a4),d7
        btst #3,d7
        beq.s .pre_octave
        addq.b #2,d7
.pre_octave:
        andi.w #7,d7
        move.b $593(a3,d7.w),d5
        add.b d6,d5
        add.b $cb(a0),d5
        add.b $734(a4),d5
        cmpi.b #$60,d5
        bcs.s .pre_clamp
        moveq #$5f,d5
.pre_clamp:
        addq.b #1,d5
        cmp.b $71c(a4),d5
        bne.s .pre_instrument
        tst.b $730(a4)
        bmi.s .pre_done
.pre_instrument:
        moveq #0,d1
        move.b $c6(a0),d1
        lsl.w #8,d1
        move.b $c5(a0),d1
        addq.w #4,d1
        cmpi.w #$8000,d1
        bcs.w .invalid
        cmpi.w #$bfff,d1
        bhi.w .invalid
        movea.l d1,a5
.pre_done:
        clr.w (a2)
        clr.l 2(a2)
        clr.l 6(a2)
        clr.l 10(a2)
        clr.l 14(a2)
; Note PLA/TAY/DEY already represented by d4/d6; no memory writes.
        tst.b $730(a4)
        bpl.s .onset
        tst.b $718(a4)
        bne.w .pitch
        moveq #$0c,d1
        bsr.w .push84
        bsr.w .retrigger
        addq.b #2,d4
        bra.w .finish
.onset:
        moveq #$12,d1
        bsr.w .push84
        move.b d6,$100(a0,d4.w)
        subq.b #1,d4
        andi.b #$f8,$704(a4)
        moveq #0,d5
        cmpi.b #$29,3(a1)
        bne.s .onset_store
        moveq #1,d5
        addq.b #1,$704(a4)
        addq.b #1,$704(a4)
.onset_store:
        move.b d5,$710(a4)
        addq.b #1,d4
        move.b $100(a0,d4.w),d6
        addq.b #2,d4
        btst #0,$cf(a0)
        bne.s .pitch
        move.b d6,$c3(a0)
        moveq #0,d1
        move.b 3(a1),d1
        andi.w #3,d1
        move.b #$ff,$77c(a0,d1.w)
        move.b $c3(a0),d6
.pitch:
        cmpi.b #$28,3(a1)
        bne.s .melodic
        clr.b $c3(a0)
        move.b d6,d5
        andi.b #15,d5
        eori.b #15,d5
        moveq #$33,d1
        bsr.w .push84
        bra.w .store_pitch
.melodic:
        move.b #8,$c4(a0)
        move.b $730(a4),d5
        btst #3,d5
        beq.s .octave
        move.b d5,d7
        moveq #2,d3
        add.b d5,d3
        moveq #2,d5
        bsr.w .overflow
        move.b d3,d5
.octave:
        move.b d6,$c3(a0)
        moveq #0,d7
        move.b d5,d7
        andi.w #7,d7
        move.w d7,d1
        addi.w #$8593,d1
        move.b $593(a3,d7.w),d3
        bsr.w .record
        move.b d6,d7
        move.b d3,d5
        add.b d6,d3
        bsr.w .overflow
        move.b d3,d7
        move.b $cb(a0),d5
        add.b d5,d3
        bsr.w .overflow
        move.b d3,d7
        move.b $734(a4),d5
        add.b d5,d3
        bsr.w .overflow
        move.b d3,d5
        moveq #$59,d1
        bsr.w .push84
        cmpi.b #$60,d5
        bcs.s .clamped
        moveq #$5f,d5
.clamped:
        move.b d5,$c3(a0)
        addq.b #1,$c3(a0)
        move.b $71c(a4),d5
        beq.s .no_glide
        cmp.b $c3(a0),d5
        bne.s .different
        tst.b $730(a4)
        bpl.s .no_glide
        bsr.w .retrigger
        addq.b #2,d4
        bra.w .finish
.different:
        move.b $718(a4),d7
        beq.s .no_glide
        cmp.b $c3(a0),d5
        bcc.s .glide_down
        ori.b #$80,d7
        bra.s .glide_store
.glide_down:
        andi.b #$7f,d7
.glide_store:
        move.b d7,$718(a4)
        ori.b #$20,$704(a4)
        move.b $c3(a0),d7
        move.b $71c(a4),d6
        move.b d6,$c3(a0)
        bra.s .note_store
.no_glide:
        andi.b #$df,$704(a4)
        move.b $c3(a0),d7
.note_store:
        move.b d7,$71c(a4)
        move.b $c3(a0),d1
        add.b d1,d1
        move.b d1,$c3(a0)
        moveq #0,d6
        move.b $c3(a0),d6
        move.w d6,d1
        addi.w #$8934,d1
        move.b $934(a3,d6.w),d3
        bsr.w .record
        move.b d3,$c3(a0)
        move.w d6,d1
        addi.w #$8935,d1
        move.b $935(a3,d6.w),d3
        bsr.w .record
        move.b d3,d5
.store_pitch:
        move.b d5,$724(a4)
        move.b $c3(a0),$720(a4)
        move.w a5,d1
        move.w d1,d0
        subi.w #$8000,d0
        move.b (a3,d0.w),d3
        bsr.w .record
        tst.b d3
        bmi.s .reset_envelope
        bsr.s .retrigger
        bra.s .pitch_done
.reset_envelope:
        bsr.s .reset
.pitch_done:
        addq.b #2,d4
.finish:
        move.b $730(a4),d6
        move.b d6,d5
        andi.b #$40,d5
        add.b d5,d5
        move.b d5,$c4(a0)
        move.b d6,d3
        andi.b #$7f,d3
        or.b d5,d3
        move.b d3,$730(a4)
        bpl.s .return
        move.b #$ff,$740(a4)
        moveq #-1,d3
.return:
        move.b d3,2(a1)
        move.b d6,4(a1)
        andi.b #$6c,d2
        tst.b d3
        bne.s .nonzero
        ori.b #2,d2
.nonzero:
        andi.b #$80,d3
        or.b d3,d2
        move.b d2,5(a1)
        addq.b #1,d4
        moveq #0,d7
        move.b $100(a0,d4.w),d7
        addq.b #1,d4
        moveq #0,d1
        move.b $100(a0,d4.w),d1
        lsl.w #8,d1
        or.w d1,d7
        addq.w #1,d7
        move.w d7,(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7/a4-a5
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d7/a4-a5
        moveq #-1,d0
        rts
.retrigger:
        btst #3,$704(a4)
        beq.s .ret
.reset:
        clr.b $708(a4)
        andi.b #$37,$704(a4)
.ret:
        rts
.push84:
        move.b #$84,$100(a0,d4.w)
        subq.b #1,d4
        move.b d1,$100(a0,d4.w)
        subq.b #1,d4
        rts
; d7 original A,d5 operand,d3 result. Only V survives to boundary.
.overflow:
        andi.b #$bf,d2
        move.b d7,d0
        eor.b d5,d0
        not.b d0
        move.b d7,d1
        eor.b d3,d1
        and.b d1,d0
        andi.b #$80,d0
        lsr.b #1,d0
        or.b d0,d2
        rts
.record:
        moveq #0,d0
        move.w (a2),d0
        lsl.w #2,d0
        move.w d1,2(a2,d0.w)
        move.b d3,4(a2,d0.w)
        clr.b 5(a2,d0.w)
        addq.w #1,(a2)
        rts
