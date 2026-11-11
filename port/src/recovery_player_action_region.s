; Static native translation of fixed-bank player action state and reached dependencies.
; No instruction bytes, runtime decoder, proprietary tables, or captured effects.
; A0 RAM2048 A1 context8 A2 counted journal60002 A4 runtime12 A5 PRG131072.
; Public D0=1 success/-1 inert rejection; core -2 is private preflight failure.
; D1-D7/A0-A6 preserved; native USER mode, >=2304 bytes native stack.
; One committed ordered RAM/resource journal after scratch validation pass.
; Disjoint stack/buffers and unchanged RAM/context/resources across passes required.
recovery_player_action_region:
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
 bsr.w recovery_player_action_region_core
 cmpi.l #1,d0
 bne.s .rejected
 movea.l 2088(sp),a0
 movea.l 2092(sp),a1
 movea.l 2096(sp),a2
 suba.l a6,a6
 bsr.w recovery_player_action_region_core
 bra.s .return
.rejected:
 moveq #-1,d0
.return:
 adda.w #2060,sp
 movem.l (sp)+,d1-d7/a0-a6
 rts
recovery_player_action_region_core:
 cmpi.b #7,3(a4)
 bhi.w .invalid
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
 cmpi.w #$c940,(a1)
 beq.w .pc940
 cmpi.w #$c946,(a1)
 beq.w .pc946
 cmpi.w #$c94c,(a1)
 beq.w .pc94c
 cmpi.w #$c96b,(a1)
 beq.w .pc96b
 cmpi.w #$c9d0,(a1)
 beq.w .pc9d0
 cmpi.w #$ca1f,(a1)
 beq.w .pca1f
 cmpi.w #$ca31,(a1)
 beq.w .pca31
 cmpi.w #$ca4e,(a1)
 beq.w .pca4e
 cmpi.w #$caa2,(a1)
 beq.w .pcaa2
 cmpi.w #$cac6,(a1)
 beq.w .pcac6
 cmpi.w #$cada,(a1)
 beq.w .pcada
 cmpi.w #$cae4,(a1)
 beq.w .pcae4
 cmpi.w #$cb70,(a1)
 beq.w .pcb70
 cmpi.w #$cb73,(a1)
 beq.w .pcb73
 cmpi.w #$cb78,(a1)
 beq.w .pcb78
 cmpi.w #$cb8e,(a1)
 beq.w .pcb8e
 cmpi.w #$cb9f,(a1)
 beq.w .pcb9f
 cmpi.w #$cbac,(a1)
 beq.w .pcbac
 cmpi.w #$cbb3,(a1)
 beq.w .pcbb3
 cmpi.w #$cbcc,(a1)
 beq.w .pcbcc
 cmpi.w #$cbd9,(a1)
 beq.w .pcbd9
 cmpi.w #$cc09,(a1)
 beq.w .pcc09
 cmpi.w #$cc18,(a1)
 beq.w .pcc18
 cmpi.w #$cc21,(a1)
 beq.w .pcc21
 cmpi.w #$cc60,(a1)
 beq.w .pcc60
 cmpi.w #$cc6d,(a1)
 beq.w .pcc6d
 cmpi.w #$d50f,(a1)
 beq.w .pd50f
 cmpi.w #$d510,(a1)
 beq.w .pd510
 cmpi.w #$d559,(a1)
 beq.w .pd559
 cmpi.w #$d57a,(a1)
 beq.w .pd57a
 cmpi.w #$d583,(a1)
 beq.w .pd583
 cmpi.w #$d588,(a1)
 beq.w .pd588
 cmpi.w #$d59a,(a1)
 beq.w .pd59a
 cmpi.w #$d5a5,(a1)
 beq.w .pd5a5
 cmpi.w #$d5b0,(a1)
 beq.w .pd5b0
 cmpi.w #$d5b8,(a1)
 beq.w .pd5b8
 cmpi.w #$d5c3,(a1)
 beq.w .pd5c3
 cmpi.w #$d5ce,(a1)
 beq.w .pd5ce
 cmpi.w #$d5d2,(a1)
 beq.w .pd5d2
 cmpi.w #$d604,(a1)
 beq.w .pd604
 cmpi.w #$d62f,(a1)
 beq.w .pd62f
 bra.w .budget_failure
.pc940: ; LDA $6c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6c,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc942: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pc943: ; JSR $cbac
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c9,d0
 bsr.w .push
 move.w #$45,d0
 bsr.w .push
 bra.w .pcbac
.pc946: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc948: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pc949: ; JSR $d510
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c9,d0
 bsr.w .push
 move.w #$4b,d0
 bsr.w .push
 bra.w .pd510
.pc94c: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pc94d: ; STA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pc94f: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pc950: ; STA $6c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$6c,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pc952: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc954: ; BEQ $c957
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc957
.pc956: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pc957: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc959: ; CMP #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc959
 ori.b #1,d7
.cmpc959:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc95b: ; BNE $c968
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc968
.pc95d: ; LDA $5e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc95f: ; BNE $c968
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc968
.pc961: ; LDA #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 move.b d0,d4
 bsr.w .nz
.pc963: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pc965: ; JMP $d05e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d05e,(a1)
 bra.w .success
.pc968: ; JSR $d559
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c9,d0
 bsr.w .push
 move.w #$6a,d0
 bsr.w .push
 bra.w .pd559
.pc96b: ; LDA $14,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc96d: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc96f: ; BEQ $c9c3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc9c3
.pc971: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc974: ; BEQ $c9ba
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc9ba
.pc976: ; CMP $0348,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0348,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc976
 ori.b #1,d7
.cmpc976:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc979: ; BEQ $c9ba
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc9ba
.pc97b: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pc97d: ; BEQ $c9a9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc9a9
.pc97f: ; LDA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc982: ; CMP #$24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc982
 ori.b #1,d7
.cmpc982:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc984: ; BCC $c98c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pc98c
.pc986: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc988: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc98a: ; BNE $c9ba
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc9ba
.pc98c: ; LDA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc98f: ; CMP #$26
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$26,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc98f
 ori.b #1,d7
.cmpc98f:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc991: ; BNE $c9a9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc9a9
.pc993: ; LDY $d69d,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d69d,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pc996: ; LDA $0200,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0200,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc999: ; CMP #$f8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f8,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc999
 ori.b #1,d7
.cmpc999:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc99b: ; BNE $c9a9
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc9a9
.pc99d: ; LDA #$9e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$9e,d0
 move.b d0,d4
 bsr.w .nz
.pc99f: ; STA $0550,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9a2: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pc9a4: ; STA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9a7: ; BNE $c9b3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc9b3
.pc9a9: ; LDA #$87
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$87,d0
 move.b d0,d4
 bsr.w .nz
.pc9ab: ; STA $0550,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9ae: ; LDA #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d0
 move.b d0,d4
 bsr.w .nz
.pc9b0: ; STA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9b3: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pc9b5: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pc9b7: ; JMP $cbac
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pcbac
.pc9ba: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc9bc: ; CMP #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpc9bc
 ori.b #1,d7
.cmpc9bc:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pc9be: ; BNE $ca05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pca05
.pc9c0: ; JMP $cc9f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc9f,(a1)
 bra.w .success
.pc9c3: ; LDA $14,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc9c5: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc9c7: ; BEQ $c9ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc9ff
.pc9c9: ; LDA $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc9cb: ; BEQ $c9ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pc9ff
.pc9cd: ; JSR $d604
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$c9,d0
 bsr.w .push
 move.w #$cf,d0
 bsr.w .push
 bra.w .pd604
.pc9d0: ; BCS $c9ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pc9ff
.pc9d2: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc9d5: ; STA $5c,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5c,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pc9d7: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pc9d9: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9dc: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9df: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pc9e1: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pc9e3: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc9e5: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pc9e7: ; BNE $c9f2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pc9f2
.pc9e9: ; LDA $0350,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0350,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pc9ec: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9ef: ; JMP $cd50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cd50,(a1)
 bra.w .success
.pc9f2: ; LDA #$44
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$44,d0
 move.b d0,d4
 bsr.w .nz
.pc9f4: ; STA $0550,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9f7: ; LDA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d4
 bsr.w .nz
.pc9f9: ; STA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pc9fc: ; JMP $cd50
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cd50,(a1)
 bra.w .success
.pc9ff: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca01: ; AND #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pca03: ; BEQ $ca34
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca34
.pca05: ; LDA $0348,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0348,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca08: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pca0a: ; BEQ $ca22
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca22
.pca0c: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca0f: ; BEQ $ca2e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca2e
.pca11: ; LDA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca14: ; CMP #$24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpca14
 ori.b #1,d7
.cmpca14:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pca16: ; BCS $ca34
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pca34
.pca18: ; LDA #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d0,d4
 bsr.w .nz
.pca1a: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pca1c: ; JSR $cf31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ca,d0
 bsr.w .push
 move.w #$1e,d0
 bsr.w .push
 move.w #$cf31,(a1)
 bra.w .success
.pca1f: ; LDA $034a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$034a,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca22: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca25: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pca27: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca2a: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca2d: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pca2e: ; JSR $cf08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ca,d0
 bsr.w .push
 move.w #$30,d0
 bsr.w .push
 move.w #$cf08,(a1)
 bra.w .success
.pca31: ; JMP $ca25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pca25
.pca34: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca36: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pca38: ; BNE $caa2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcaa2
.pca3a: ; LDA $58,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$58,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca3c: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pca3e: ; BEQ $ca58
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca58
.pca40: ; TAY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d6
 move.b d6,d0
 bsr.w .nz
.pca41: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca44: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pca45: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pca47: ; STA $0540,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0540,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca4a: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.pca4b: ; JSR $caa2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ca,d0
 bsr.w .push
 move.w #$4d,d0
 bsr.w .push
 bra.w .pcaa2
.pca4e: ; LDA $58,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$58,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca50: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pca52: ; STA $58,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$58,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pca54: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pca55: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca58: ; LDA $0340,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0340,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca5b: ; CMP $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpca5b
 ori.b #1,d7
.cmpca5b:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pca5e: ; BEQ $ca6d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca6d
.pca60: ; LDA $0342,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0342,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca63: ; CMP $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpca63
 ori.b #1,d7
.cmpca63:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pca66: ; BEQ $ca6d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca6d
.pca68: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pca6a: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca6d: ; LDA $0340,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0340,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca70: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pca72: ; BEQ $ca77
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca77
.pca74: ; LDA $0342,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0342,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca77: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca7a: ; LDA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca7d: ; BEQ $ca87
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pca87
.pca7f: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pca81: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pca84: ; JMP $d3e7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d3e7,(a1)
 bra.w .success
.pca87: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pca89: ; BEQ $caa1
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcaa1
.pca8b: ; LDA $0510,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0510,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca8e: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pca8f: ; SBC #$0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0c,d0
 bsr.w .sbc
.pca91: ; BCS $ca96
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pca96
.pca93: ; SBC #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 bsr.w .sbc
.pca95: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pca96: ; STA $0490,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0490,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pca99: ; LDA $0520,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0520,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pca9c: ; SBC #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 bsr.w .sbc
.pca9e: ; STA $04a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04a0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcaa1: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pcaa2: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pcaa3: ; LDA $0344,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0344,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcaa6: ; CMP $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcaa6
 ori.b #1,d7
.cmpcaa6:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcaa9: ; BEQ $cac5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcac5
.pcaab: ; LDA $0346,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0346,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcaae: ; CMP $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcaae
 ori.b #1,d7
.cmpcaae:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcab1: ; BEQ $cac5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcac5
.pcab3: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pcab5: ; BNE $caba
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcaba
.pcab7: ; LDA $0344,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0344,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcaba: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcabd: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcabf: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcac2: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcac5: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pcac6: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pcac7: ; LDA $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcac9: ; STA $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcacc: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pcacd: ; STA $52,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$52,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcacf: ; AND #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcad1: ; BEQ $cadd
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcadd
.pcad3: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcad5: ; LDY #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d6
 bsr.w .nz
.pcad7: ; JSR $f000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ca,d0
 bsr.w .push
 move.w #$d9,d0
 bsr.w .push
 move.w #$f000,(a1)
 bra.w .success
.pcada: ; JMP $cae4
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pcae4
.pcadd: ; LDA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d4
 bsr.w .nz
.pcadf: ; LDY #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d6
 bsr.w .nz
.pcae1: ; JSR $f066
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ca,d0
 bsr.w .push
 move.w #$e3,d0
 bsr.w .push
 move.w #$f066,(a1)
 bra.w .success
.pcae4: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcae6: ; CMP #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcae6
 ori.b #1,d7
.cmpcae6:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcae8: ; BNE $caf5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcaf5
.pcaea: ; LDA $5e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5e,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcaec: ; BNE $caf5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcaf5
.pcaee: ; LDA #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 move.b d0,d4
 bsr.w .nz
.pcaf0: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcaf2: ; JMP $d05e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d05e,(a1)
 bra.w .success
.pcaf5: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcaf7: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcaf7
 ori.b #1,d7
.cmpcaf7:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcaf9: ; BCC $caff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pcaff
.pcafb: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcafd: ; STA $52,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$52,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcaff: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pcb01: ; BEQ $cb0d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcb0d
.pcb03: ; LDA $0480,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb06: ; CMP $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcb06
 ori.b #1,d7
.cmpcb06:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcb08: ; BNE $cb73
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcb73
.pcb0a: ; JMP $d3e7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d3e7,(a1)
 bra.w .success
.pcb0d: ; LDA $14,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb0f: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcb11: ; BEQ $cb8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcb8a
.pcb13: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb15: ; CMP #$0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0e,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcb15
 ori.b #1,d7
.cmpcb15:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcb17: ; BCC $cb8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pcb8a
.pcb19: ; LDY #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d6
 bsr.w .nz
.pcb1b: ; LDA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb1e: ; BPL $cb27
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pcb27
.pcb20: ; INY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 addq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pcb21: ; CPY #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcb21
 ori.b #1,d7
.cmpcb21:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcb23: ; BNE $cb1b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcb1b
.pcb25: ; BEQ $cb8a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcb8a
.pcb27: ; TYA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d6,d4
 move.b d4,d0
 bsr.w .nz
.pcb28: ; ORA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcb2a: ; STA $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcb2c: ; LDA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 move.b d0,d4
 bsr.w .nz
.pcb2e: ; STA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb31: ; LDA #$90
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$90,d0
 move.b d0,d4
 bsr.w .nz
.pcb33: ; STA $0400,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb36: ; LDA #$ab
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ab,d0
 move.b d0,d4
 bsr.w .nz
.pcb38: ; STA $0550,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0550,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb3b: ; LDA #$ff
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$ff,d0
 move.b d0,d4
 bsr.w .nz
.pcb3d: ; STA $0560,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb40: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcb42: ; STA $0430,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb45: ; STA $0410,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb48: ; STA $04e0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb4b: ; STA $0570,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0570,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb4e: ; STA $0480,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0480,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb51: ; STA $0490,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0490,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb54: ; STA $04a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04a0,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb57: ; STX $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d5,d0
 bsr.w .write
.pcb59: ; LDX $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pcb5b: ; LDA $cb9c,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb9c,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb5e: ; STA $0420,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d6,d1
 move.b d4,d0
 bsr.w .write
.pcb61: ; LDX $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d5
 bsr.w .nz
.pcb63: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb65: ; BNE $cb8b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcb8b
.pcb67: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb69: ; AND #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcb6b: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pcb6d: ; JSR $d460
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$6f,d0
 bsr.w .push
 move.w #$d460,(a1)
 bra.w .success
.pcb70: ; JSR $e817
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$72,d0
 bsr.w .push
 move.w #$e817,(a1)
 bra.w .success
.pcb73: ; LDA #$11
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$11,d0
 move.b d0,d4
 bsr.w .nz
.pcb75: ; JSR $f379
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$77,d0
 bsr.w .push
 move.w #$f379,(a1)
 bra.w .success
.pcb78: ; LDA $0342,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0342,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb7b: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcb7e: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcb80: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcb83: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcb86: ; LDA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d4
 bsr.w .nz
.pcb88: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcb8a: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pcb8b: ; JSR $e817
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$8d,d0
 bsr.w .push
 move.w #$e817,(a1)
 bra.w .success
.pcb8e: ; LDA $034e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$034e,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcb91: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcb94: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcb96: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcb99: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcb9c: ; JSR $d3e7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$9e,d0
 bsr.w .push
 move.w #$d3e7,(a1)
 bra.w .success
.pcb9f: ; JMP $d40b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d40b,(a1)
 bra.w .success
.pcbac: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbae: ; BEQ $cbb3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcbb3
.pcbb0: ; JSR $d510
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$b2,d0
 bsr.w .push
 bra.w .pd510
.pcbb3: ; LDA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbb6: ; BMI $cbcc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pcbcc
.pcbb8: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcbba: ; STA $5a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5a,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcbbc: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbbe: ; AND #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcbc0: ; BNE $cbcc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcbcc
.pcbc2: ; LDA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbc5: ; CMP #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcbc5
 ori.b #1,d7
.cmpcbc5:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcbc7: ; BCS $cbcc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pcbcc
.pcbc9: ; JSR $f31d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$cb,d0
 bsr.w .push
 move.w #$f31d,(a1)
 bra.w .success
.pcbcc: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbcf: ; AND #$20
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$20,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcbd1: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pcbd2: ; LDA #$06
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$06,d0
 move.b d0,d4
 bsr.w .nz
.pcbd4: ; LDY #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d6
 bsr.w .nz
.pcbd6: ; JSR $f0fb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cb,d0
 bsr.w .push
 move.w #$d8,d0
 bsr.w .push
 move.w #$f0fb,(a1)
 bra.w .success
.pcbd9: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pcbda: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcbdc: ; PHP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d7,d0
 ori.b #$30,d0
 bsr.w .push
.pcbdd: ; LDA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbe0: ; BPL $cbf5
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pcbf5
.pcbe2: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbe4: ; CMP #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcbe4
 ori.b #1,d7
.cmpcbe4:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcbe6: ; BCC $cbfb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pcbfb
.pcbe8: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbeb: ; AND #$df
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$df,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcbed: ; ORA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 or.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcbef: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcbf2: ; JMP $cbfb
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pcbfb
.pcbf5: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbf7: ; CMP #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcbf7
 ori.b #1,d7
.cmpcbf7:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcbf9: ; BEQ $cbe8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcbe8
.pcbfb: ; PLP 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 ori.b #$30,d0
 move.b d0,d7
.pcbfc: ; LDA $5a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5a,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcbfe: ; BEQ $cc0c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc0c
.pcc00: ; BCS $cc0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pcc0e
.pcc02: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcc04: ; STA $5a,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5a,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcc06: ; JSR $ed7a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc,d0
 bsr.w .push
 move.w #$08,d0
 bsr.w .push
 move.w #$ed7a,(a1)
 bra.w .success
.pcc09: ; JMP $cc0e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pcc0e
.pcc0c: ; BCC $cc3a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pcc3a
.pcc0e: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc10: ; CMP #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcc10
 ori.b #1,d7
.cmpcc10:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcc12: ; BNE $cc15
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcc15
.pcc14: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pcc15: ; JSR $d40b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc,d0
 bsr.w .push
 move.w #$17,d0
 bsr.w .push
 move.w #$d40b,(a1)
 bra.w .success
.pcc18: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc1a: ; BEQ $cc9b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc9b
.pcc1c: ; LDA #$10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d0
 move.b d0,d4
 bsr.w .nz
.pcc1e: ; JSR $f379
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc,d0
 bsr.w .push
 move.w #$20,d0
 bsr.w .push
 move.w #$f379,(a1)
 bra.w .success
.pcc21: ; LDA $0340,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0340,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc24: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pcc26: ; BEQ $cc2b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc2b
.pcc28: ; LDA $0342,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0342,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc2b: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc2e: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcc30: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcc32: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc35: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc38: ; BEQ $cc5d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc5d
.pcc3a: ; LDA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc3c: ; CMP #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcc3c
 ori.b #1,d7
.cmpcc3c:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcc3e: ; BEQ $cc9b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc9b
.pcc40: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpcc40
 ori.b #1,d7
.cmpcc40:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pcc42: ; BEQ $cc14
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc14
.pcc44: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pcc46: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcc48: ; LDA $034c,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$034c,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc4b: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pcc4d: ; BEQ $cc52
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc52
.pcc4f: ; LDA $034e,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$034e,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc52: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc55: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcc57: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc5a: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc5d: ; JSR $d40b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc,d0
 bsr.w .push
 move.w #$5f,d0
 bsr.w .push
 move.w #$d40b,(a1)
 bra.w .success
.pcc60: ; LDA $14,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$14,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc62: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcc64: ; BEQ $cc95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc95
.pcc66: ; LDA $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc68: ; BEQ $cc95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pcc95
.pcc6a: ; JSR $d604
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$cc,d0
 bsr.w .push
 move.w #$6c,d0
 bsr.w .push
 bra.w .pd604
.pcc6d: ; BCS $cc95
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pcc95
.pcc6f: ; LDA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc72: ; STA $5c,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$5c,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcc74: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pcc76: ; STA $0430,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0430,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc79: ; STA $0410,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0410,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc7c: ; LDA #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d4
 bsr.w .nz
.pcc7e: ; STA $54,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$54,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pcc80: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc82: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcc84: ; BNE $cc8d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcc8d
.pcc86: ; LDA $0350,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0350,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc89: ; STA $0420,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0420,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pcc8c: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pcc8d: ; LDA $0560,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0560,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc90: ; BMI $cc9b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pcc9b
.pcc92: ; JMP $f31d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$f31d,(a1)
 bra.w .success
.pcc95: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pcc97: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pcc99: ; BNE $cc9c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pcc9c
.pcc9b: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pcc9c: ; JMP $cac6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pcac6
.pd50f: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd510: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd512: ; CMP #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd512
 ori.b #1,d7
.cmpd512:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd514: ; BNE $d532
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd532
.pd516: ; LDY #$0f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0f,d0
 move.b d0,d6
 bsr.w .nz
.pd518: ; LDA $04d0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04d0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd51b: ; BPL $d52d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pd52d
.pd51d: ; LDA $0400,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd520: ; BPL $d52d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pd52d
.pd522: ; LDA $04e0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04e0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd525: ; CMP #$36
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$36,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd525
 ori.b #1,d7
.cmpd525:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd527: ; BEQ $d533
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd533
.pd529: ; CMP #$37
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$37,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd529
 ori.b #1,d7
.cmpd529:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd52b: ; BEQ $d546
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd546
.pd52d: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pd52e: ; CPY #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd52e
 ori.b #1,d7
.cmpd52e:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd530: ; BNE $d518
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd518
.pd532: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd533: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd536: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pd537: ; SBC $04f0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .sbc
.pd53a: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd53d: ; SBC $0500,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .sbc
.pd540: ; BCS $d52d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pd52d
.pd542: ; LDY #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d6
 bsr.w .nz
.pd544: ; BNE $d59a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd59a
.pd546: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd549: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pd54a: ; SBC $04f0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .sbc
.pd54d: ; LDA $0500,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd550: ; SBC $0500,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0500,d1
 add.w d6,d1
 bsr.w .read
 bsr.w .sbc
.pd553: ; BCC $d52d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pd52d
.pd555: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.pd557: ; BEQ $d59a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd59a
.pd559: ; LDA $31
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$31,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd55b: ; CMP #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd55b
 ori.b #1,d7
.cmpd55b:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd55d: ; BNE $d56f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd56f
.pd55f: ; LDY #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d6
 bsr.w .nz
.pd561: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd563: ; CMP #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd563
 ori.b #1,d7
.cmpd563:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd565: ; BEQ $d59a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd59a
.pd567: ; LDY #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d0,d6
 bsr.w .nz
.pd569: ; CMP #$09
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$09,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd569
 ori.b #1,d7
.cmpd569:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd56b: ; BEQ $d59a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd59a
.pd56d: ; BNE $d50f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd50f
.pd56f: ; CMP #$0a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0a,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd56f
 ori.b #1,d7
.cmpd56f:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd571: ; BNE $d50f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd50f
.pd573: ; TXA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d5,d4
 move.b d4,d0
 bsr.w .nz
.pd574: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pd575: ; LDY $4a
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4a,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pd577: ; JSR $e06b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$79,d0
 bsr.w .push
 move.w #$e06b,(a1)
 bra.w .success
.pd57a: ; LDA $4b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4b,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd57c: ; AND #$3f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$3f,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pd57e: ; STA $24
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$24,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pd580: ; JSR $e01b
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$82,d0
 bsr.w .push
 move.w #$e01b,(a1)
 bra.w .success
.pd583: ; LDA $36
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$36,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd585: ; JSR $ff53
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$87,d0
 bsr.w .push
 move.w #$ff53,(a1)
 bra.w .success
.pd588: ; LDY $4c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4c,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pd58a: ; LDA ($00),Y
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
.pd58c: ; LDY #$07
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$07,d0
 move.b d0,d6
 bsr.w .nz
.pd58e: ; CMP $d5fc,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5fc,d1
 add.w d6,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd58e
 ori.b #1,d7
.cmpd58e:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd591: ; BEQ $d598
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd598
.pd593: ; DEY 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 subq.b #1,d6
 move.b d6,d0
 bsr.w .nz
.pd594: ; BPL $d58e
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pd58e
.pd596: ; BMI $d5cf
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 bne.w .pd5cf
.pd598: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pd599: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pd59a: ; CPY #$04
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd59a
 ori.b #1,d7
.cmpd59a:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd59c: ; LDY #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d6
 bsr.w .nz
.pd59e: ; BCS $d5b3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pd5b3
.pd5a0: ; LDA #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d4
 bsr.w .nz
.pd5a2: ; JSR $d5d2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$a4,d0
 bsr.w .push
 bra.w .pd5d2
.pd5a5: ; BCC $d5ce
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pd5ce
.pd5a7: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd5aa: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pd5ab: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pd5ad: ; JSR $f000
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$af,d0
 bsr.w .push
 move.w #$f000,(a1)
 bra.w .success
.pd5b0: ; JMP $d5c3
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bra.w .pd5c3
.pd5b3: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.pd5b5: ; JSR $d5d2
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$b7,d0
 bsr.w .push
 bra.w .pd5d2
.pd5b8: ; BCC $d5ce
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pd5ce
.pd5ba: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd5bd: ; PHA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d0
 bsr.w .push
.pd5be: ; LDA #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d0,d4
 bsr.w .nz
.pd5c0: ; JSR $f066
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$c2,d0
 bsr.w .push
 move.w #$f066,(a1)
 bra.w .success
.pd5c3: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pd5c4: ; STA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pd5c7: ; LDA $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd5c9: ; BEQ $d5ce
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd5ce
.pd5cb: ; JSR $d3e7
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d5,d0
 bsr.w .push
 move.w #$cd,d0
 bsr.w .push
 move.w #$d3e7,(a1)
 bra.w .success
.pd5ce: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd5cf: ; PLA 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d4
 bsr.w .nz
.pd5d0: ; TAX 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.b d4,d5
 move.b d5,d0
 bsr.w .nz
.pd5d1: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd5d2: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pd5d4: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd5d6: ; AND #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pd5d8: ; BEQ $d5f6
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd5f6
.pd5da: ; CMP $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd5da
 ori.b #1,d7
.cmpd5da:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd5dc: ; BEQ $d5ea
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd5ea
.pd5de: ; LDA #$4c
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$4c,d0
 move.b d0,d4
 bsr.w .nz
.pd5e0: ; STA $0530,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0530,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pd5e3: ; LDA #$00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d0
 move.b d0,d4
 bsr.w .nz
.pd5e5: ; STA $0540,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0540,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pd5e8: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pd5e9: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd5ea: ; LDA #$80
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$80,d0
 move.b d0,d4
 bsr.w .nz
.pd5ec: ; STA $0530,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0530,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pd5ef: ; LDA #$02
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$02,d0
 move.b d0,d4
 bsr.w .nz
.pd5f1: ; STA $0540,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0540,d1
 add.w d5,d1
 move.b d4,d0
 bsr.w .write
.pd5f4: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pd5f5: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd5f6: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd5f8: ; STA $52,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$52,d1
 add.w d5,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pd5fa: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pd5fb: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd604: ; LDY $56,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$56,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d6
 bsr.w .nz
.pd606: ; CPY #$82
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$82,d0
 move.b d6,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd606
 ori.b #1,d7
.cmpd606:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd608: ; BCC $d619
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pd619
.pd60a: ; LDA $16,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$16,d1
 add.w d5,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd60c: ; AND #$08
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$08,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pd60e: ; BEQ $d637
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd637
.pd610: ; LDA $03a0,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03a0,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd613: ; CMP #$25
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$25,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd613
 ori.b #1,d7
.cmpd613:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd615: ; BNE $d635
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd635
.pd617: ; BEQ $d624
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd624
.pd619: ; LDA $0380,Y
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0380,d1
 add.w d6,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd61c: ; BPL $d655
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #7,d7
 beq.w .pd655
.pd61e: ; LDA #$97
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$97,d0
 move.b d0,d4
 bsr.w .nz
.pd620: ; LDY #$05
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$05,d0
 move.b d0,d6
 bsr.w .nz
.pd622: ; BNE $d628
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 beq.w .pd628
.pd624: ; LDA #$8d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$8d,d0
 move.b d0,d4
 bsr.w .nz
.pd626: ; LDY #$01
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$01,d0
 move.b d0,d6
 bsr.w .nz
.pd628: ; STA $40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pd62a: ; STY $41
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$41,d1
 andi.w #$ff,d1
 move.b d6,d0
 bsr.w .write
.pd62c: ; JSR $ea8f
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$d6,d0
 bsr.w .push
 move.w #$2e,d0
 bsr.w .push
 move.w #$ea8f,(a1)
 bra.w .success
.pd62f: ; LDA $10
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$10,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd631: ; CMP #$03
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$03,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd631
 ori.b #1,d7
.cmpd631:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd633: ; BCS $d655
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pd655
.pd635: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pd636: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd637: ; LDA $04f0,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$04f0,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd63a: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pd63b: ; SBC $fc
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$fc,d1
 andi.w #$ff,d1
 bsr.w .read
 bsr.w .sbc
.pd63d: ; STA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 move.b d4,d0
 bsr.w .write
.pd63f: ; LDA $0400,X
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$0400,d1
 add.w d5,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd642: ; AND #$40
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$40,d0
 and.b d0,d4
 move.b d4,d0
 bsr.w .nz
.pd644: ; BEQ $d64d
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #1,d7
 bne.w .pd64d
.pd646: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd648: ; CMP #$e8
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$e8,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd648
 ori.b #1,d7
.cmpd648:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd64a: ; BCS $d655
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 bne.w .pd655
.pd64c: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd64d: ; LDA $00
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$00,d1
 andi.w #$ff,d1
 bsr.w .read
 move.b d0,d4
 bsr.w .nz
.pd64f: ; CMP #$19
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 move.w #$19,d0
 move.b d4,d2
 andi.b #$fe,d7
 cmp.b d0,d2
 bcs.s .cmpd64f
 ori.b #1,d7
.cmpd64f:
 sub.b d0,d2
 move.b d2,d0
 bsr.w .nz
.pd651: ; BCC $d655
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 btst #0,d7
 beq.w .pd655
.pd653: ; CLC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 andi.b #$fe,d7
.pd654: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
 move.w d0,(a1)
 bra.w .success
.pd655: ; SEC 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 ori.b #1,d7
.pd656: ; RTS 
 subq.l #1,a4
 cmpa.l #0,a4
 beq.w .budget_failure
 bsr.w .pop
 move.b d0,d2
 bsr.w .pop
 lsl.w #8,d0
 move.b d2,d0
 addq.w #1,d0
 cmpi.w #$c946,d0
 beq.w .pc946
 cmpi.w #$c94c,d0
 beq.w .pc94c
 cmpi.w #$c96b,d0
 beq.w .pc96b
 cmpi.w #$c9d0,d0
 beq.w .pc9d0
 cmpi.w #$ca1f,d0
 beq.w .pca1f
 cmpi.w #$ca31,d0
 beq.w .pca31
 cmpi.w #$ca4e,d0
 beq.w .pca4e
 cmpi.w #$cada,d0
 beq.w .pcada
 cmpi.w #$cae4,d0
 beq.w .pcae4
 cmpi.w #$cb70,d0
 beq.w .pcb70
 cmpi.w #$cb73,d0
 beq.w .pcb73
 cmpi.w #$cb78,d0
 beq.w .pcb78
 cmpi.w #$cb8e,d0
 beq.w .pcb8e
 cmpi.w #$cb9f,d0
 beq.w .pcb9f
 cmpi.w #$cbb3,d0
 beq.w .pcbb3
 cmpi.w #$cbcc,d0
 beq.w .pcbcc
 cmpi.w #$cbd9,d0
 beq.w .pcbd9
 cmpi.w #$cc09,d0
 beq.w .pcc09
 cmpi.w #$cc18,d0
 beq.w .pcc18
 cmpi.w #$cc21,d0
 beq.w .pcc21
 cmpi.w #$cc60,d0
 beq.w .pcc60
 cmpi.w #$cc6d,d0
 beq.w .pcc6d
 cmpi.w #$d57a,d0
 beq.w .pd57a
 cmpi.w #$d583,d0
 beq.w .pd583
 cmpi.w #$d588,d0
 beq.w .pd588
 cmpi.w #$d5a5,d0
 beq.w .pd5a5
 cmpi.w #$d5b0,d0
 beq.w .pd5b0
 cmpi.w #$d5b8,d0
 beq.w .pd5b8
 cmpi.w #$d5c3,d0
 beq.w .pd5c3
 cmpi.w #$d5ce,d0
 beq.w .pd5ce
 cmpi.w #$d62f,d0
 beq.w .pd62f
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
