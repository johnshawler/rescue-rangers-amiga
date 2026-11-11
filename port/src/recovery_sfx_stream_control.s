; Native PAL 68020 high-bit SFX stream control, bank 3. Entry 8235.
; Even D7: clear stream, restore music channels, genuine outer RTS.
; Odd D7: genuine JSR and stop at unsupported header dispatch 80FB.
; No resource reads. A0 RAM2048 A1 context8 A2 journal30 A3 unused.
; D0=1/-1; all other general registers preserved. Exact raw NES status.
recovery_sfx_stream_control:
 movem.l d1-d7/a4-a6,-(sp)
 cmpi.w #$8235,(a1)
 bne.w .reject
 clr.w (a2)
 moveq #0,d1
 moveq #0,d2
 moveq #0,d3
 moveq #0,d4
 move.b 2(a1),d1
 move.b 3(a1),d2
 move.b 4(a1),d3
 move.b 5(a1),d5
 move.b 6(a1),d4
 bra.w .p8235
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
.p8235: ; STY $ce
 move.b d3,$ce(a0)
.p8237: ; LDA $d7
 move.b $d7(a0),d1
 move.b d1,d6
 bsr.w .nz
.p8239: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p823a: ; BCC $8242
 btst #0,d5
 beq.w .p8242
.p823c: ; JSR $80fb
 move.b #$82,d6
 bsr.w .push
 move.b #$3e,d6
 bsr.w .push
 move.w #$80fb,d7
 bra.w .publish
.p8242: ; JMP $8197
 bra.w .p8197
.p8197: ; LDA #$00
 move.b #$00,d1
 move.b d1,d6
 bsr.w .nz
.p8199: ; STA $ce
 move.b d1,$ce(a0)
.p819b: ; STA $d0
 move.b d1,$d0(a0)
.p819d: ; STA $d1
 move.b d1,$d1(a0)
.p819f: ; STA $d7
 move.b d1,$d7(a0)
.p81a1: ; STA $d8
 move.b d1,$d8(a0)
.p81a3: ; LDA $cf
 move.b $cf(a0),d1
 move.b d1,d6
 bsr.w .nz
.p81a5: ; BEQ $81b2
 btst #1,d5
 bne.w .p81b2
.p81a7: ; EOR #$0f
 eori.b #15,d1
 move.b d1,d6
 bsr.w .nz
.p81a9: ; STA $cf
 move.b d1,$cf(a0)
.p81ab: ; JSR $81c0
 move.b #$81,d6
 bsr.w .push
 move.b #$ad,d6
 bsr.w .push
 bsr.w .p81c0
.p81ae: ; LDA #$00
 move.b #$00,d1
 move.b d1,d6
 bsr.w .nz
.p81b0: ; STA $cf
 move.b d1,$cf(a0)
.p81b2: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 bra.w .publish
.p81c0: ; LDA $cf
 move.b $cf(a0),d1
 move.b d1,d6
 bsr.w .nz
.p81c2: ; PHA
 move.b d1,d6
 bsr.w .push
.p81c3: ; LDX #$03
 move.b #$03,d2
 move.b d2,d6
 bsr.w .nz
.p81c5: ; LDA $cf
 move.b $cf(a0),d1
 move.b d1,d6
 bsr.w .nz
.p81c7: ; LSR A
 move.b d1,d6
 bsr.w .lsr
 move.b d6,d1
.p81c8: ; BCS $81da
 btst #0,d5
 bne.w .p81da
.p81ca: ; JSR $80bb
 move.b #$81,d6
 bsr.w .push
 move.b #$cc,d6
 bsr.w .push
 bsr.w .p80bb
.p81cd: ; LDA $0754,X
 move.b $754(a0,d2.w),d1
 move.b d1,d6
 bsr.w .nz
.p81d0: ; ORA $0750,X
 or.b $750(a0,d2.w),d1
 move.b d1,d6
 bsr.w .nz
.p81d3: ; BEQ $81da
 btst #1,d5
 bne.w .p81da
.p81d5: ; LDA #$ff
 move.b #$ff,d1
 move.b d1,d6
 bsr.w .nz
.p81d7: ; STA $077c,X
 move.b d1,$77c(a0,d2.w)
.p81da: ; LSR $cf
 move.b $cf(a0),d6
 bsr.w .lsr
 move.b d6,$cf(a0)
.p81dc: ; DEX
 subq.b #1,d2
 move.b d2,d6
 bsr.w .nz
.p81dd: ; BPL $81c5
 btst #7,d5
 beq.w .p81c5
.p81df: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p81e0: ; STA $cf
 move.b d1,$cf(a0)
.p81e2: ; LDA #$08
 move.b #$08,d1
 move.b d1,d6
 bsr.w .nz
.p81e4: ; STA $4001
 move.w #$4001,d7
 move.b d1,d6
 bsr.w .apu
.p81e7: ; STA $4005
 move.w #$4005,d7
 move.b d1,d6
 bsr.w .apu
.p81ea: ; LDA #$0f
 move.b #$0f,d1
 move.b d1,d6
 bsr.w .nz
.p81ec: ; STA $4015
 move.w #$4015,d7
 move.b d1,d6
 bsr.w .apu
.p81ef: ; RTS
 bsr.w .pop
 bsr.w .pop
 rts
.p80bb: ; TXA
 move.b d2,d1
 move.b d1,d6
 bsr.w .nz
.p80bc: ; AND #$03
 andi.b #3,d1
 move.b d1,d6
 bsr.w .nz
.p80be: ; EOR #$03
 eori.b #3,d1
 move.b d1,d6
 bsr.w .nz
.p80c0: ; ASL A
 andi.b #$fe,d5
 btst #7,d1
 beq.s .nocarry80c0
 ori.b #1,d5
 .nocarry80c0:
 add.b d1,d1
 move.b d1,d6
 bsr.w .nz
.p80c1: ; ASL A
 andi.b #$fe,d5
 btst #7,d1
 beq.s .nocarry80c1
 ori.b #1,d5
 .nocarry80c1:
 add.b d1,d1
 move.b d1,d6
 bsr.w .nz
.p80c2: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p80c3: ; LDA #$30
 move.b #$30,d1
 move.b d1,d6
 bsr.w .nz
.p80c5: ; CPY #$08
 andi.b #$fe,d5
 cmpi.b #8,d3
 bcs.s .cmpbelow
 ori.b #1,d5
 .cmpbelow:
 move.b d3,d6
 subq.b #8,d6
 bsr.w .nz
.p80c7: ; BNE $80cb
 btst #1,d5
 beq.w .p80cb
.p80c9: ; LDA #$00
 move.b #$00,d1
 move.b d1,d6
 bsr.w .nz
.p80cb: ; STA $4000,Y
 moveq #0,d7
 move.b d3,d7
 addi.w #$4000,d7
 move.b d1,d6
 bsr.w .apu
.p80ce: ; RTS
 bsr.w .pop
 bsr.w .pop
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
.lsr:
 andi.b #$fe,d5
 btst #0,d6
 beq.s .lsr_nc
 ori.b #1,d5
.lsr_nc:
 lsr.b #1,d6
 bra.w .nz
