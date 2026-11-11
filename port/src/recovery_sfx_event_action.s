; Static SFX event actions, bank3 830B/831B, X0..3, raw flags/wrapped stack.
; A0 RAM2048 A1 context8 A2 journal14 A3 immutable bank3[16384].
; Valid disjoint exclusively owned buffers required. D0=1/-1, other registers preserved.
recovery_sfx_event_action:
 movem.l d1-d7/a4-a6,-(sp)
 cmpi.b #3,3(a1)
 bhi.w .reject
 cmpi.w #$830b,(a1)
 beq.s .valid
 cmpi.w #$831b,(a1)
 bne.w .reject
 tst.b 4(a1)
 bmi.s .valid
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 addq.w #4,d7
 cmpi.w #$8000,d7
 bcs.w .reject
 cmpi.w #$bfff,d7
 bhi.w .reject
.valid:
 moveq #0,d1
 moveq #0,d2
 moveq #0,d3
 moveq #0,d4
 move.b 2(a1),d1
 move.b 3(a1),d2
 move.b 4(a1),d3
 move.b 6(a1),d4
 move.b 5(a1),d5
 clr.w (a2)
 cmpi.w #$830b,(a1)
 beq.w .p830b
 bra.w .p831b
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
.p830b: ; STA $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p830e: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8311: ; AND #$f8
 moveq #0,d6
 move.b #$f8,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8313: ; ORA #$04
 moveq #0,d6
 move.b #$04,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8315: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8318: ; JMP $80bb
 bra.w .p80bb
.p831b: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p831e: ; ORA #$20
 moveq #0,d6
 move.b #$20,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8320: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8323: ; LDA $0718,X
 move.l #$718,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8326: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8327: ; LDA #$54
 moveq #0,d6
 move.b #$54,d6
 move.b d6,d1
 bsr.w .nz
.p8329: ; BCS $832d
 btst #0,d5
 bne.w .p832d
.p832b: ; LDA #$0a
 moveq #0,d6
 move.b #$0a,d6
 move.b d6,d1
 bsr.w .nz
.p832d: ; STA $071c,X
 move.l #$71c,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8330: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p8331: ; BPL $833d
 btst #7,d5
 beq.w .p833d
.p8333: ; CPX #$01
 moveq #0,d6
 move.b #$01,d6
 andi.b #$fe,d5
 cmp.b d6,d2
 bcs.s .cmp_nc18
 ori.b #1,d5
.cmp_nc18:
 move.b d2,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p8335: ; BNE $833a
 btst #1,d5
 beq.w .p833a
.p8337: ; JSR $85a6
 move.b #$83,d6
 bsr.w .push
 move.b #$39,d6
 bsr.w .push
 bsr.w .p85a6
.p833a: ; JMP $863c
 bra.w .p863c
.p833d: ; JSR $85a6
 move.b #$83,d6
 bsr.w .push
 move.b #$3f,d6
 bsr.w .push
 bsr.w .p85a6
.p8340: ; LDA #$ff
 moveq #0,d6
 move.b #$ff,d6
 move.b d6,d1
 bsr.w .nz
.p8342: ; STA $077c,X
 move.l #$77c,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8345: ; DEY
 subq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8346: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p8347: ; BNE $8351
 btst #1,d5
 beq.w .p8351
.p8349: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p834b: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p834c: ; EOR #$0f
 moveq #0,d6
 move.b #$0f,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p834e: ; JMP $862e
 bra.w .p862e
.p8351: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p8352: ; CLC
 andi.b #$fe,d5
.p8353: ; ADC $d2
 move.l #$d2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p8355: ; JMP $85d6
 bra.w .p85d6
.p85a6: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p85a7: ; PHA
 move.b d1,d6
 bsr.w .push
.p85a8: ; LDY #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d3
 bsr.w .nz
.p85aa: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p85ad: ; AND #$f8
 moveq #0,d6
 move.b #$f8,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p85af: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p85b2: ; CPX #$29
 moveq #0,d6
 move.b #$29,d6
 andi.b #$fe,d5
 cmp.b d6,d2
 bcs.s .cmp_nc42
 ori.b #1,d5
.cmp_nc42:
 move.b d2,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p85b4: ; BEQ $85c8
 btst #1,d5
 bne.w .p85c8
.p85b6: ; CPX #$01
 moveq #0,d6
 move.b #$01,d6
 andi.b #$fe,d5
 cmp.b d6,d2
 bcs.s .cmp_nc44
 ori.b #1,d5
.cmp_nc44:
 move.b d2,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p85b8: ; BNE $85cf
 btst #1,d5
 beq.w .p85cf
.p85ba: ; LDA $d3
 move.l #$d3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p85bc: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p85be: ; LDA $070c,X
 move.l #$70c,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p85c1: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p85c3: ; JSR $8006
 move.b #$85,d6
 bsr.w .push
 move.b #$c5,d6
 bsr.w .push
 bsr.w .p8006
.p85c6: ; LDY $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 move.b d6,d3
 bsr.w .nz
.p85c8: ; INY
 addq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p85c9: ; INC $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p85cc: ; INC $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p85cf: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p85d0: ; STA $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p85d3: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p85d4: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p85d5: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p85d6: ; CMP #$60
 moveq #0,d6
 move.b #$60,d6
 andi.b #$fe,d5
 cmp.b d6,d1
 bcs.s .cmp_nc60
 ori.b #1,d5
.cmp_nc60:
 move.b d1,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p85d8: ; BCC $85dc
 btst #0,d5
 beq.w .p85dc
.p85da: ; LDA #$5f
 moveq #0,d6
 move.b #$5f,d6
 move.b d6,d1
 bsr.w .nz
.p85dc: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p85de: ; INC $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p85e0: ; CPX #$28
 moveq #0,d6
 move.b #$28,d6
 andi.b #$fe,d5
 cmp.b d6,d2
 bcs.s .cmp_nc65
 ori.b #1,d5
.cmp_nc65:
 move.b d2,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p85e2: ; BCC $8622
 btst #0,d5
 beq.w .p8622
 bra.w .reject
.p8622: ; ASL $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 bsr.w .asl
 move.b d6,(a0,d7.w)
.p8624: ; LDY $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d6,d3
 bsr.w .nz
.p8626: ; LDA $8934,Y
 move.l #$8934,d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p8629: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p862b: ; LDA $8935,Y
 move.l #$8935,d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p862e: ; STA $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8631: ; LDA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8633: ; STA $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8636: ; LDY #$04
 moveq #0,d6
 move.b #$04,d6
 move.b d6,d3
 bsr.w .nz
.p8638: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p863a: ; BMI $8644
 btst #7,d5
 bne.w .p8644
.p863c: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p863f: ; AND #$08
 moveq #0,d6
 move.b #$08,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8641: ; BNE $8644
 btst #1,d5
 beq.w .p8644
.p8643: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .publish
.p8644: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p8646: ; STA $0708,X
 move.l #$708,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8649: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p864c: ; AND #$37
 moveq #0,d6
 move.b #$37,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p864e: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8651: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .publish
.p8006: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p8008: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p800a: ; LDY #$08
 moveq #0,d6
 move.b #$08,d6
 move.b d6,d3
 bsr.w .nz
.p800c: ; ASL $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .asl
 move.b d6,(a0,d7.w)
.p800e: ; ROL $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 bsr.w .rol
 move.b d6,(a0,d7.w)
.p8010: ; BCC $801f
 btst #0,d5
 beq.w .p801f
.p8012: ; CLC
 andi.b #$fe,d5
.p8013: ; LDA $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8015: ; ADC $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p8017: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p8019: ; LDA $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p801b: ; ADC #$00
 moveq #0,d6
 move.b #$00,d6
 bsr.w .adc
.p801d: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p801f: ; DEY
 subq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8020: ; BNE $800c
 btst #1,d5
 beq.w .p800c
.p8022: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p80bb: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p80bc: ; AND #$03
 moveq #0,d6
 move.b #$03,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p80be: ; EOR #$03
 moveq #0,d6
 move.b #$03,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p80c0: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p80c1: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p80c2: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p80c3: ; LDA #$30
 moveq #0,d6
 move.b #$30,d6
 move.b d6,d1
 bsr.w .nz
.p80c5: ; CPY #$08
 moveq #0,d6
 move.b #$08,d6
 andi.b #$fe,d5
 cmp.b d6,d3
 bcs.s .cmp_nc111
 ori.b #1,d5
.cmp_nc111:
 move.b d3,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p80c7: ; BNE $80cb
 btst #1,d5
 beq.w .p80cb
.p80c9: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p80cb: ; STA $4000,Y
 move.l #$4000,d7
 add.w d3,d7
 move.b d1,d6
 bsr.w .apu
.p80ce: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
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
.apu:
 moveq #0,d0
 move.w (a2),d0
 lsl.w #2,d0
 move.w d7,2(a2,d0.w)
 move.b d6,4(a2,d0.w)
 move.b #1,5(a2,d0.w)
 addq.w #1,(a2)
 rts
