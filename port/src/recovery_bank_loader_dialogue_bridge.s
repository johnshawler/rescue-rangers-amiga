; Static native translation of bounded bank2 interstitial return and fixed-bank stage-entry setup.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_bank_loader_dialogue_bridge:
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
 bsr.w recovery_bank_loader_dialogue_bridge_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_bank_loader_dialogue_bridge_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_bank_loader_dialogue_bridge_core:
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
 cmpi.w #$911c,(a1)
 beq.w .p911c
 cmpi.w #$911f,(a1)
 beq.w .p911f
 cmpi.w #$c60a,(a1)
 beq.w .pc60a
 bra.w .budget_failure
.p8d16: ; LDX #$27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d0
 move.b d0,d5
 bsr.w .nz
.p8d18: ; LDA $0100,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0100,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8d1b: ; STA $0200,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p8d1e: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p8d1f: ; BPL $8d18
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8d18
.p8d21: ; LDA #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d0,d4
 bsr.w .nz
.p8d23: ; STA $97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8d25: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$9122,d0
 beq.w .p9122
 cmpi.w #$c611,d0
 beq.w .pc611
 cmpi.w #$c614,d0
 beq.w .pc614
 move.w d0,(a1)
 bra.w .success
.p911c: ; JSR $92ac
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$91,d0
 bsr.w .push
 move.w #$1e,d0
 bsr.w .push
 move.w #$92ac,(a1)
 bra.w .success
.p911f: ; JSR $8d16
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$91,d0
 bsr.w .push
 move.w #$21,d0
 bsr.w .push
 bra.w .p8d16
.p9122: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.p9123: ; STA $04d1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d1,d1
 move.b d4,(a0,d1.w)
.p9126: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.p9127: ; STA $04d0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 move.b d4,(a0,d1.w)
.p912a: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$9122,d0
 beq.w .p9122
 cmpi.w #$c611,d0
 beq.w .pc611
 cmpi.w #$c614,d0
 beq.w .pc614
 move.w d0,(a1)
 bra.w .success
.pc60a: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc60c: ; STA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.pc60e: ; JSR $c63b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c6,d0
 bsr.w .push
 move.w #$10,d0
 bsr.w .push
 bra.w .pc63b
.pc611: ; JSR $c645
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c6,d0
 bsr.w .push
 move.w #$13,d0
 bsr.w .push
 bra.w .pc645
.pc614: ; JSR $c6b5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c6,d0
 bsr.w .push
 move.w #$16,d0
 bsr.w .push
 move.w #$c6b5,(a1)
 bra.w .success
.pc63b: ; LDX #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d5
 bsr.w .nz
.pc63d: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc63f: ; STA $e8,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e8,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.pc641: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc642: ; BPL $c63f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pc63f
.pc644: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$9122,d0
 beq.w .p9122
 cmpi.w #$c611,d0
 beq.w .pc611
 cmpi.w #$c614,d0
 beq.w .pc614
 move.w d0,(a1)
 bra.w .success
.pc645: ; LDA $0204
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0204,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc648: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pc649: ; LDA $0218
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0218,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc64c: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pc64d: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.pc64f: ; LDA $c717,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c717,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc652: ; STA $0200,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.pc655: ; LDA $c718,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c718,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc658: ; STA $0201,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0201,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.pc65b: ; LDA $c719,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c719,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc65e: ; STA $0202,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0202,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.pc661: ; LDA $c71a,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c71a,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc664: ; STA $0203,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0203,d1
 add.w d6,d1
 move.b d4,(a0,d1.w)
.pc667: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc668: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc669: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc66a: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pc66b: ; CPY #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc66b
 ori.b #1,d7
.cmpc66b:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc66d: ; BNE $c64f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc64f
.pc66f: ; STY $97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d1
 andi.w #$ff,d1
 move.b d6,(a0,d1.w)
.pc671: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pc672: ; STA $0218
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0218,d1
 move.b d4,(a0,d1.w)
.pc675: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pc676: ; STA $0204
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0204,d1
 move.b d4,(a0,d1.w)
.pc679: ; LDX $50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$50,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pc67b: ; BNE $c699
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc699
.pc67d: ; LDX #$14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d0
 move.b d0,d5
 bsr.w .nz
.pc67f: ; LDA #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f8,d0
 move.b d0,d4
 bsr.w .nz
.pc681: ; STA $0200,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.pc684: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc685: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc686: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc687: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc688: ; CPX #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc688
 ori.b #1,d7
.cmpc688:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc68a: ; BNE $c681
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc681
.pc68c: ; LDA $05a2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05a2,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc68f: ; CMP #$8d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8d,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc68f
 ori.b #1,d7
.cmpc68f:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc691: ; BNE $c698
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc698
.pc693: ; LDA #$2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2a,d0
 move.b d0,d4
 bsr.w .nz
.pc695: ; STA $0201
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0201,d1
 move.b d4,(a0,d1.w)
.pc698: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$9122,d0
 beq.w .p9122
 cmpi.w #$c611,d0
 beq.w .pc611
 cmpi.w #$c614,d0
 beq.w .pc614
 move.w d0,(a1)
 bra.w .success
.pc699: ; LDA $55
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$55,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc69b: ; CMP #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc69b
 ori.b #1,d7
.cmpc69b:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc69d: ; BEQ $c67d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc67d
.pc69f: ; LDA $54
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc6a1: ; CMP #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc6a1
 ori.b #1,d7
.cmpc6a1:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc6a3: ; BNE $c6b4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc6b4
.pc6a5: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.pc6a7: ; LDA #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f8,d0
 move.b d0,d4
 bsr.w .nz
.pc6a9: ; STA $0200,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.pc6ac: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc6ad: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc6ae: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc6af: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.pc6b0: ; CPX #$14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc6b0
 ori.b #1,d7
.cmpc6b0:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc6b2: ; BNE $c6a9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc6a9
.pc6b4: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$9122,d0
 beq.w .p9122
 cmpi.w #$c611,d0
 beq.w .pc611
 cmpi.w #$c614,d0
 beq.w .pc614
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
