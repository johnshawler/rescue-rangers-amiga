; Static native translation of fixed-bank stage camera, scrolling and map update orchestration.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_stage_scroll_region:
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
 bsr.l recovery_stage_scroll_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.l recovery_stage_scroll_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_stage_scroll_region_core:
 cmpi.b #7,3(a4)
 bhi.l .invalid
 cmpi.b #$1e,(a4)
 bne.l .invalid
 tst.w 4(a4)
 bne.l .invalid
 cmpi.w #$d501,10(a4)
 bne.l .invalid
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
 movea.l #20000,a4
 cmpi.w #$d6a3,(a1)
 beq.l .pd6a3
 cmpi.w #$d6df,(a1)
 beq.l .pd6df
 cmpi.w #$d710,(a1)
 beq.l .pd710
 cmpi.w #$d885,(a1)
 beq.l .pd885
 cmpi.w #$d891,(a1)
 beq.l .pd891
 cmpi.w #$d8ab,(a1)
 beq.l .pd8ab
 cmpi.w #$d8b7,(a1)
 beq.l .pd8b7
 cmpi.w #$d8c9,(a1)
 beq.l .pd8c9
 cmpi.w #$d8d7,(a1)
 beq.l .pd8d7
 cmpi.w #$d904,(a1)
 beq.l .pd904
 cmpi.w #$d912,(a1)
 beq.l .pd912
 cmpi.w #$d9b4,(a1)
 beq.l .pd9b4
 cmpi.w #$d9cc,(a1)
 beq.l .pd9cc
 cmpi.w #$d9d6,(a1)
 beq.l .pd9d6
 cmpi.w #$d9f6,(a1)
 beq.l .pd9f6
 cmpi.w #$da24,(a1)
 beq.l .pda24
 cmpi.w #$da50,(a1)
 beq.l .pda50
 cmpi.w #$da74,(a1)
 beq.l .pda74
 cmpi.w #$daad,(a1)
 beq.l .pdaad
 cmpi.w #$daaf,(a1)
 beq.l .pdaaf
 cmpi.w #$dac7,(a1)
 beq.l .pdac7
 cmpi.w #$dafd,(a1)
 beq.l .pdafd
 cmpi.w #$db14,(a1)
 beq.l .pdb14
 cmpi.w #$db50,(a1)
 beq.l .pdb50
 cmpi.w #$db6f,(a1)
 beq.l .pdb6f
 cmpi.w #$db90,(a1)
 beq.l .pdb90
 cmpi.w #$dd1a,(a1)
 beq.l .pdd1a
 cmpi.w #$dd4d,(a1)
 beq.l .pdd4d
 cmpi.w #$dd53,(a1)
 beq.l .pdd53
 cmpi.w #$dd7a,(a1)
 beq.l .pdd7a
 cmpi.w #$ddc7,(a1)
 beq.l .pddc7
 cmpi.w #$de4d,(a1)
 beq.l .pde4d
 cmpi.w #$de61,(a1)
 beq.l .pde61
 cmpi.w #$de8a,(a1)
 beq.l .pde8a
 cmpi.w #$dea8,(a1)
 beq.l .pdea8
 cmpi.w #$deb3,(a1)
 beq.l .pdeb3
 cmpi.w #$deb8,(a1)
 beq.l .pdeb8
 cmpi.w #$deb9,(a1)
 beq.l .pdeb9
 cmpi.w #$deca,(a1)
 beq.l .pdeca
 cmpi.w #$decd,(a1)
 beq.l .pdecd
 cmpi.w #$deee,(a1)
 beq.l .pdeee
 cmpi.w #$df01,(a1)
 beq.l .pdf01
 cmpi.w #$df04,(a1)
 beq.l .pdf04
 bra.l .budget_failure
.pd6a3: ; LDA $50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$50,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6a5: ; BEQ $d6aa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd6aa
.pd6a7: ; JMP $d72d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd72d
.pd6aa: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.l .nz
.pd6ac: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6af: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd6b0: ; SBC $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd6b2: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd6b4: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6b7: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd6b8: ; SBC $68,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$68,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd6ba: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd6bc: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6bf: ; SBC $6a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$6a,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd6c1: ; ORA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd6c3: ; BEQ $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd72a
.pd6c5: ; BCS $d6fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd6fc
.pd6c7: ; LDA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6c9: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd6cb: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 bsr.l .adc
.pd6cd: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd6cf: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6d1: ; CMP #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd6d1
 ori.b #1,d7
.cmpd6d1:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd6d3: ; BCS $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd72a
.pd6d5: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6d7: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pd6d8: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.l .nz
.pd6da: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd6dc: ; JSR $da50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d6,d0
 bsr.l .push
 move.w #$de,d0
 bsr.l .push
 bra.l .pda50
.pd6df: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pd6e0: ; BCS $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd72a
.pd6e2: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd6e4: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6e6: ; CMP #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd6e6
 ori.b #1,d7
.cmpd6e6:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd6e8: ; BCS $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd72a
.pd6ea: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6ec: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd6ed: ; ADC #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d0
 bsr.l .adc
.pd6ef: ; STA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd6f2: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6f4: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .adc
.pd6f6: ; STA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd6f9: ; JMP $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd72a
.pd6fc: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd6fe: ; CMP #$89
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$89,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd6fe
 ori.b #1,d7
.cmpd6fe:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd700: ; BCC $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd72a
.pd702: ; LDA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd704: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd706: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd708: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pd709: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.l .nz
.pd70b: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd70d: ; JSR $d9f6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d7,d0
 bsr.l .push
 move.w #$0f,d0
 bsr.l .push
 bra.l .pd9f6
.pd710: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pd711: ; BCS $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd72a
.pd713: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd715: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd717: ; CMP #$f1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f1,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd717
 ori.b #1,d7
.cmpd717:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd719: ; BCC $d72a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd72a
.pd71b: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd71d: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd71e: ; ADC #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f0,d0
 bsr.l .adc
.pd720: ; STA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd723: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd725: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .adc
.pd727: ; STA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd72a: ; JMP $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd93f
.pd72d: ; LDX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d5
 bsr.l .nz
.pd72f: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd731: ; CMP #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd731
 ori.b #1,d7
.cmpd731:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd733: ; BEQ $d73a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd73a
.pd735: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.l .nz
.pd736: ; BPL $d72f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd72f
.pd738: ; BMI $d741
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 bne.l .pd741
.pd73a: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.l .nz
.pd73b: ; EOR #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd73d: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pd73e: ; JMP $d6ac
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd6ac
.pd741: ; LDA $04f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd744: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd745: ; SBC $04f1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f1,d1
 bsr.l .read
 bsr.l .sbc
.pd748: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd74a: ; LDA $0500
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd74d: ; SBC $0501
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0501,d1
 bsr.l .read
 bsr.l .sbc
.pd750: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd752: ; BCS $d758
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd758
.pd754: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd756: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 bsr.l .adc
.pd758: ; CMP #$e0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$e0,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd758
 ori.b #1,d7
.cmpd758:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd75a: ; BCC $d76e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd76e
.pd75c: ; LDX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d5
 bsr.l .nz
.pd75e: ; LDA $68,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$68,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd760: ; STA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd763: ; LDA $6a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$6a,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd765: ; STA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd768: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.l .nz
.pd769: ; BPL $d75e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd75e
.pd76b: ; JMP $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd93f
.pd76e: ; LDX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d5
 bsr.l .nz
.pd770: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd773: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd774: ; SBC $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd776: ; STA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd778: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd77b: ; SBC $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd77d: ; STA $02,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd77f: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.l .nz
.pd780: ; BPL $d770
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd770
.pd782: ; LDX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d5
 bsr.l .nz
.pd784: ; LDA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd786: ; CMP #$f1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f1,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd786
 ori.b #1,d7
.cmpd786:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd788: ; BCC $d78d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd78d
.pd78a: ; JMP $d8bf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd8bf
.pd78d: ; CMP #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd78d
 ori.b #1,d7
.cmpd78d:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd78f: ; BCS $d794
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd794
.pd791: ; JMP $d8fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd8fa
.pd794: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.l .nz
.pd795: ; BPL $d784
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd784
.pd797: ; LDX #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d5
 bsr.l .nz
.pd799: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd79c: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd79d: ; SBC $68,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$68,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd79f: ; STA $04,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd7a1: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7a4: ; SBC $6a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$6a,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd7a6: ; ORA $04,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd7a8: ; BEQ $d7cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd7cf
.pd7aa: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.l .nz
.pd7ac: ; STA $06,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd7ae: ; BCS $d7bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd7bc
.pd7b0: ; LDA $04,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7b2: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd7b4: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 bsr.l .adc
.pd7b6: ; STA $04,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd7b8: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.l .nz
.pd7ba: ; STA $06,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd7bc: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.l .nz
.pd7bd: ; BPL $d799
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd799
.pd7bf: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.l .nz
.pd7c1: ; LDY #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d6
 bsr.l .nz
.pd7c3: ; LDA $06,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7c5: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd7c7: ; BEQ $d813
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd813
.pd7c9: ; LDA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7cb: ; CMP #$89
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$89,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd7cb
 ori.b #1,d7
.cmpd7cb:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd7cd: ; BCS $d7d2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd7d2
.pd7cf: ; JMP $d856
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd856
.pd7d2: ; LDA $0006,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0006,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7d5: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd7d7: ; BEQ $d7f3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd7f3
.pd7d9: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7dc: ; CMP #$89
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$89,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd7dc
 ori.b #1,d7
.cmpd7dc:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd7de: ; BCC $d7ec
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd7ec
.pd7e0: ; CMP $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd7e0
 ori.b #1,d7
.cmpd7e0:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd7e2: ; BCS $d7ec
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd7ec
.pd7e4: ; LDA $0004,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0004,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7e7: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd7e9: ; JMP $d8a6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd8a6
.pd7ec: ; LDA $04,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7ee: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd7f0: ; JMP $d8a8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd8a8
.pd7f3: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd7f6: ; CMP #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd7f6
 ori.b #1,d7
.cmpd7f6:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd7f8: ; BCS $d7ec
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd7ec
.pd7fa: ; LDA #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 move.b d0,d4
 bsr.l .nz
.pd7fc: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd7fd: ; SBC $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 bsr.l .sbc
.pd800: ; STA $08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd802: ; LDA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd804: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd805: ; SBC #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 bsr.l .sbc
.pd807: ; CMP $08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd807
 ori.b #1,d7
.cmpd807:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd809: ; BCC $d7ec
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd7ec
.pd80b: ; LDA $0004,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0004,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd80e: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd810: ; JMP $d880
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd880
.pd813: ; LDA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd815: ; CMP #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd815
 ori.b #1,d7
.cmpd815:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd817: ; BCS $d856
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd856
.pd819: ; LDA $0006,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0006,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd81c: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd81e: ; BEQ $d83a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd83a
.pd820: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd823: ; CMP #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd823
 ori.b #1,d7
.cmpd823:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd825: ; BCS $d833
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd833
.pd827: ; CMP $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd827
 ori.b #1,d7
.cmpd827:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd829: ; BCC $d833
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd833
.pd82b: ; LDA $0004,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0004,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd82e: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd830: ; JMP $d880
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd880
.pd833: ; LDA $04,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd835: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd837: ; JMP $d882
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd882
.pd83a: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd83d: ; CMP #$89
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$89,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd83d
 ori.b #1,d7
.cmpd83d:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd83f: ; BCC $d833
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd833
.pd841: ; SBC #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 bsr.l .sbc
.pd843: ; STA $08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd845: ; LDA #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 move.b d0,d4
 bsr.l .nz
.pd847: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd848: ; SBC $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd84a: ; CMP $08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd84a
 ori.b #1,d7
.cmpd84a:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd84c: ; BCC $d833
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd833
.pd84e: ; LDA $0004,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0004,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd851: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd853: ; JMP $d8a6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd8a6
.pd856: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.l .nz
.pd857: ; EOR #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd859: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pd85a: ; LDA $04f0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd85d: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd85e: ; SBC $0068,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0068,d1
 add.w d6,d1
 bsr.l .read
 bsr.l .sbc
.pd861: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd863: ; LDA $0500,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd866: ; SBC $006a,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$006a,d1
 add.w d6,d1
 bsr.l .read
 bsr.l .sbc
.pd869: ; BCS $d899
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd899
.pd86b: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd86d: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd86f: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 bsr.l .adc
.pd871: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd873: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd876: ; CMP #$88
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$88,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd876
 ori.b #1,d7
.cmpd876:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd878: ; BCS $d896
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd896
.pd87a: ; LDA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd87c: ; CMP #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f0,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd87c
 ori.b #1,d7
.cmpd87c:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd87e: ; BCS $d896
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd896
.pd880: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.l .nz
.pd881: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pd882: ; JSR $d9d6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d8,d0
 bsr.l .push
 move.w #$84,d0
 bsr.l .push
 bra.l .pd9d6
.pd885: ; BCS $d896
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd896
.pd887: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd889: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pd88a: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.l .nz
.pd88c: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd88e: ; JSR $da50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d8,d0
 bsr.l .push
 move.w #$90,d0
 bsr.l .push
 bra.l .pda50
.pd891: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pd892: ; BCS $d896
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd896
.pd894: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd896: ; JMP $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd93f
.pd899: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd89c: ; CMP #$89
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$89,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd89c
 ori.b #1,d7
.cmpd89c:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd89e: ; BCC $d8bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd8bc
.pd8a0: ; LDA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd8a2: ; CMP #$11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd8a2
 ori.b #1,d7
.cmpd8a2:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd8a4: ; BCC $d8bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd8bc
.pd8a6: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.l .nz
.pd8a7: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pd8a8: ; JSR $d9cc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d8,d0
 bsr.l .push
 move.w #$aa,d0
 bsr.l .push
 bra.l .pd9cc
.pd8ab: ; BCS $d8bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd8bc
.pd8ad: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd8af: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pd8b0: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.l .nz
.pd8b2: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd8b4: ; JSR $d9f6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d8,d0
 bsr.l .push
 move.w #$b6,d0
 bsr.l .push
 bra.l .pd9f6
.pd8b7: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pd8b8: ; BCS $d8bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd8bc
.pd8ba: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd8bc: ; JMP $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd93f
.pd8bf: ; LDA $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd8c1: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd8c2: ; SBC #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f0,d0
 bsr.l .sbc
.pd8c4: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd8c6: ; JSR $d9cc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d8,d0
 bsr.l .push
 move.w #$c8,d0
 bsr.l .push
 bra.l .pd9cc
.pd8c9: ; BCS $d8de
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd8de
.pd8cb: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd8cd: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pd8ce: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.l .nz
.pd8d0: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd8d2: ; STX $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.l .write
.pd8d4: ; JSR $d9f6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d8,d0
 bsr.l .push
 move.w #$d6,d0
 bsr.l .push
 bra.l .pd9f6
.pd8d7: ; LDX $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pd8d9: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pd8da: ; BCS $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd93f
.pd8dc: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd8de: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd8e0: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd8e1: ; ADC #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f0,d0
 bsr.l .adc
.pd8e3: ; STA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd8e6: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd8e8: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .adc
.pd8ea: ; STA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd8ed: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.l .nz
.pd8ee: ; EOR #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd8f0: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pd8f1: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd8f4: ; CMP #$f1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f1,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd8f4
 ori.b #1,d7
.cmpd8f4:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd8f6: ; BCS $d933
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd933
.pd8f8: ; BCC $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd93f
.pd8fa: ; LDA #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d0
 move.b d0,d4
 bsr.l .nz
.pd8fc: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd8fd: ; SBC $00,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd8ff: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd901: ; JSR $d9d6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d9,d0
 bsr.l .push
 move.w #$03,d0
 bsr.l .push
 bra.l .pd9d6
.pd904: ; BCS $d919
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd919
.pd906: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd908: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pd909: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.l .nz
.pd90b: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd90d: ; STX $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.l .write
.pd90f: ; JSR $da50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$d9,d0
 bsr.l .push
 move.w #$11,d0
 bsr.l .push
 bra.l .pda50
.pd912: ; LDX $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pd914: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pd915: ; BCS $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd93f
.pd917: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd919: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd91b: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd91c: ; ADC #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d0
 bsr.l .adc
.pd91e: ; STA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd921: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd923: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .adc
.pd925: ; STA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pd928: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.l .nz
.pd929: ; EOR #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd92b: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pd92c: ; LDA $0000,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0000,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd92f: ; CMP #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd92f
 ori.b #1,d7
.cmpd92f:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd931: ; BCS $d93f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd93f
.pd933: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd936: ; STA $04f0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pd939: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd93c: ; STA $0500,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0500,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pd93f: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd941: ; BNE $d9b4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pd9b4
.pd943: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pd945: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd947: ; STA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd949: ; LDA $04d0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04d0,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd94c: ; BPL $d966
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd966
.pd94e: ; LDA $54
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$54,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd950: ; CMP #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd950
 ori.b #1,d7
.cmpd950:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd952: ; BEQ $d966
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd966
.pd954: ; LDA $0400
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0400,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd957: ; BPL $d966
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd966
.pd959: ; LDA $0510
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0510,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd95c: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd95d: ; SBC $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd95f: ; BCS $d964
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd964
.pd961: ; SBC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0f,d0
 bsr.l .sbc
.pd963: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd964: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd966: ; LDA $04d1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04d1,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd969: ; BPL $d983
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd983
.pd96b: ; LDA $55
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$55,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd96d: ; CMP #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd96d
 ori.b #1,d7
.cmpd96d:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd96f: ; BEQ $d983
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd983
.pd971: ; LDA $0401
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0401,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd974: ; BPL $d983
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pd983
.pd976: ; LDA $0511
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0511,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd979: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd97a: ; SBC $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd97c: ; BCS $d981
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd981
.pd97e: ; SBC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0f,d0
 bsr.l .sbc
.pd980: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd981: ; STA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd983: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd985: ; ORA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd987: ; BEQ $d9b4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd9b4
.pd989: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd98b: ; BEQ $d9b5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pd9b5
.pd98d: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd98f: ; BNE $d998
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pd998
.pd991: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd993: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd995: ; JMP $d9b5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd9b5
.pd998: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd99a: ; CMP #$a0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$a0,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd99a
 ori.b #1,d7
.cmpd99a:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd99c: ; BCS $d9b4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd9b4
.pd99e: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9a0: ; CMP #$a0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$a0,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9a0
 ori.b #1,d7
.cmpd9a0:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd9a2: ; BCS $d9b4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd9b4
.pd9a4: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9a6: ; CMP $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9a6
 ori.b #1,d7
.cmpd9a6:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd9a8: ; BCS $d9ae
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd9ae
.pd9aa: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9ac: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd9ae: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9b0: ; CMP #$58
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$58,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9b0
 ori.b #1,d7
.cmpd9b0:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd9b2: ; BCC $d9b5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd9b5
.pd9b4: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pd9b5: ; LDA #$58
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$58,d0
 move.b d0,d4
 bsr.l .nz
.pd9b7: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd9b8: ; SBC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd9ba: ; BCC $d9cb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd9cb
.pd9bc: ; CMP #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$09,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9bc
 ori.b #1,d7
.cmpd9bc:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd9be: ; BCC $d9c2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd9c2
.pd9c0: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.l .nz
.pd9c2: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd9c4: ; LDA #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d0
 move.b d0,d4
 bsr.l .nz
.pd9c6: ; STA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd9c8: ; JMP $dafd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pdafd
.pd9cb: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pd9cc: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9ce: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd9cf: ; ADC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pd9d1: ; STA $0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd9d3: ; JMP $d9e0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd9e0
.pd9d6: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9d8: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd9d9: ; SBC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd9db: ; STA $0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pd9dd: ; JMP $d9e0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pd9e0
.pd9e0: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.l .nz
.pd9e1: ; EOR #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pd9e3: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pd9e4: ; LDA $04f0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04f0,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9e7: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd9e8: ; SBC $0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pd9ea: ; CMP #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9ea
 ori.b #1,d7
.cmpd9ea:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd9ec: ; BCC $d9f4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pd9f4
.pd9ee: ; CMP #$f1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f1,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9ee
 ori.b #1,d7
.cmpd9ee:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd9f0: ; BCS $d9f4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pd9f4
.pd9f2: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pd9f3: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pd9f4: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pd9f5: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pd9f6: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9f8: ; CMP #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9f8
 ori.b #1,d7
.cmpd9f8:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pd9fa: ; BNE $da02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pda02
.pd9fc: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pd9fe: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd9fe
 ori.b #1,d7
.cmpd9fe:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pda00: ; BCC $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pda4e
.pda02: ; LDY $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pda04: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pda05: ; LDA ($34),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $35(a0),d1
 lsl.w #8,d1
 move.b $34(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda07: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pda09: ; BEQ $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda4e
.pda0b: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda0d: ; BNE $da19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pda19
.pda0f: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda11: ; BEQ $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda4e
.pda13: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda15: ; CMP $2c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2c,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpda15
 ori.b #1,d7
.cmpda15:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pda17: ; BEQ $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda4e
.pda19: ; LDA #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d0
 move.b d0,d4
 bsr.l .nz
.pda1b: ; CMP $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpda1b
 ori.b #1,d7
.cmpda1b:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pda1d: ; BCS $da21
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pda21
.pda1f: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda21: ; JSR $db50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$da,d0
 bsr.l .push
 move.w #$23,d0
 bsr.l .push
 bra.l .pdb50
.pda24: ; BCC $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pda4e
.pda26: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda28: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pda29: ; ADC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pda2b: ; STA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda2d: ; PHP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d7,d0
 ori.b #$30,d0
 bsr.l .push
.pda2e: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda30: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .adc
.pda32: ; STA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda34: ; PLP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 ori.b #$30,d0
 move.b d0,d7
.pda35: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda37: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .adc
.pda39: ; STA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda3b: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pda3c: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pda3d: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda3f: ; BEQ $da47
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda47
.pda41: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda43: ; CMP $2c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2c,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpda43
 ori.b #1,d7
.cmpda43:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pda45: ; BNE $daaa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdaaa
.pda47: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pda49: ; STA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda4b: ; JMP $daaa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pdaaa
.pda4e: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pda4f: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pda50: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda52: ; CMP #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpda52
 ori.b #1,d7
.cmpda52:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pda54: ; BNE $da5c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pda5c
.pda56: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda58: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpda58
 ori.b #1,d7
.cmpda58:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pda5a: ; BCC $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pda4e
.pda5c: ; LDY $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pda5e: ; LDA ($34),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $35(a0),d1
 lsl.w #8,d1
 move.b $34(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda60: ; AND #$20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$20,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pda62: ; BEQ $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda4e
.pda64: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda66: ; BNE $da71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pda71
.pda68: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pda69: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda6b: ; BEQ $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda4e
.pda6d: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda6f: ; BEQ $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda4e
.pda71: ; JSR $db50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$da,d0
 bsr.l .push
 move.w #$73,d0
 bsr.l .push
 bra.l .pdb50
.pda74: ; BCC $da4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pda4e
.pda76: ; LDA #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d0
 move.b d0,d4
 bsr.l .nz
.pda78: ; CMP $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpda78
 ori.b #1,d7
.cmpda78:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pda7a: ; BCS $da7e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pda7e
.pda7c: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda7e: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda80: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pda81: ; SBC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pda83: ; STA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda85: ; PHP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d7,d0
 ori.b #$30,d0
 bsr.l .push
.pda86: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda88: ; SBC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .sbc
.pda8a: ; STA $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda8c: ; PLP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 ori.b #$30,d0
 move.b d0,d7
.pda8d: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda8f: ; SBC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .sbc
.pda91: ; STA $0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pda93: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pda94: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda96: ; BEQ $da9c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pda9c
.pda98: ; LDA $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pda9a: ; BPL $daa2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pdaa2
.pda9c: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pda9e: ; STA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdaa0: ; BEQ $daaa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdaaa
.pdaa2: ; LDA $0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0e,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdaa4: ; STA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdaa6: ; LDA $0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdaa8: ; STA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdaaa: ; JSR $db90
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$da,d0
 bsr.l .push
 move.w #$ac,d0
 bsr.l .push
 bra.l .pdb90
.pdaad: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdaae: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdaaf: ; LDA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdab1: ; BNE $dac4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdac4
.pdab3: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdab5: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdab6: ; ADC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pdab8: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pdab9: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdabb: ; BEQ $dac3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdac3
.pdabd: ; LDA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdabf: ; CMP $2d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2d,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdabf
 ori.b #1,d7
.cmpdabf:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdac1: ; BNE $dac4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdac4
.pdac3: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdac4: ; JSR $db6f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$da,d0
 bsr.l .push
 move.w #$c6,d0
 bsr.l .push
 bra.l .pdb6f
.pdac7: ; BCC $dac3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pdac3
.pdac9: ; LDA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdacb: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdacc: ; ADC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pdace: ; STA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdad0: ; CMP #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f0,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdad0
 ori.b #1,d7
.cmpdad0:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdad2: ; BCC $dafa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pdafa
.pdad4: ; ADC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0f,d0
 bsr.l .adc
.pdad6: ; STA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdad8: ; LDA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdada: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 bsr.l .adc
.pdadc: ; STA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdade: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdae0: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdae1: ; ADC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pdae3: ; STA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdae5: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdae6: ; ADC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pdae8: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pdae9: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdaeb: ; BEQ $daf6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdaf6
.pdaed: ; LDA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdaef: ; CMP $2d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2d,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdaef
 ori.b #1,d7
.cmpdaef:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdaf1: ; BEQ $daf6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdaf6
.pdaf3: ; JMP $db4d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pdb4d
.pdaf6: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pdaf8: ; STA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdafa: ; JMP $db4d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pdb4d
.pdafd: ; LDA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdaff: ; BNE $db11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdb11
.pdb01: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb03: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pdb04: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdb05: ; SBC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pdb07: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pdb08: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb0a: ; BEQ $db10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdb10
.pdb0c: ; LDA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb0e: ; BNE $db11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdb11
.pdb10: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdb11: ; JSR $db6f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$db,d0
 bsr.l .push
 move.w #$13,d0
 bsr.l .push
 bra.l .pdb6f
.pdb14: ; BCC $db10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pdb10
.pdb16: ; LDA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb18: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdb19: ; SBC $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pdb1b: ; STA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb1d: ; BCS $db4d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 bne.l .pdb4d
.pdb1f: ; SBC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0f,d0
 bsr.l .sbc
.pdb21: ; STA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb23: ; LDY $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pdb25: ; LDA ($34),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $35(a0),d1
 lsl.w #8,d1
 move.b $34(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb27: ; BMI $db3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 bne.l .pdb3f
.pdb29: ; LDA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb2b: ; SBC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 bsr.l .sbc
.pdb2d: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb2f: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb31: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdb32: ; SBC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pdb34: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb36: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pdb37: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb39: ; BEQ $db3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdb3f
.pdb3b: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb3d: ; BPL $db45
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pdb45
.pdb3f: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pdb41: ; STA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb43: ; BEQ $db4d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdb4d
.pdb45: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb47: ; STA $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb49: ; LDA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb4b: ; STA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb4d: ; JMP $dd1a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pdd1a
.pdb50: ; LDA $2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2b,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb52: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdb54: ; BNE $db69
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdb69
.pdb56: ; LDA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb58: ; BNE $db6b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdb6b
.pdb5a: ; LDA $20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$20,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb5c: ; STA $2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2b,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb5e: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdb60: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pdb61: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb63: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdb64: ; ADC $db6d,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$db6d,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pdb67: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb69: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdb6a: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdb6b: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdb6c: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdb6f: ; LDA $2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2b,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb71: ; AND #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdb73: ; BNE $db8c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdb8c
.pdb75: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb77: ; BNE $db8e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdb8e
.pdb79: ; LDA $22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$22,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb7b: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdb7c: ; ADC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pdb7e: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb80: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pdb82: ; STA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb84: ; STA $29
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$29,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb86: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.l .nz
.pdb88: ; STA $21
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$21,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb8a: ; STA $2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2b,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb8c: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdb8d: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdb8e: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdb8f: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdb90: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdb92: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdb93: ; SBC $28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$28,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pdb95: ; BPL $db9c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pdb9c
.pdb97: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdb99: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdb9a: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 bsr.l .adc
.pdb9c: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdb9e: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdba0: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdba2: ; BNE $dbb1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdbb1
.pdba4: ; LDA $28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$28,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdba6: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdba8: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdba9: ; ADC $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pdbab: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdbab
 ori.b #1,d7
.shiftdbab:
 lsr.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdbac: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdbae: ; BNE $dbc0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdbc0
.pdbb0: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdbb1: ; LDA $28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$28,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdbb3: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdbb5: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdbb7: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdbb8: ; ADC $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pdbba: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdbba
 ori.b #1,d7
.shiftdbba:
 lsr.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdbbb: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdbbd: ; BNE $dbc0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdbc0
.pdbbf: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdbc0: ; LDA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdbc2: ; STA $1f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$1f,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdbc4: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdbc6: ; CMP $20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$20,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdbc6
 ori.b #1,d7
.cmpdbc6:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdbc8: ; STA $20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$20,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdbca: ; BEQ $dbec
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdbec
.pdbcc: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdbce: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pdbcf: ; LDA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdbd1: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pdbd2: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdbd4: ; STA $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdbd6: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pdbd7: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdbd8: ; ADC $dd0a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$dd0a,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pdbdb: ; STA $25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$25,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdbdd: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdbdf: ; CMP $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdbdf
 ori.b #1,d7
.cmpdbdf:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdbe1: ; BEQ $dbe4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdbe4
.pdbe3: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.l .nz
.pdbe4: ; LDA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdbe6: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdbe7: ; ADC $dd0e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$dd0e,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pdbea: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
 move.w #$dbec,(a1)
 bra.l .success
.pdd1a: ; LDA $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdd1c: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdd1d: ; SBC $29
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$29,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pdd1f: ; BPL $dd26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #7,d7
 beq.l .pdd26
.pdd21: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd23: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdd24: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 bsr.l .adc
.pdd26: ; AND #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd28: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdd28
 ori.b #1,d7
.shiftdd28:
 lsr.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd29: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdd29
 ori.b #1,d7
.shiftdd29:
 lsr.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd2a: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdd2a
 ori.b #1,d7
.shiftdd2a:
 lsr.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd2b: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd2d: ; BNE $dd30
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdd30
.pdd2f: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdd30: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdd32: ; CMP $21
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$21,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdd32
 ori.b #1,d7
.cmpdd32:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdd34: ; BEQ $dd53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdd53
.pdd36: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd38: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pdd39: ; LDA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdd3b: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdd3c: ; ADC $df62,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df62,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pdd3f: ; CMP #$1e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$1e,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdd3f
 ori.b #1,d7
.cmpdd3f:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdd41: ; BCC $dd4e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pdd4e
.pdd43: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdd44: ; ADC $df64,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df64,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pdd47: ; AND #$1f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$1f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd49: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pdd4a: ; JSR $de8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$dd,d0
 bsr.l .push
 move.w #$4c,d0
 bsr.l .push
 bra.l .pde8a
.pdd4d: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pdd4e: ; STA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd50: ; JSR $de8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$dd,d0
 bsr.l .push
 move.w #$52,d0
 bsr.l .push
 bra.l .pde8a
.pdd53: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.l .nz
.pdd55: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.l .write
.pdd57: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.l .nz
.pdd58: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdd59: ; ADC #$26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$26,d0
 bsr.l .adc
.pdd5b: ; STA $08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd5d: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdd5f: ; CMP $21
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$21,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdd5f
 ori.b #1,d7
.cmpdd5f:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdd61: ; STA $21
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$21,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd63: ; BEQ $dd69
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdd69
.pdd65: ; LDA #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d0
 move.b d0,d4
 bsr.l .nz
.pdd67: ; BNE $dd6b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdd6b
.pdd69: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd6b: ; STA $09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$09,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd6d: ; LDA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdd6f: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd71: ; ORA $09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$09,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd73: ; STA $09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$09,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd75: ; LDY $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pdd77: ; JSR $e06b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$dd,d0
 bsr.l .push
 move.w #$79,d0
 bsr.l .push
 move.w #$e06b,(a1)
 bra.l .success
.pdd7a: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pdd7c: ; LDA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdd7e: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 bsr.l .push
.pdd7f: ; AND #$1c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$1c,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd81: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdd81
 ori.b #1,d7
.shiftdd81:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd82: ; STA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd84: ; ORA #$c0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$c0,d0
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd86: ; STA $0384,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0384,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdd89: ; STA $0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd8b: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d4
 bsr.l .nz
.pdd8c: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdd8c
 ori.b #1,d7
.shiftdd8c:
 lsr.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd8d: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdd8d
 ori.b #1,d7
.shiftdd8d:
 lsr.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd8e: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pdd8f: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdd91: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd93: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdd93
 ori.b #1,d7
.shiftdd93:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd94: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdd94
 ori.b #1,d7
.shiftdd94:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdd95: ; ORA $e063,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$e063,d1
 add.w d5,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd98: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdd9b: ; STA $0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0b,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdd9d: ; ORA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdd9f: ; STA $0383,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0383,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdda2: ; LDA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdda4: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdda6: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdda6
 ori.b #1,d7
.shiftdda6:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdda7: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdda7
 ori.b #1,d7
.shiftdda7:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdda8: ; STA $07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pddaa: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftddaa
 ori.b #1,d7
.shiftddaa:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pddab: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftddab
 ori.b #1,d7
.shiftddab:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pddac: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftddac
 ori.b #1,d7
.shiftddac:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pddad: ; ORA $e05b,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$e05b,d1
 add.w d5,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pddb0: ; STA $0361,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0361,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pddb3: ; STA $0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0a,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pddb5: ; LDA #$1f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$1f,d0
 move.b d0,d4
 bsr.l .nz
.pddb7: ; STA $0362,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0362,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pddba: ; LDA #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d0
 move.b d0,d4
 bsr.l .nz
.pddbc: ; STA $0385,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0385,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pddbf: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pddc0: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pddc1: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pddc2: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.l .write
.pddc4: ; JSR $df8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$dd,d0
 bsr.l .push
 move.w #$c6,d0
 bsr.l .push
 move.w #$df8a,(a1)
 bra.l .success
.pddc7: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pddc9: ; LDX $07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pddcb: ; LDA $0140,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0140,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pddce: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pddd1: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pddd2: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.l .nz
.pddd3: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.l .nz
.pddd4: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pddd6: ; BNE $ddcb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pddcb
.pddd8: ; LDX $09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$09,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pddda: ; LDA $df6a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df6a,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdddd: ; BEQ $de30
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pde30
.pdddf: ; AND $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdde1: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdde3: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.l .write
.pdde5: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdde7: ; ROR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdde7
 ori.b #1,d7
.shiftdde7:
 lsr.b #1,d0
 btst #0,d2
 beq.s .rotatedde7
 ori.b #128,d0
.rotatedde7:
 move.b d0,d4
 bsr.l .nz
.pdde8: ; ROR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdde8
 ori.b #1,d7
.shiftdde8:
 lsr.b #1,d0
 btst #0,d2
 beq.s .rotatedde8
 ori.b #128,d0
.rotatedde8:
 move.b d0,d4
 bsr.l .nz
.pdde9: ; ROR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #0,d0
 beq.s .shiftdde9
 ori.b #1,d7
.shiftdde9:
 lsr.b #1,d0
 btst #0,d2
 beq.s .rotatedde9
 ori.b #128,d0
.rotatedde9:
 move.b d0,d4
 bsr.l .nz
.pddea: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pddec: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdded: ; ADC $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pddef: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pddf0: ; LDA $0780,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0780,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pddf3: ; AND $df76,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df76,d1
 add.w d5,d1
 bsr.l .read
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pddf6: ; ORA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pddf8: ; STA $0780,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0780,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pddfb: ; LDX $08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pddfd: ; STA $0360,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0360,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pde00: ; INC $08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d1
 andi.w #$ff,d1
 bsr.l .read
 addq.b #1,d0
 bsr.l .write
 bsr.l .nz
.pde02: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.l .nz
.pde03: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftde03
 ori.b #1,d7
.shiftde03:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pde04: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pde05: ; LDA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde07: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde09: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pde0a: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde0c: ; AND $df72,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df72,d1
 add.w d5,d1
 bsr.l .read
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde0f: ; STA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pde11: ; LDA $0600,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0600,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde14: ; AND $df7e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df7e,d1
 add.w d5,d1
 bsr.l .read
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde17: ; ORA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde19: ; STA $0600,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0600,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pde1c: ; LDA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde1e: ; AND $df72,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df72,d1
 add.w d5,d1
 bsr.l .read
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde21: ; STA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pde23: ; LDA $0601,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0601,d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde26: ; AND $df7e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df7e,d1
 add.w d5,d1
 bsr.l .read
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde29: ; ORA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde2b: ; STA $0601,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0601,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pde2e: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pde30: ; LDA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde32: ; AND #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde34: ; CMP #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpde34
 ori.b #1,d7
.cmpde34:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pde36: ; BEQ $de3c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pde3c
.pde38: ; INC $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.l .read
 addq.b #1,d0
 bsr.l .write
 bsr.l .nz
.pde3a: ; BNE $ddc2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pddc2
.pde3c: ; LDX $09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$09,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pde3e: ; LDA $df6a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df6a,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde41: ; BEQ $de48
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pde48
.pde43: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.l .nz
.pde44: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pde45: ; ADC #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0b,d0
 bsr.l .adc
.pde47: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pde48: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.l .write
.pde4a: ; JSR $dea8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$de,d0
 bsr.l .push
 move.w #$4c,d0
 bsr.l .push
 bra.l .pdea8
.pde4d: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pde4f: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde51: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde53: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pde54: ; LDA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde56: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pde57: ; ADC $df62,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df62,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pde5a: ; CMP #$1e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$1e,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpde5a
 ori.b #1,d7
.cmpde5a:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pde5c: ; BCC $de64
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pde64
.pde5e: ; JSR $de8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$de,d0
 bsr.l .push
 move.w #$60,d0
 bsr.l .push
 bra.l .pde8a
.pde61: ; LDA $df63,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df63,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde64: ; STA $2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2a,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pde66: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde68: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde6a: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pde6b: ; LDA $29
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$29,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde6d: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pde6e: ; ADC $df82,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df82,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pde71: ; CMP #$f0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f0,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpde71
 ori.b #1,d7
.cmpde71:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pde73: ; BCC $de79
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #0,d7
 beq.l .pde79
.pde75: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pde76: ; ADC $df83,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df83,d1
 add.w d5,d1
 bsr.l .read
 bsr.l .adc
.pde79: ; STA $29
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$29,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pde7b: ; DEC $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 bsr.l .read
 subq.b #1,d0
 bsr.l .write
 bsr.l .nz
.pde7d: ; BEQ $de82
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pde82
.pde7f: ; JMP $dd55
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pdd55
.pde82: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.l .nz
.pde84: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pde87: ; STA $19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$19,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pde89: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pde8a: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde8c: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pde8e: ; BNE $dea0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdea0
.pde90: ; LDA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pde92: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pde93: ; ADC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .adc
.pde95: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pde97: ; CMP #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$05,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpde97
 ori.b #1,d7
.cmpde97:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pde99: ; BNE $de9f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pde9f
.pde9b: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pde9d: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pde9f: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdea0: ; LDA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdea2: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 ori.b #1,d7
.pdea3: ; SBC $2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2e,d1
 andi.w #$ff,d1
 bsr.l .read
 bsr.l .sbc
.pdea5: ; STA $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdea7: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdea8: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdeaa: ; BEQ $deb9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdeb9
.pdeac: ; CMP $2c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$2c,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpdeac
 ori.b #1,d7
.cmpdeac:
 sub.b d0,d2
 move.b d2,d0
 bsr.l .nz
.pdeae: ; BEQ $deee
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 bne.l .pdeee
.pdeb0: ; JSR $deb9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$de,d0
 bsr.l .push
 move.w #$b2,d0
 bsr.l .push
 bra.l .pdeb9
.pdeb3: ; BNE $deb8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdeb8
.pdeb5: ; JSR $deee
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$de,d0
 bsr.l .push
 move.w #$b7,d0
 bsr.l .push
 bra.l .pdeee
.pdeb8: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdeb9: ; LDY $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pdebb: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pdebc: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdebe: ; BNE $dec1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdec1
.pdec0: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdec1: ; LDA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdec3: ; AND #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f8,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdec5: ; STA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdec7: ; JSR $e06b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$de,d0
 bsr.l .push
 move.w #$c9,d0
 bsr.l .push
 move.w #$e06b,(a1)
 bra.l .success
.pdeca: ; JSR $df8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$de,d0
 bsr.l .push
 move.w #$cc,d0
 bsr.l .push
 move.w #$df8a,(a1)
 bra.l .success
.pdecd: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pdecf: ; LDX $07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pded1: ; LDA $0140,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0140,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pded4: ; STA $0363,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0363,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pded7: ; LDA $0141,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0141,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdeda: ; STA $0364,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0364,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdedd: ; LDA $0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdedf: ; AND #$e0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$e0,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdee1: ; STA $0361,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0361,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdee4: ; LDA $0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdee6: ; AND #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f8,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdee8: ; STA $0366,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0366,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdeeb: ; JMP $df26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bra.l .pdf26
.pdeee: ; LDY $23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$23,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pdef0: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.l .nz
.pdef1: ; LDA ($32),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 moveq #0,d1
 move.b $33(a0),d1
 lsl.w #8,d1
 move.b $32(a0),d1
 add.w d6,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdef3: ; BNE $def6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 btst #1,d7
 beq.l .pdef6
.pdef5: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdef6: ; LDA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdef8: ; AND #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f8,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdefa: ; ORA #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d0
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdefc: ; STA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.l .write
.pdefe: ; JSR $e06b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df,d0
 bsr.l .push
 move.w #$00,d0
 bsr.l .push
 move.w #$e06b,(a1)
 bra.l .success
.pdf01: ; JSR $df8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$df,d0
 bsr.l .push
 move.w #$03,d0
 bsr.l .push
 move.w #$df8a,(a1)
 bra.l .success
.pdf04: ; LDY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d6
 bsr.l .nz
.pdf06: ; LDX $07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d5
 bsr.l .nz
.pdf08: ; LDA $0142,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0142,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf0b: ; STA $0363,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0363,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf0e: ; LDA $0143,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0143,d1
 add.w d5,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf11: ; STA $0364,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0364,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf14: ; LDA $0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0a,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf16: ; AND #$e0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$e0,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf18: ; ORA #$1e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$1e,d0
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf1a: ; STA $0361,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0361,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf1d: ; LDA $0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0c,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf1f: ; AND #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$f8,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf21: ; ORA #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$07,d0
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf23: ; STA $0366,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0366,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf26: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.l .nz
.pdf28: ; STA $0362,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0362,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf2b: ; LDA $0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0b,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf2d: ; EOR #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf2f: ; STA $0360,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0360,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf32: ; ORA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$03,d0
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf34: ; STA $0365,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0365,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf37: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf39: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdf39
 ori.b #1,d7
.shiftdf39:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdf3a: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdf3a
 ori.b #1,d7
.shiftdf3a:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdf3b: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdf3b
 ori.b #1,d7
.shiftdf3b:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdf3c: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdf3c
 ori.b #1,d7
.shiftdf3c:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdf3d: ; ORA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 bsr.l .read
 or.b d0,d4
 move.b d4,d0
 bsr.l .nz
.pdf3f: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pdf40: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf42: ; STA $0368,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0368,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf45: ; STA $0780,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0780,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pdf48: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.l .nz
.pdf49: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shiftdf49
 ori.b #1,d7
.shiftdf49:
 lsl.b #1,d0
 move.b d0,d4
 bsr.l .nz
.pdf4a: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.l .nz
.pdf4b: ; LDA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf4d: ; STA $0600,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0600,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pdf50: ; LDA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.l .read
 move.b d0,d4
 bsr.l .nz
.pdf52: ; STA $0601,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0601,d1
 add.w d5,d1
 move.b d4,d0
 bsr.l .write
.pdf55: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.l .nz
.pdf57: ; STA $0367,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$0367,d1
 add.w d6,d1
 move.b d4,d0
 bsr.l .write
.pdf5a: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.l .nz
.pdf5b: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 andi.b #$fe,d7
.pdf5c: ; ADC #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$09,d0
 bsr.l .adc
.pdf5e: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.l .nz
.pdf5f: ; STY $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.l .write
.pdf61: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.l .budget_failure
 bsr.l .pop
 move.b d0,d2
 bsr.l .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$d6df,d0
 beq.l .pd6df
 cmpi.w #$d710,d0
 beq.l .pd710
 cmpi.w #$d885,d0
 beq.l .pd885
 cmpi.w #$d891,d0
 beq.l .pd891
 cmpi.w #$d8ab,d0
 beq.l .pd8ab
 cmpi.w #$d8b7,d0
 beq.l .pd8b7
 cmpi.w #$d8c9,d0
 beq.l .pd8c9
 cmpi.w #$d8d7,d0
 beq.l .pd8d7
 cmpi.w #$d904,d0
 beq.l .pd904
 cmpi.w #$d912,d0
 beq.l .pd912
 cmpi.w #$da24,d0
 beq.l .pda24
 cmpi.w #$da74,d0
 beq.l .pda74
 cmpi.w #$daad,d0
 beq.l .pdaad
 cmpi.w #$dac7,d0
 beq.l .pdac7
 cmpi.w #$db14,d0
 beq.l .pdb14
 cmpi.w #$dd4d,d0
 beq.l .pdd4d
 cmpi.w #$dd53,d0
 beq.l .pdd53
 cmpi.w #$dd7a,d0
 beq.l .pdd7a
 cmpi.w #$ddc7,d0
 beq.l .pddc7
 cmpi.w #$de4d,d0
 beq.l .pde4d
 cmpi.w #$de61,d0
 beq.l .pde61
 cmpi.w #$deb3,d0
 beq.l .pdeb3
 cmpi.w #$deb8,d0
 beq.l .pdeb8
 cmpi.w #$deca,d0
 beq.l .pdeca
 cmpi.w #$decd,d0
 beq.l .pdecd
 cmpi.w #$df01,d0
 beq.l .pdf01
 cmpi.w #$df04,d0
 beq.l .pdf04
 move.w d0,(a1)
 bra.l .success
.pdbec:
 move.w #$dbec,(a1)
 bra.l .success
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
 bhs.l .bad_read
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
 bcs.l .bad_read
 cmpi.w #15000,(a2)
 bhs.l .bad_read
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
 bra.l .nz
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
 bra.l .nz
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
