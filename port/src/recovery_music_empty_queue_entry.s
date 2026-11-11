; Static fixed-bank C0BF→C0F6, empty audio-command queue only.
; A0 RAM2048,A1 context8,A2 mapper journal22. No resource view needed.
; Require F5=0,DB<8,DC[DB]=88; otherwise inert reject. All status bytes accepted.
; D0=1/-1; D1-D7/A0-A6 preserved; RAM unchanged; no skipped pending work.
recovery_music_empty_queue_entry:
 movem.l d1-d3/a3,-(sp)
 cmpi.w #$c0bf,(a1)
 bne.s .reject
 tst.b $f5(a0)
 bne.s .reject
 moveq #0,d3
 move.b $db(a0),d3
 cmpi.b #8,d3
 bcc.s .reject
 cmpi.b #$88,$dc(a0,d3.w)
 bne.s .reject
 clr.w (a2)
 lea 2(a2),a3
 moveq #3,d1
 moveq #4,d2
.next:
 move.w #$fff0,(a3)+
 move.b d1,(a3)+
 move.b $f5(a0),(a3)+
 addq.w #1,(a2)
 lsr.b #1,d1
 dbra d2,.next
 move.w #$c0f6,(a1)
 move.b #$88,2(a1)
 move.b d3,3(a1)
 andi.b #$7c,5(a1)
 ori.b #3,5(a1)
 moveq #1,d0
 bra.s .done
.reject:
 moveq #-1,d0
.done:
 movem.l (sp)+,d1-d3/a3
 rts
