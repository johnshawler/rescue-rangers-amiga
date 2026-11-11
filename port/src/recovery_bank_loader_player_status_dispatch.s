; Additive input-path ABI publication. The raw player helper remains unchanged.
; Only a successful helper140 result is converted to the existing canonical P ABI.
recovery_bank_loader_player_status_dispatch:
 bsr.w recovery_bank_loader_player_contact_dispatch
 cmpi.l #1,d0
 bne.s .done
 cmpi.w #140,6(a4)
 bne.s .done
 movem.l a6,-(sp)
 lea recovery_bank_loader_canonical_status(pc),a6
 jsr (a6)
 movem.l (sp)+,a6
.done:
 rts
