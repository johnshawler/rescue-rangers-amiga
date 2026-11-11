; Static SFX tick entry and countdown. Bank3 82B0/82C0, X0..3, all raw P/SP.
; A0 RAM2048,A1 context8,A2 journal30,A3 immutable bank3 16384.
; D0=1/-1; D1-D7/A0-A6 preserved. Stops before command parser or envelope.
recovery_sfx_tick_entry:
 movem.l d1-d7/a4-a6,-(sp)
 cmpi.w #$82b0,(a1)
 beq.s .valid_pc
 cmpi.w #$82c0,(a1)
 bne.w .reject
.valid_pc:
 cmpi.b #3,3(a1)
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
 cmpi.w #$82c0,(a1)
 beq.w .p82c0
 bra.w .p82b0
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
.p82b0: ; LDY $0700,X
 move.l #$700,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d3
 bsr.w .nz
.p82b3: ; BEQ $82b8
 btst #1,d5
 bne.w .p82b8
.p82b5: ; JSR $867c
 move.b #$82,d6
 bsr.w .push
 move.b #$b7,d6
 bsr.w .push
 bsr.w .p867c
.p82b8: ; LDA $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p82ba: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p82bb: ; BCS $82dc
 btst #0,d5
 bne.w .p82dc
.p82bd: ; JSR $86b2
 move.b #$82,d6
 bsr.w .push
 move.b #$bf,d6
 bsr.w .push
 bra.w .p86b2
.p82c0: ; LDA $d3
 move.l #$d3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p82c2: ; BEQ $82cc
 btst #1,d5
 bne.w .p82cc
.p82c4: ; CPX #$01
 moveq #0,d6
 move.b #$01,d6
 andi.b #$fe,d5
 cmp.b d6,d2
 bcs.s .cmp_no_carry
 ori.b #1,d5
.cmp_no_carry:
 move.b d2,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p82c6: ; BEQ $82cd
 btst #1,d5
 bne.w .p82cd
.p82c8: ; LDA $d5
 move.l #$d5,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p82ca: ; BEQ $82d2
 btst #1,d5
 bne.w .p82d2
.p82cc: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .publish
.p82cd: ; DEC $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 subq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p82d0: ; BNE $82cc
 btst #1,d5
 beq.w .p82cc
.p82d2: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p82d5: ; AND #$04
 moveq #0,d6
 move.b #$04,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p82d7: ; BNE $82cc
 btst #1,d5
 beq.w .p82cc
.p82d9: ; JMP $859b
 bra.w .p859b
.p859b: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p859e: ; AND #$f8
 moveq #0,d6
 move.b #$f8,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p85a0: ; ORA #$03
 moveq #0,d6
 move.b #$03,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p85a2: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p85a5: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .publish
.p867c: ; DEY
 subq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p867d: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p867f: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p8681: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p8682: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8683: ; ROL $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 bsr.w .rol
 move.b d6,(a0,d7.w)
.p8685: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8686: ; ROL $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 bsr.w .rol
 move.b d6,(a0,d7.w)
.p8688: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8689: ; ROL $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 bsr.w .rol
 move.b d6,(a0,d7.w)
.p868b: ; CLC
 andi.b #$fe,d5
.p868c: ; ADC $8a02
 move.w #$8a02,d7
 bsr.w .resource
 bsr.w .adc
.p868f: ; STA $c5
 move.l #$c5,d7
 move.b d1,(a0,d7.w)
.p8691: ; LDA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8693: ; ADC $8a01
 move.w #$8a01,d7
 bsr.w .resource
 bsr.w .adc
.p8696: ; STA $c6
 move.l #$c6,d7
 move.b d1,(a0,d7.w)
.p8698: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p82dc:
 move.w #$82dc,d7
 bra.w .publish
.p86b2:
 move.w #$86b2,d7
 bra.w .publish
.resource:
 move.w d7,d6
 subi.w #$8000,d6
 andi.l #$ffff,d6
 move.b (a3,d6.l),d6
 moveq #0,d0
 move.w (a2),d0
 lsl.w #2,d0
 move.w d7,2(a2,d0.w)
 move.b d6,4(a2,d0.w)
 clr.b 5(a2,d0.w)
 addq.w #1,(a2)
 rts
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
