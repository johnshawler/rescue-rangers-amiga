; Static C0F9..C114 native translation. No ROM/interpreter/captured frame.
; A0=2048 RAM, A1=8-byte PC/A/X/Y/P/S/reserved context, A2=22-byte journal.
; Valid disjoint exclusive buffers. D0=1 success / -1 inert unsupported.
; D1-D7/A0-A6 preserved, balanced native stack, CCR scratch.
; F6 is not read or written: pending deferred work remains pending.
; Mapper adapter must apply all five original bytes (including MMC1 resets),
; and supply fixed bank7 at C000: control PRG mode3 on entry. No latch or
; bank is silently reset here. F1/F5, RAM and original saved frame untouched.
; Canonical architectural status output B=0 U=1; other six bits from RTI.
recovery_active_nmi_return:
        movem.l d1-d3/a3,-(sp)
        cmpi.w #$c0f9,(a1)
        bne.w .invalid
        clr.w (a2)
        lea 2(a2),a3
        move.b $f1(a0),d1
        moveq #4,d2
.publish:
        move.w #$fff0,(a3)+
        move.b d1,(a3)+
        move.b $f5(a0),(a3)+
        addq.w #1,(a2)
        lsr.b #1,d1
        dbra d2,.publish
; Seven original frame reads, each with page-one wrap. The intervening PLP
; is fully overwritten by RTI; consume its byte without changing saved RAM.
        moveq #0,d2
        move.b 6(a1),d2
        lea $100(a0),a3
        addq.b #1,d2
        move.b (a3,d2.w),4(a1)
        addq.b #1,d2
        move.b (a3,d2.w),3(a1)
        addq.b #1,d2
        move.b (a3,d2.w),2(a1)
        addq.b #1,d2
        move.b (a3,d2.w),d3
        addq.b #1,d2
        move.b (a3,d2.w),d3
        andi.b #$ef,d3
        ori.b #$20,d3
        move.b d3,5(a1)
        addq.b #1,d2
        move.b (a3,d2.w),1(a1)
        addq.b #1,d2
        move.b (a3,d2.w),(a1)
        move.b d2,6(a1)
        movem.l (sp)+,d1-d3/a3
        moveq #1,d0
        rts
.invalid:
        movem.l (sp)+,d1-d3/a3
        moveq #-1,d0
        rts
