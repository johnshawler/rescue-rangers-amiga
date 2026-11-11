; Original PRG bank 3 $8003 command $F0, startup CF=0, return to fixed $C0F3.
; A0=2048-byte RAM, A1=8-byte context, A2=30-byte APU journal.
; Journal count.w then seven {address.w,data.b,kind.b}; kind=1 write.
; Caller selects bank-3 implementation; this is not a runtime mapper/interpreter.
; Require PC=$8003,A=$F0,CF=0 and original RTS frame $C0F2 at SP+1/SP+2.
; D0=1 at $C0F3; -1 invalid/inert. Other D/A preserved; CCR scratch.
recovery_audio_reset_command:
        movem.l d1-d5/a3,-(sp)
        cmpi.w  #$8003,(a1)
        bne.w   .invalid
        cmpi.b  #$f0,2(a1)
        bne.w   .invalid
        tst.b   $cf(a0)
        bne.w   .invalid
        moveq   #0,d4
        move.b  6(a1),d4
        addq.b  #1,d4
        cmpi.b  #$f2,$100(a0,d4.w)
        bne.w   .invalid
        addq.b  #1,d4
        cmpi.b  #$c0,$100(a0,d4.w)
        bne.w   .invalid
        subq.b  #2,d4
        clr.w   (a2)
        lea     2(a2),a3
        addq.b  #1,$c0(a0)
; Outer JSR $80E9 return $80E5.
        move.b  #$80,d1
        bsr.w   .push
        move.b  #$e5,d1
        bsr.w   .push
        move.b  4(a1),$c3(a0)
; Stack dispatcher JSR $8023 return $8183, consumed by dispatcher PLAs.
        move.b  #$81,d1
        bsr.w   .push
        move.b  #$83,d1
        bsr.w   .push
        addq.b  #1,d4
        move.b  #$83,$c1(a0)
        addq.b  #1,d4
        move.b  #$81,$c2(a0)
; ROM's first command-table target is $8194, via temporary PHA/PLA.
        move.b  #$94,d1
        bsr.w   .push
        move.b  #$81,$c2(a0)
        addq.b  #1,d4
        move.b  #$94,$c1(a0)
; JSR $81B3 at $8194 returns to $8197.
        move.b  #$81,d1
        bsr.w   .push
        move.b  #$96,d1
        bsr.w   .push
        moveq   #3,d3
.channels:
        move.b  #0,$754(a0,d3.w)
        move.b  #0,$750(a0,d3.w)
        dbra    d3,.channels
; PHA saved CF=0; four mute subcalls, X=3 down to 0.
        moveq   #0,d1
        bsr.w   .push
        moveq   #0,d5
.mute:
        move.b  #$81,d1
        bsr.w   .push
        move.b  #$cc,d1
        bsr.w   .push
        move.w  #$4000,d2
        add.w   d5,d2
        moveq   #$30,d1
        cmpi.w  #8,d5
        bne.s   .publish_mute
        moveq   #0,d1
.publish_mute:
        bsr.w   .publish
        addq.b  #2,d4
        move.b  #0,$cf(a0)
        addq.w  #4,d5
        cmpi.w  #16,d5
        bne.s   .mute
; Restore CF, reset sweeps and enable pulse/triangle/noise without DMC.
        addq.b  #1,d4
        move.b  #0,$cf(a0)
        moveq   #8,d1
        move.w  #$4001,d2
        bsr.w   .publish
        move.w  #$4005,d2
        bsr.w   .publish
        moveq   #$0f,d1
        move.w  #$4015,d2
        bsr.w   .publish
        addq.b  #2,d4
        move.b  #0,$ce(a0)
        move.b  #0,$d0(a0)
        move.b  #0,$d1(a0)
        move.b  #0,$d7(a0)
        move.b  #0,$d8(a0)
; CF remains zero, so original skips the second conditional mute pass.
        addq.b  #2,d4
        subq.b  #1,$c0(a0)
        addq.b  #2,d4
        move.w  #$c0f3,(a1)
        move.b  #0,2(a1)
        move.b  #$ff,3(a1)
        move.b  #$0c,4(a1)
        andi.b  #$7c,5(a1)
        move.b  $c0(a0),d1
        bne.s   .nonzero
        ori.b   #2,5(a1)
.nonzero:
        andi.b  #$80,d1
        or.b    d1,5(a1)
        move.b  d4,6(a1)
        movem.l (sp)+,d1-d5/a3
        moveq   #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d5/a3
        moveq   #-1,d0
        rts
.push:
        move.b  d1,$100(a0,d4.w)
        subq.b  #1,d4
        rts
.publish:
        move.w  d2,(a3)+
        move.b  d1,(a3)+
        move.b  #1,(a3)+
        addq.w  #1,(a2)
        rts
