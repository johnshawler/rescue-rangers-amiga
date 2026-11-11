; Static outer music-channel iteration, original bank3 PC8085.
; A0=2048-byte original RAM,A1=8-byte context; all buffers disjoint/owned.
; No resource or hardware access. D0=1 success,-1 inert rejection.
; D1-D7/A0-A6 preserved; CCR scratch; native stack balanced.
; Canonical D=0 status, stacked channel index0..3 required.
; Reject before any write if a visited CF callback is needed or an active
; channel has nonzero duration. Ends at general fetch boundary839D or
; original tick RTS destination. No captured return address is assumed.
recovery_music_channel_iteration:
        movem.l d1-d7,-(sp)
        cmpi.w #$8085,(a1)
        bne.w .invalid
        move.b 5(a1),d5
        andi.b #$38,d5
        cmpi.b #$20,d5
        bne.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        addq.b #1,d4
        moveq #0,d2
        move.b $100(a0,d4.w),d2
        cmpi.b #3,d2
        bhi.w .invalid
        move.b $cf(a0),d6
.preflight:
        lsr.b #1,d6
        subq.b #1,d2
        bmi.s .accepted
        btst #0,d6
        bne.w .invalid
        btst #1,$c0(a0)
        bne.s .preflight
        move.w d2,d7
        ori.b #$28,d7
        move.b $728(a0,d7.w),d1
        or.b $72c(a0,d7.w),d1
        beq.s .preflight
        tst.b $738(a0,d7.w)
        bne.w .invalid
.accepted:
        move.b 5(a1),d5
        move.b 4(a1),d3
        moveq #0,d2
        move.b $100(a0,d4.w),d1
        move.b d1,d2
        bsr.w .nz
.iterate:
; LSR CF, DEX, BPL.
        move.b $cf(a0),d6
        andi.b #$7c,d5
        btst #0,d6
        beq.s .cfcarry
        ori.b #1,d5
.cfcarry:
        lsr.b #1,d6
        move.b d6,$cf(a0)
        subq.b #1,d2
        move.b d1,d7
        move.b d2,d1
        bsr.w .nz
        move.b d7,d1
        tst.b d2
        bmi.w .finish
; LDA CF, LSR A (preflight proved C clear), LDA C0, AND2.
        move.b $cf(a0),d1
        lsr.b #1,d1
        andi.b #$fe,d5
        bsr.w .nz
        move.b $c0(a0),d1
        andi.b #2,d1
        bsr.w .nz
        bne.s .phase_skip
        move.b d2,d1
        bsr.w .nz
        bsr.w .push
        move.b #$80,d6
        bsr.w .push6
        move.b #$84,d6
        bsr.w .push6
; Original TXA ORA28 TAX, indexed channel pointer/activity probe.
        ori.b #$28,d1
        move.b d1,d2
        bsr.w .nz
        move.b $728(a0,d2.w),d1
        or.b $72c(a0,d2.w),d1
        bsr.w .nz
        beq.s .inactive
        move.b $738(a0,d2.w),d1
        bsr.w .nz
        move.w #$839d,(a1)
        bra.w .publish
.inactive:
; Original RTS to8085 then PLA/TAX. Preserve dead stack stores.
        addq.b #2,d4
        addq.b #1,d4
        moveq #0,d2
        move.b $100(a0,d4.w),d1
        move.b d1,d2
        bsr.w .nz
.phase_skip:
        bra.w .iterate
.finish:
        addq.b #1,d4
        move.b $100(a0,d4.w),d1
        move.b d1,$cf(a0)
; LSR C0 / ASL C0 sets C=0 and clears low bit.
        andi.b #$fe,d5
        move.b $c0(a0),d6
        andi.b #$fe,d6
        move.b $c0(a0),d7
        lsr.b #1,d7
        move.b d7,$c0(a0)
        move.b d6,$c0(a0)
        move.b $cc(a0),d1
        andi.b #$7f,d1
        bsr.w .nz
        beq.w .return
        moveq #0,d3
        move.b d3,$c1(a0)
        moveq #4,d3
.scale:
; ASL A, ROL C1, DEY. C from ROL remains for next ASL.
        moveq #0,d6
        btst #7,d1
        beq.s .scale_carry
        moveq #1,d6
.scale_carry:
        add.b d1,d1
        move.b $c1(a0),d7
        andi.b #$fe,d5
        btst #7,d7
        beq.s .rotate_carry
        ori.b #1,d5
.rotate_carry:
        add.b d7,d7
        or.b d6,d7
        move.b d7,$c1(a0)
        subq.b #1,d3
        bne.s .scale
; CLC ADC C0.
        andi.b #$fe,d5
        move.b $c0(a0),d6
        bsr.w .adc
        move.b d1,$c0(a0)
        move.b $c1(a0),d1
        move.b $cd(a0),d6
        bsr.w .adc
        btst #0,d5
        beq.s .store_cd
        move.b $cc(a0),d1
        andi.b #$80,d1
        move.b d1,$cc(a0)
        move.b #$ff,d1
        bsr.w .nz
.store_cd:
        move.b d1,$cd(a0)
.return:
        moveq #0,d6
        addq.b #1,d4
        move.b $100(a0,d4.w),d6
        moveq #0,d7
        addq.b #1,d4
        move.b $100(a0,d4.w),d7
        lsl.w #8,d7
        or.w d7,d6
        addq.w #1,d6
        move.w d6,(a1)
.publish:
        move.b d1,2(a1)
        move.b d2,3(a1)
        move.b d3,4(a1)
        move.b d5,5(a1)
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d7
        moveq #-1,d0
        rts
.nz:
        andi.b #$7d,d5
        tst.b d1
        bne.s .nz_nonzero
        ori.b #2,d5
.nz_nonzero:
        btst #7,d1
        beq.s .nz_done
        ori.b #$80,d5
.nz_done:
        tst.b d1
        rts
.push:
        move.b d1,$100(a0,d4.w)
        subq.b #1,d4
        rts
.push6:
        move.b d6,$100(a0,d4.w)
        subq.b #1,d4
        rts
.adc:
; Binary 6502 ADC D1 + D6 + P.C; compute carry and signed overflow.
        andi.w #$ff,d1
        andi.w #$ff,d6
        move.w d1,d7
        add.w d6,d7
        btst #0,d5
        beq.s .adc_sum
        addq.w #1,d7
.adc_sum:
        eor.b d1,d6
        not.b d6
        eor.b d7,d1
        and.b d1,d6
        andi.b #$80,d6
        lsr.b #1,d6
        andi.b #$3c,d5
        or.b d6,d5
        btst #8,d7
        beq.s .adc_carry
        ori.b #1,d5
.adc_carry:
        move.b d7,d1
        bsr.w .nz
        rts
