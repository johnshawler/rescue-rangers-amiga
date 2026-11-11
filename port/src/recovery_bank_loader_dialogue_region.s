; Static native translation of bounded bank2 dialogue logic $92AC-$94B5.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_dialogue_region:
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
 bsr.w recovery_bank_loader_dialogue_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_dialogue_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_dialogue_region_core:
 cmpi.b #$0b,$31(a0)
 bne.w .invalid
 cmpi.b #2,3(a4)
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
 cmpi.w #$92ac,(a1)
 beq.w .p92ac
 cmpi.w #$9475,(a1)
 beq.w .p9475
 cmpi.w #$9478,(a1)
 beq.w .p9478
 cmpi.w #$947b,(a1)
 beq.w .p947b
 cmpi.w #$947e,(a1)
 beq.w .p947e
 bra.w .budget_failure
.p92ac: ; LDY $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p92ae: ; LDA $94b6,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94b6,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p92b1: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p92b3: ; LDX $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p92b5: ; INC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p92b7: ; LDA $94f7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94f7,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p92ba: ; STA $0360
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 move.b d4,(a0,d1.w)
.p92bd: ; LDA $94f6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94f6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p92c0: ; STA $0361
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 move.b d4,(a0,d1.w)
.p92c3: ; LDY #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 move.b d0,d6
 bsr.w .nz
.p92c5: ; STY $0362
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0362,d1
 move.b d6,(a0,d1.w)
.p92c8: ; LDA $94c2,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94c2,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p92cb: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shift92cb
 ori.b #1,d7
.shift92cb:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.p92cc: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shift92cc
 ori.b #1,d7
.shift92cc:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.p92cd: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #7,d4
 beq.s .shift92cd
 ori.b #1,d7
.shift92cd:
 lsl.b #1,d4
 move.b d4,d0
 bsr.w .nz
.p92ce: ; ADC #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 bsr.w .adc
.p92d0: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d4,d0
 bsr.w .nz
.p92d1: ; LDA $9506,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9506,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p92d4: ; STA $0363,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0363,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.p92d7: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p92d8: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p92d9: ; BPL $92d1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p92d1
.p92db: ; STY $036b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$036b,d1
 move.b d6,(a0,d1.w)
.p92de: ; STY $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 move.b d6,(a0,d1.w)
.p92e0: ; JSR $947b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$92,d0
 bsr.w .push
 move.w #$e2,d0
 bsr.w .push
 bra.w .p947b
.p92e3: ; LDX $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p92e5: ; INC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p92e7: ; LDY $94c2,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94c2,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p92ea: ; LDA $9536,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9536,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p92ed: ; STA $0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p92ef: ; LDA $954a,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$954a,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p92f2: ; STA $0d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0d,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p92f4: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.p92f6: ; STX $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d5,(a0,d1.w)
.p92f8: ; STX $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 move.b d5,(a0,d1.w)
.p92fa: ; LDX $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p92fc: ; LDY $94fe,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94fe,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p92ff: ; STY $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 move.b d6,(a0,d1.w)
.p9301: ; LDX #$17
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$17,d0
 move.b d0,d5
 bsr.w .nz
.p9303: ; LDA #$a4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$a4,d0
 move.b d0,d4
 bsr.w .nz
.p9305: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.p9308: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p9309: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p930a: ; BPL $9305
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p9305
.p930c: ; LDX $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p930e: ; LDA #$17
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$17,d0
 move.b d0,d4
 bsr.w .nz
.p9310: ; STA $13
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$13,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p9312: ; LDA $94fb,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94fb,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9315: ; STA $0360
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 move.b d4,(a0,d1.w)
.p9318: ; LDA $94f8,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94f8,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p931b: ; STA $0361
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 move.b d4,(a0,d1.w)
.p931e: ; LDY $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p9320: ; LDA ($0c),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $0d(a0),d1
 lsl.w #8,d1
 move.b $0c(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9322: ; CMP #$fe
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fe,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9322
 ori.b #1,d7
.cmp9322:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p9324: ; BEQ $9365
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p9365
.p9326: ; CMP #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9326
 ori.b #1,d7
.cmp9326:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p9328: ; BNE $9334
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p9334
.p932a: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p932c: ; STA $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p932e: ; JSR $949b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$30,d0
 bsr.w .push
 bra.w .p949b
.p9331: ; JMP $940d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p940d
.p9334: ; STA $0363
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0363,d1
 move.b d4,(a0,d1.w)
.p9337: ; LDX $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p9339: ; STA $0360,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p933c: ; INC $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p933e: ; JSR $9469
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$40,d0
 bsr.w .push
 bra.w .p9469
.p9341: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p9343: ; STY $0362
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0362,d1
 move.b d6,(a0,d1.w)
.p9346: ; DEC $13
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$13,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p9348: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p9349: ; STY $0364
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0364,d1
 move.b d6,(a0,d1.w)
.p934c: ; STY $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 move.b d6,(a0,d1.w)
.p934e: ; JSR $9470
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$50,d0
 bsr.w .push
 bra.w .p9470
.p9351: ; LDA $16
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9353: ; AND #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p9355: ; BEQ $9360
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p9360
.p9357: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9359: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9359
 ori.b #1,d7
.cmp9359:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p935b: ; BEQ $9360
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p9360
.p935d: ; JMP $9457
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p9457
.p9360: ; INC $0361
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p9363: ; BNE $931e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p931e
.p9365: ; INC $13
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$13,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p9367: ; LDY $13
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$13,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p9369: ; BMI $938f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p938f
.p936b: ; STY $0362
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0362,d1
 move.b d6,(a0,d1.w)
.p936e: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.p9370: ; STA $0364,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0364,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.p9373: ; LDA #$a4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$a4,d0
 move.b d0,d4
 bsr.w .nz
.p9375: ; STA $0363,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0363,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.p9378: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p9379: ; BPL $9375
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p9375
.p937b: ; STY $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 move.b d6,(a0,d1.w)
.p937d: ; JSR $9470
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$7f,d0
 bsr.w .push
 bra.w .p9470
.p9380: ; LDA $16
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9382: ; AND #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p9384: ; BEQ $938f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p938f
.p9386: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9388: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9388
 ori.b #1,d7
.cmp9388:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p938a: ; BEQ $938f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p938f
.p938c: ; JMP $9457
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p9457
.p938f: ; JSR $9469
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$91,d0
 bsr.w .push
 bra.w .p9469
.p9392: ; INC $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p9394: ; LDA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9396: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9396
 ori.b #1,d7
.cmp9396:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p9398: ; BEQ $939d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p939d
.p939a: ; JMP $92fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p92fa
.p939d: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p939f: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p93a1: ; BNE $93bb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p93bb
.p93a3: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p93a5: ; AND #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p93a7: ; BEQ $93b2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p93b2
.p93a9: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p93ab: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp93ab
 ori.b #1,d7
.cmp93ab:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p93ad: ; BEQ $93b2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p93b2
.p93af: ; JMP $9457
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p9457
.p93b2: ; JSR $947b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$b4,d0
 bsr.w .push
 bra.w .p947b
.p93b5: ; JSR $949b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$b7,d0
 bsr.w .push
 bra.w .p949b
.p93b8: ; JMP $939d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p939d
.p93bb: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p93bd: ; STA $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p93bf: ; JSR $949b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$c1,d0
 bsr.w .push
 bra.w .p949b
.p93c2: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.p93c4: ; LDA $94fb,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94fb,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p93c7: ; STA $0360
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 move.b d4,(a0,d1.w)
.p93ca: ; LDA $94f8,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94f8,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p93cd: ; STA $0361
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 move.b d4,(a0,d1.w)
.p93d0: ; LDA #$17
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$17,d0
 move.b d0,d4
 bsr.w .nz
.p93d2: ; STA $0362
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0362,d1
 move.b d4,(a0,d1.w)
.p93d5: ; LDY $94ff,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94ff,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p93d8: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p93d9: ; STX $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 move.b d5,(a0,d1.w)
.p93db: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.p93dd: ; LDA $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p93df: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp93df
 ori.b #1,d7
.cmp93df:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p93e1: ; BNE $93e7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p93e7
.p93e3: ; LDA #$a4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$a4,d0
 move.b d0,d4
 bsr.w .nz
.p93e5: ; BNE $93ea
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p93ea
.p93e7: ; LDA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p93ea: ; STA $0363,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0363,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p93ed: ; STA $0348,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0348,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.p93f0: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p93f1: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p93f2: ; CPX #$24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp93f2
 ori.b #1,d7
.cmp93f2:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p93f4: ; BNE $93dd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p93dd
.p93f6: ; LDX #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d5
 bsr.w .nz
.p93f8: ; STX $037b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$037b,d1
 move.b d5,(a0,d1.w)
.p93fb: ; STX $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 move.b d5,(a0,d1.w)
.p93fd: ; JSR $947b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$93,d0
 bsr.w .push
 move.w #$ff,d0
 bsr.w .push
 bra.w .p947b
.p9400: ; LDX $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p9402: ; CPX #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9402
 ori.b #1,d7
.cmp9402:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p9404: ; BNE $93c4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p93c4
.p9406: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.p9408: ; STA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p940a: ; JMP $92fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p92fa
.p940d: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p940f: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p9411: ; BNE $9425
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p9425
.p9413: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9415: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9415
 ori.b #1,d7
.cmp9415:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p9417: ; BEQ $941f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p941f
.p9419: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p941b: ; AND #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p941d: ; BNE $9457
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p9457
.p941f: ; JSR $947b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$21,d0
 bsr.w .push
 bra.w .p947b
.p9422: ; JMP $940d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p940d
.p9425: ; LDX $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p9427: ; LDA $94c2,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94c2,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p942a: ; BMI $9457
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p9457
.p942c: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.p942e: ; LDA $94fb,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94fb,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9431: ; STA $0360
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 move.b d4,(a0,d1.w)
.p9434: ; LDA $94f8,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94f8,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9437: ; STA $0361
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 move.b d4,(a0,d1.w)
.p943a: ; LDY #$17
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$17,d0
 move.b d0,d6
 bsr.w .nz
.p943c: ; STY $0362
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0362,d1
 move.b d6,(a0,d1.w)
.p943f: ; LDA #$a4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$a4,d0
 move.b d0,d4
 bsr.w .nz
.p9441: ; STA $0363,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0363,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.p9444: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p9445: ; BPL $9441
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p9441
.p9447: ; STY $037b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$037b,d1
 move.b d6,(a0,d1.w)
.p944a: ; STY $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 move.b d6,(a0,d1.w)
.p944c: ; JSR $947b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$4e,d0
 bsr.w .push
 bra.w .p947b
.p944f: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p9450: ; CPX #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9450
 ori.b #1,d7
.cmp9450:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p9452: ; BNE $942e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p942e
.p9454: ; JMP $92b3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p92b3
.p9457: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9459: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9459
 ori.b #1,d7
.cmp9459:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p945b: ; BEQ $945e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p945e
.p945d: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$92e3,d0
 beq.w .p92e3
 cmpi.w #$9331,d0
 beq.w .p9331
 cmpi.w #$9341,d0
 beq.w .p9341
 cmpi.w #$9351,d0
 beq.w .p9351
 cmpi.w #$9380,d0
 beq.w .p9380
 cmpi.w #$9392,d0
 beq.w .p9392
 cmpi.w #$93b5,d0
 beq.w .p93b5
 cmpi.w #$93b8,d0
 beq.w .p93b8
 cmpi.w #$93c2,d0
 beq.w .p93c2
 cmpi.w #$9400,d0
 beq.w .p9400
 cmpi.w #$9422,d0
 beq.w .p9422
 cmpi.w #$944f,d0
 beq.w .p944f
 move.w d0,(a1)
 bra.w .success
.p945e: ; LDA #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 move.b d0,d4
 bsr.w .nz
.p9460: ; JSR $f377
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$62,d0
 bsr.w .push
 move.w #$f377,(a1)
 bra.w .success
.p9463: ; JSR $ff04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$65,d0
 bsr.w .push
 move.w #$ff04,(a1)
 bra.w .success
.p9466: ; JMP $9463
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p9463
.p9469: ; INC $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p946b: ; BNE $946f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p946f
.p946d: ; INC $0d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0d,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p946f: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$92e3,d0
 beq.w .p92e3
 cmpi.w #$9331,d0
 beq.w .p9331
 cmpi.w #$9341,d0
 beq.w .p9341
 cmpi.w #$9351,d0
 beq.w .p9351
 cmpi.w #$9380,d0
 beq.w .p9380
 cmpi.w #$9392,d0
 beq.w .p9392
 cmpi.w #$93b5,d0
 beq.w .p93b5
 cmpi.w #$93b8,d0
 beq.w .p93b8
 cmpi.w #$93c2,d0
 beq.w .p93c2
 cmpi.w #$9400,d0
 beq.w .p9400
 cmpi.w #$9422,d0
 beq.w .p9422
 cmpi.w #$944f,d0
 beq.w .p944f
 move.w d0,(a1)
 bra.w .success
.p9470: ; LDA #$27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d0
 move.b d0,d4
 bsr.w .nz
.p9472: ; JSR $f379
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$74,d0
 bsr.w .push
 move.w #$f379,(a1)
 bra.w .success
.p9475: ; JSR $ff04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$77,d0
 bsr.w .push
 move.w #$ff04,(a1)
 bra.w .success
.p9478: ; JSR $ff04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$7a,d0
 bsr.w .push
 move.w #$ff04,(a1)
 bra.w .success
.p947b: ; JSR $ff04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$94,d0
 bsr.w .push
 move.w #$7d,d0
 bsr.w .push
 move.w #$ff04,(a1)
 bra.w .success
.p947e: ; INC $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p9480: ; LDA $50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$50,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9482: ; BEQ $949a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p949a
.p9484: ; LDA $54
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9486: ; CMP #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp9486
 ori.b #1,d7
.cmp9486:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p9488: ; BNE $949a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p949a
.p948a: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p948c: ; AND #$30
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$30,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p948e: ; ORA $15
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$15,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p9490: ; STA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p9492: ; LDA $16
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p9494: ; AND #$30
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$30,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p9496: ; ORA $17
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$17,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p9498: ; STA $16
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p949a: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$92e3,d0
 beq.w .p92e3
 cmpi.w #$9331,d0
 beq.w .p9331
 cmpi.w #$9341,d0
 beq.w .p9341
 cmpi.w #$9351,d0
 beq.w .p9351
 cmpi.w #$9380,d0
 beq.w .p9380
 cmpi.w #$9392,d0
 beq.w .p9392
 cmpi.w #$93b5,d0
 beq.w .p93b5
 cmpi.w #$93b8,d0
 beq.w .p93b8
 cmpi.w #$93c2,d0
 beq.w .p93c2
 cmpi.w #$9400,d0
 beq.w .p9400
 cmpi.w #$9422,d0
 beq.w .p9422
 cmpi.w #$944f,d0
 beq.w .p944f
 move.w d0,(a1)
 bra.w .success
.p949b: ; LDX #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d5
 bsr.w .nz
.p949d: ; LDA $9501,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9501,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p94a0: ; STA $03e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03e0,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p94a3: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p94a4: ; BPL $949d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p949d
.p94a6: ; LDA $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p94a8: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p94aa: ; BNE $94b1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p94b1
.p94ac: ; LDA #$a4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$a4,d0
 move.b d0,d4
 bsr.w .nz
.p94ae: ; STA $03e3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03e3,d1
 move.b d4,(a0,d1.w)
.p94b1: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.p94b3: ; STA $1c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1c,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p94b5: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$92e3,d0
 beq.w .p92e3
 cmpi.w #$9331,d0
 beq.w .p9331
 cmpi.w #$9341,d0
 beq.w .p9341
 cmpi.w #$9351,d0
 beq.w .p9351
 cmpi.w #$9380,d0
 beq.w .p9380
 cmpi.w #$9392,d0
 beq.w .p9392
 cmpi.w #$93b5,d0
 beq.w .p93b5
 cmpi.w #$93b8,d0
 beq.w .p93b8
 cmpi.w #$93c2,d0
 beq.w .p93c2
 cmpi.w #$9400,d0
 beq.w .p9400
 cmpi.w #$9422,d0
 beq.w .p9422
 cmpi.w #$944f,d0
 beq.w .p944f
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
 subi.l #$0000,d2
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
