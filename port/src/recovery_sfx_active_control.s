; Static active-SFX tick control, bank3 mapped. Entries C0F6 and8052.
; Stops at8224/8060 or genuine80BA RTS. Raw P, NES binary ADC, all SP.
; A0 RAM2048 A1 context8 A2 journal2. No resource/APU/mapper effects.
; D0=1/-1 atomically, D1-D7/A0-A6 preserved. No interpreter.
recovery_sfx_active_control:
 movem.l d1-d7/a4-a6,-(sp)
 cmpi.w #$c0f6,(a1)
 beq.s .accepted
 cmpi.w #$8052,(a1)
 bne.w .reject
.accepted:
 clr.w (a2)
 moveq #0,d4
 move.b 6(a1),d4
 moveq #0,d1
 moveq #0,d2
 moveq #0,d3
 move.b 2(a1),d1
 move.b 3(a1),d2
 move.b 4(a1),d3
 move.b 5(a1),d5
 cmpi.w #$8052,(a1)
 beq.w .p8052
 move.b #$c0,d6
 bsr.w .push
 move.b #$f8,d6
 bsr.w .push
 bra.w .p803a
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
.p803a: ; LDA $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p803c: ; AND #$f3
 moveq #0,d6
 move.b #$f3,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p803e: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p8040: ; CLC
 andi.b #$fe,d5
.p8041: ; LDA #$04
 moveq #0,d6
 move.b #$04,d6
 move.b d6,d1
 bsr.w .nz
.p8043: ; ADC $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p8045: ; AND #$0c
 moveq #0,d6
 move.b #$0c,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8047: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8048: ; ORA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p804a: ; STA $c0
 move.l #$c0,d7
 move.b d1,(a0,d7.w)
.p804c: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p804d: ; BNE $8052
 btst #1,d5
 beq.w .p8052
.p804f: ; JSR $8052
 move.b #$80,d6
 bsr.w .push
 move.b #$51,d6
 bsr.w .push
 bra.w .p8052
.p8052: ; LDA $c0
 move.l #$c0,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8054: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p8055: ; BCS $80ba
 btst #0,d5
 bne.w .p80ba
.p8057: ; LDA $d0
 move.l #$d0,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8059: ; ORA $d1
 move.l #$d1,d7
 move.b (a0,d7.w),d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p805b: ; BEQ $8060
 btst #1,d5
 bne.w .p8060
.p805d: ; JSR $8224
 move.b #$80,d6
 bsr.w .push
 move.b #$5f,d6
 bsr.w .push
 bra.w .p8224
.p8224:
 move.w #$8224,d7
 bra.w .publish
.p8060:
 move.w #$8060,d7
 bra.w .publish
.p80ba:
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .publish
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
.resource:
 move.l d7,-(sp)
 subi.w #$8000,d7
 moveq #0,d6
 move.b (a3,d7.w),d6
 move.l (sp)+,d7
 moveq #0,d0
 bra.s .journal
.apu:
 moveq #1,d0
.journal:
 move.l a4,-(sp)
 move.l d0,-(sp)
 moveq #0,d0
 move.w (a2),d0
 lsl.w #2,d0
 lea 2(a2,d0.w),a4
 move.w d7,(a4)
 move.b d6,2(a4)
 move.l (sp)+,d0
 move.b d0,3(a4)
 addq.w #1,(a2)
 move.l (sp)+,a4
 rts
.compare:
 andi.b #$fe,d5
 cmp.b d6,d0
 bcs.s .compare_nc
 ori.b #1,d5
.compare_nc:
 sub.b d6,d0
 move.b d0,d6
 bra.w .nz
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
.sbc:
 eori.b #$ff,d6
 bra.w .adc
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
.ror:
 move.b d5,d0
 bsr.w .lsr
 andi.b #1,d0
 ror.b #1,d0
 or.b d0,d6
 bra.w .nz
