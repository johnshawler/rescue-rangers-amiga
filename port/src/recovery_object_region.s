; Static native translation of bounded bank5 object/sprite logic $8000-$81DF.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_object_region:
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
 bsr.w recovery_object_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_object_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_object_region_core:
 cmpi.w #$8000,(a1)
 bne.w .invalid
 cmpi.b #5,3(a4)
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 ; A top-level return into this routine would defeat the bounded contract.
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
 cmpi.w #$8000,d0
 bcs.s .return_valid
 cmpi.w #$81e0,d0
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
 movea.l #200000,a4
.p8000: ; INC $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p8002: ; LDA $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8004: ; LSR A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
 btst #0,d4
 beq.s .shift8004
 ori.b #1,d7
.shift8004:
 lsr.b #1,d4
 move.b d4,d0
 bsr.w .nz
.p8005: ; BCS $801c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p801c
.p8007: ; LDX #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d5
 bsr.w .nz
.p8009: ; STX $96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$96,d1
 andi.w #$ff,d1
 move.b d5,(a0,d1.w)
.p800b: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p800e: ; BPL $8013
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8013
.p8010: ; JSR $802f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$12,d0
 bsr.w .push
 bra.w .p802f
.p8013: ; INC $96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$96,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p8015: ; LDX $96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$96,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p8017: ; CPX #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8017
 ori.b #1,d7
.cmp8017:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8019: ; BNE $800b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p800b
.p801b: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p801c: ; LDX #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d0,d5
 bsr.w .nz
.p801e: ; STX $96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$96,d1
 andi.w #$ff,d1
 move.b d5,(a0,d1.w)
.p8020: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8023: ; BPL $8028
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8028
.p8025: ; JSR $802f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$27,d0
 bsr.w .push
 bra.w .p802f
.p8028: ; DEC $96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$96,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p802a: ; LDX $96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$96,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p802c: ; BPL $8020
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8020
.p802e: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p802f: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8032: ; AND #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8034: ; BNE $8039
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8039
.p8036: ; JMP $80ba
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p80ba
.p8039: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p803c: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p803d: ; SBC $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p803f: ; STA $0450,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0450,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p8042: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8045: ; SBC $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p8047: ; BNE $80a4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80a4
.p8049: ; LDA $0510,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p804c: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p804d: ; SBC $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p804f: ; BCS $8054
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p8054
.p8051: ; SBC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 bsr.w .sbc
.p8053: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.p8054: ; STA $0440,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0440,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p8057: ; LDA $0520,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0520,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p805a: ; SBC $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p805c: ; BEQ $80c6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80c6
.p805e: ; CPX #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp805e
 ori.b #1,d7
.cmp805e:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8060: ; BCS $807a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p807a
.p8062: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.p8063: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8066: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8068: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p806b: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.p806c: ; CMP #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp806c
 ori.b #1,d7
.cmp806c:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p806e: ; BNE $80d4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80d4
.p8070: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8072: ; STA $5e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8074: ; LDA #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d0,d4
 bsr.w .nz
.p8076: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8078: ; BNE $809e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p809e
.p807a: ; LDA $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p807d: ; ORA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8080: ; BEQ $80a3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80a3
.p8082: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8085: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8087: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p808a: ; LDA $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p808d: ; BEQ $80a3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80a3
.p808f: ; CMP #$4b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4b,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp808f
 ori.b #1,d7
.cmp808f:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8091: ; BEQ $80a3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80a3
.p8093: ; CMP #$60
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$60,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8093
 ori.b #1,d7
.cmp8093:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8095: ; BEQ $80a3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80a3
.p8097: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p809a: ; CMP #$25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp809a
 ori.b #1,d7
.cmp809a:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p809c: ; BEQ $80a3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80a3
.p809e: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p80a0: ; STA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p80a3: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p80a4: ; LDA $0450,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0450,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80a7: ; BCS $80ad
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p80ad
.p80a9: ; EOR #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80ab: ; ADC #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 bsr.w .adc
.p80ad: ; CMP #$60
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$60,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp80ad
 ori.b #1,d7
.cmp80ad:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p80af: ; BCS $807a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p807a
.p80b1: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80b4: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80b6: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p80b9: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p80ba: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80bd: ; STA $0450,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0450,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p80c0: ; LDA $0510,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80c3: ; STA $0440,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0440,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p80c6: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80c9: ; ORA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80cb: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p80ce: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80d1: ; BNE $80d4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80d4
.p80d3: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p80d4: ; CPX #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp80d4
 ori.b #1,d7
.cmp80d4:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p80d6: ; BCS $80e5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p80e5
.p80d8: ; LDA $5e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80da: ; BEQ $80e5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80e5
.p80dc: ; DEC $5e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p80de: ; LDA $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80e0: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80e2: ; BNE $80e5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80e5
.p80e4: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p80e5: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p80e7: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80ea: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80ec: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p80ee: ; BEQ $80f1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80f1
.p80f0: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p80f1: ; STY $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d6,(a0,d1.w)
.p80f3: ; LDY $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p80f6: ; LDA $b4b6,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b4b6,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80f9: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p80fb: ; LDA $b55f,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b55f,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80fe: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8100: ; LDA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8103: ; BMI $8129
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p8129
.p8105: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8107: ; INC $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p810a: ; LDY #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d6
 bsr.w .nz
.p810c: ; CMP ($00),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $01(a0),d1
 lsl.w #8,d1
 move.b $00(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp810c
 ori.b #1,d7
.cmp810c:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p810e: ; BNE $8129
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8129
.p8110: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8112: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p8115: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8116: ; LDA ($00),Y
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
.p8118: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p811a: ; CMP $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp811a
 ori.b #1,d7
.cmp811a:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p811d: ; PHP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d7,d0
 ori.b #$30,d0
 bsr.w .push
.p811e: ; INC $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b (a0,d1.w),d0
 addq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p8121: ; PLP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 ori.b #$30,d0
 move.b d0,d7
.p8122: ; BNE $8129
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8129
.p8124: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8126: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p8129: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p812c: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p812e: ; BNE $8135
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8135
.p8130: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8133: ; BMI $8136
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p8136
.p8135: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p8136: ; LDA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8139: ; AND #$7f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$7f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p813b: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.p813c: ; ADC #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 bsr.w .adc
.p813e: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d4,d0
 bsr.w .nz
.p813f: ; LDA ($00),Y
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
.p8141: ; STA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8143: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p8145: ; LDA ($00),Y
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
.p8147: ; BPL $8158
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8158
.p8149: ; LDY $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p814b: ; LDA $9c82,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9c82,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p814e: ; STA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8150: ; LDA $9dae,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9dae,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8153: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8155: ; JMP $8164
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p8164
.p8158: ; LDY $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p815a: ; LDA $9b82,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9b82,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p815d: ; STA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p815f: ; LDA $9cae,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9cae,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8162: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8164: ; LDA $0450,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0450,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8167: ; STA $13
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$13,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8169: ; LDA $0440,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0440,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p816c: ; STA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p816e: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p8170: ; LDA ($02),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $03(a0),d1
 lsl.w #8,d1
 move.b $02(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8172: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8174: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8175: ; LDA ($02),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $03(a0),d1
 lsl.w #8,d1
 move.b $02(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8177: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.p8178: ; ADC $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .adc
.p817a: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.p817b: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p817e: ; AND #$20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$20,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8180: ; STA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8182: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.p8183: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d4,d0
 bsr.w .nz
.p8184: ; LDA $b08e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b08e,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8187: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p8188: ; SBC #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 bsr.w .sbc
.p818a: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p818c: ; LDA $b145,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$b145,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p818f: ; SBC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 bsr.w .sbc
.p8191: ; STA $06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d1
 andi.w #$ff,d1
 move.b d4,(a0,d1.w)
.p8193: ; LDX $97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p8195: ; BEQ $81d7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p81d7
.p8197: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8198: ; LDA ($02),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $03(a0),d1
 lsl.w #8,d1
 move.b $02(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p819a: ; STA $0201,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0201,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p819d: ; LDA $12
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$12,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p819f: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.p81a0: ; ADC ($05),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $06(a0),d1
 lsl.w #8,d1
 move.b $05(a0),d1
 add.w d6,d1
 bsr.w .read
 bsr.w .adc
.p81a2: ; STA $0200,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p81a5: ; LDA ($05),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $06(a0),d1
 lsl.w #8,d1
 move.b $05(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81a7: ; BMI $81ad
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p81ad
.p81a9: ; BCC $81af
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p81af
.p81ab: ; BCS $81d8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p81d8
.p81ad: ; BCC $81d8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p81d8
.p81af: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p81b0: ; LDA ($02),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $03(a0),d1
 lsl.w #8,d1
 move.b $02(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81b2: ; EOR $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p81b4: ; ORA $11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p81b6: ; STA $0202,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0202,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p81b9: ; LDA $13
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$13,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81bb: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.p81bc: ; ADC ($05),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $06(a0),d1
 lsl.w #8,d1
 move.b $05(a0),d1
 add.w d6,d1
 bsr.w .read
 bsr.w .adc
.p81be: ; STA $0203,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0203,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p81c1: ; LDA ($05),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $06(a0),d1
 lsl.w #8,d1
 move.b $05(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81c3: ; BMI $81c9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p81c9
.p81c5: ; BCC $81cb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p81cb
.p81c7: ; BCS $81d9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p81d9
.p81c9: ; BCC $81d9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p81d9
.p81cb: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p81cc: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p81cd: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p81ce: ; INX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p81cf: ; STX $97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d1
 andi.w #$ff,d1
 move.b d5,(a0,d1.w)
.p81d1: ; BEQ $81d7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p81d7
.p81d3: ; DEC $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b (a0,d1.w),d0
 subq.b #1,d0
 move.b d0,(a0,d1.w)
 bsr.w .nz
.p81d5: ; BPL $8197
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8197
.p81d7: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$8013,d0
 beq.w .p8013
 cmpi.w #$8028,d0
 beq.w .p8028
 move.w d0,(a1)
 bra.w .success
.p81d8: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p81d9: ; LDA #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f8,d0
 move.b d0,d4
 bsr.w .nz
.p81db: ; STA $0200,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d5,d1
 move.b d4,(a0,d1.w)
.p81de: ; BNE $81d3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p81d3
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
 addi.l #$c000,d2
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
