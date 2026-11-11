; Bounded original $C574 through first $FF04 yield, stop at $FE8D.
; A0=2048-byte RAM, A1=8-byte boundary context, A2=6-byte PPU journal.
; Journal count.w then {address.w,data.b,kind.b}; kind=1 means write.
; Require PC=$C574, task selector $91=0, queue index $DA<8.
; D0=1 at untranslated $FE8D; -1 invalid/inert. All other D/A preserved.
; No audio playback, actual PPU MMIO, or asynchronous NMI/IRQ execution.
recovery_first_yield:
        cmpi.w  #$c574,(a1)
        bne.w   .invalid
        tst.b   $91(a0)
        bne.w   .invalid
        cmpi.b  #8,$da(a0)
        bcc.w   .invalid
        movem.l d1-d2,-(sp)
; Original LDX #$BF/TXS, followed by LDA $FF/STA $2000.
        clr.w   (a2)
        move.w  #$2000,2(a2)
        move.b  $ff(a0),4(a2)
        move.b  #1,5(a2)
        move.w  #1,(a2)
; JSR $F377 pushes $C580 with original SP=$BF.
        move.b  #$c5,$1bf(a0)
        move.b  #$80,$1be(a0)
        move.b  #$f0,$d9(a0)
        move.b  #$bf,(a0)
        moveq   #0,d1
        move.b  $da(a0),d1
        move.b  #$f0,1(a0)
        cmpi.b  #$88,$dc(a0,d1.w)
        bne.s   .queue_done
        move.b  #$f0,$dc(a0,d1.w)
        addq.b  #1,d1
        andi.b  #7,d1
        move.b  d1,$da(a0)
.queue_done:
; JSR $FF04 pushes $C583 after the sound helper's RTS restored SP=$BF.
        move.b  #$c5,$1bf(a0)
        move.b  #$83,$1be(a0)
        move.b  #1,$93(a0)
; Save X=$BF and original Y exactly, then nested JSR $FEF7 pushes $FF0E.
        move.b  #$bf,$1bd(a0)
        move.b  4(a1),$1bc(a0)
        move.b  #$ff,$1bb(a0)
        move.b  #$0e,$1ba(a0)
; Guarded task zero: $FEF7/$FEF9 returns X=0. Save timer/state/SP.
        move.b  $93(a0),$81(a0)
        move.b  #1,$80(a0)
        move.b  #$bb,$82(a0)
; Stop before scheduler re-entry at $FE8D resets the original stack.
        move.w  #$fe8d,(a1)
        move.b  #0,2(a1)
        move.b  #$bb,3(a1)
        move.b  #0,4(a1)
        andi.b  #$7c,5(a1)
        ori.b   #$80,5(a1)
        move.b  #$bb,6(a1)
        movem.l (sp)+,d1-d2
        moveq   #1,d0
        rts
.invalid:
        moveq   #-1,d0
        rts
