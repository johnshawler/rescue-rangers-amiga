; Static bank3 phase accumulation and mixed channel dispatcher.
; Entries8060,807A with X0..3,8085 with stacked channel0..3.
; A0 RAM2048,A1 raw context8,A2 journal30,A3 unused. Raw P/D, all SP.
; Exits82B0,8374,839D or actual caller return. No resource or APU effects.
; D0=1/-1; D1-D7/A0-A6 preserved. No interpreter or forced state.
recovery_sfx_phase_dispatch:
 movem.l d1-d7/a4-a6,-(sp)
 moveq #0,d4
 move.b 6(a1),d4
 cmpi.w #$8060,(a1)
 beq.s .accepted
 cmpi.w #$807a,(a1)
 bne.s .check_resume
 cmpi.b #3,3(a1)
 bhi.w .reject
 bra.s .accepted
.check_resume:
 cmpi.w #$8085,(a1)
 bne.w .reject
 addq.b #1,d4
 cmpi.b #3,$100(a0,d4.w)
 bhi.w .reject
.accepted:
 moveq #0,d4
 move.b 6(a1),d4
 moveq #0,d1
 moveq #0,d2
 moveq #0,d3
 move.b 2(a1),d1
 move.b 3(a1),d2
 move.b 4(a1),d3
 move.b 5(a1),d5
 clr.w (a2)
 cmpi.w #$8085,(a1)
 beq.w .p8085
 cmpi.w #$807a,(a1)
 beq.w .p807a
 bra.w .p8060
.publish:
 move.w d7,(a1)
 move.b d1,2(a1)
 move.b d2,3(a1)
 move.b d3,4(a1)
 move.b d5,5(a1)
 move.b d4,6(a1)
 moveq #1,d0
 bra.s .done
.reject:
 moveq #-1,d0
.done:
 movem.l (sp)+,d1-d7/a4-a6
 rts
.p8374:
 move.w #$8374,d7
 bra.w .publish
.p839d:
 move.w #$839d,d7
 bra.w .publish
.p82b0:
 move.w #$82b0,d7
 bra.w .publish
.p8060: ; CLC
 andi.b #$fe,d5
.p8061: ; LDA $ca
 move.l #$ca,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8063: ; ADC $c8
 move.l #$c8,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p8065: ; STA $c8
 move.l #$c8,d7
 move.b d1,(a0,d7.w)
.p8067: ; LDA $c9
 move.l #$c9,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8069: ; ADC #$00
 moveq #0,d6
 move.b #$00,d6
 bsr.w .adc
.p806b: ; STA $c7
 move.l #$c7,d7
 move.b d1,(a0,d7.w)
.p806d: ; LDA $cf
 move.l #$cf,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p806f: ; PHA
 move.b d1,d6
 bsr.w .push
.p8070: ; LDX #$03
 moveq #0,d6
 move.b #$03,d6
 move.b d6,d2
 bsr.w .nz
.p8072: ; LDA $cf
 move.l #$cf,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8074: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p8075: ; BCC $807a
 btst #0,d5
 beq.w .p807a
.p8077: ; JSR $82b0
 move.b #$80,d6
 bsr.w .push
 move.b #$79,d6
 bsr.w .push
 bra.w .p82b0
.p807a: ; LDA $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p807c: ; AND #$02
 moveq #0,d6
 move.b #$02,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p807e: ; BNE $8087
 btst #1,d5
 beq.w .p8087
.p8080: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p8081: ; PHA
 move.b d1,d6
 bsr.w .push
.p8082: ; JSR $8363
 move.b #$80,d6
 bsr.w .push
 move.b #$84,d6
 bsr.w .push
 bra.w .p8363
.p8085: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p8086: ; TAX
 move.b d1,d2
 move.b d2,d6
 bsr.w .nz
.p8087: ; LSR $cf
 move.l #$cf,d7
 move.b (a0,d7.w),d6
 bsr.w .lsr
 move.b d6,(a0,d7.w)
.p8089: ; DEX
 subq.b #1,d2
 move.b d2,d6
 bsr.w .nz
.p808a: ; BPL $8072
 btst #7,d5
 beq.w .p8072
.p808c: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p808d: ; STA $cf
 move.l #$cf,d7
 move.b d1,(a0,d7.w)
.p808f: ; LSR $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 bsr.w .lsr
 move.b d6,(a0,d7.w)
.p8091: ; ASL $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 bsr.w .asl
 move.b d6,(a0,d7.w)
.p8093: ; LDA $cc
 move.l #$cc,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8095: ; AND #$7f
 moveq #0,d6
 move.b #$7f,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8097: ; BEQ $80ba
 btst #1,d5
 bne.w .p80ba
.p8099: ; LDY #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d3
 bsr.w .nz
.p809b: ; STY $c1
 move.l #$c1,d7
 move.b d3,(a0,d7.w)
.p809d: ; LDY #$04
 moveq #0,d6
 move.b #$04,d6
 move.b d6,d3
 bsr.w .nz
.p809f: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p80a0: ; ROL $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 bsr.w .rol
 move.b d6,(a0,d7.w)
.p80a2: ; DEY
 subq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p80a3: ; BNE $809f
 btst #1,d5
 beq.w .p809f
.p80a5: ; CLC
 andi.b #$fe,d5
.p80a6: ; ADC $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p80a8: ; STA $c0
 move.l #$c0,d7
 move.b d1,(a0,d7.w)
.p80aa: ; LDA $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p80ac: ; ADC $cd
 move.l #$cd,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p80ae: ; BCC $80b8
 btst #0,d5
 beq.w .p80b8
.p80b0: ; LDA $cc
 move.l #$cc,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p80b2: ; AND #$80
 moveq #0,d6
 move.b #$80,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p80b4: ; STA $cc
 move.l #$cc,d7
 move.b d1,(a0,d7.w)
.p80b6: ; LDA #$ff
 moveq #0,d6
 move.b #$ff,d6
 move.b d6,d1
 bsr.w .nz
.p80b8: ; STA $cd
 move.l #$cd,d7
 move.b d1,(a0,d7.w)
.p80ba: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .publish
.p8363: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p8364: ; ORA #$28
 moveq #0,d6
 move.b #$28,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8366: ; TAX
 move.b d1,d2
 move.b d2,d6
 bsr.w .nz
.p8367: ; LDA $0728,X
 move.l #$728,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p836a: ; ORA $072c,X
 move.l #$72c,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p836d: ; BEQ $839c
 btst #1,d5
 bne.w .p839c
.p836f: ; LDA $0738,X
 move.l #$738,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8372: ; BEQ $839d
 btst #1,d5
 bne.w .p839d
 bra.w .p8374
.p839c: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .p8085

.nz:
 andi.b #$7d,d5
 tst.b d6
 bne.s .nz_nonzero
 ori.b #2,d5
 rts
.nz_nonzero:
 bpl.s .nz_done
 ori.b #$80,d5
.nz_done:
 rts
.push:
 move.b d6,$100(a0,d4.w)
 subq.b #1,d4
 rts
.pop:
 addq.b #1,d4
 moveq #0,d6
 move.b $100(a0,d4.w),d6
 rts
.adc:
 movem.l d7/a4,-(sp)
 moveq #0,d7
 move.b d1,d7
 move.b d1,d0
 eor.b d6,d0
 not.b d0
 move.l d0,a4
 andi.l #$ff,d6
 add.w d6,d7
 btst #0,d5
 beq.s .adc_nc
 addq.w #1,d7
.adc_nc:
 andi.b #$3c,d5
 cmpi.w #$100,d7
 bcs.s .adc_no_carry
 ori.b #1,d5
.adc_no_carry:
 move.b d1,d0
 eor.b d7,d0
 move.l a4,d6
 and.b d6,d0
 bpl.s .adc_no_v
 ori.b #$40,d5
.adc_no_v:
 move.b d7,d1
 move.b d1,d6
 bsr.w .nz
 movem.l (sp)+,d7/a4
 rts
.asl:
 andi.b #$fe,d5
 btst #7,d6
 beq.s .asl_nc
 ori.b #1,d5
.asl_nc:
 lsl.b #1,d6
 bra.w .nz
.lsr:
 andi.b #$fe,d5
 btst #0,d6
 beq.s .lsr_nc
 ori.b #1,d5
.lsr_nc:
 lsr.b #1,d6
 bra.w .nz
.rol:
 move.b d5,d0
 bsr.w .asl
 andi.b #1,d0
 or.b d0,d6
 bra.w .nz
