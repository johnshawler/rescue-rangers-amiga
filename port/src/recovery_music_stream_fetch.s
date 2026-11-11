; Static reusable channel3 stream fetch,839D ->83A0. No CPU interpreter.
; A0=2KiB RAM,A1=8-byte canonical context,A2=6-byte resource journal,
; A3=read-only16KiB bank3 view. Valid/disjoint/owned buffers required.
; PC839D,X2B,canonical P and pointer8000..BFFF required. D allowed.
; Journal count.w then address.w,value.b,kind.b=0; exactly one read.
; D0=1 success,-1 inert; D1-D7/A0-A6 preserved; native stack balanced.
recovery_music_stream_fetch:
        movem.l d1-d7,-(sp)
        cmpi.w #$839d,(a1)
        bne.w .invalid
        cmpi.b #$2b,3(a1)
        bne.w .invalid
        move.b 5(a1),d1
        andi.b #$30,d1
        cmpi.b #$20,d1
        bne.w .invalid
        moveq #0,d6
        move.b $757(a0),d6
        lsl.w #8,d6
        move.b $753(a0),d6
        cmpi.w #$8000,d6
        bcs.w .invalid
        cmpi.w #$bfff,d6
        bhi.w .invalid
        moveq #0,d4
        move.b 6(a1),d4
        clr.w (a2)
        move.b #$83,d1
        bsr.w .push
        move.b #$9f,d1
        bsr.w .push
        move.b $753(a0),$c1(a0)
        move.b $757(a0),$c2(a0)
        move.w d6,2(a2)
        subi.w #$8000,d6
        move.b (a3,d6.w),d7
        move.b d7,4(a2)
        move.b #0,5(a2)
        move.w #1,(a2)
        addq.b #1,$753(a0)
        move.b $753(a0),d1
        bne.s .pointer_ready
        addq.b #1,$757(a0)
        move.b $757(a0),d1
.pointer_ready:
        move.b 5(a1),d2
        andi.b #$6d,d2
        tst.b d1
        bne.s .nonzero
        ori.b #2,d2
.nonzero:
        andi.b #$80,d1
        or.b d1,d2
        move.w #$83a0,(a1)
        move.b d7,2(a1)
        move.b #0,4(a1)
        move.b d2,5(a1)
        addq.b #2,d4
        move.b d4,6(a1)
        movem.l (sp)+,d1-d7
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d7
        moveq #-1,d0
        rts
.push:
        move.b d1,$100(a0,d4.w)
        subq.b #1,d4
        rts
