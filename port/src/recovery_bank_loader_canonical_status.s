; Explicit adapter from raw helper status to the established live context ABI.
; The live ABI represents physical P flags with U=1/B=0 at boundaries.
; B is not a processor latch: PHP/BRK force its stack image to1, NMI/IRQ to0.
; Call ONLY after a successful raw helper, after its original stack effects.
; This never changes N,V,U,D,I,Z,C. It is not part of raw helper contracts.
; A1 context8; data/address registers including D0 and native SP preserved.
; Native CCR is clobbered, as permitted by the existing helper ABI.
recovery_bank_loader_canonical_status:
 andi.b #$ef,5(a1)
 rts
