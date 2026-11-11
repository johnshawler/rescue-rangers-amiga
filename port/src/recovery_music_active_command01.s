; Static indexed music command01, toggles channel bit40 without consuming data.
; A0 RAM2048,A1 context8,A2 journal10,A3 immutable bank3. Raw P preserved except original flag effects.
; D0=1/-1 inert; D1-D7/A0-A6 preserved. No opcode decoder.
recovery_music_active_command01:
 movem.l d1-d7/a4-a6,-(sp)
 cmpi.w #$83a0,(a1)
 bne.w .reject
 cmpi.b #1,2(a1)
 bne.w .reject
 moveq #0,d2
 move.b 3(a1),d2
 cmpi.b #$28,d2
 bcs.w .reject
 cmpi.b #$2b,d2
 bhi.w .reject
 cmpi.b #$b9,$485(a3)
 bne.w .reject
 cmpi.b #$84,$486(a3)
 bne.w .reject
 clr.w (a2)
 clr.l 2(a2)
 clr.l 6(a2)
 moveq #0,d1
 moveq #0,d3
 moveq #0,d4
 move.b 2(a1),d1
 move.b 4(a1),d3
 move.b 5(a1),d5
 move.b 6(a1),d4
 bsr.w .p83a0
 move.w #$839d,(a1)
 move.b d1,2(a1)
 move.b d2,3(a1)
 move.b d3,4(a1)
 move.b d5,5(a1)
 move.b d4,6(a1)
 moveq #1,d0
 bra.s .done
.reject:
 moveq #-1,d0
.done:
 movem.l (sp)+,d1-d7/a4-a6
 rts
.p839d:
 rts
.p83aa:
 illegal
.p8023: ; ASL A
 move.b d1,d6
 bsr.w .asl
 move.b d6,d1
.p8024: ; TAY
 move.b d1,d3
 move.b d3,d6
 bsr.w .nz
.p8025: ; INY
 addq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8026: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p8027: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p8029: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p802a: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p802c: ; LDA ($c1),Y
 moveq #0,d7
 move.b $c2(a0),d7
 lsl.w #8,d7
 move.b $c1(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p802e: ; PHA
 move.b d1,d6
 bsr.w .push
.p802f: ; INY
 addq.b #1,d3
 move.b d3,d6
 bsr.w .nz
.p8030: ; LDA ($c1),Y
 moveq #0,d7
 move.b $c2(a0),d7
 lsl.w #8,d7
 move.b $c1(a0),d7
 add.w d3,d7
 bsr.w .resource
 move.b d6,d1
 bsr.w .nz
.p8032: ; STA $c2
 move.l #$c2,d7
 move.b d1,(a0,d7.w)
.p8034: ; PLA
 bsr.w .pop
 move.b d6,d1
 bsr.w .nz
.p8035: ; STA $c1
 move.l #$c1,d7
 move.b d1,(a0,d7.w)
.p8037: ; JMP ($00c1)
 cmpi.b #$b9,$c1(a0)
 beq.w .p84b9
 illegal
.p83a0: ; CMP #$20
 moveq #0,d6
 move.b #$20,d6
 move.b d1,d0
 bsr.w .compare
.p83a2: ; BCS $83aa
 btst #0,d5
 bne.w .p83aa
.p83a4: ; JSR $8473
 move.b #$83,d6
 bsr.w .push
 move.b #$a6,d6
 bsr.w .push
 bsr.w .p8473
.p83a7: ; JMP $839d
 bra.w .p839d
.p8473: ; CMP #$04
 moveq #0,d6
 move.b #$04,d6
 move.b d1,d0
 bsr.w .compare
.p8475: ; BCC $8480
 btst #0,d5
 beq.w .p8480
.p8480: ; JSR $8023
 move.b #$84,d6
 bsr.w .push
 move.b #$82,d6
 bsr.w .push
 bra.w .p8023
.p84b9: ; LDA #$40
 moveq #$40,d1
 move.b d1,d6
 bsr.w .nz
.p84bb: ; BNE $84c6 (immediate40 is nonzero)
.p84c6: ; EOR $0730,X
 move.l #$730,d7
 add.w d2,d7
 move.b (a0,d7.w),d6
 eor.b d6,d1
 move.b d1,d6
 bsr.w .nz
.p84c9: ; STA $0730,X
 move.l #$730,d7
 add.w d2,d7
 move.b d1,(a0,d7.w)
.p84cc: ; RTS
 bsr.w .pop
 moveq #0,d7
 move.b d6,d7
 bsr.w .pop
 lsl.w #8,d6
 or.w d6,d7
 addq.w #1,d7
 rts

.nz:
 andi.b #$7d,d5
 tst.b d6
 bne.s .nz_nonzero
 ori.b #2,d5
 rts
.nz_nonzero:
 bpl.s .nz_done
 ori.b #$80,d5
.nz_done:
 rts
.push:
 move.b d6,$100(a0,d4.w)
 subq.b #1,d4
 rts
.pop:
 addq.b #1,d4
 moveq #0,d6
 move.b $100(a0,d4.w),d6
 rts
.resource:
 move.l d7,-(sp)
 subi.w #$8000,d7
 moveq #0,d6
 move.b (a3,d7.w),d6
 move.l (sp)+,d7
 moveq #0,d0
 bra.s .journal
.apu:
 moveq #1,d0
.journal:
 move.l a4,-(sp)
 move.l d0,-(sp)
 moveq #0,d0
 move.w (a2),d0
 lsl.w #2,d0
 lea 2(a2,d0.w),a4
 move.w d7,(a4)
 move.b d6,2(a4)
 move.l (sp)+,d0
 move.b d0,3(a4)
 addq.w #1,(a2)
 move.l (sp)+,a4
 rts
.compare:
 andi.b #$fe,d5
 cmp.b d6,d0
 bcs.s .compare_nc
 ori.b #1,d5
.compare_nc:
 sub.b d6,d0
 move.b d0,d6
 bra.w .nz
.asl:
 andi.b #$fe,d5
 btst #7,d6
 beq.s .asl_nc
 ori.b #1,d5
.asl_nc:
 lsl.b #1,d6
 bra.w .nz
