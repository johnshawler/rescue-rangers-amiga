; Static native translation of fixed-bank live palette-cycle table update.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_palette_cycle:
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
 bsr.w recovery_bank_loader_palette_cycle_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_palette_cycle_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_palette_cycle_core:
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
 cmpi.w #$e9c9,(a1)
 beq.w .pe9c9
 bra.w .budget_failure
.pe9c9: ; LDA $3d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3d,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe9cb: ; BPL $ea0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pea0e
.pe9cd: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pe9cf: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe9d1: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pe9d2: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pe9d4: ; LDA $3e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3e,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe9d6: ; INC $3e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3e,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pe9d8: ; CMP $ea71,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ea71,d1
 add.w d6,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe9d8
 ori.b #1,d7
.cmpe9d8:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe9db: ; BNE $ea0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pea0e
.pe9dd: ; STX $3e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3e,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pe9df: ; LDA $3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3f,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe9e1: ; INC $3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3f,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pe9e3: ; CMP $ea70,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ea70,d1
 add.w d6,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe9e3
 ori.b #1,d7
.cmpe9e3:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe9e6: ; BNE $e9ea
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pe9ea
.pe9e8: ; STX $3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3f,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pe9ea: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pe9eb: ; ADC #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 bsr.w .adc
.pe9ed: ; ADC $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .adc
.pe9ef: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pe9f0: ; LDX $ea70,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ea70,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pe9f3: ; LDA $ea0f,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ea0f,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe9f6: ; BMI $ea0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pea0c
.pe9f8: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pe9f9: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pe9fa: ; LDA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d4
 bsr.w .nz
.pe9fc: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe9fe: ; LDA $ea0f,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ea0f,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pea01: ; STA $0300,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0300,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pea04: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pea05: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pea06: ; DEC $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pea08: ; BNE $e9fe
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pe9fe
.pea0a: ; BEQ $e9f3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pe9f3
.pea0c: ; STA $18
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$18,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pea0e: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
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
