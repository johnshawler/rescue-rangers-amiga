; Fixed-bank $C0BF through JSR at $C0F0; STOP before bank-3 $8003 executes.
; A0=2048-byte RAM, A1=8-byte context, A2=22-byte mapper publication journal.
; Journal count.w then five {address.w,data.b,busy.b}, matching mapper helper.
; Require PC=$C0BF, F5=0, DB<8, current DC+DB != $88. Reject before mutation.
; D0=1 at $8003, -1 invalid/inert; all other D/A preserved, CCR scratch.
recovery_nmi_audio_entry:
        movem.l d1-d5/a3,-(sp)
        cmpi.w  #$c0bf,(a1)
        bne.w   .invalid
        tst.b   $f5(a0)
        bne.w   .invalid
        cmpi.b  #8,$db(a0)
        bcc.w   .invalid
        moveq   #0,d3
        move.b  $db(a0),d3
        moveq   #0,d5
        move.b  $dc(a0,d3.w),d5
        cmpi.b  #$88,d5
        beq.w   .invalid
        clr.w   (a2)
        lea     2(a2),a3
        moveq   #3,d1
        moveq   #4,d2
.serial:
        move.w  #$fff0,(a3)+
        move.b  d1,(a3)+
        move.b  #0,(a3)+
        addq.w  #1,(a2)
        lsr.b   #1,d1
        dbra    d2,.serial
; Original PHA/PLA temporarily saves command; original JSR then overwrites it.
        moveq   #0,d4
        move.b  6(a1),d4
        move.b  d5,$100(a0,d4.w)
        move.b  #$88,$dc(a0,d3.w)
        addq.b  #1,d3
        move.b  d3,d1
        andi.b  #7,d1
        move.b  d1,$db(a0)
        move.b  #$c0,$100(a0,d4.w)
        subq.b  #1,d4
        move.b  #$f2,$100(a0,d4.w)
        subq.b  #1,d4
        move.w  #$8003,(a1)
        move.b  d5,2(a1)
        move.b  d3,3(a1)
        move.b  d4,6(a1)
        andi.b  #$7c,5(a1)
        tst.b   d5
        bne.s   .nonzero
        ori.b   #2,5(a1)
.nonzero:
        move.b  d5,d1
        andi.b  #$80,d1
        or.b    d1,5(a1)
        cmpi.b  #$88,d5
        bcs.s   .done
        ori.b   #1,5(a1)
.done:
        movem.l (sp)+,d1-d5/a3
        moveq   #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d5/a3
        moveq   #-1,d0
        rts
