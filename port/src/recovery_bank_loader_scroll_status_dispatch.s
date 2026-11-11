; Additive input-path ABI publication. The raw scroll helper remains unchanged.
; Only a successful helper160 result is converted to the existing canonical P ABI.
recovery_bank_loader_scroll_status_dispatch:
 bsr.w recovery_bank_loader_envelope_dispatch
 cmpi.l #1,d0
 bne.s .done
 cmpi.w #160,6(a4)
 bne.s .done
 movem.l a6,-(sp)
 lea recovery_bank_loader_canonical_status(pc),a6
 jsr (a6)
 movem.l (sp)+,a6
.done:
 rts
