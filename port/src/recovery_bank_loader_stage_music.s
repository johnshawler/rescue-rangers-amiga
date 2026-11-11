; Static native translation of bounded bank3 original stage music command0 initialization.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_stage_music:
 ; Transaction preflight uses temporary RAM/context and publishes no effects.
 ; The external resource must remain immutable between both passes.
 movem.l d1-d7/a0-a6,-(sp)
 suba.w #2060,sp
 movea.l a0,a3
 movea.l sp,a0
 movea.l a0,a6
 move.w #511,d0
.copy_ram:
 move.l (a3)+,(a6)+
 dbra d0,.copy_ram
 move.l (a1),(a6)+
 move.l 4(a1),(a6)+
 lea 2048(sp),a1
 lea 2056(sp),a2
 movea.w #1,a6
 bsr.w recovery_bank_loader_stage_music_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_stage_music_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_stage_music_core:
 cmpi.w #$8003,(a1)
 bne.w .invalid
 tst.b 2(a1)
 bne.w .invalid
 tst.b $cf(a0)
 bne.w .invalid
 cmpi.b #3,3(a4)
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 movem.l d1-d7/a3-a4/a6,-(sp)
 lea 2(a2),a3
 clr.w (a2)
 moveq #0,d4
 moveq #0,d5
 moveq #0,d6
 moveq #0,d7
 move.b 2(a1),d4
 move.b 3(a1),d5
 move.b 4(a1),d6
 move.b 5(a1),d7
 movea.l #200000,a4
 cmpi.w #$8003,(a1)
 beq.w .p8003
 bra.w .budget_failure
.p8003: ; JMP $80e1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p80e1
.p80bb: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.w .nz
.p80bc: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80be: ; EOR #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80c0: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shift80c0
 ori.b #1,d7
.shift80c0:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.p80c1: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shift80c1
 ori.b #1,d7
.shift80c1:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.p80c2: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.p80c3: ; LDA #$30
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$30,d0
 move.b d0,d4
 bsr.w .nz
.p80c5: ; CPY #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp80c5
 ori.b #1,d7
.cmp80c5:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p80c7: ; BNE $80cb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80cb
.p80c9: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p80cb: ; STA $4000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4000,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.p80ce: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80e6,d0
 beq.w .p80e6
 cmpi.w #$81cd,d0
 beq.w .p81cd
 move.w d0,(a1)
 bra.w .success
.p80e1: ; INC $c0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c0,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p80e3: ; JSR $80e9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$e5,d0
 bsr.w .push
 bra.w .p80e9
.p80e6: ; DEC $c0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c0,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p80e8: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80e6,d0
 beq.w .p80e6
 cmpi.w #$81cd,d0
 beq.w .p81cd
 move.w d0,(a1)
 bra.w .success
.p80e9: ; CMP #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f0,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp80e9
 ori.b #1,d7
.cmp80e9:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p80eb: ; BCC $80f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p80f0
.p80ed: ; JMP $817d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$817d,(a1)
 bra.w .success
.p80f0: ; CMP $8a00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8a00,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp80f0
 ori.b #1,d7
.cmp80f0:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p80f3: ; BCC $80fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p80fb
.p80f5: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p80f6: ; SBC $8a00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8a00,d1
 bsr.w .read
 bsr.w .sbc
.p80f9: ; BCS $80f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p80f0
.p80fb: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shift80fb
 ori.b #1,d7
.shift80fb:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.p80fc: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d4,d0
 bsr.w .nz
.p80fd: ; LDA $8a04,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8a04,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8100: ; STA $c1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c1,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8102: ; LDA $8a03,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8a03,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8105: ; STA $c2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c2,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8107: ; ORA $c1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c1,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8109: ; BEQ $8151
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8151
.p810b: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p810d: ; LDA ($c1),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $c2(a0),d1
 lsl.w #8,d1
 move.b $c1(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p810f: ; BEQ $8152
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8152
.p8111: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p8112: ; STA $c4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c4,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8114: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8116: ; CMP $ce
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ce,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8116
 ori.b #1,d7
.cmp8116:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8118: ; BCC $8151
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p8151
.p811a: ; STA $ce
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ce,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p811c: ; BNE $8128
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8128
.p811e: ; LDA $d6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d6,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8120: ; BPL $8128
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8128
.p8122: ; LDA $c4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c4,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8124: ; BMI $8128
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p8128
.p8126: ; STY $d7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d7,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.p8128: ; STY $d6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d6,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.p812a: ; ASL $c4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c4,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shift812a
 ori.b #1,d7
.shift812a:
 lsl.b #1,d0
 bsr.w .store
 bsr.w .nz
.p812c: ; ROR $d6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d6,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shift812c
 ori.b #1,d7
.shift812c:
 lsr.b #1,d0
 btst #0,d2
 beq.s .rotate812c
 ori.b #128,d0
.rotate812c:
 bsr.w .store
 bsr.w .nz
.p812e: ; BPL $8132
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8132
.p8130: ; STX $d7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d7,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.p8132: ; INC $c1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c1,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p8134: ; LDA $c1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c1,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8136: ; STA $d0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d0,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8138: ; BNE $813c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p813c
.p813a: ; INC $c2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c2,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p813c: ; LDA $c2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c2,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p813e: ; STA $d1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d1,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8140: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.p8141: ; STA $d2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d2,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8143: ; STA $d3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d3,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8145: ; STA $d4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d4,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8147: ; STA $d5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8149: ; LDY #$27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d0
 move.b d0,d6
 bsr.w .nz
.p814b: ; STA $0700,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0700,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.p814e: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p814f: ; BPL $814b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p814b
.p8151: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80e6,d0
 beq.w .p80e6
 cmpi.w #$81cd,d0
 beq.w .p81cd
 move.w d0,(a1)
 bra.w .success
.p8152: ; LDX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d5
 bsr.w .nz
.p8154: ; STX $c9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c9,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.p8156: ; LDX #$99
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$99,d0
 move.b d0,d5
 bsr.w .nz
.p8158: ; STX $ca
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ca,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.p815a: ; STA $c8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p815c: ; STA $cb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p815e: ; STA $cc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8160: ; STA $cd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cd,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p8162: ; LDX #$53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$53,d0
 move.b d0,d5
 bsr.w .nz
.p8164: ; STA $0728,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0728,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.p8167: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p8168: ; BPL $8164
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8164
.p816a: ; LDX #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d5
 bsr.w .nz
.p816c: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p816d: ; LDA ($c1),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $c2(a0),d1
 lsl.w #8,d1
 move.b $c1(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p816f: ; STA $0754,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0754,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.p8172: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8173: ; LDA ($c1),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $c2(a0),d1
 lsl.w #8,d1
 move.b $c1(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8175: ; STA $0750,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0750,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.p8178: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p8179: ; BPL $816c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p816c
.p817b: ; BMI $81c0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p81c0
.p81c0: ; LDA $cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cf,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81c2: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.p81c3: ; LDX #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d5
 bsr.w .nz
.p81c5: ; LDA $cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cf,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81c7: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shift81c7
 ori.b #1,d7
.shift81c7:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.p81c8: ; BCS $81da
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p81da
.p81ca: ; JSR $80bb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$81,d0
 bsr.w .push
 move.w #$cc,d0
 bsr.w .push
 bra.w .p80bb
.p81cd: ; LDA $0754,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0754,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81d0: ; ORA $0750,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0750,d1
 add.w d5,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p81d3: ; BEQ $81da
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p81da
.p81d5: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.p81d7: ; STA $077c,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$077c,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.p81da: ; LSR $cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cf,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shift81da
 ori.b #1,d7
.shift81da:
 lsr.b #1,d0
 bsr.w .store
 bsr.w .nz
.p81dc: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p81dd: ; BPL $81c5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p81c5
.p81df: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.p81e0: ; STA $cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cf,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.p81e2: ; LDA #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 move.b d0,d4
 bsr.w .nz
.p81e4: ; STA $4001
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4001,d1
 move.b d4,d0
 bsr.w .store
.p81e7: ; STA $4005
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4005,d1
 move.b d4,d0
 bsr.w .store
.p81ea: ; LDA #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d0,d4
 bsr.w .nz
.p81ec: ; STA $4015
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4015,d1
 move.b d4,d0
 bsr.w .store
.p81ef: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80e6,d0
 beq.w .p80e6
 cmpi.w #$81cd,d0
 beq.w .p81cd
 move.w d0,(a1)
 bra.w .success
; NZ preserves all other raw bits, including noncanonical B/U/D.
.nz:
 andi.b #$7d,d7
 tst.b d0
 bne.s .nonzero
 ori.b #2,d7
.nonzero:
 tst.b d0
 bpl.s .nzdone
 ori.b #$80,d7
.nzdone:
 rts
.push:
 moveq #0,d1
 move.b 6(a1),d1
 move.b d0,$100(a0,d1.w)
 subq.b #1,6(a1)
 rts
.pop:
 addq.b #1,6(a1)
 moveq #0,d1
 move.b 6(a1),d1
 moveq #0,d0
 move.b $100(a0,d1.w),d0
 rts
; Data read only, never instruction fetch. RAM mirrors and fixed/mapped PRG.
.read:
 andi.l #$ffff,d1
 cmpi.w #$2000,d1
 bhs.s .external
 andi.w #$7ff,d1
 moveq #0,d0
 move.b (a0,d1.w),d0
 rts
.external:
 cmpi.w #$8000,d1
 bcs.w .bad_read
 cmpi.w #15000,(a2)
 bhs.w .bad_read
 move.l d1,d2
 cmpi.w #$c000,d1
 bhs.s .fixed
 addi.l #$4000,d2
 bra.s .resource
.fixed:
 addi.l #$10000,d2
.resource:
 moveq #0,d0
 move.b (a5,d2.l),d0
 cmpa.w #0,a6
 bne.s .validation_read
 move.w d1,(a3)+
 move.b d0,(a3)+
 clr.b (a3)+
.validation_read:
 addq.w #1,(a2)
 rts
.store:
 andi.l #$ffff,d1
 cmpi.w #$2000,d1
 bhs.s .store_device
 andi.w #$7ff,d1
 move.b d0,(a0,d1.w)
 rts
.store_device:
 cmpi.w #$4000,d1
 bcs.w .bad_read
 cmpi.w #$4015,d1
 bhi.w .bad_read
.store_accepted:
 cmpi.w #15000,(a2)
 bhs.w .bad_read
 cmpa.w #0,a6
 bne.s .store_validated
 move.w d1,(a3)+
 move.b d0,(a3)+
 move.b #1,(a3)+
.store_validated:
 addq.w #1,(a2)
 rts
; Binary 2A03 math: the raw decimal bit never changes arithmetic.
.adc:
 andi.l #255,d0
 move.l d4,d2
 andi.l #255,d2
 move.l d2,d3
 add.w d0,d3
 btst #0,d7
 beq.s .adc0
 addq.w #1,d3
.adc0:
 eor.b d2,d0
 not.b d0
 eor.b d3,d2
 and.b d2,d0
 andi.b #$3c,d7
 btst #7,d0
 beq.s .adcv
 ori.b #$40,d7
.adcv:
 cmpi.w #255,d3
 bls.s .adcc
 ori.b #1,d7
.adcc:
 move.b d3,d4
 move.b d4,d0
 bra.w .nz
.sbc:
 andi.l #255,d0
 move.l d4,d2
 andi.l #255,d2
 move.l d2,d3
 sub.w d0,d3
 btst #0,d7
 bne.s .sbc0
 subq.w #1,d3
.sbc0:
 eor.b d2,d0
 eor.b d3,d2
 and.b d2,d0
 andi.b #$3c,d7
 btst #7,d0
 beq.s .sbcv
 ori.b #$40,d7
.sbcv:
 tst.w d3
 bmi.s .sbcc
 ori.b #1,d7
.sbcc:
 move.b d3,d4
 move.b d4,d0
 bra.w .nz
.bad_read:
 addq.l #4,sp
.budget_failure:
 moveq #-2,d0
 bra.s .save
.success:
 moveq #1,d0
.save:
 move.b d4,2(a1)
 move.b d5,3(a1)
 move.b d6,4(a1)
 move.b d7,5(a1)
 movem.l (sp)+,d1-d7/a3-a4/a6
 rts
.invalid:
 moveq #-1,d0
 rts
