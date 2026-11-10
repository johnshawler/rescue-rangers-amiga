; Recovery-only static translation: fixed PRG bank 7 $FE24 .. $FE42.
; A0: writable 2048-byte original RAM; A1: 8-byte context:
;   +0 PC (big-endian word), +2 A, +3 X, +4 Y, +5 P, +6 SP, +7 reserved.
; Requires PC=$FE24 and Y=0, following completed original hardware warmup.
; Returns D0=1 at untranslated boundary $FE43, or -1 for invalid context.
; D1-D7/A0-A6 preserved; CCR scratch. No MMIO or target CPU interpreter.
; RAM/context must be disjoint valid buffers; caller excludes concurrent access.
recovery_reset_ram:
        cmpi.w  #$fe24,(a1)
        bne.w   .invalid
        tst.b   4(a1)
        bne.w   .invalid
        movem.l d1-d2/a2,-(sp)
; TYA; STA $0000,Y; DEY/BNE: do not replace with a forward bulk clear.
        moveq   #0,d1
        move.b  #0,(a0)
        move.w  #255,d1
.zp:
        move.b  #0,(a0,d1.w)
        subq.w  #1,d1
        bne.s   .zp
; INC $01; STA ($00),Y. Keep page-pointer writes interleaved.
        moveq   #1,d2
        lea     $100(a0),a2
.page:
        addq.b  #1,1(a0)
        move.w  #255,d1
.bytes:
        move.b  #0,(a2)+
        dbra    d1,.bytes
        addq.w  #1,d2
        cmpi.w  #8,d2
        bne.s   .page
; LDX $01 was 7; original queue stores descend to X=$FF.
        moveq   #7,d1
.queue:
        move.b  #$88,$dc(a0,d1.w)
        dbra    d1,.queue
        move.b  #$1e,$fe(a0)
; Exact original register boundary. CMP #7 leaves C=1, final LDA clears N/Z.
        move.w  #$fe43,(a1)
        move.b  #$1e,2(a1)
        move.b  #$ff,3(a1)
        andi.b  #$7c,5(a1)
        ori.b   #1,5(a1)
        movem.l (sp)+,d1-d2/a2
        moveq   #1,d0
        rts
.invalid:
        moveq   #-1,d0
        rts
