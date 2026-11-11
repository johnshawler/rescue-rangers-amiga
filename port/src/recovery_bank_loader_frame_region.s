; Static native translation of fixed-bank frame orchestration, object hide, RNG and audio enqueue.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_frame_region:
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
 bsr.w recovery_bank_loader_frame_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_frame_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_frame_region_core:
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
 cmpi.w #$c77b,(a1)
 beq.w .pc77b
 cmpi.w #$c786,(a1)
 beq.w .pc786
 cmpi.w #$c795,(a1)
 beq.w .pc795
 cmpi.w #$c7a7,(a1)
 beq.w .pc7a7
 cmpi.w #$c7aa,(a1)
 beq.w .pc7aa
 cmpi.w #$c7c4,(a1)
 beq.w .pc7c4
 cmpi.w #$c7cd,(a1)
 beq.w .pc7cd
 cmpi.w #$c7d0,(a1)
 beq.w .pc7d0
 cmpi.w #$c7df,(a1)
 beq.w .pc7df
 cmpi.w #$c7e7,(a1)
 beq.w .pc7e7
 cmpi.w #$c7f0,(a1)
 beq.w .pc7f0
 cmpi.w #$c7f5,(a1)
 beq.w .pc7f5
 cmpi.w #$c7f8,(a1)
 beq.w .pc7f8
 cmpi.w #$c80a,(a1)
 beq.w .pc80a
 cmpi.w #$c81e,(a1)
 beq.w .pc81e
 cmpi.w #$c821,(a1)
 beq.w .pc821
 cmpi.w #$c828,(a1)
 beq.w .pc828
 cmpi.w #$c82b,(a1)
 beq.w .pc82b
 cmpi.w #$c830,(a1)
 beq.w .pc830
 cmpi.w #$c837,(a1)
 beq.w .pc837
 cmpi.w #$c83a,(a1)
 beq.w .pc83a
 cmpi.w #$c841,(a1)
 beq.w .pc841
 cmpi.w #$c848,(a1)
 beq.w .pc848
 cmpi.w #$c85b,(a1)
 beq.w .pc85b
 cmpi.w #$c85e,(a1)
 beq.w .pc85e
 cmpi.w #$c879,(a1)
 beq.w .pc879
 cmpi.w #$c8ab,(a1)
 beq.w .pc8ab
 cmpi.w #$c8b0,(a1)
 beq.w .pc8b0
 cmpi.w #$c8b3,(a1)
 beq.w .pc8b3
 cmpi.w #$c8d8,(a1)
 beq.w .pc8d8
 cmpi.w #$c8e0,(a1)
 beq.w .pc8e0
 cmpi.w #$c21e,(a1)
 beq.w .pc21e
 cmpi.w #$c2dc,(a1)
 beq.w .pc2dc
 cmpi.w #$f379,(a1)
 beq.w .pf379
 cmpi.w #$c8ee,(a1)
 beq.w .pc8ee
 bra.w .budget_failure
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
 cmpi.w #$c786,d0
 beq.w .pc786
 cmpi.w #$c795,d0
 beq.w .pc795
 cmpi.w #$c7f0,d0
 beq.w .pc7f0
 cmpi.w #$c837,d0
 beq.w .pc837
 cmpi.w #$c841,d0
 beq.w .pc841
 cmpi.w #$c8e0,d0
 beq.w .pc8e0
 move.w d0,(a1)
 bra.w .success
.pc2dc: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pc2de: ; LDY #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d6
 bsr.w .nz
.pc2e0: ; LDA $e4,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e4,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc2e2: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc2e4: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc2e6: ; LDA $e5,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e5,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc2e8: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc2ea: ; EOR $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc2ec: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pc2ed: ; BEQ $c2f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc2f0
.pc2ef: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pc2f0: ; ROR $e4,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e4,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 move.b d7,d2
 andi.b #1,d2
 lsl.b #7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .rorc2f0
 ori.b #1,d7
.rorc2f0:
 lsr.b #1,d0
 or.b d2,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pc2f2: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc2f3: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc2f4: ; BNE $c2f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc2f0
.pc2f6: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c786,d0
 beq.w .pc786
 cmpi.w #$c795,d0
 beq.w .pc795
 cmpi.w #$c7f0,d0
 beq.w .pc7f0
 cmpi.w #$c837,d0
 beq.w .pc837
 cmpi.w #$c841,d0
 beq.w .pc841
 cmpi.w #$c8e0,d0
 beq.w .pc8e0
 move.w d0,(a1)
 bra.w .success
.pc77b: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc77d: ; AND #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc77f: ; BEQ $c795
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc795
.pc781: ; LDA #$24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d0
 move.b d0,d4
 bsr.w .nz
.pc783: ; JSR $f379
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$85,d0
 bsr.w .push
 bra.w .pf379
.pc786: ; LDY #$f3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f3,d0
 move.b d0,d6
 bsr.w .nz
.pc788: ; LDA $98
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$98,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc78a: ; EOR #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc78c: ; STA $98
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$98,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc78e: ; BNE $c791
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc791
.pc790: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc791: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.pc792: ; JSR $f379
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$94,d0
 bsr.w .push
 bra.w .pf379
.pc795: ; LDA $98
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$98,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc797: ; BEQ $c79c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc79c
.pc799: ; JMP $c83e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pc83e
.pc79c: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc79e: ; AND #$20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$20,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc7a0: ; BEQ $c7aa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc7aa
.pc7a2: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.pc7a4: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$a6,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc7a7: ; JSR $8900
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$a9,d0
 bsr.w .push
 move.w #$8900,(a1)
 bra.w .success
.pc7aa: ; LDA $4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4e,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc7ac: ; ORA $4f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4f,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc7ae: ; BEQ $c7ed
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc7ed
.pc7b0: ; LDA $4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4e,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc7b2: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pc7b3: ; SBC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 bsr.w .sbc
.pc7b5: ; STA $4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4e,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc7b7: ; LDA $4f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4f,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc7b9: ; SBC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 bsr.w .sbc
.pc7bb: ; STA $4f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc7bd: ; ORA $4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4e,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc7bf: ; BNE $c7ed
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc7ed
.pc7c1: ; JSR $c235
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$c3,d0
 bsr.w .push
 move.w #$c235,(a1)
 bra.w .success
.pc7c4: ; LDA $37
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$37,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc7c6: ; STA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc7c8: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.pc7ca: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$cc,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc7cd: ; JSR $9000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$cf,d0
 bsr.w .push
 move.w #$9000,(a1)
 bra.w .success
.pc7d0: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc7d2: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pc7d3: ; LDX #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0b,d0
 move.b d0,d5
 bsr.w .nz
.pc7d5: ; CMP #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc7d5
 ori.b #1,d7
.cmpc7d5:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc7d7: ; BCC $c7da
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pc7da
.pc7d9: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc7da: ; STX $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .store
.pc7dc: ; JSR $e096
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$de,d0
 bsr.w .push
 move.w #$e096,(a1)
 bra.w .success
.pc7df: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pc7e0: ; STA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc7e2: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.pc7e4: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$e6,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc7e7: ; JSR $8b00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$e9,d0
 bsr.w .push
 move.w #$8b00,(a1)
 bra.w .success
.pc7ea: ; JMP $c60e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c60e,(a1)
 bra.w .success
.pc7ed: ; JSR $c879
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$ef,d0
 bsr.w .push
 bra.w .pc879
.pc7f0: ; LDA #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d0
 move.b d0,d4
 bsr.w .nz
.pc7f2: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$f4,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc7f5: ; JSR $8000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c7,d0
 bsr.w .push
 move.w #$f7,d0
 bsr.w .push
 move.w #$8000,(a1)
 bra.w .success
.pc7f8: ; LDX $30
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$30,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pc7fa: ; BEQ $c807
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc807
.pc7fc: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.pc7fe: ; STA $03e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03e0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc801: ; STA $1c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1c,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc803: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc805: ; STA $30
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$30,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc807: ; JSR $d6a3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$09,d0
 bsr.w .push
 move.w #$d6a3,(a1)
 bra.w .success
.pc80a: ; LDX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d5
 bsr.w .nz
.pc80c: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc80f: ; STA $68,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$68,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc811: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc814: ; STA $6a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6a,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc816: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc817: ; BPL $c80c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pc80c
.pc819: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pc81b: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$1d,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc81e: ; JSR $8090
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$20,d0
 bsr.w .push
 move.w #$8090,(a1)
 bra.w .success
.pc821: ; LDX $6c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6c,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pc823: ; BEQ $c828
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc828
.pc825: ; JSR $e576
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$27,d0
 bsr.w .push
 move.w #$e576,(a1)
 bra.w .success
.pc828: ; JSR $e9c9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$2a,d0
 bsr.w .push
 move.w #$e9c9,(a1)
 bra.w .success
.pc82b: ; LDA #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d0,d4
 bsr.w .nz
.pc82d: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$2f,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc830: ; LDA #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d0,d4
 bsr.w .nz
.pc832: ; STA $97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc834: ; JSR $c21e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$36,d0
 bsr.w .push
 bra.w .pc21e
.pc837: ; JSR $8000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$39,d0
 bsr.w .push
 move.w #$8000,(a1)
 bra.w .success
.pc83a: ; LDA #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d0,d4
 bsr.w .nz
.pc83c: ; STA $97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc83e: ; JSR $c2dc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$40,d0
 bsr.w .push
 bra.w .pc2dc
.pc841: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc843: ; STA $9a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9a,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc845: ; JSR $ff04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$47,d0
 bsr.w .push
 move.w #$ff04,(a1)
 bra.w .success
.pc848: ; INC $9a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9a,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pc84a: ; LDA $b8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b8,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc84c: ; BEQ $c85e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc85e
.pc84e: ; BMI $c861
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pc861
.pc850: ; LDA $14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc852: ; AND #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc854: ; BNE $c861
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc861
.pc856: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pc858: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$5a,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc85b: ; JSR $9000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$5d,d0
 bsr.w .push
 move.w #$9000,(a1)
 bra.w .success
.pc85e: ; JMP $c77b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c77b,(a1)
 bra.w .success
.pc861: ; INC $bd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bd,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pc863: ; LDA $bd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bd,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc865: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc865
 ori.b #1,d7
.cmpc865:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc867: ; BNE $c86d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc86d
.pc869: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc86b: ; STA $bd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bd,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc86d: ; LDX #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 move.b d0,d5
 bsr.w .nz
.pc86f: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc871: ; STA $b0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b0,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc873: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc874: ; BPL $c871
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pc871
.pc876: ; JMP $c588
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c588,(a1)
 bra.w .success
.pc879: ; LDA $6d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6d,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc87b: ; BEQ $c8cd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc8cd
.pc87d: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc87f: ; STA $0430
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 move.b d4,d0
 bsr.w .store
.pc882: ; STA $0431
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0431,d1
 move.b d4,d0
 bsr.w .store
.pc885: ; STA $5e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc887: ; STA $5f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc889: ; DEC $6d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6d,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.pc88b: ; BEQ $c88e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc88e
.pc88d: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c786,d0
 beq.w .pc786
 cmpi.w #$c795,d0
 beq.w .pc795
 cmpi.w #$c7f0,d0
 beq.w .pc7f0
 cmpi.w #$c837,d0
 beq.w .pc837
 cmpi.w #$c841,d0
 beq.w .pc841
 cmpi.w #$c8e0,d0
 beq.w .pc8e0
 move.w d0,(a1)
 bra.w .success
.pc88e: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc890: ; STA $37
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$37,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc892: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc892
 ori.b #1,d7
.cmpc892:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc894: ; BEQ $c8c0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc8c0
.pc896: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.pc897: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #0,d4
 beq.s .shiftc897
 ori.b #1,d7
.shiftc897:
 lsr.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc898: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #0,d4
 beq.s .shiftc898
 ori.b #1,d7
.shiftc898:
 lsr.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc899: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #0,d4
 beq.s .shiftc899
 ori.b #1,d7
.shiftc899:
 lsr.b #1,d4
 move.b d4,d0
 bsr.w .nz
.pc89a: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc89c: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d4,d0
 bsr.w .nz
.pc89d: ; LDA $38,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$38,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc89f: ; ORA $d692,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d692,d1
 add.w d6,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc8a2: ; STA $38,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$38,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8a4: ; LDA #$0d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0d,d0
 move.b d0,d4
 bsr.w .nz
.pc8a6: ; STA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8a8: ; JSR $c6b5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$aa,d0
 bsr.w .push
 move.w #$c6b5,(a1)
 bra.w .success
.pc8ab: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.pc8ad: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$af,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pc8b0: ; JSR $a410
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$b2,d0
 bsr.w .push
 move.w #$a410,(a1)
 bra.w .success
.pc8b3: ; LDA #$2c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2c,d0
 move.b d0,d4
 bsr.w .nz
.pc8b5: ; STA $4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4e,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8b7: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pc8b9: ; STA $4f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8bb: ; LDA #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 move.b d0,d4
 bsr.w .nz
.pc8bd: ; JMP $f377
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f377,(a1)
 bra.w .success
.pc8c0: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pc8c2: ; STA $4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4e,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8c4: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc8c6: ; STA $4f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8c8: ; LDA #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 move.b d0,d4
 bsr.w .nz
.pc8ca: ; JMP $f377
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f377,(a1)
 bra.w .success
.pc8cd: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pc8cf: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc8d1: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc8d1
 ori.b #1,d7
.cmpc8d1:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc8d3: ; BNE $c8d8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc8d8
.pc8d5: ; JSR $d1dc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$d7,d0
 bsr.w .push
 move.w #$d1dc,(a1)
 bra.w .success
.pc8d8: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc8db: ; BPL $c8e0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pc8e0
.pc8dd: ; JSR $c8ee
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c8,d0
 bsr.w .push
 move.w #$df,d0
 bsr.w .push
 bra.w .pc8ee
.pc8e0: ; LDA $5e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc8e2: ; BPL $c8e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pc8e8
.pc8e4: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.pc8e6: ; STA $5e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8e8: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc8e9: ; CPX #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc8e9
 ori.b #1,d7
.cmpc8e9:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc8eb: ; BNE $c8cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc8cf
.pc8ed: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c786,d0
 beq.w .pc786
 cmpi.w #$c795,d0
 beq.w .pc795
 cmpi.w #$c7f0,d0
 beq.w .pc7f0
 cmpi.w #$c837,d0
 beq.w .pc837
 cmpi.w #$c841,d0
 beq.w .pc841
 cmpi.w #$c8e0,d0
 beq.w .pc8e0
 move.w d0,(a1)
 bra.w .success
.pc8ee: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pc8f0: ; BEQ $c903
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc903
.pc8f2: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc8f5: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc8f7: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc8f9: ; LDA $0380,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0380,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc8fc: ; AND #$bf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bf,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc8fe: ; ORA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc900: ; STA $0380,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0380,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .store
.pc903: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc905: ; CMP #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc905
 ori.b #1,d7
.cmpc905:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc907: ; BEQ $c913
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc913
.pc909: ; LDA #$cc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc,d0
 move.b d0,d4
 bsr.w .nz
.pc90b: ; STA $0530,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0530,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc90e: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pc910: ; STA $0540,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0540,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .store
.pc913: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc915: ; STA $52,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$52,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc917: ; LDY $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pc919: ; LDA $c926,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c926,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc91c: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc91e: ; LDA $c933,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c933,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc921: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .store
.pc923: ; JMP ($0000)
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d0
 move.b 1(a0),d0
 lsl.w #8,d0
 move.b (a0),d0
 move.w d0,(a1)
 bra.w .success
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
 cmpi.w #$c786,d0
 beq.w .pc786
 cmpi.w #$c795,d0
 beq.w .pc795
 cmpi.w #$c7f0,d0
 beq.w .pc7f0
 cmpi.w #$c837,d0
 beq.w .pc837
 cmpi.w #$c841,d0
 beq.w .pc841
 cmpi.w #$c8e0,d0
 beq.w .pc8e0
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
