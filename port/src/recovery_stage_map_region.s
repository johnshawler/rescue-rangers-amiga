; Static native translation of bounded fixed-bank stage-map orchestration and expansion.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_stage_map_region:
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
 bsr.w recovery_stage_map_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_stage_map_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_stage_map_region_core:
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
 cmpi.w #$e179,(a1)
 beq.w .pe179
 cmpi.w #$e17c,(a1)
 beq.w .pe17c
 cmpi.w #$e1d3,(a1)
 beq.w .pe1d3
 cmpi.w #$e1e4,(a1)
 beq.w .pe1e4
 cmpi.w #$e1e7,(a1)
 beq.w .pe1e7
 cmpi.w #$e1ea,(a1)
 beq.w .pe1ea
 cmpi.w #$dbec,(a1)
 beq.w .pdbec
 cmpi.w #$dc5c,(a1)
 beq.w .pdc5c
 cmpi.w #$dc5f,(a1)
 beq.w .pdc5f
 cmpi.w #$df97,(a1)
 beq.w .pdf97
 cmpi.w #$e028,(a1)
 beq.w .pe028
 bra.w .budget_failure
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
 bsr.w .write
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
 bsr.w .write
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
 cmpi.w #$dc5c,d0
 beq.w .pdc5c
 cmpi.w #$dc5f,d0
 beq.w .pdc5f
 cmpi.w #$df92,d0
 beq.w .pdf92
 cmpi.w #$df97,d0
 beq.w .pdf97
 cmpi.w #$e028,d0
 beq.w .pe028
 cmpi.w #$e17c,d0
 beq.w .pe17c
 cmpi.w #$e17f,d0
 beq.w .pe17f
 cmpi.w #$e1d3,d0
 beq.w .pe1d3
 cmpi.w #$e1e4,d0
 beq.w .pe1e4
 cmpi.w #$e1e7,d0
 beq.w .pe1e7
 cmpi.w #$e1ea,d0
 beq.w .pe1ea
 move.w d0,(a1)
 bra.w .success
.pdbec: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.pdbee: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.pdbf0: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdbf2: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pdbf3: ; AND #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdbf5: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pdbf6: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdbf6
 ori.b #1,d7
.shiftdbf6:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdbf7: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdbf7
 ori.b #1,d7
.shiftdbf7:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdbf8: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdbf8
 ori.b #1,d7
.shiftdbf8:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdbf9: ; STA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdbfb: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pdbfc: ; AND #$78
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$78,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdbfe: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdbfe
 ori.b #1,d7
.shiftdbfe:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdbff: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdbff
 ori.b #1,d7
.shiftdbff:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdc00: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pdc01: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdc01
 ori.b #1,d7
.shiftdc01:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdc02: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdc02
 ori.b #1,d7
.shiftdc02:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdc03: ; ORA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc05: ; STA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdc07: ; ORA #$c0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c0,d0
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc09: ; STA $0375,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0375,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc0c: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pdc0d: ; ORA $e05b,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e05b,d1
 add.w d5,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc10: ; STA $0361,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc13: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pdc14: ; ADC #$20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$20,d0
 bsr.w .adc
.pdc16: ; STA $0366,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0366,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc19: ; ADC #$20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$20,d0
 bsr.w .adc
.pdc1b: ; STA $036b,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$036b,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc1e: ; ADC #$20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$20,d0
 bsr.w .adc
.pdc20: ; STA $0370,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0370,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc23: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdc25: ; ROL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdc25
 ori.b #1,d7
.shiftdc25:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatedc25
 ori.b #1,d0
.rotatedc25:
 move.b d0,d4
 bsr.w .nz
.pdc26: ; ROL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdc26
 ori.b #1,d7
.shiftdc26:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatedc26
 ori.b #1,d0
.rotatedc26:
 move.b d0,d4
 bsr.w .nz
.pdc27: ; ROL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdc27
 ori.b #1,d7
.shiftdc27:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatedc27
 ori.b #1,d0
.rotatedc27:
 move.b d0,d4
 bsr.w .nz
.pdc28: ; ROL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdc28
 ori.b #1,d7
.shiftdc28:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatedc28
 ori.b #1,d0
.rotatedc28:
 move.b d0,d4
 bsr.w .nz
.pdc29: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc2b: ; ORA $e063,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e063,d1
 add.w d5,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc2e: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc31: ; STA $0365,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0365,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc34: ; STA $036a,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$036a,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc37: ; STA $036f,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$036f,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc3a: ; ORA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc3c: ; STA $0374,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0374,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc3f: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pdc41: ; STA $0362,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0362,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc44: ; STA $0367,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0367,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc47: ; STA $036c,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$036c,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc4a: ; STA $0371,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0371,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc4d: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pdc4f: ; STA $0376,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0376,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc52: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc53: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc54: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc55: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.pdc57: ; LDY $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pdc59: ; JSR $e06b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dc,d0
 bsr.w .push
 move.w #$5b,d0
 bsr.w .push
 bra.w .pe06b
.pdc5c: ; JSR $df8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dc,d0
 bsr.w .push
 move.w #$5e,d0
 bsr.w .push
 bra.w .pdf8a
.pdc5f: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pdc61: ; LDA $035e,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$035e,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdc64: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc66: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pdc67: ; LDA $0140,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0140,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdc6a: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc6d: ; LDA $0141,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0141,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdc70: ; STA $0361,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0361,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc73: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc74: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc75: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc76: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc77: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc78: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pdc79: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pdc7a: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pdc7b: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pdc7c: ; CPX #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdc7c
 ori.b #1,d7
.cmpdc7c:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pdc7e: ; BCC $dc67
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pdc67
.pdc80: ; LDA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdc82: ; CMP #$38
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$38,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdc82
 ori.b #1,d7
.cmpdc82:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pdc84: ; BCC $dc96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pdc96
.pdc86: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.pdc87: ; SBC #$0d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0d,d0
 bsr.w .sbc
.pdc89: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.w .nz
.pdc8a: ; LDX #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d5
 bsr.w .nz
.pdc8c: ; LDA $036a,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$036a,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdc8f: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdc92: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdc93: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pdc94: ; BPL $dc8c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pdc8c
.pdc96: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.pdc98: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdc9a: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdc9a
 ori.b #1,d7
.shiftdc9a:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdc9b: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdc9b
 ori.b #1,d7
.shiftdc9b:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdc9c: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdc9c
 ori.b #1,d7
.shiftdc9c:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdc9d: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdc9f: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.w .nz
.pdca0: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdca2: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdca4: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdca4
 ori.b #1,d7
.shiftdca4:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdca5: ; ORA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdca7: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pdca8: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcaa: ; AND $dd16,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dd16,d1
 add.w d6,d1
 bsr.w .read
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdcad: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdcaf: ; LDA $0780,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0780,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcb2: ; AND $dd18,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dd18,d1
 add.w d6,d1
 bsr.w .read
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdcb5: ; ORA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdcb7: ; STA $0780,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0780,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pdcba: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pdcbc: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdcbf: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdcc0: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.pdcc2: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdcc5: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.w .nz
.pdcc6: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdcc6
 ori.b #1,d7
.shiftdcc6:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdcc7: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pdcc8: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcca: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdccc: ; BNE $dcd3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pdcd3
.pdcce: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcd0: ; JMP $dcd6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pdcd6
.pdcd3: ; LDA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcd5: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pdcd6: ; STA $0600,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0600,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pdcd9: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcdb: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdcdd: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pdcde: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdce0: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pdce1: ; ADC $dd12,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dd12,d1
 add.w d5,d1
 bsr.w .read
 bsr.w .adc
.pdce4: ; STA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdce6: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdce8: ; CMP $dd13,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dd13,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdce8
 ori.b #1,d7
.cmpdce8:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pdceb: ; BNE $dcf5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pdcf5
.pdced: ; LDA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcef: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pdcf0: ; ADC $dd12,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$dd12,d1
 add.w d5,d1
 bsr.w .read
 bsr.w .adc
.pdcf3: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdcf5: ; DEC $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 bsr.w .read
 subq.b #1,d0
 bsr.w .write
 bsr.w .nz
.pdcf7: ; BEQ $dcfc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pdcfc
.pdcf9: ; JMP $dbee
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pdbee
.pdcfc: ; LDA $f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f0,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdcfe: ; BEQ $dd03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pdd03
.pdd00: ; JMP $c115
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c115,(a1)
 bra.w .success
.pdd03: ; INC $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 bsr.w .read
 addq.b #1,d0
 bsr.w .write
 bsr.w .nz
.pdd05: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdd07: ; STA $28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdd09: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$dc5c,d0
 beq.w .pdc5c
 cmpi.w #$dc5f,d0
 beq.w .pdc5f
 cmpi.w #$df92,d0
 beq.w .pdf92
 cmpi.w #$df97,d0
 beq.w .pdf97
 cmpi.w #$e028,d0
 beq.w .pe028
 cmpi.w #$e17c,d0
 beq.w .pe17c
 cmpi.w #$e17f,d0
 beq.w .pe17f
 cmpi.w #$e1d3,d0
 beq.w .pe1d3
 cmpi.w #$e1e4,d0
 beq.w .pe1e4
 cmpi.w #$e1e7,d0
 beq.w .pe1e7
 cmpi.w #$e1ea,d0
 beq.w .pe1ea
 move.w d0,(a1)
 bra.w .success
.pdf8a: ; LDA $27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdf8c: ; BMI $df8f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pdf8f
.pdf8e: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$dc5c,d0
 beq.w .pdc5c
 cmpi.w #$dc5f,d0
 beq.w .pdc5f
 cmpi.w #$df92,d0
 beq.w .pdf92
 cmpi.w #$df97,d0
 beq.w .pdf97
 cmpi.w #$e028,d0
 beq.w .pe028
 cmpi.w #$e17c,d0
 beq.w .pe17c
 cmpi.w #$e17f,d0
 beq.w .pe17f
 cmpi.w #$e1d3,d0
 beq.w .pe1d3
 cmpi.w #$e1e4,d0
 beq.w .pe1e4
 cmpi.w #$e1e7,d0
 beq.w .pe1e7
 cmpi.w #$e1ea,d0
 beq.w .pe1ea
 move.w d0,(a1)
 bra.w .success
.pdf8f: ; JSR $e01b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$df,d0
 bsr.w .push
 move.w #$91,d0
 bsr.w .push
 bra.w .pe01b
.pdf92: ; LDA $36
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$36,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdf94: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$df,d0
 bsr.w .push
 move.w #$96,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pdf97: ; LDY #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d6
 bsr.w .nz
.pdf99: ; STY $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.pdf9b: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pdf9d: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdf9f: ; STA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdfa1: ; STA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdfa3: ; LDY $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pdfa5: ; LDA $e04f,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e04f,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdfa8: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdfaa: ; LDA ($00),Y
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
.pdfac: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pdfad: ; LDA $bee0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bee0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdfb0: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdfb2: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pdfb3: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.w .nz
.pdfb4: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pdfb5: ; LDX $e053,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e053,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pdfb8: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.pdfb9: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdfbb: ; BEQ $dfc4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pdfc4
.pdfbd: ; LDA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdfbf: ; AND #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f0,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdfc1: ; JMP $dfca
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pdfca
.pdfc4: ; LDA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdfc6: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdfc6
 ori.b #1,d7
.shiftdfc6:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdfc7: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdfc7
 ori.b #1,d7
.shiftdfc7:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdfc8: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdfc8
 ori.b #1,d7
.shiftdfc8:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdfc9: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdfc9
 ori.b #1,d7
.shiftdfc9:
 lsr.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdfca: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdfcc: ; LDA $11,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdfce: ; AND $e057,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e057,d1
 add.w d5,d1
 bsr.w .read
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdfd1: ; ORA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdfd3: ; STA $11,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdfd5: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pdfd6: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pdfd7: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pdfd8: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdfda: ; CPY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdfda
 ori.b #1,d7
.cmpdfda:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pdfdc: ; BEQ $dfe3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pdfe3
.pdfde: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdfde
 ori.b #1,d7
.shiftdfde:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdfdf: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdfdf
 ori.b #1,d7
.shiftdfdf:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pdfe0: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pdfe1: ; BNE $dfde
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pdfde
.pdfe3: ; ORA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pdfe5: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pdfe7: ; LDY $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pdfe9: ; LDA $bae0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bae0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdfec: ; STA $0140,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0140,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdfef: ; LDA $bbe0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bbe0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdff2: ; STA $0141,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0141,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdff5: ; LDA $bce0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bce0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdff8: ; STA $0144,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0144,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pdffb: ; LDA $bde0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bde0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pdffe: ; STA $0145,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0145,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pe001: ; DEC $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 subq.b #1,d0
 bsr.w .write
 bsr.w .nz
.pe003: ; BMI $e008
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pe008
.pe005: ; JMP $dfa3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pdfa3
.pe008: ; LDA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe00a: ; CMP #$38
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$38,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe00a
 ori.b #1,d7
.cmpe00a:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe00c: ; BCC $e01a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pe01a
.pe00e: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe010: ; AND #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe012: ; STA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe014: ; LDA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe016: ; AND #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe018: ; STA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe01a: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$dc5c,d0
 beq.w .pdc5c
 cmpi.w #$dc5f,d0
 beq.w .pdc5f
 cmpi.w #$df92,d0
 beq.w .pdf92
 cmpi.w #$df97,d0
 beq.w .pdf97
 cmpi.w #$e028,d0
 beq.w .pe028
 cmpi.w #$e17c,d0
 beq.w .pe17c
 cmpi.w #$e17f,d0
 beq.w .pe17f
 cmpi.w #$e1d3,d0
 beq.w .pe1d3
 cmpi.w #$e1e4,d0
 beq.w .pe1e4
 cmpi.w #$e1e7,d0
 beq.w .pe1e7
 cmpi.w #$e1ea,d0
 beq.w .pe1ea
 move.w d0,(a1)
 bra.w .success
.pe01b: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pe01d: ; LDX $36
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$36,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pe01f: ; CPX #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe01f
 ori.b #1,d7
.cmpe01f:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe021: ; BCC $e025
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pe025
.pe023: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pe025: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e0,d0
 bsr.w .push
 move.w #$27,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pe028: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pe02a: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe02c: ; LDA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe02e: ; AND #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe030: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pe031: ; LDY $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pe033: ; LDA ($26),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $27(a0),d1
 lsl.w #8,d1
 move.b $26(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe035: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte035
 ori.b #1,d7
.shifte035:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe036: ; ROL $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte036
 ori.b #1,d7
.shifte036:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee036
 ori.b #1,d0
.rotatee036:
 bsr.w .write
 bsr.w .nz
.pe038: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte038
 ori.b #1,d7
.shifte038:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe039: ; ROL $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte039
 ori.b #1,d7
.shifte039:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee039
 ori.b #1,d0
.rotatee039:
 bsr.w .write
 bsr.w .nz
.pe03b: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pe03c: ; ADC #$e0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e0,d0
 bsr.w .adc
.pe03e: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe040: ; LDA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe042: ; ADC #$b6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b6,d0
 bsr.w .adc
.pe044: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe046: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$dc5c,d0
 beq.w .pdc5c
 cmpi.w #$dc5f,d0
 beq.w .pdc5f
 cmpi.w #$df92,d0
 beq.w .pdf92
 cmpi.w #$df97,d0
 beq.w .pdf97
 cmpi.w #$e028,d0
 beq.w .pe028
 cmpi.w #$e17c,d0
 beq.w .pe17c
 cmpi.w #$e17f,d0
 beq.w .pe17f
 cmpi.w #$e1d3,d0
 beq.w .pe1d3
 cmpi.w #$e1e4,d0
 beq.w .pe1e4
 cmpi.w #$e1e7,d0
 beq.w .pe1e7
 cmpi.w #$e1ea,d0
 beq.w .pe1ea
 move.w d0,(a1)
 bra.w .success
.pe06b: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pe06d: ; STX $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .write
.pe06f: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe071: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte071
 ori.b #1,d7
.shifte071:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe072: ; ROL $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte072
 ori.b #1,d7
.shifte072:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee072
 ori.b #1,d0
.rotatee072:
 bsr.w .write
 bsr.w .nz
.pe074: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte074
 ori.b #1,d7
.shifte074:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe075: ; ROL $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte075
 ori.b #1,d7
.shifte075:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee075
 ori.b #1,d0
.rotatee075:
 bsr.w .write
 bsr.w .nz
.pe077: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte077
 ori.b #1,d7
.shifte077:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe078: ; ROL $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte078
 ori.b #1,d7
.shifte078:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee078
 ori.b #1,d0
.rotatee078:
 bsr.w .write
 bsr.w .nz
.pe07a: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte07a
 ori.b #1,d7
.shifte07a:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe07b: ; ROL $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte07b
 ori.b #1,d7
.shifte07b:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee07b
 ori.b #1,d0
.rotatee07b:
 bsr.w .write
 bsr.w .nz
.pe07d: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte07d
 ori.b #1,d7
.shifte07d:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe07e: ; ROL $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte07e
 ori.b #1,d7
.shifte07e:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee07e
 ori.b #1,d0
.rotatee07e:
 bsr.w .write
 bsr.w .nz
.pe080: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte080
 ori.b #1,d7
.shifte080:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.pe081: ; ROL $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shifte081
 ori.b #1,d7
.shifte081:
 lsl.b #1,d0
 btst #0,d2
 beq.s .rotatee081
 ori.b #1,d0
.rotatee081:
 bsr.w .write
 bsr.w .nz
.pe083: ; STA $26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$26,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe085: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe087: ; STA $27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe089: ; LDA $26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$26,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe08b: ; ADC #$c0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c0,d0
 bsr.w .adc
.pe08d: ; STA $26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$26,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe08f: ; LDA $27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe091: ; ADC #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 bsr.w .adc
.pe093: ; STA $27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe095: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$dc5c,d0
 beq.w .pdc5c
 cmpi.w #$dc5f,d0
 beq.w .pdc5f
 cmpi.w #$df92,d0
 beq.w .pdf92
 cmpi.w #$df97,d0
 beq.w .pdf97
 cmpi.w #$e028,d0
 beq.w .pe028
 cmpi.w #$e17c,d0
 beq.w .pe17c
 cmpi.w #$e17f,d0
 beq.w .pe17f
 cmpi.w #$e1d3,d0
 beq.w .pe1d3
 cmpi.w #$e1e4,d0
 beq.w .pe1e4
 cmpi.w #$e1e7,d0
 beq.w .pe1e7
 cmpi.w #$e1ea,d0
 beq.w .pe1ea
 move.w d0,(a1)
 bra.w .success
.pe179: ; JSR $c14e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$7b,d0
 bsr.w .push
 move.w #$c14e,(a1)
 bra.w .success
.pe17c: ; JSR $c235
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$7e,d0
 bsr.w .push
 bra.w .pc235
.pe17f: ; LDX $50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$50,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pe181: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe184: ; AND #$df
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$df,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe186: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pe189: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe18b: ; CMP #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe18b
 ori.b #1,d7
.cmpe18b:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe18d: ; BNE $e193
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pe193
.pe18f: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pe191: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe193: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pe194: ; BPL $e181
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pe181
.pe196: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pe198: ; STA $52
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$52,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe19a: ; STA $20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$20,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe19c: ; STA $2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2b,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe19e: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1a0: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pe1a2: ; STA $21
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$21,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1a4: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pe1a6: ; STA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1a8: ; STA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1aa: ; STA $28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1ac: ; STA $29
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$29,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1ae: ; STA $70
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$70,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1b0: ; STA $71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$71,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1b2: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe1b4: ; ROR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shifte1b4
 ori.b #1,d7
.shifte1b4:
 lsr.b #1,d0
 btst #0,d2
 beq.s .rotatee1b4
 ori.b #128,d0
.rotatee1b4:
 move.b d0,d4
 bsr.w .nz
.pe1b5: ; ROR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shifte1b5
 ori.b #1,d7
.shifte1b5:
 lsr.b #1,d0
 btst #0,d2
 beq.s .rotatee1b5
 ori.b #128,d0
.rotatee1b5:
 move.b d0,d4
 bsr.w .nz
.pe1b6: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe1b8: ; STA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1ba: ; EOR #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe1bc: ; ORA #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe1be: ; STA $0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1c0: ; LDA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe1c2: ; BEQ $e1cc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pe1cc
.pe1c4: ; DEC $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.w .read
 subq.b #1,d0
 bsr.w .write
 bsr.w .nz
.pe1c6: ; LDA $0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe1c8: ; ORA #$70
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$70,d0
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe1ca: ; STA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1cc: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pe1ce: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pe1d0: ; JSR $dbec
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$d2,d0
 bsr.w .push
 bra.w .pdbec
.pe1d3: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe1d5: ; CMP $0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe1d5
 ori.b #1,d7
.cmpe1d5:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe1d7: ; BNE $e1cc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pe1cc
.pe1d9: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe1db: ; CMP #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe1db
 ori.b #1,d7
.cmpe1db:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe1dd: ; BCS $e1ea
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pe1ea
.pe1df: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pe1e1: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$e3,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pe1e4: ; JSR $8040
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$e6,d0
 bsr.w .push
 move.w #$8040,(a1)
 bra.w .success
.pe1e7: ; JSR $8090
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$e9,d0
 bsr.w .push
 move.w #$8090,(a1)
 bra.w .success
.pe1ea: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$dc5c,d0
 beq.w .pdc5c
 cmpi.w #$dc5f,d0
 beq.w .pdc5f
 cmpi.w #$df92,d0
 beq.w .pdf92
 cmpi.w #$df97,d0
 beq.w .pdf97
 cmpi.w #$e028,d0
 beq.w .pe028
 cmpi.w #$e17c,d0
 beq.w .pe17c
 cmpi.w #$e17f,d0
 beq.w .pe17f
 cmpi.w #$e1d3,d0
 beq.w .pe1d3
 cmpi.w #$e1e4,d0
 beq.w .pe1e4
 cmpi.w #$e1e7,d0
 beq.w .pe1e7
 cmpi.w #$e1ea,d0
 beq.w .pe1ea
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
.write:
 andi.l #$ffff,d1
 cmpi.w #$2000,d1
 bhs.w .bad_read
 andi.w #$7ff,d1
 move.b d0,(a0,d1.w)
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
 move.l a4,-(sp)
 movea.l 40(sp),a4
 moveq #0,d2
 move.b 3(a4),d2
 movea.l (sp)+,a4
 lsl.l #8,d2
 lsl.l #6,d2
 subi.w #$8000,d1
 add.l d1,d2
 addi.w #$8000,d1
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
