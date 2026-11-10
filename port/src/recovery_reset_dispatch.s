; Bounded fixed-bank original $FE7C through first dispatch to $C574.
; Includes $FED5/$FEF9 initialization and ONLY the deterministic first scan.
; A0=2048-byte RAM; A1=8-byte original boundary context.
; PC must be $FE7C. D0=1 at untranslated $C574, -1 invalid/inert.
; D1-D7/A0-A6 preserved, CCR scratch, native stack balanced.
recovery_reset_dispatch:
        cmpi.w  #$fe7c,(a1)
        bne.w   .invalid
        move.l  d1,-(sp)
        move.b  #$c5,$94(a0)
        move.b  #$74,$93(a0)
        moveq   #0,d1
        move.b  6(a1),d1
; Original JSR $FED5 pushes $FE88, then its JSR $FEF9 pushes $FED7.
; Preserve all four stores and 8-bit original SP wrap, before TXS resets SP.
        move.b  #$fe,$100(a0,d1.w)
        subq.b  #1,d1
        move.b  #$88,$100(a0,d1.w)
        subq.b  #1,d1
        move.b  #$fe,$100(a0,d1.w)
        subq.b  #1,d1
        move.b  #$d7,$100(a0,d1.w)
; A=0 through $FEF9 produces task slot X=0.
        move.b  $93(a0),$82(a0)
        move.b  $94(a0),$83(a0)
        move.b  #8,$80(a0)
        move.b  #$90,$ff(a0)
; SP=$FF; first scan necessarily finds the newly created state-8 slot zero.
        move.b  #0,$90(a0)
        move.b  #0,$91(a0)
        move.b  #2,$80(a0)
        move.b  $82(a0),$93(a0)
        move.b  $83(a0),$94(a0)
; Stop before executing $C574. CPY #8 leaves C=1; final LDA $83 sets N.
        move.w  #$c574,(a1)
        move.b  #$c5,2(a1)
        move.b  #0,3(a1)
        move.b  #8,4(a1)
        andi.b  #$7c,5(a1)
        ori.b   #$81,5(a1)
        move.b  #$ff,6(a1)
        move.l  (sp)+,d1
        moveq   #1,d0
        rts
.invalid:
        moveq   #-1,d0
        rts
