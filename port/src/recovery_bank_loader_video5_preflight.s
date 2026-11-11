; Read-only validation for bank5 queued-NMI waiting and service.
; Identical finite-script admission as the frozen combined NMI98; no mutation.
recovery_bank_loader_video5_preflight:
 movem.l d1-d7,-(sp)
 move.b $f0(a0),d1
 or.b $9a(a0),d1
 bne.s .accepted
 moveq #0,d7
 tst.b $1c(a0)
 beq.s .next1d
 move.w #$80,d3
 bsr.w .validate_script
 tst.l d0
 bmi.s .done
.next1d:
 tst.b $1d(a0)
 beq.s .next19
 moveq #$58,d3
 bsr.w .validate_script
 tst.l d0
 bmi.s .done
.next19:
 tst.b $19(a0)
 beq.s .accepted
 moveq #0,d3
 bsr.w .validate_script
 tst.l d0
 bmi.s .done
.accepted:
 moveq #1,d0
.done:
 movem.l (sp)+,d1-d7
 rts
.validate_script:
        move.w #255,d6
.validate_command:
        tst.b $360(a0,d3.w)
        bmi.s .validate_ok
        moveq #0,d5
        move.b $362(a0,d3.w),d5
        cmpi.w #128,d5
        bls.s .length
        moveq #0,d5
.length:
        addq.w #3,d5
        add.l d5,d7
        cmpi.l #33500,d7
        bhi.s .validate_bad
        addq.w #1,d5
        add.b d5,d3
        beq.s .validate_ok
        dbra d6,.validate_command
.validate_bad:
        moveq #-1,d0
        rts
.validate_ok:
        moveq #1,d0
        rts
