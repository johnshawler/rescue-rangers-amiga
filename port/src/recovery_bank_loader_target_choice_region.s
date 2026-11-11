; Static native translation of fixed-bank F328 horizontal player-slot targeting.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal2; no resources A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_target_choice_region:
 cmpi.w #$f328,(a1)
 bne.w .public_invalid
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
 bsr.w recovery_bank_loader_target_choice_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_target_choice_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
.public_invalid:
 moveq #-1,d0
 rts
recovery_bank_loader_target_choice_region_core:
 cmpi.b #8,3(a4)
 bhs.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 movem.l d0-d2,-(sp)
 moveq #0,d1
 move.b 6(a1),d1
 addq.b #1,d1
 moveq #0,d0
 move.b $100(a0,d1.w),d0
 addq.b #1,d1
 moveq #0,d2
 move.b $100(a0,d1.w),d2
 lsl.w #8,d2
 or.w d2,d0
 addq.w #1,d0
 cmpi.w #$f328,d0
 bcs.s .return_valid
 cmpi.w #$f36c,d0
 bhs.s .return_valid
 movem.l (sp)+,d0-d2
 bra.w .invalid
.return_valid:
 movem.l (sp)+,d0-d2
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
 movea.l #512,a4
 cmpi.w #$f328,(a1)
 beq.w .pf328
 bra.w .budget_failure
.pf328: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.pf32a: ; JSR $f345
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f3,d0
 bsr.w .push
 move.w #$2c,d0
 bsr.w .push
 bra.w .pf345
.pf32d: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf32f: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf331: ; STA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf333: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pf334: ; JSR $f345
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f3,d0
 bsr.w .push
 move.w #$36,d0
 bsr.w .push
 bra.w .pf345
.pf337: ; CMP $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf337
 ori.b #1,d7
.cmpf337:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf339: ; BCC $f33f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pf33f
.pf33b: ; LDA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf33d: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf33f: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf341: ; STA $0580,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pf344: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$f32d,d0
 beq.w .pf32d
 cmpi.w #$f337,d0
 beq.w .pf337
 move.w d0,(a1)
 bra.w .success
.pf345: ; LDA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf348: ; BPL $f369
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pf369
.pf34a: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pf34c: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf34e: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf351: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pf352: ; SBC $04f0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .sbc
.pf355: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pf356: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf359: ; SBC $0500,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .sbc
.pf35c: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pf35d: ; BCS $f364
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pf364
.pf35f: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pf361: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 bsr.w .adc
.pf363: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$f32d,d0
 beq.w .pf32d
 cmpi.w #$f337,d0
 beq.w .pf337
 move.w d0,(a1)
 bra.w .success
.pf364: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.pf366: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf368: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$f32d,d0
 beq.w .pf32d
 cmpi.w #$f337,d0
 beq.w .pf337
 move.w d0,(a1)
 bra.w .success
.pf369: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.pf36b: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$f32d,d0
 beq.w .pf32d
 cmpi.w #$f337,d0
 beq.w .pf337
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
; RAM-only data accesses, no opcode fetch or external resource/device path.
.read:
 andi.l #$ffff,d1
 cmpi.w #$2000,d1
 bhs.w .bad_read
 andi.w #$7ff,d1
 moveq #0,d0
 move.b (a0,d1.w),d0
 rts
.store:
 andi.l #$ffff,d1
 cmpi.w #$2000,d1
 bhs.w .bad_read
 andi.w #$7ff,d1
 move.b d0,(a0,d1.w)
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
