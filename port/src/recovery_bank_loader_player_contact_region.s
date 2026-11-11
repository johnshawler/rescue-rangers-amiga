; Static native translation of fixed-bank F92B player-contact scan.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal6 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_player_contact_region:
 cmpi.w #$f92b,(a1)
 beq.s .admitted
 cmpi.w #$f95a,(a1)
 beq.s .admitted
 cmpi.w #$f96c,(a1)
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
 bsr.w recovery_bank_loader_player_contact_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_player_contact_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_player_contact_region_core:
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
 cmpi.w #$f92b,(a1)
 beq.w .pf92b
 cmpi.w #$f95a,(a1)
 beq.w .pf95a
 cmpi.w #$f96c,(a1)
 beq.w .pf96c
 bra.w .budget_failure
.pf92b: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.pf92d: ; LDA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf930: ; BPL $f943
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pf943
.pf932: ; LDA $0400,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf935: ; BPL $f943
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pf943
.pf937: ; LDA $0054,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0054,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf93a: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf93a
 ori.b #1,d7
.cmpf93a:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf93c: ; BCS $f943
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pf943
.pf93e: ; JSR $f949
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9,d0
 bsr.w .push
 move.w #$40,d0
 bsr.w .push
 bra.w .pf949
.pf941: ; BCC $f974
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pf974
.pf943: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pf944: ; LDA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf947: ; BPL $f973
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pf973
.pf949: ; STY $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .store
.pf94b: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf94e: ; BPL $f973
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pf973
.pf950: ; LDA $0570,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0570,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf953: ; AND #$3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pf955: ; STA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pf957: ; JSR $f696
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9,d0
 bsr.w .push
 move.w #$59,d0
 bsr.w .push
 move.w #$f696,(a1)
 bra.w .success
.pf95a: ; LDA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf95c: ; BNE $f973
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pf973
.pf95e: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pf960: ; LDY $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pf962: ; CMP $fa18,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fa18,d1
 add.w d6,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf962
 ori.b #1,d7
.cmpf962:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf965: ; BCS $f973
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pf973
.pf967: ; LDY $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pf969: ; JSR $f6dc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9,d0
 bsr.w .push
 move.w #$6b,d0
 bsr.w .push
 move.w #$f6dc,(a1)
 bra.w .success
.pf96c: ; LDY $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pf96e: ; CMP $f9fc,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f9fc,d1
 add.w d6,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpf96e
 ori.b #1,d7
.cmpf96e:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pf971: ; BCC $f974
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pf974
.pf973: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pf974: ; LDY $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pf976: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$f941,d0
 beq.w .pf941
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
 cmpi.w #1,(a2)
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
