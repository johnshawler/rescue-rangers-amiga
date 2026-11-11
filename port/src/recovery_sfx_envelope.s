; Static native envelope, bank3 86B2 through actual RTS. No opcode interpreter.
; A0 RAM2048,A1 context8,A2 journal514,A3 immutable bank3 view16384.
; Journal count.w then address.w,value.b,kind.b (0 resource,1 APU).
; D0=1 accepted,-1 inert rejection. D1-D7/A0-A6 preserved; CCR scratch.
; Caller buffers valid, disjoint, exclusively owned. X0..3, all raw P/SP.
; Independent SFX qualification; frozen music implementation remains unchanged.
recovery_sfx_envelope:
 movem.l d1-d7/a4-a6,-(sp)
 cmpi.w #$86b2,(a1)
 bne.w .reject
 moveq #0,d2
 move.b 3(a1),d2
 cmpi.b #3,d2
 bhi.w .reject
 move.b $704(a0,d2.w),d6
 andi.b #7,d6
 cmpi.b #4,d6
 bhi.w .reject
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 cmpi.w #$8000,d7
 bcs.w .reject
 cmpi.w #$bff8,d7
 bhi.w .reject
 tst.b $92e(a3)
 bne.w .reject
 cmpi.b #$c9,$6bf(a3)
 bne.w .reject
 cmpi.b #$86,$6c0(a3)
 bne.w .reject
 cmpi.b #$de,$6c1(a3)
 bne.w .reject
 cmpi.b #$86,$6c2(a3)
 bne.w .reject
 cmpi.b #$18,$6c3(a3)
 bne.w .reject
 cmpi.b #$87,$6c4(a3)
 bne.w .reject
 cmpi.b #$fa,$6c5(a3)
 bne.w .reject
 cmpi.b #$86,$6c6(a3)
 bne.w .reject
 cmpi.b #$0d,$6c7(a3)
 bne.w .reject
 cmpi.b #$89,$6c8(a3)
 bne.w .reject
 clr.w (a2)
 moveq #0,d1
 moveq #0,d3
 moveq #0,d4
 move.b 2(a1),d1
 move.b 4(a1),d3
 move.b 6(a1),d4
 move.b 5(a1),d5
 bsr.w .p86b2
 move.w d7,(a1)
 move.b d1,2(a1)
 move.b d2,3(a1)
 move.b d3,4(a1)
 move.b d5,5(a1)
 move.b d4,6(a1)
 moveq #1,d0
 bra.w .done
.reject:
 moveq #-1,d0
.done:
 movem.l (sp)+,d1-d7/a4-a6
 rts
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
.p8023: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8024: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8025: ; INY
 addq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8026: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p8027: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p8029: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p802a: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p802c: ; LDA ($c1),Y
 moveq #0,d7
 move.b $c2(a0),d7
 lsl.w #8,d7
 move.b $c1(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p802e: ; PHA
 move.b d1,d6
 bsr.w .push
.p802f: ; INY
 addq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8030: ; LDA ($c1),Y
 moveq #0,d7
 move.b $c2(a0),d7
 lsl.w #8,d7
 move.b $c1(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p8032: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p8034: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p8035: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p8037: ; JMP ($00c1)
 cmpi.b #$c9,$c1(a0)
 beq.w .p86c9
 cmpi.b #$de,$c1(a0)
 beq.w .p86de
 cmpi.b #$18,$c1(a0)
 beq.w .p8718
 cmpi.b #$fa,$c1(a0)
 beq.w .p86fa
 cmpi.b #$0d,$c1(a0)
 beq.w .p890d
 illegal
.p80cf: ; PHA
 move.b d1,d6
 bsr.w .push
.p80d0: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p80d1: ; AND #$03
 moveq #0,d6
 move.b #$03,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p80d3: ; EOR #$03
 moveq #0,d6
 move.b #$03,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p80d5: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p80d6: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p80d7: ; STY $c4
 move.l #$c4,d7
 move.b d3,(a0,d7.w)
.p80d9: ; ORA $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p80db: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p80dc: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p80dd: ; STA $4000,Y
 move.l #$4000,d7
 add.w d3,d7
 move.b d1,d6
 bsr.w .apu
.p80e0: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p86b2: ; LDA $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p86b5: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p86b7: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p86ba: ; AND #$07
 moveq #0,d6
 move.b #$07,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p86bc: ; JSR $8023
 move.b #$86,d6
 bsr.w .push
 move.b #$be,d6
 bsr.w .push
 bra.w .p8023
.p86c9: ; LDY #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d3
 bsr.w .nz
.p86cb: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p86cd: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p86ce: ; LDA $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p86d0: ; CLC
 andi.b #$fe,d5
.p86d1: ; ADC $890e,Y
 move.l #$890e,d7
 add.w d3,d7
 bsr.w .resource
 bsr.w .adc
.p86d4: ; BCS $86da
 btst #0,d5
 bne.w .p86da
.p86d6: ; CMP #$f0
 moveq #0,d6
 move.b #$f0,d6
 move.b d1,d0
 bsr.w .compare
.p86d8: ; BCC $8715
 btst #0,d5
 beq.w .p8715
.p86da: ; LDA #$f0
 moveq #0,d6
 move.b #$f0,d6
 move.b d6,d1
 bsr.w .nz
.p86dc: ; BNE $8712
 btst #1,d5
 beq.w .p8712
.p86de: ; LDY #$01
 moveq #0,d6
 move.b #$01,d6
 move.b d6,d3
 bsr.w .nz
.p86e0: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p86e2: ; BEQ $86f3
 btst #1,d5
 bne.w .p86f3
.p86e4: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p86e5: ; LDA $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p86e7: ; SEC
 ori.b #1,d5
.p86e8: ; SBC $890e,Y
 move.l #$890e,d7
 add.w d3,d7
 bsr.w .resource
 bsr.w .sbc
.p86eb: ; BCC $86f3
 btst #0,d5
 beq.w .p86f3
.p86ed: ; LDY #$02
 moveq #0,d6
 move.b #$02,d6
 move.b d6,d3
 bsr.w .nz
.p86ef: ; CMP ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d1,d0
 bsr.w .compare
.p86f1: ; BCS $8715
 btst #0,d5
 bne.w .p8715
.p86f3: ; LDY #$02
 moveq #0,d6
 move.b #$02,d6
 move.b d6,d3
 bsr.w .nz
.p86f5: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p86f7: ; JMP $8712
 bra.w .p8712
.p86fa: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p86fb: ; AND #$03
 moveq #0,d6
 move.b #$03,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p86fd: ; CMP #$01
 moveq #0,d6
 move.b #$01,d6
 move.b d1,d0
 bsr.w .compare
.p86ff: ; BEQ $8710
 btst #1,d5
 bne.w .p8710
.p8701: ; LDY #$03
 moveq #0,d6
 move.b #$03,d6
 move.b d6,d3
 bsr.w .nz
.p8703: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p8705: ; BEQ $8718
 btst #1,d5
 bne.w .p8718
.p8707: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8708: ; LDA $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p870a: ; SEC
 ori.b #1,d5
.p870b: ; SBC $890e,Y
 move.l #$890e,d7
 add.w d3,d7
 bsr.w .resource
 bsr.w .sbc
.p870e: ; BCS $8715
 btst #0,d5
 bne.w .p8715
.p8710: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p8712: ; INC $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p8715: ; STA $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8718: ; CPX #$28
 moveq #0,d6
 move.b #$28,d6
 move.b d2,d0
 bsr.w .compare
.p871a: ; BCC $8730
 btst #0,d5
 beq.w .p8730
.p871c: ; LDA $cf
 move.l #$cf,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p871e: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p871f: ; BCC $8724
 btst #0,d5
 beq.w .p8724
.p8721: ; JMP $8899
 bra.w .p8899
.p8724: ; LDA $cd
 move.l #$cd,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8726: ; LDY $cc
 move.l #$cc,d7
 move.b (a0,d7.w),d6
 move.b d6,d3
 bsr.w .nz
.p8728: ; BMI $872c
 btst #7,d5
 bne.w .p872c
.p872a: ; EOR #$ff
 moveq #0,d6
 move.b #$ff,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p872c: ; CMP #$ff
 moveq #0,d6
 move.b #$ff,d6
 move.b d1,d0
 bsr.w .compare
.p872e: ; BNE $8739
 btst #1,d5
 beq.w .p8739
.p8730: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p8731: ; AND #$03
 moveq #0,d6
 move.b #$03,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8733: ; CMP #$01
 moveq #0,d6
 move.b #$01,d6
 move.b d1,d0
 bsr.w .compare
.p8735: ; BNE $8759
 btst #1,d5
 beq.w .p8759
.p8737: ; BEQ $874b
 btst #1,d5
 bne.w .p874b
.p8739: ; CPX #$29
 moveq #0,d6
 move.b #$29,d6
 move.b d2,d0
 bsr.w .compare
.p873b: ; BNE $8754
 btst #1,d5
 beq.w .p8754
.p873d: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p873f: ; LDA $0740,X
 move.l #$740,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8742: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p8744: ; JSR $8006
 move.b #$87,d6
 bsr.w .push
 move.b #$46,d6
 bsr.w .push
 bsr.w .p8006
.p8747: ; LDA $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8749: ; BEQ $87a3
 btst #1,d5
 bne.w .p87a3
.p874b: ; LDA $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p874e: ; BEQ $87a3
 btst #1,d5
 bne.w .p87a3
.p8750: ; LDA #$ff
 moveq #0,d6
 move.b #$ff,d6
 move.b d6,d1
 bsr.w .nz
.p8752: ; BNE $87a3
 btst #1,d5
 beq.w .p87a3
.p8754: ; CMP $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d1,d0
 bsr.w .compare
.p8757: ; BCC $875c
 btst #0,d5
 beq.w .p875c
.p8759: ; LDA $0710,X
 move.l #$710,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p875c: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p875d: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p875e: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p875f: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p8760: ; EOR #$0f
 moveq #0,d6
 move.b #$0f,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8762: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p8764: ; LDY #$06
 moveq #0,d6
 move.b #$06,d6
 move.b d6,d3
 bsr.w .nz
.p8766: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p8768: ; CMP #$05
 moveq #0,d6
 move.b #$05,d6
 move.b d1,d0
 bsr.w .compare
.p876a: ; BCC $8790
 btst #0,d5
 beq.w .p8790
.p876c: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p876e: ; LDY $0708,X
 move.l #$708,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d3
 bsr.w .nz
.p8771: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8774: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8775: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8776: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p8777: ; BCC $877b
 btst #0,d5
 beq.w .p877b
.p8779: ; EOR #$ff
 moveq #0,d6
 move.b #$ff,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p877b: ; BEQ $8790
 btst #1,d5
 bne.w .p8790
.p877d: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p877f: ; JSR $8006
 move.b #$87,d6
 bsr.w .push
 move.b #$81,d6
 bsr.w .push
 bsr.w .p8006
.p8782: ; LDA $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8784: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p8785: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p8786: ; CMP #$10
 moveq #0,d6
 move.b #$10,d6
 move.b d1,d0
 bsr.w .compare
.p8788: ; BCS $879e
 btst #0,d5
 bne.w .p879e
.p878a: ; CMP $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d1,d0
 bsr.w .compare
.p878c: ; BCC $8790
 btst #0,d5
 beq.w .p8790
.p878e: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p8790: ; LDA #$10
 moveq #0,d6
 move.b #$10,d6
 move.b d6,d1
 bsr.w .nz
.p8792: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p8794: ; LDA $070c,X
 move.l #$70c,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8797: ; SEC
 ori.b #1,d5
.p8798: ; SBC $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 bsr.w .sbc
.p879a: ; BIT $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 andi.b #$3d,d5
 move.b d6,d0
 andi.b #$c0,d0
 or.b d0,d5
 and.b d1,d6
 bne.s .bit879a
 ori.b #2,d5
.bit879a:
.p879c: ; BNE $87a3
 btst #1,d5
 beq.w .p87a3
.p879e: ; LDA $070c,X
 move.l #$70c,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87a1: ; AND #$f0
 moveq #0,d6
 move.b #$f0,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p87a3: ; LDY #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d3
 bsr.w .nz
.p87a5: ; JSR $80cf
 move.b #$87,d6
 bsr.w .push
 move.b #$a7,d6
 bsr.w .push
 bsr.w .p80cf
.p87a8: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p87a9: ; AND #$03
 moveq #0,d6
 move.b #$03,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p87ab: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p87ac: ; LDA $077c,Y
 move.l #$77c,d7
 add.w d3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87af: ; BMI $8805
 btst #7,d5
 bne.w .p8805
.p87b1: ; LDY #$05
 moveq #0,d6
 move.b #$05,d6
 move.b d6,d3
 bsr.w .nz
.p87b3: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p87b5: ; BEQ $8805
 btst #1,d5
 bne.w .p8805
.p87b7: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p87b9: ; LDY $0708,X
 move.l #$708,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d3
 bsr.w .nz
.p87bc: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87bf: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p87c0: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p87c1: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p87c2: ; BCC $87c6
 btst #0,d5
 beq.w .p87c6
.p87c4: ; EOR #$ff
 moveq #0,d6
 move.b #$ff,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p87c6: ; BEQ $8805
 btst #1,d5
 bne.w .p8805
.p87c8: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p87ca: ; JSR $8006
 move.b #$87,d6
 bsr.w .push
 move.b #$cc,d6
 bsr.w .push
 bsr.w .p8006
.p87cd: ; LDA $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87cf: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p87d0: ; ROR $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .ror
 move.b d6,(a0,d7.w)
.p87d2: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p87d3: ; ROR $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .ror
 move.b d6,(a0,d7.w)
.p87d5: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p87d6: ; ROR $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .ror
 move.b d6,(a0,d7.w)
.p87d8: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p87d9: ; ROR $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .ror
 move.b d6,(a0,d7.w)
.p87db: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p87dc: ; ORA $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p87de: ; BEQ $8805
 btst #1,d5
 bne.w .p8805
.p87e0: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87e3: ; BMI $87f3
 btst #7,d5
 bne.w .p87f3
.p87e5: ; CLC
 andi.b #$fe,d5
.p87e6: ; LDA $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87e8: ; ADC $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p87eb: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p87ed: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p87ee: ; ADC $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p87f1: ; BNE $8802
 btst #1,d5
 beq.w .p8802
.p87f3: ; SEC
 ori.b #1,d5
.p87f4: ; LDA $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87f7: ; SBC $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .sbc
.p87f9: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p87fb: ; LDA $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p87fe: ; STY $c1
 move.l #$c1,d7
 move.b d3,(a0,d7.w)
.p8800: ; SBC $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 bsr.w .sbc
.p8802: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8803: ; BNE $880d
 btst #1,d5
 beq.w .p880d
.p8805: ; LDA $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8808: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p880a: ; LDY $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d3
 bsr.w .nz
.p880d: ; CPX #$28
 moveq #0,d6
 move.b #$28,d6
 move.b d2,d0
 bsr.w .compare
.p880f: ; BCS $882e
 btst #0,d5
 bne.w .p882e
.p8811: ; LDA $d6
 move.l #$d6,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8813: ; BPL $882e
 btst #7,d5
 beq.w .p882e
.p8815: ; LDA $d8
 move.l #$d8,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8817: ; BEQ $882e
 btst #1,d5
 bne.w .p882e
.p8819: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p881b: ; STY $c1
 move.l #$c1,d7
 move.b d3,(a0,d7.w)
.p881d: ; LDA $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p881f: ; PHA
 move.b d1,d6
 bsr.w .push
.p8820: ; JSR $8006
 move.b #$88,d6
 bsr.w .push
 move.b #$22,d6
 bsr.w .push
 bsr.w .p8006
.p8823: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p8824: ; CLC
 andi.b #$fe,d5
.p8825: ; ADC $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p8827: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p8829: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p882b: ; ADC $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p882d: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p882e: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p882f: ; AND #$03
 moveq #0,d6
 move.b #$03,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8831: ; BNE $8842
 btst #1,d5
 beq.w .p8842
.p8833: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p8834: ; AND #$0f
 moveq #0,d6
 move.b #$0f,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8836: ; LDY #$07
 moveq #0,d6
 move.b #$07,d6
 move.b d6,d3
 bsr.w .nz
.p8838: ; ORA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p883a: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p883c: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p883e: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p8840: ; BEQ $887d
 btst #1,d5
 bne.w .p887d
.p8842: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p8843: ; LDY #$08
 moveq #0,d6
 move.b #$08,d6
 move.b d6,d3
 bsr.w .nz
.p8845: ; DEY
 subq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8846: ; CMP $892e,Y
 move.l #$892e,d7
 add.w d3,d7
 bsr.w .resource
 move.b d1,d0
 bsr.w .compare
.p8849: ; BCC $8845
 btst #0,d5
 beq.w .p8845
.p884b: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p884d: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p884e: ; CLC
 andi.b #$fe,d5
.p884f: ; ADC $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p8851: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8852: ; AND #$07
 moveq #0,d6
 move.b #$07,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8854: ; CLC
 andi.b #$fe,d5
.p8855: ; ADC #$06
 moveq #0,d6
 move.b #$06,d6
 bsr.w .adc
.p8857: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p8859: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p885a: ; AND #$38
 moveq #0,d6
 move.b #$38,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p885c: ; EOR #$38
 moveq #0,d6
 move.b #$38,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p885e: ; BEQ $8869
 btst #1,d5
 bne.w .p8869
.p8860: ; LSR $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 bsr.w .lsr
 move.b d6,(a0,d7.w)
.p8862: ; ROR $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .ror
 move.b d6,(a0,d7.w)
.p8864: ; SEC
 ori.b #1,d5
.p8865: ; SBC #$08
 moveq #0,d6
 move.b #$08,d6
 bsr.w .sbc
.p8867: ; BNE $8860
 btst #1,d5
 beq.w .p8860
.p8869: ; LDY #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d3
 bsr.w .nz
.p886b: ; LDA $0714,X
 move.l #$714,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p886e: ; BEQ $887d
 btst #1,d5
 bne.w .p887d
.p8870: ; BPL $8873
 btst #7,d5
 beq.w .p8873
.p8872: ; DEY
 subq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8873: ; CLC
 andi.b #$fe,d5
.p8874: ; ADC $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p8876: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p8878: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p8879: ; ADC $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p887b: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p887d: ; LDY #$02
 moveq #0,d6
 move.b #$02,d6
 move.b d6,d3
 bsr.w .nz
.p887f: ; LDA $c2
 move.l #$c2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8881: ; JSR $80cf
 move.b #$88,d6
 bsr.w .push
 move.b #$83,d6
 bsr.w .push
 bsr.w .p80cf
.p8884: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p8885: ; AND #$03
 moveq #0,d6
 move.b #$03,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8887: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8888: ; LDA $c1
 move.l #$c1,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p888a: ; CMP $077c,Y
 move.l #$77c,d7
 add.w d3,d7
 move.b (a0,d7.w),d6
 move.b d1,d0
 bsr.w .compare
.p888d: ; BEQ $8899
 btst #1,d5
 bne.w .p8899
.p888f: ; STA $077c,Y
 move.l #$77c,d7
 add.w d3,d7
 move.b d1,(a0,d7.w)
.p8892: ; ORA #$08
 moveq #0,d6
 move.b #$08,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8894: ; LDY #$03
 moveq #0,d6
 move.b #$03,d6
 move.b d6,d3
 bsr.w .nz
.p8896: ; JSR $80cf
 move.b #$88,d6
 bsr.w .push
 move.b #$98,d6
 bsr.w .push
 bsr.w .p80cf
.p8899: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p889c: ; AND #$20
 moveq #0,d6
 move.b #$20,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p889e: ; BEQ $88f3
 btst #1,d5
 bne.w .p88f3
.p88a0: ; LDA $0718,X
 move.l #$718,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p88a3: ; BEQ $88eb
 btst #1,d5
 bne.w .p88eb
.p88a5: ; LDY #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d3
 bsr.w .nz
.p88a7: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p88a8: ; PHP
 move.b d5,d6
 ori.b #$30,d6
 bsr.w .push
.p88a9: ; BCC $88b1
 btst #0,d5
 beq.w .p88b1
.p88ab: ; EOR #$ff
 moveq #0,d6
 move.b #$ff,d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p88ad: ; CLC
 andi.b #$fe,d5
.p88ae: ; ADC #$01
 moveq #0,d6
 move.b #$01,d6
 bsr.w .adc
.p88b0: ; DEY
 subq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p88b1: ; CLC
 andi.b #$fe,d5
.p88b2: ; ADC $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p88b5: ; STA $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p88b8: ; TYA
 move.b d3,d1
 move.b d1,d6
 bsr.w .nz
.p88b9: ; ADC $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p88bc: ; STA $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p88bf: ; LDA $071c,X
 move.l #$71c,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p88c2: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p88c3: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p88c4: ; SEC
 ori.b #1,d5
.p88c5: ; LDA $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p88c8: ; SBC $8934,Y
 move.l #$8934,d7
 add.w d3,d7
 bsr.w .resource
 bsr.w .sbc
.p88cb: ; LDA $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p88ce: ; AND #$3f
 moveq #0,d6
 move.b #$3f,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p88d0: ; SBC $8935,Y
 move.l #$8935,d7
 add.w d3,d7
 bsr.w .resource
 bsr.w .sbc
.p88d3: ; LDA #$ff
 moveq #0,d6
 move.b #$ff,d6
 move.b d6,d1
 bsr.w .nz
.p88d5: ; ADC #$00
 moveq #0,d6
 move.b #$00,d6
 bsr.w .adc
.p88d7: ; PLP
 bsr.w .pop
 move.b d6,d5
 ori.b #$30,d5
.p88d8: ; ADC #$00
 moveq #0,d6
 move.b #$00,d6
 bsr.w .adc
.p88da: ; BNE $88f3
 btst #1,d5
 beq.w .p88f3
.p88dc: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p88dd: ; BEQ $88f3
 btst #1,d5
 bne.w .p88f3
.p88df: ; LDA $8934,Y
 move.l #$8934,d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p88e2: ; STA $0720,X
 move.l #$720,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p88e5: ; LDA $8935,Y
 move.l #$8935,d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p88e8: ; STA $0724,X
 move.l #$724,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p88eb: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p88ee: ; AND #$df
 moveq #0,d6
 move.b #$df,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p88f0: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p88f3: ; LDY #$04
 moveq #0,d6
 move.b #$04,d6
 move.b d6,d3
 bsr.w .nz
.p88f5: ; LDA ($c5),Y
 moveq #0,d7
 move.b $c6(a0),d7
 lsl.w #8,d7
 move.b $c5(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p88f7: ; AND #$7f
 moveq #0,d6
 move.b #$7f,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p88f9: ; BEQ $890d
 btst #1,d5
 bne.w .p890d
.p88fb: ; CLC
 andi.b #$fe,d5
.p88fc: ; ADC $0708,X
 move.l #$708,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 bsr.w .adc
.p88ff: ; STA $0708,X
 move.l #$708,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8902: ; BCC $890d
 btst #0,d5
 beq.w .p890d
.p8904: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8907: ; CLC
 andi.b #$fe,d5
.p8908: ; ADC #$40
 moveq #0,d6
 move.b #$40,d6
 bsr.w .adc
.p890a: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p890d: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
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
