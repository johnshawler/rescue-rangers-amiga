; Static native translation of bank-4 object-window initialization and spawning.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_stage_object_region:
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
 bsr.w recovery_stage_object_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_stage_object_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_stage_object_region_core:
 cmpi.b #4,3(a4)
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
 movea.l #20000,a4
 cmpi.w #$8040,(a1)
 beq.w .p8040
 cmpi.w #$8090,(a1)
 beq.w .p8090
 bra.w .budget_failure
.p8040: ; LDY $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p8042: ; LDA ($7c),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $7d(a0),d1
 lsl.w #8,d1
 move.b $7c(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8044: ; BMI $8083
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p8083
.p8046: ; BNE $8060
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8060
.p8048: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p804a: ; LDA ($78),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $79(a0),d1
 lsl.w #8,d1
 move.b $78(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p804c: ; CMP $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp804c
 ori.b #1,d7
.cmp804c:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p804e: ; BNE $805b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p805b
.p8050: ; LDA ($72),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $73(a0),d1
 lsl.w #8,d1
 move.b $72(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8052: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p8053: ; SBC $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p8055: ; LDA ($74),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $75(a0),d1
 lsl.w #8,d1
 move.b $74(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8057: ; SBC $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p8059: ; BCS $8083
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p8083
.p805b: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p805c: ; BNE $804a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p804a
.p805e: ; BEQ $8083
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8083
.p8060: ; LDA $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8062: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.p8063: ; ADC #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 bsr.w .adc
.p8065: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p8067: ; LDA $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8069: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 bsr.w .adc
.p806b: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p806d: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p806f: ; LDA ($78),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $79(a0),d1
 lsl.w #8,d1
 move.b $78(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8071: ; CMP $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8071
 ori.b #1,d7
.cmp8071:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8073: ; BNE $8080
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8080
.p8075: ; LDA ($72),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $73(a0),d1
 lsl.w #8,d1
 move.b $72(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8077: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p8078: ; SBC $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p807a: ; LDA ($74),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $75(a0),d1
 lsl.w #8,d1
 move.b $74(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p807c: ; SBC $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p807e: ; BCC $8083
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p8083
.p8080: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8081: ; BNE $806f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p806f
.p8083: ; STY $70
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$70,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.p8085: ; STY $71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$71,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.p8087: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80a9,d0
 beq.w .p80a9
 cmpi.w #$80ae,d0
 beq.w .p80ae
 cmpi.w #$80b8,d0
 beq.w .p80b8
 cmpi.w #$80c2,d0
 beq.w .p80c2
 cmpi.w #$80c7,d0
 beq.w .p80c7
 cmpi.w #$80d3,d0
 beq.w .p80d3
 cmpi.w #$8192,d0
 beq.w .p8192
 move.w d0,(a1)
 bra.w .success
.p8090: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8092: ; AND #$0b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0b,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8094: ; BEQ $80bc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80bc
.p8096: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8098: ; BNE $80bd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80bd
.p809a: ; LDY $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p809c: ; LDA $2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2f,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p809e: ; EOR ($7c),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $7d(a0),d1
 lsl.w #8,d1
 move.b $7c(a0),d1
 add.w d6,d1
 bsr.w .read
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80a0: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p80a2: ; BNE $80bd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80bd
.p80a4: ; LDY $71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$71,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p80a6: ; JSR $80d8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$a8,d0
 bsr.w .push
 bra.w .p80d8
.p80a9: ; BNE $80b2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80b2
.p80ab: ; JSR $80fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$ad,d0
 bsr.w .push
 bra.w .p80fa
.p80ae: ; DEC $71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$71,d1
 andi.w #$ff,d1
 bsr.w .read
 subq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p80b0: ; BNE $80a4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80a4
.p80b2: ; LDY $71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$71,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p80b4: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p80b5: ; JSR $80d8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$b7,d0
 bsr.w .push
 bra.w .p80d8
.p80b8: ; BEQ $80b4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80b4
.p80ba: ; STY $70
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$70,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.p80bc: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80a9,d0
 beq.w .p80a9
 cmpi.w #$80ae,d0
 beq.w .p80ae
 cmpi.w #$80b8,d0
 beq.w .p80b8
 cmpi.w #$80c2,d0
 beq.w .p80c2
 cmpi.w #$80c7,d0
 beq.w .p80c7
 cmpi.w #$80d3,d0
 beq.w .p80d3
 cmpi.w #$8192,d0
 beq.w .p8192
 move.w d0,(a1)
 bra.w .success
.p80bd: ; LDY $70
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$70,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p80bf: ; JSR $80d8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$c1,d0
 bsr.w .push
 bra.w .p80d8
.p80c2: ; BNE $80cb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80cb
.p80c4: ; JSR $80fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$c6,d0
 bsr.w .push
 bra.w .p80fa
.p80c7: ; INC $70
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$70,d1
 andi.w #$ff,d1
 bsr.w .read
 addq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p80c9: ; BNE $80bd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80bd
.p80cb: ; LDY $70
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$70,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p80cd: ; BEQ $80d5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80d5
.p80cf: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p80d0: ; JSR $80d8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$d2,d0
 bsr.w .push
 bra.w .p80d8
.p80d3: ; BEQ $80cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p80cf
.p80d5: ; STY $71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$71,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.p80d7: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80a9,d0
 beq.w .p80a9
 cmpi.w #$80ae,d0
 beq.w .p80ae
 cmpi.w #$80b8,d0
 beq.w .p80b8
 cmpi.w #$80c2,d0
 beq.w .p80c2
 cmpi.w #$80c7,d0
 beq.w .p80c7
 cmpi.w #$80d3,d0
 beq.w .p80d3
 cmpi.w #$8192,d0
 beq.w .p8192
 move.w d0,(a1)
 bra.w .success
.p80d8: ; LDA ($72),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $73(a0),d1
 lsl.w #8,d1
 move.b $72(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80da: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p80dc: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p80dd: ; SBC $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p80df: ; LDA ($74),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $75(a0),d1
 lsl.w #8,d1
 move.b $74(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80e1: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p80e3: ; SBC $fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fd,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p80e5: ; BNE $80f9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80f9
.p80e7: ; LDA ($76),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $77(a0),d1
 lsl.w #8,d1
 move.b $76(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80e9: ; STA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p80eb: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p80ec: ; SBC $fa
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fa,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p80ee: ; BCS $80f3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p80f3
.p80f0: ; SBC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 bsr.w .sbc
.p80f2: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.p80f3: ; LDA ($78),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $79(a0),d1
 lsl.w #8,d1
 move.b $78(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p80f5: ; STA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p80f7: ; SBC $fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fb,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.p80f9: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80a9,d0
 beq.w .p80a9
 cmpi.w #$80ae,d0
 beq.w .p80ae
 cmpi.w #$80b8,d0
 beq.w .p80b8
 cmpi.w #$80c2,d0
 beq.w .p80c2
 cmpi.w #$80c7,d0
 beq.w .p80c7
 cmpi.w #$80d3,d0
 beq.w .p80d3
 cmpi.w #$8192,d0
 beq.w .p8192
 move.w d0,(a1)
 bra.w .success
.p80fa: ; LDX #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d0,d5
 bsr.w .nz
.p80fc: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.p80fd: ; CMP $0590,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0590,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp80fd
 ori.b #1,d7
.cmp80fd:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8100: ; BEQ $8109
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8109
.p8102: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p8103: ; CPX #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8103
 ori.b #1,d7
.cmp8103:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8105: ; BNE $80fd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p80fd
.p8107: ; BEQ $810e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p810e
.p8109: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p810c: ; BMI $80f9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .p80f9
.p810e: ; LDA ($7a),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $7b(a0),d1
 lsl.w #8,d1
 move.b $7a(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8110: ; CMP #$53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$53,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8110
 ori.b #1,d7
.cmp8110:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8112: ; BNE $8118
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8118
.p8114: ; LDX #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d5
 bsr.w .nz
.p8116: ; BNE $8125
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8125
.p8118: ; LDX #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d0,d5
 bsr.w .nz
.p811a: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p811d: ; BPL $8125
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8125
.p811f: ; DEX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d5
 move.b d5,d0
 bsr.w .nz
.p8120: ; CPX #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8120
 ori.b #1,d7
.cmp8120:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8122: ; BNE $811a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p811a
.p8124: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80a9,d0
 beq.w .p80a9
 cmpi.w #$80ae,d0
 beq.w .p80ae
 cmpi.w #$80b8,d0
 beq.w .p80b8
 cmpi.w #$80c2,d0
 beq.w .p80c2
 cmpi.w #$80c7,d0
 beq.w .p80c7
 cmpi.w #$80d3,d0
 beq.w .p80d3
 cmpi.w #$8192,d0
 beq.w .p8192
 move.w d0,(a1)
 bra.w .success
.p8125: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.p8126: ; STA $0590,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0590,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8129: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p812b: ; STA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p812e: ; LDA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8130: ; STA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8133: ; LDA $02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8135: ; STA $0510,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8138: ; LDA $03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p813a: ; STA $0520,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0520,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p813d: ; LDA #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d0,d4
 bsr.w .nz
.p813f: ; STA $04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p8141: ; LDA #$90
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$90,d0
 move.b d0,d4
 bsr.w .nz
.p8143: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p8145: ; LDA ($7a),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $7b(a0),d1
 lsl.w #8,d1
 move.b $7a(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8147: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shift8147
 ori.b #1,d7
.shift8147:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.p8148: ; ASL A
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 move.b d7,d2
 andi.b #$fe,d7
 btst #7,d0
 beq.s .shift8148
 ori.b #1,d7
.shift8148:
 lsl.b #1,d0
 move.b d0,d4
 bsr.w .nz
.p8149: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.w .nz
.p814a: ; LDA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p814c: ; ADC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 bsr.w .adc
.p814e: ; STA $05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p8150: ; LDA ($04),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $05(a0),d1
 lsl.w #8,d1
 move.b $04(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8152: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.p8153: ; AND #$bf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$bf,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8155: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8158: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.p8159: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p815b: ; ORA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p815d: ; STA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8160: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8161: ; LDA ($04),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $05(a0),d1
 lsl.w #8,d1
 move.b $04(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8163: ; STA $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8166: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8167: ; LDA ($04),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $05(a0),d1
 lsl.w #8,d1
 move.b $04(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8169: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p816c: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p816d: ; LDA ($04),Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 moveq #0,d1
 move.b $05(a0),d1
 lsl.w #8,d1
 move.b $04(a0),d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p816f: ; STA $0570,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0570,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8172: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8174: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8177: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p817a: ; STA $0460,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0460,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p817d: ; STA $0470,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0470,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8180: ; STA $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8183: ; STA $0490,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0490,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8186: ; STA $04a0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04a0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8189: ; STA $04b0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04b0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p818c: ; STA $04c0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04c0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p818f: ; JSR $f31d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$81,d0
 bsr.w .push
 move.w #$91,d0
 bsr.w .push
 bra.w .pf31d
.p8192: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80a9,d0
 beq.w .p80a9
 cmpi.w #$80ae,d0
 beq.w .p80ae
 cmpi.w #$80b8,d0
 beq.w .p80b8
 cmpi.w #$80c2,d0
 beq.w .p80c2
 cmpi.w #$80c7,d0
 beq.w .p80c7
 cmpi.w #$80d3,d0
 beq.w .p80d3
 cmpi.w #$8192,d0
 beq.w .p8192
 move.w d0,(a1)
 bra.w .success
.pf31d: ; LDA #$ab
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ab,d0
 move.b d0,d4
 bsr.w .nz
.pf31f: ; STA $0550,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pf322: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.pf324: ; STA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pf327: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$80a9,d0
 beq.w .p80a9
 cmpi.w #$80ae,d0
 beq.w .p80ae
 cmpi.w #$80b8,d0
 beq.w .p80b8
 cmpi.w #$80c2,d0
 beq.w .p80c2
 cmpi.w #$80c7,d0
 beq.w .p80c7
 cmpi.w #$80d3,d0
 beq.w .p80d3
 cmpi.w #$8192,d0
 beq.w .p8192
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
