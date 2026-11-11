; Static native translation of bounded fixed-bank stage fade/resource/video/audio-request setup.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_stage_fixed:
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
 bsr.w recovery_bank_loader_stage_fixed_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_stage_fixed_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_stage_fixed_core:
 cmpi.b #8,3(a4)
 bhs.w .invalid
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
 cmpi.w #$c115,(a1)
 beq.w .pc115
 cmpi.w #$c14e,(a1)
 beq.w .pc14e
 cmpi.w #$c158,(a1)
 beq.w .pc158
 cmpi.w #$c24a,(a1)
 beq.w .pc24a
 cmpi.w #$e099,(a1)
 beq.w .pe099
 bra.w .budget_failure
.pc115: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pc117: ; STX $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pc119: ; LDA $0360,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc11c: ; BMI $c139
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pc139
.pc11e: ; STA $2006
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2006,d1
 move.b d4,d0
 bsr.w .store
.pc121: ; LDA $0361,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc124: ; STA $2006
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2006,d1
 move.b d4,d0
 bsr.w .store
.pc127: ; LDY $0362,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0362,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pc12a: ; LDA $0363,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0363,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc12d: ; STA $2007
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2007,d1
 move.b d4,d0
 bsr.w .store
.pc130: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc131: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc132: ; BPL $c12a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pc12a
.pc134: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc135: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc136: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc137: ; BNE $c119
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc119
.pc139: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
 move.w d0,(a1)
 bra.w .success
.pc14e: ; INC $f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f0,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pc150: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc152: ; STA $fe
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fe,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc154: ; STA $2001
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2001,d1
 move.b d4,d0
 bsr.w .store
.pc157: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
 move.w d0,(a1)
 bra.w .success
.pc158: ; DEC $f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f0,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pc15a: ; LDA #$1e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1e,d0
 move.b d0,d4
 bsr.w .nz
.pc15c: ; STA $fe
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fe,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc15e: ; STA $2001
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2001,d1
 move.b d4,d0
 bsr.w .store
.pc161: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
 move.w d0,(a1)
 bra.w .success
.pc21e: ; LDX $97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pc220: ; CPX #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc220
 ori.b #1,d7
.cmpc220:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc222: ; BNE $c229
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc229
.pc224: ; LDA #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f8,d0
 move.b d0,d4
 bsr.w .nz
.pc226: ; STA $0200
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 move.b d4,d0
 bsr.w .store
.pc229: ; LDA #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f8,d0
 move.b d0,d4
 bsr.w .nz
.pc22b: ; STA $0200,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc22e: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc22f: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc230: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc231: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc232: ; BNE $c22b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc22b
.pc234: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
 move.w d0,(a1)
 bra.w .success
.pc235: ; LDX #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d0,d5
 bsr.w .nz
.pc237: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc239: ; STA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc23c: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.pc23e: ; STA $0590,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0590,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc241: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc242: ; CPX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc242
 ori.b #1,d7
.cmpc242:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc244: ; BNE $c237
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc237
.pc246: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
 move.w d0,(a1)
 bra.w .success
.pc24a: ; JSR $c235
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c2,d0
 bsr.w .push
 move.w #$4c,d0
 bsr.w .push
 bra.w .pc235
.pc24d: ; JSR $c21e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c2,d0
 bsr.w .push
 move.w #$4f,d0
 bsr.w .push
 bra.w .pc21e
.pc250: ; JMP $ff04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff04,(a1)
 bra.w .success
.pc2f7: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shiftc2f7
 ori.b #1,d7
.shiftc2f7:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc2f8: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shiftc2f8
 ori.b #1,d7
.shiftc2f8:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc2f9: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shiftc2f9
 ori.b #1,d7
.shiftc2f9:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc2fa: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shiftc2fa
 ori.b #1,d7
.shiftc2fa:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc2fb: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pc2fc: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc2fe: ; ADC #$c3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c3,d0
 bsr.w .adc
.pc300: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc302: ; LDA #$44
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$44,d0
 move.b d0,d4
 bsr.w .nz
.pc304: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc306: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pc308: ; LDA ($00),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $01(a0),d1
 lsl.w #8,d1
 move.b $00(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc30a: ; STA $0300,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0300,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc30d: ; STA $0320,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0320,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc310: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc311: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc312: ; CPX #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc312
 ori.b #1,d7
.cmpc312:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc314: ; BNE $c308
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc308
.pc316: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
 move.w d0,(a1)
 bra.w .success
.pc317: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shiftc317
 ori.b #1,d7
.shiftc317:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc318: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shiftc318
 ori.b #1,d7
.shiftc318:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc319: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shiftc319
 ori.b #1,d7
.shiftc319:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc31a: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pc31b: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pc31d: ; LDA $c4d4,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c4d4,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc320: ; STA $0310,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0310,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc323: ; STA $0330,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0330,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc326: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc327: ; CPX #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc327
 ori.b #1,d7
.cmpc327:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc329: ; BNE $c31d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc31d
.pc32b: ; LDA $c4dc,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c4dc,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc32e: ; STA $0310,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0310,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc331: ; STA $0330,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0330,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc334: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc335: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc336: ; CPX #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc336
 ori.b #1,d7
.cmpc336:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc338: ; BNE $c32b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc32b
.pc33a: ; LDA $0300
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0300,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc33d: ; STA $0310
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0310,d1
 move.b d4,d0
 bsr.w .store
.pc340: ; STA $0330
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0330,d1
 move.b d4,d0
 bsr.w .store
.pc343: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
 move.w d0,(a1)
 bra.w .success
.pe099: ; LDX $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pe09b: ; LDA $e287,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e287,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe09e: ; STA $32
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$32,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0a0: ; LDA $e296,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e296,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0a3: ; STA $33
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$33,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0a5: ; LDA $e2a5,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e2a5,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0a8: ; STA $34
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$34,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0aa: ; LDA $e2b4,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e2b4,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0ad: ; STA $35
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$35,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0af: ; LDA $e1f1,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1f1,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0b2: ; STA $36
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$36,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0b4: ; LDA $e200,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e200,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0b7: ; STA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0b9: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0bb: ; LDA $e20f,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e20f,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0be: ; STA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0c0: ; STA $0520
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0520,d1
 move.b d4,d0
 bsr.w .store
.pe0c3: ; STA $0521
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0521,d1
 move.b d4,d0
 bsr.w .store
.pe0c6: ; STA $2d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2d,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0c8: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pe0ca: ; STA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0cc: ; STA $0500
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 move.b d4,d0
 bsr.w .store
.pe0cf: ; STA $0501
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0501,d1
 move.b d4,d0
 bsr.w .store
.pe0d2: ; LDY $e21e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e21e,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pe0d5: ; STY $2c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2c,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.pe0d7: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pe0d8: ; STY $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.pe0da: ; LDA $e22d,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e22d,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0dd: ; STA $1a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1a,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0df: ; LDA $e23c,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e23c,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0e2: ; STA $1b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1b,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0e4: ; LDA $e25a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e25a,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0e7: ; LDY $b8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b8,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pe0e9: ; BNE $e0ee
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pe0ee
.pe0eb: ; JSR $f377
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e0,d0
 bsr.w .push
 move.w #$ed,d0
 bsr.w .push
 bra.w .pf377
.pe0ee: ; LDA $e278,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e278,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0f1: ; STA $3d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3d,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe0f3: ; LDA $e24b,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e24b,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe0f6: ; STX $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pe0f8: ; JSR $c2f7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e0,d0
 bsr.w .push
 move.w #$fa,d0
 bsr.w .push
 bra.w .pc2f7
.pe0fb: ; LDX $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pe0fd: ; LDA $e269,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e269,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe100: ; JSR $c317
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$02,d0
 bsr.w .push
 bra.w .pc317
.pe103: ; JSR $e179
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$05,d0
 bsr.w .push
 move.w #$e179,(a1)
 bra.w .success
.pf377: ; STA $d9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d9,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf379: ; STX $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pf37b: ; LDX $da
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$da,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pf37d: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf37f: ; LDA $dc,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dc,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf381: ; CMP #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$88,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf381
 ori.b #1,d7
.cmpf381:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf383: ; BNE $f38f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pf38f
.pf385: ; LDA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf387: ; STA $dc,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dc,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf389: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pf38a: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.w .nz
.pf38b: ; AND #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pf38d: ; STA $da
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$da,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf38f: ; LDX $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pf391: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c24d,d0
 beq.w .pc24d
 cmpi.w #$c250,d0
 beq.w .pc250
 cmpi.w #$e0ee,d0
 beq.w .pe0ee
 cmpi.w #$e0fb,d0
 beq.w .pe0fb
 cmpi.w #$e103,d0
 beq.w .pe103
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
 bra.w .bad_read
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
 cmpi.w #$2001,d1
 beq.s .store_accepted
 cmpi.w #$2006,d1
 beq.s .store_accepted
 cmpi.w #$2007,d1
 bne.w .bad_read
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
