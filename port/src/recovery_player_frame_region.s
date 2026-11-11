; Static native translation of bank-6 live frame dispatcher and collision response.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_player_frame_region:
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
 bsr.w recovery_player_frame_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_player_frame_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_player_frame_region_core:
 cmpi.b #6,3(a4)
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
 cmpi.w #$8000,(a1)
 beq.w .p8000
 cmpi.w #$801f,(a1)
 beq.w .p801f
 cmpi.w #$8029,(a1)
 beq.w .p8029
 cmpi.w #$8033,(a1)
 beq.w .p8033
 cmpi.w #$8050,(a1)
 beq.w .p8050
 cmpi.w #$8e15,(a1)
 beq.w .p8e15
 cmpi.w #$8e18,(a1)
 beq.w .p8e18
 cmpi.w #$8e1a,(a1)
 beq.w .p8e1a
 cmpi.w #$8e32,(a1)
 beq.w .p8e32
 cmpi.w #$81bc,(a1)
 beq.w .p81bc
 cmpi.w #$8bc8,(a1)
 beq.w .p8bc8
 cmpi.w #$8bd6,(a1)
 beq.w .p8bd6
 cmpi.w #$8c22,(a1)
 beq.w .p8c22
 cmpi.w #$8f38,(a1)
 beq.w .p8f38
 cmpi.w #$8f4c,(a1)
 beq.w .p8f4c
 cmpi.w #$8f7c,(a1)
 beq.w .p8f7c
 cmpi.w #$8f83,(a1)
 beq.w .p8f83
 cmpi.w #$8f92,(a1)
 beq.w .p8f92
 cmpi.w #$8f9a,(a1)
 beq.w .p8f9a
 bra.w .budget_failure
.p8000: ; LDX #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d5
 bsr.w .nz
.p8002: ; STX $4d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4d,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .write
.p8004: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8007: ; BPL $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8082
.p8009: ; LDY $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.p800c: ; LDA $80a7,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80a7,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p800f: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p8011: ; LDA $810c,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$810c,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8014: ; STA $01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.p8016: ; LDA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 move.b d0,d4
 bsr.w .nz
.p8018: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.p8019: ; LDA #$1e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1e,d0
 move.b d0,d4
 bsr.w .nz
.p801b: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.p801c: ; JMP ($0000)
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0000,d1
 bsr.w .read
 move.b d0,d3
 move.w #$0001,d1
 bsr.w .read
 lsl.w #8,d0
 move.b d3,d0
 move.w d0,(a1)
 bra.w .success
.p801f: ; LDA $0570,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0570,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8022: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8024: ; BEQ $8029
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8029
.p8026: ; JSR $8e15
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$28,d0
 bsr.w .push
 bra.w .p8e15
.p8029: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p802c: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p802e: ; BEQ $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8082
.p8030: ; JSR $f92b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$32,d0
 bsr.w .push
 move.w #$f92b,(a1)
 bra.w .success
.p8033: ; BCS $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p8082
.p8035: ; LDA $005e,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$005e,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8038: ; BNE $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8082
.p803a: ; LDA $0054,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0054,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p803d: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp803d
 ori.b #1,d7
.cmp803d:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p803f: ; BCS $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p8082
.p8041: ; LDA $0420,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8044: ; BEQ $804d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p804d
.p8046: ; LDA #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 move.b d0,d4
 bsr.w .nz
.p8048: ; STA $0054,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0054,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p804b: ; BNE $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8082
.p804d: ; JSR $808e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 bsr.w .push
 move.w #$4f,d0
 bsr.w .push
 bra.w .p808e
.p8050: ; LDA $0056,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0056,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8053: ; BPL $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8082
.p8055: ; AND #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8057: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.p8058: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p805a: ; STA $0056,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0056,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p805d: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.p805e: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.w .nz
.p805f: ; LDA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 move.b d0,d4
 bsr.w .nz
.p8061: ; STA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8064: ; LDA #$3e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3e,d0
 move.b d0,d4
 bsr.w .nz
.p8066: ; STA $04e0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8069: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p806b: ; STA $0410,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p806e: ; STA $0430,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8071: ; LDA $0420,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8074: ; CMP #$22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$22,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8074
 ori.b #1,d7
.cmp8074:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8076: ; BEQ $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8082
.p8078: ; CMP #$23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$23,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8078
 ori.b #1,d7
.cmp8078:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p807a: ; BEQ $8082
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8082
.p807c: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.p807d: ; SBC #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 bsr.w .sbc
.p807f: ; STA $0420,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8082: ; INC $4d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4d,d1
 andi.w #$ff,d1
 bsr.w .read
 addq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p8084: ; LDX $4d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4d,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.p8086: ; CPX #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d5,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8086
 ori.b #1,d7
.cmp8086:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8088: ; BEQ $808d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p808d
.p808a: ; JMP $8004
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p8004
.p808d: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p808e: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8091: ; CMP #$66
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$66,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8091
 ori.b #1,d7
.cmp8091:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8093: ; BEQ $808d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p808d
.p8095: ; CMP #$4c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4c,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8095
 ori.b #1,d7
.cmp8095:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8097: ; BEQ $808d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p808d
.p8099: ; LDA $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p809c: ; CMP #$27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp809c
 ori.b #1,d7
.cmp809c:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p809e: ; BEQ $808d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p808d
.p80a0: ; CMP #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp80a0
 ori.b #1,d7
.cmp80a0:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p80a2: ; BEQ $808d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p808d
.p80a4: ; JMP $8e1a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p8e1a
.p81bc: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p81bf: ; CMP #$25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp81bf
 ori.b #1,d7
.cmp81bf:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p81c1: ; BEQ $8192
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8192
.p81c3: ; CMP #$27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$27,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp81c3
 ori.b #1,d7
.cmp81c3:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p81c5: ; BEQ $8192
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8192
.p81c7: ; CMP #$28
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$28,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp81c7
 ori.b #1,d7
.cmp81c7:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p81c9: ; BEQ $8192
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8192
.p81cb: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8bc8: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8bcb: ; AND #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8bcd: ; BNE $8bdd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8bdd
.p8bcf: ; LDA #$8c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8c,d0
 move.b d0,d4
 bsr.w .nz
.p8bd1: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.p8bd3: ; JSR $f217
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8b,d0
 bsr.w .push
 move.w #$d5,d0
 bsr.w .push
 move.w #$f217,(a1)
 bra.w .success
.p8bd6: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8bd8: ; CMP #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8bd8
 ori.b #1,d7
.cmp8bd8:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8bda: ; BNE $8bdd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8bdd
.p8bdc: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8bdd: ; LDY #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d0,d6
 bsr.w .nz
.p8bdf: ; LDA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8be2: ; BPL $8c08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8c08
.p8be4: ; LDA $0400,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8be7: ; BPL $8c08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .p8c08
.p8be9: ; LDA $04e0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8bec: ; CMP #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8bec
 ori.b #1,d7
.cmp8bec:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8bee: ; BNE $8c08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8c08
.p8bf0: ; LDA $0420,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8bf3: ; CMP #$22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$22,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8bf3
 ori.b #1,d7
.cmp8bf3:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8bf5: ; BNE $8c08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8c08
.p8bf7: ; LDA $0510,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8bfa: ; CMP $0510,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8bfa
 ori.b #1,d7
.cmp8bfa:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8bfd: ; BNE $8c08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8c08
.p8bff: ; LDA $04f0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8c02: ; CMP $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8c02
 ori.b #1,d7
.cmp8c02:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8c05: ; BNE $8c08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8c08
.p8c07: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8c08: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.p8c09: ; CPY #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8c09
 ori.b #1,d7
.cmp8c09:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8c0b: ; BNE $8bdf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8bdf
.p8c0d: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8c10: ; AND #$f7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f7,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8c12: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8c15: ; INC $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 bsr.w .read
 addq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p8c18: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8c1b: ; CMP #$2f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$2f,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8c1b
 ori.b #1,d7
.cmp8c1b:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8c1d: ; BNE $8c22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8c22
.p8c1f: ; JSR $8c23
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8c,d0
 bsr.w .push
 move.w #$21,d0
 bsr.w .push
 move.w #$8c23,(a1)
 bra.w .success
.p8c22: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8e15: ; JSR $f977
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8e,d0
 bsr.w .push
 move.w #$17,d0
 bsr.w .push
 move.w #$f977,(a1)
 bra.w .success
.p8e18: ; BCS $8e80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .p8e80
.p8e1a: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8e1c: ; STA $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e1f: ; LDA $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8e22: ; CMP #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8e22
 ori.b #1,d7
.cmp8e22:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8e24: ; BEQ $8e2a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8e2a
.p8e26: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8e26
 ori.b #1,d7
.cmp8e26:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8e28: ; BNE $8e2d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8e2d
.p8e2a: ; STA $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e2d: ; LDA #$16
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d0
 move.b d0,d4
 bsr.w .nz
.p8e2f: ; JSR $f379
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8e,d0
 bsr.w .push
 move.w #$31,d0
 bsr.w .push
 move.w #$f379,(a1)
 bra.w .success
.p8e32: ; LDA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 move.b d0,d4
 bsr.w .nz
.p8e34: ; STA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e37: ; LDA $0580,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8e3a: ; STA $0580,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e3d: ; LDA #$a8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$a8,d0
 move.b d0,d4
 bsr.w .nz
.p8e3f: ; STA $0530,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0530,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e42: ; STA $0550,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e45: ; LDA #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d0,d4
 bsr.w .nz
.p8e47: ; STA $0540,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0540,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e4a: ; STA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e4d: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8e4f: ; STA $0570,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0570,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e52: ; LDA #$1c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1c,d0
 move.b d0,d4
 bsr.w .nz
.p8e54: ; STA $04e0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8e57: ; LDA $0420,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8e5a: ; CMP #$22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$22,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8e5a
 ori.b #1,d7
.cmp8e5a:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8e5c: ; BNE $8e80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8e80
.p8e5e: ; LDA $0580,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8e61: ; EOR #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8e63: ; STA $0580,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8e66: ; LDA #$a8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$a8,d0
 move.b d0,d4
 bsr.w .nz
.p8e68: ; STA $0530,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0530,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8e6b: ; STA $0550,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8e6e: ; LDA #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d0,d4
 bsr.w .nz
.p8e70: ; STA $0540,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0540,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8e73: ; STA $0560,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8e76: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8e78: ; STA $0570,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0570,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8e7b: ; LDA #$1c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1c,d0
 move.b d0,d4
 bsr.w .nz
.p8e7d: ; STA $04e0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.p8e80: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8f38: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8f3b: ; AND #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8f3d: ; BNE $8f55
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8f55
.p8f3f: ; LDA #$33
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$33,d0
 move.b d0,d4
 bsr.w .nz
.p8f41: ; STA $0530,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0530,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8f44: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.p8f46: ; STA $0540,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0540,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8f49: ; JSR $f328
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8f,d0
 bsr.w .push
 move.w #$4b,d0
 bsr.w .push
 move.w #$f328,(a1)
 bra.w .success
.p8f4c: ; LDA #$1e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1e,d0
 move.b d0,d4
 bsr.w .nz
.p8f4e: ; STA $0490,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0490,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8f51: ; INC $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 addq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p8f54: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8f55: ; LDA $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8f58: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8f5a: ; BNE $8f71
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8f71
.p8f5c: ; DEC $0490,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0490,d1
 add.w d5,d1
 bsr.w .read
 subq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p8f5f: ; BNE $8f54
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8f54
.p8f61: ; LDA #$1c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1c,d0
 move.b d0,d4
 bsr.w .nz
.p8f63: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8f66: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8f68: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8f6b: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8f6e: ; INC $04d0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d5,d1
 bsr.w .read
 addq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p8f71: ; LDA $95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$95,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8f73: ; AND #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8f75: ; BNE $8f7c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .p8f7c
.p8f77: ; LDA #$1a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$1a,d0
 move.b d0,d4
 bsr.w .nz
.p8f79: ; JSR $f379
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8f,d0
 bsr.w .push
 move.w #$7b,d0
 bsr.w .push
 move.w #$f379,(a1)
 bra.w .success
.p8f7c: ; LDY #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d6
 bsr.w .nz
.p8f7e: ; LDA #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d0,d4
 bsr.w .nz
.p8f80: ; JSR $f0fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8f,d0
 bsr.w .push
 move.w #$82,d0
 bsr.w .push
 move.w #$f0fb,(a1)
 bra.w .success
.p8f83: ; PHP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d7,d0
 ori.b #$30,d0
 bsr.w .push
.p8f84: ; LDY #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d6
 bsr.w .nz
.p8f86: ; LDA $0580,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8f89: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8f8b: ; BEQ $8f95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8f95
.p8f8d: ; LDA #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d0,d4
 bsr.w .nz
.p8f8f: ; JSR $f000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8f,d0
 bsr.w .push
 move.w #$91,d0
 bsr.w .push
 move.w #$f000,(a1)
 bra.w .success
.p8f92: ; JMP $8f9a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .p8f9a
.p8f95: ; LDA #$0d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0d,d0
 move.b d0,d4
 bsr.w .nz
.p8f97: ; JSR $f066
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8f,d0
 bsr.w .push
 move.w #$99,d0
 bsr.w .push
 move.w #$f066,(a1)
 bra.w .success
.p8f9a: ; PLP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 ori.b #$30,d0
 move.b d0,d7
.p8f9b: ; BCC $8fc5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p8fc5
.p8f9d: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8f9f: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8f9f
 ori.b #1,d7
.cmp8f9f:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8fa1: ; BCC $8fc0
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .p8fc0
.p8fa3: ; INC $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 bsr.w .read
 addq.b #1,d0
 bsr.w .write
 bsr.w .nz
.p8fa6: ; LDA $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8fa9: ; CMP #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmp8fa9
 ori.b #1,d7
.cmp8fa9:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.p8fab: ; BEQ $8fb8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .p8fb8
.p8fad: ; LDA #$9e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9e,d0
 move.b d0,d4
 bsr.w .nz
.p8faf: ; STA $0550,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8fb2: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.p8fb4: ; STA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8fb7: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8fb8: ; LDA $0580,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.p8fbb: ; EOR #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 eor.b d0,d4
 move.b d4,d0
 bsr.w .nz
.p8fbd: ; STA $0580,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0580,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8fc0: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.p8fc2: ; STA $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.p8fc5: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$801f,d0
 beq.w .p801f
 cmpi.w #$8029,d0
 beq.w .p8029
 cmpi.w #$8033,d0
 beq.w .p8033
 cmpi.w #$8050,d0
 beq.w .p8050
 cmpi.w #$8bd6,d0
 beq.w .p8bd6
 cmpi.w #$8c22,d0
 beq.w .p8c22
 cmpi.w #$8e18,d0
 beq.w .p8e18
 cmpi.w #$8e32,d0
 beq.w .p8e32
 cmpi.w #$8f4c,d0
 beq.w .p8f4c
 cmpi.w #$8f7c,d0
 beq.w .p8f7c
 cmpi.w #$8f83,d0
 beq.w .p8f83
 cmpi.w #$8f92,d0
 beq.w .p8f92
 cmpi.w #$8f9a,d0
 beq.w .p8f9a
 move.w d0,(a1)
 bra.w .success
.p8192:
 move.w #$8192,(a1)
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
