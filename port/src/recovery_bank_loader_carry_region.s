; Static native translation of fixed-bank carried-object positioning and appearance.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_carry_region:
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
 bsr.w recovery_bank_loader_carry_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_carry_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_carry_region_core:
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
 cmpi.w #$d3e7,(a1)
 beq.w .pd3e7
 cmpi.w #$d40b,(a1)
 beq.w .pd40b
 cmpi.w #$d435,(a1)
 beq.w .pd435
 cmpi.w #$d460,(a1)
 beq.w .pd460
 bra.w .budget_failure
.pd3e7: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pd3e9: ; BEQ $d40a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd40a
.pd3eb: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd3ee: ; STA $0470,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0470,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd3f1: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd3f4: ; STA $0480,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd3f7: ; CPY #$82
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$82,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd3f7
 ori.b #1,d7
.cmpd3f7:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd3f9: ; BCS $d407
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pd407
.pd3fb: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd3fe: ; STA $ffe8,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ffe8,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd401: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd404: ; STA $ffea,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ffea,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd407: ; JSR $d435
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d4,d0
 bsr.w .push
 move.w #$09,d0
 bsr.w .push
 bra.w .pd435
.pd40a: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d40a,d0
 beq.w .pd40a
 cmpi.w #$d434,d0
 beq.w .pd434
 move.w d0,(a1)
 bra.w .success
.pd40b: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pd40d: ; BEQ $d434
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd434
.pd40f: ; STX $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pd411: ; LDX $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pd414: ; LDA $d653,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d653,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd417: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pd419: ; LDX $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pd41b: ; LDA $0510,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd41e: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pd41f: ; SBC $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.pd421: ; BCS $d426
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pd426
.pd423: ; SBC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 bsr.w .sbc
.pd425: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pd426: ; STA $0490,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0490,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd429: ; LDA $0520,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0520,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd42c: ; SBC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 bsr.w .sbc
.pd42e: ; STA $04a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04a0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd431: ; JSR $d435
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d4,d0
 bsr.w .push
 move.w #$33,d0
 bsr.w .push
 bra.w .pd435
.pd434: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d40a,d0
 beq.w .pd40a
 cmpi.w #$d434,d0
 beq.w .pd434
 move.w d0,(a1)
 bra.w .success
.pd435: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd438: ; BEQ $d445
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd445
.pd43a: ; LDA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd43d: ; CMP #$2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd43d
 ori.b #1,d7
.cmpd43d:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd43f: ; BCC $d45f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pd45f
.pd441: ; SBC #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 bsr.w .sbc
.pd443: ; BNE $d44e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd44e
.pd445: ; LDA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd448: ; CMP #$2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd448
 ori.b #1,d7
.cmpd448:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd44a: ; BCS $d45f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pd45f
.pd44c: ; ADC #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 bsr.w .adc
.pd44e: ; STA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd451: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pd453: ; STA $0390,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0390,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd456: ; STA $03b0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03b0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd459: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd45c: ; STA $0380,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0380,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd45f: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d40a,d0
 beq.w .pd40a
 cmpi.w #$d434,d0
 beq.w .pd434
 move.w d0,(a1)
 bra.w .success
.pd460: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pd462: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pd464: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pd466: ; LDA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd469: ; CMP #$26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$26,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd469
 ori.b #1,d7
.cmpd469:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd46b: ; BNE $d471
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd471
.pd46d: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pd46f: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pd471: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd473: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pd474: ; ADC $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .adc
.pd476: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pd477: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd47a: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pd47b: ; ADC $cba2,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cba2,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .adc
.pd47e: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pd480: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd483: ; ADC $cba3,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cba3,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .adc
.pd486: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pd488: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pd48a: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd48c: ; STA $0470,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0470,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd48f: ; LDA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd491: ; STA $0480,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd494: ; LDA $0510,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd497: ; STA $0490,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0490,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd49a: ; LDA $0520,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0520,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd49d: ; STA $04a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04a0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pd4a0: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d40a,d0
 beq.w .pd40a
 cmpi.w #$d434,d0
 beq.w .pd434
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
