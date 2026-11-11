; Static SFX command mask, bank3 82DC, X0..3, raw flags and wrapped SP.
; A0 RAM2048,A1 context8,A2 journal78,A3 immutable bank3 16384.
; Supports five fixed callbacks; stops at event action830B/831B. No envelope.
recovery_sfx_command_mask:
 movem.l d1-d7/a4-a6,-(sp)
 cmpi.w #$82dc,(a1)
 bne.w .reject
 cmpi.b #3,3(a1)
 bhi.w .reject
 moveq #0,d7
 move.b $d1(a0),d7
 lsl.w #8,d7
 move.b $d0(a0),d7
 cmpi.w #$8000,d7
 bcs.w .reject
 cmpi.w #$bffe,d7
 bhi.w .reject
 move.w d7,d6
 subi.w #$8000,d6
 moveq #0,d0
 move.b (a3,d6.w),d0
 cmpi.b #31,d0
 bhi.w .reject
 addq.w #1,d7
 moveq #4,d6
.count:
 lsr.b #1,d0
 bcc.s .not_set
 addq.w #1,d7
.not_set:
 dbra d6,.count
 cmpi.w #$bfff,d7
 bhi.w .reject
 cmpi.b #$67,$2fb(a3)
 bne.w .reject
 cmpi.b #$86,$2fc(a3)
 bne.w .reject
 cmpi.b #$a5,$2fd(a3)
 bne.w .reject
 cmpi.b #$86,$2fe(a3)
 bne.w .reject
 cmpi.b #$52,$2ff(a3)
 bne.w .reject
 cmpi.b #$86,$300(a3)
 bne.w .reject
 cmpi.b #$9f,$301(a3)
 bne.w .reject
 cmpi.b #$86,$302(a3)
 bne.w .reject
 cmpi.b #$99,$303(a3)
 bne.w .reject
 cmpi.b #$86,$304(a3)
 bne.w .reject
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
 bra.w .p82dc
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
.p82dc: ; LDA #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d1
 bsr.w .nz
.p82de: ; STA $c4
 move.l #$c4,d7
 move.b d1,(a0,d7.w)
.p82e0: ; JSR $8358
 move.b #$82,d6
 bsr.w .push
 move.b #$e2,d6
 bsr.w .push
 bsr.w .p8358
.p82e3: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p82e4: ; BCC $82f2
 btst #0,d5
 beq.w .p82f2
.p82e6: ; PHA
 move.b d1,d6
 bsr.w .push
.p82e7: ; JSR $8358
 move.b #$82,d6
 bsr.w .push
 move.b #$e9,d6
 bsr.w .push
 bsr.w .p8358
.p82ea: ; STA $c3
 move.l #$c3,d7
 move.b d1,(a0,d7.w)
.p82ec: ; LDA $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p82ee: ; JSR $82f8
 move.b #$82,d6
 bsr.w .push
 move.b #$f0,d6
 bsr.w .push
 bsr.w .p82f8
.p82f1: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p82f2: ; BEQ $8305
 btst #1,d5
 bne.w .p8305
.p82f4: ; INC $c4
 move.l #$c4,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p82f6: ; BNE $82e3
 btst #1,d5
 beq.w .p82e3
 bra.w .p8305
.p82f8: ; JSR $8023
 move.b #$82,d6
 bsr.w .push
 move.b #$fa,d6
 bsr.w .push
 bsr.w .p8023
 rts
.p8305: ; JSR $8358
 move.b #$83,d6
 bsr.w .push
 move.b #$07,d6
 bsr.w .push
 bsr.w .p8358
.p8308: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8309: ; BNE $831b
 btst #1,d5
 beq.w .p831b
 bra.w .p830b
.p8358: ; LDY #$00
 moveq #0,d6
 move.b #$00,d6
 move.b d6,d3
 bsr.w .nz
.p835a: ; LDA ($d0),Y
 moveq #0,d7
 move.b $d1(a0),d7
 lsl.w #8,d7
 move.b $d0(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p835c: ; INC $d0
 move.l #$d0,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p835e: ; BNE $8362
 btst #1,d5
 beq.w .p8362
.p8360: ; INC $d1
 move.l #$d1,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p8362: ; RTS
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
 moveq #0,d7
 move.b $c2(a0),d7
 lsl.w #8,d7
 move.b $c1(a0),d7
 cmpi.w #$8667,d7
 beq.w .p8667
 cmpi.w #$86a5,d7
 beq.w .p86a5
 cmpi.w #$8652,d7
 beq.w .p8652
 cmpi.w #$869f,d7
 beq.w .p869f
 bra.w .p8699
.p8652: ; CPX #$01
 moveq #0,d6
 move.b #$01,d6
 andi.b #$fe,d5
 cmp.b d6,d2
 bcs.s .cmp_no_carry1
 ori.b #1,d5
.cmp_no_carry1:
 move.b d2,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p8654: ; BNE $865a
 btst #1,d5
 beq.w .p865a
.p8656: ; LDA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8658: ; BNE $8663
 btst #1,d5
 beq.w .p8663
.p865a: ; LDA $070c,X
 move.l #$70c,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p865d: ; AND #$c0
 moveq #0,d6
 move.b #$c0,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p865f: ; ORA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8661: ; ORA #$30
 moveq #0,d6
 move.b #$30,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8663: ; STA $070c,X
 move.l #$70c,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8666: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p8667: ; INC $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 addq.b #1,d6
 move.b d6,(a0,d7.w)
 bsr.w .nz
.p8669: ; LDA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p866b: ; CMP $0700,X
 move.l #$700,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 andi.b #$fe,d5
 cmp.b d6,d1
 bcs.s .cmp_no_carry2
 ori.b #1,d5
.cmp_no_carry2:
 move.b d1,d0
 sub.b d6,d0
 move.b d0,d6
 bsr.w .nz
.p866e: ; BEQ $8698
 btst #1,d5
 bne.w .p8698
.p8670: ; STA $0700,X
 move.l #$700,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p8673: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8674: ; LDA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p8677: ; ORA #$08
 moveq #0,d6
 move.b #$08,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p8679: ; STA $0704,X
 move.l #$704,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
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
.p8699: ; LDA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p869b: ; STA $0714,X
 move.l #$714,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p869e: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p869f: ; LDA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p86a1: ; STA $0718,X
 move.l #$718,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p86a4: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p86a5: ; LDA $070c,X
 move.l #$70c,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 move.b d6,d1
 bsr.w .nz
.p86a8: ; AND #$0f
 moveq #0,d6
 move.b #$0f,d6
 and.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p86aa: ; ORA $c3
 move.l #$c3,d7
 move.b (a0,d7.w),d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p86ac: ; ORA #$30
 moveq #0,d6
 move.b #$30,d6
 or.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p86ae: ; STA $070c,X
 move.l #$70c,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p86b1: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts
.p830b:
 move.w #$830b,d7
 bra.w .publish
.p831b:
 move.w #$831b,d7
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
