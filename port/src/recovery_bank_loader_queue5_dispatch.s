; Additive genuine bank5 pending audio entry. No queue skipping or mapper spoofing.
recovery_bank_loader_queue5_dispatch:
 cmpi.w #$c0bf,(a1)
 bne.w recovery_bank_loader_input_dispatch
 cmpi.b #5,3(a4)
 bne.w recovery_bank_loader_input_dispatch
 movem.l d1-d7/a2-a6,-(sp)
 tst.l d2
 bne.w .invalid
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.w .invalid
 tst.b $f6(a0)
 bne.w .invalid
 moveq #0,d3
 move.b $db(a0),d3
 cmpi.b #8,d3
 bhs.w .invalid
 cmpi.b #$88,$dc(a0,d3.w)
 beq.s .empty
 moveq #70,d6
 lea recovery_nmi_audio_entry(pc),a6
 bra.s .invoke
.empty:
 moveq #41,d6
 lea recovery_music_empty_queue_entry(pc),a6
.invoke:
 jsr (a6)
 cmpi.l #1,d0
 bne.w .done
 move.w d6,6(a4)
 move.w #22,8(a4)
.mapper:
 moveq #0,d7
 move.w (a2),d7
 subq.w #1,d7
 bmi.s .done
 lea 2(a2),a3
.record:
 moveq #0,d3
 move.w (a3)+,d3
 moveq #0,d4
 move.b (a3)+,d4
 addq.l #1,a3
 cmpi.w #$8000,d3
 bcs.s .next
 btst #7,d4
 beq.s .bit
 clr.w 4(a4)
 ori.b #12,(a4)
 bra.s .next
.bit:
 andi.l #1,d4
 moveq #0,d5
 move.b 5(a4),d5
 lsl.b d5,d4
 or.b d4,4(a4)
 addq.b #1,5(a4)
 cmpi.b #5,5(a4)
 bne.s .next
 lsr.w #8,d3
 lsr.w #5,d3
 andi.w #3,d3
 move.b 4(a4),(a4,d3.w)
 clr.w 4(a4)
.next:
 dbra d7,.record
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
