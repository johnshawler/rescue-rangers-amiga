; Static native translation of bounded fixed-bank stage fade/resource/video/audio-request setup.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_stage_finish:
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
 bsr.w recovery_bank_loader_stage_finish_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_stage_finish_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_stage_finish_core:
 tst.b $31(a0)
 bne.w .invalid
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
 cmpi.w #$e106,(a1)
 beq.w .pe106
 cmpi.w #$e10c,(a1)
 beq.w .pe10c
 cmpi.w #$e10f,(a1)
 beq.w .pe10f
 cmpi.w #$c262,(a1)
 beq.w .pc262
 cmpi.w #$c265,(a1)
 beq.w .pc265
 cmpi.w #$c703,(a1)
 beq.w .pc703
 cmpi.w #$c617,(a1)
 beq.w .pc617
 bra.w .budget_failure
.pc253: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc255: ; CMP #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc255
 ori.b #1,d7
.cmpc255:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc257: ; BEQ $c265
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc265
.pc259: ; CMP #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc259
 ori.b #1,d7
.cmpc259:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc25b: ; BEQ $c265
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc265
.pc25d: ; LDA #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d0,d4
 bsr.w .nz
.pc25f: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c2,d0
 bsr.w .push
 move.w #$61,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc262: ; JSR $8000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c2,d0
 bsr.w .push
 move.w #$64,d0
 bsr.w .push
 move.w #$8000,(a1)
 bra.w .success
.pc265: ; JMP $c26e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c26e,(a1)
 bra.w .success
.pc617: ; JMP $c77b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c77b,(a1)
 bra.w .success
.pc703: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc705: ; STA $6e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6e,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc707: ; LDX $50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$50,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pc709: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc70c: ; STA $68,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$68,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc70e: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc711: ; STA $6a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6a,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc713: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc714: ; BPL $c709
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pc709
.pc716: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$e109,d0
 beq.w .pe109
 cmpi.w #$c617,d0
 beq.w .pc617
 move.w d0,(a1)
 bra.w .success
.pe106: ; JSR $e754
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$08,d0
 bsr.w .push
 bra.w .pe754
.pe109: ; JSR $c158
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$0b,d0
 bsr.w .push
 move.w #$c158,(a1)
 bra.w .success
.pe10c: ; JSR $ff04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e1,d0
 bsr.w .push
 move.w #$0e,d0
 bsr.w .push
 move.w #$ff04,(a1)
 bra.w .success
.pe10f: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pe111: ; STA $3e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3e,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe113: ; STA $3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pe115: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe117: ; CMP #$0d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0d,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe117
 ori.b #1,d7
.cmpe117:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe119: ; BNE $e176
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pe176
.pe176: ; JMP $c253
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pc253
.pe754: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pe756: ; CMP #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe756
 ori.b #1,d7
.cmpe756:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe758: ; BEQ $e75f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .budget_failure
.pe75a: ; CMP #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpe75a
 ori.b #1,d7
.cmpe75a:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pe75c: ; BEQ $e76d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .budget_failure
.pe75e: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$e109,d0
 beq.w .pe109
 cmpi.w #$c617,d0
 beq.w .pc617
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
