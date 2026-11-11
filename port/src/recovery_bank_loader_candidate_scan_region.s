; Static native translation of fixed-bank F977 candidate-object scan.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal18 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_candidate_scan_region:
 cmpi.w #$f977,(a1)
 beq.s .admitted
 cmpi.w #$f9d7,(a1)
 beq.s .admitted
 cmpi.w #$f9e4,(a1)
 beq.s .admitted
 moveq #-1,d0
 rts
.admitted:
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
 bsr.w recovery_bank_loader_candidate_scan_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_candidate_scan_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_candidate_scan_region_core:
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
 movea.l #8192,a4
 cmpi.w #$f977,(a1)
 beq.w .pf977
 cmpi.w #$f9d7,(a1)
 beq.w .pf9d7
 cmpi.w #$f9e4,(a1)
 beq.w .pf9e4
 bra.w .budget_failure
.pf977: ; STX $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pf979: ; LDY #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d6
 bsr.w .nz
.pf97b: ; LDA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf97e: ; BPL $f9e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pf9e8
.pf980: ; LDA $0400,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf983: ; BPL $f9e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pf9e8
.pf985: ; LDA $04e0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf988: ; CMP #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf988
 ori.b #1,d7
.cmpf988:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf98a: ; BEQ $f9ac
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pf9ac
.pf98c: ; CMP #$60
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$60,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf98c
 ori.b #1,d7
.cmpf98c:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf98e: ; BEQ $f9a0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pf9a0
.pf990: ; CMP #$3a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf990
 ori.b #1,d7
.cmpf990:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf992: ; BNE $f9e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pf9e8
.pf994: ; STY $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.pf996: ; LDA #$fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d0
 move.b d0,d4
 bsr.w .nz
.pf998: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf99a: ; LDA #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 move.b d0,d4
 bsr.w .nz
.pf99c: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf99e: ; BEQ $f9bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pf9bc
.pf9a0: ; STY $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.pf9a2: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pf9a4: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf9a6: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pf9a8: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf9aa: ; BEQ $f9bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pf9bc
.pf9ac: ; STY $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.pf9ae: ; LDA $0420,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9b1: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pf9b2: ; LDA $f9d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9b5: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf9b7: ; LDA $f9d5,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9d5,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9ba: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf9bc: ; LDA $0570,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0570,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9bf: ; AND #$3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pf9c1: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pf9c2: ; LDA $f9fc,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9fc,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9c5: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pf9c6: ; SBC $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.pf9c8: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf9ca: ; LDA $fa18,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fa18,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9cd: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pf9ce: ; ADC $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .adc
.pf9d0: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf9d2: ; LDY $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pf9d4: ; JSR $f696
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9,d0
 bsr.w .push
 move.w #$d6,d0
 bsr.w .push
 move.w #$f696,(a1)
 bra.w .success
.pf9d7: ; LDA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9d9: ; BNE $f9e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pf9e8
.pf9db: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf9dd: ; CMP $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf9dd
 ori.b #1,d7
.cmpf9dd:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf9df: ; BCS $f9e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pf9e8
.pf9e1: ; JSR $f6dc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9,d0
 bsr.w .push
 move.w #$e3,d0
 bsr.w .push
 move.w #$f6dc,(a1)
 bra.w .success
.pf9e4: ; CMP $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf9e4
 ori.b #1,d7
.cmpf9e4:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf9e6: ; BCC $f9f1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pf9f1
.pf9e8: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pf9e9: ; CPY $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf9e9
 ori.b #1,d7
.cmpf9e9:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf9eb: ; BEQ $f9e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pf9e8
.pf9ed: ; CPY #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf9ed
 ori.b #1,d7
.cmpf9ed:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf9ef: ; BNE $f97b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pf97b
.pf9f1: ; RTS 
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
 cmpi.w #4,(a2)
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
 bra.w .bad_read
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
