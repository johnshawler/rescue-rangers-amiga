; Static C2A8 fade continuation and C594 outer-yield call setup.
; A0=RAM[2048], A1=PC.w/A/X/Y/raw-P/SP/reserved, A2=journal[512].
; D0=ordered RAM-store count, or -1 inert unsupported PC.
; All other registers preserved. Disjoint valid buffers/code/host stack required.
; Stops at C2A5, live RTS destination, or FF04 (from C594).
; Binary Ricoh arithmetic even with D set. No ROM decoding/audio bypass.
        xdef recovery_startup_fade_continue
recovery_startup_fade_continue:
        cmpi.w #$c2a8,(a1)
        beq.s .valid
        cmpi.w #$c594,(a1)
        bne.w .invalid
.valid:
        movem.l d1-d7/a3,-(sp)
        movea.l a2,a3
        moveq #0,d5
        moveq #0,d7
        move.b 6(a1),d7
        moveq #0,d6
        move.b 5(a1),d6
        cmpi.w #$c594,(a1)
        bne.s .countdown
        move.b #$c5,d3
        bsr.w .push
        move.b #$96,d3
        bsr.w .push
        move.w #$ff04,(a1)
        bra.w .done
.countdown:
        bsr.w .pop
        moveq #1,d1
        bsr.w .subtract
        tst.b d3
        bne.w .delay
        moveq #0,d3
        move.b $0f(a0),d3
        moveq #0,d1
        move.b $0d(a0),d1
        move.b d3,d4
        add.w d1,d3
        andi.b #$3c,d6
        btst #8,d3
        beq.s .adc_c
        ori.b #1,d6
.adc_c:
        eor.b d4,d1
        not.b d1
        eor.b d3,d4
        and.b d4,d1
        andi.b #$80,d1
        beq.s .adc_v
        ori.b #$40,d6
.adc_v:
        moveq #$0f,d2
        bsr.w .write
; CMP #$50 replaces C/N/Z, preserving ADC V and other flags.
        andi.b #$7c,d6
        cmpi.b #$50,d3
        bcs.s .cmp_c
        ori.b #1,d6
.cmp_c:
        move.b d3,d1
        subi.b #$50,d1
        bne.s .cmp_z
        ori.b #2,d6
.cmp_z:
        andi.b #$80,d1
        or.b d1,d6
        cmpi.b #$50,d3
        beq.w .return
; LDA $0f replaces N/Z only.
        bsr.w .nz
        tst.b d3
        bmi.w .return
        moveq #31,d4
.copy:
        move.b $320(a0,d4.w),d3
        move.w #$300,d2
        add.w d4,d2
        bsr.w .write
        dbra d4,.copy
        moveq #31,d4
.attenuate:
        move.b $300(a0,d4.w),d3
        move.b $0f(a0),d1
        bsr.w .subtract
        tst.b d3
        bpl.s .store
        moveq #15,d3
.store:
        move.w #$300,d2
        add.w d4,d2
        bsr.w .write
        dbra d4,.attenuate
        moveq #$18,d2
        move.b #$ff,d3
        bsr.w .write
        move.b #$ff,4(a1)
        move.b $0e(a0),d3
        bsr.w .nz
.delay:
        bsr.w .push
        move.b d3,2(a1)
        move.w #$c2a5,(a1)
        bra.s .status
.return:
        move.b d3,2(a1)
        bsr.s .pop
        moveq #0,d4
        move.b d3,d4
        bsr.s .pop
        lsl.w #8,d3
        or.w d3,d4
        addq.w #1,d4
        move.w d4,(a1)
.status:
        move.b d6,5(a1)
.done:
        move.b d7,6(a1)
        move.l d5,d0
        movem.l (sp)+,d1-d7/a3
        rts
; SBC with SEC: preserve D/I/B/U, compute binary C/V/N/Z.
.subtract:
        andi.b #$3c,d6
        cmp.b d1,d3
        bcs.s .sbc_c
        ori.b #1,d6
.sbc_c:
        move.b d3,d0
        sub.b d1,d3
        eor.b d0,d1
        eor.b d3,d0
        and.b d0,d1
        andi.b #$80,d1
        beq.s .nz
        ori.b #$40,d6
.nz:
        andi.b #$7d,d6
        tst.b d3
        bne.s .nz_nonzero
        ori.b #2,d6
.nz_nonzero:
        move.b d3,d0
        andi.b #$80,d0
        or.b d0,d6
        rts
.pop:
        addq.b #1,d7
        move.w d7,d2
        ori.w #$100,d2
        moveq #0,d3
        move.b (a0,d2.w),d3
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
