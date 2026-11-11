; Additive bounded extension. Frozen prefix remains separately callable.
; Same ABI as prefix plus A5 = immutable contiguous 8*16KiB PRG resource.
; No pointer probing: valid aligned disjoint buffers remain caller obligations.
; D0 result 1/0/-1; D1-D7/A0-A6 and exact native SP preserved.
; IDs 11=palette NMI, 12=music07. No schedule or speculative helper trials.
recovery_state_dispatch_palette:
        cmpi.w #$fe8d,(a1)
        bne.s .music_select
        tst.b $18(a0)
        bne.w .palette
.music_select:
        cmpi.w #$8003,(a1)
        bne.s .terminal
        cmpi.b #7,2(a1)
        beq.w .music
.terminal:
        cmpi.w #$c0f3,(a1)
        bne.s .prefix
        tst.b $c9(a0)
        bne.w .invalid
.prefix:
        bra.w recovery_state_dispatch_prefix
.palette:
        cmpi.w #$d501,10(a4)
        bne.w .invalid
        tst.w 4(a4)
        bne.w .invalid
        cmpi.b #$1e,(a4)
        bne.w .invalid
        cmpi.b #6,3(a4)
        bne.w .invalid
        cmpi.l #1,d2
        bhi.w .invalid
        cmpi.b #1,$80(a0)
        bne.w .invalid
; Validate even idle polls; no candidate helper is run to discover readiness.
        movem.l d3,-(sp)
        move.b 5(a1),d3
        andi.b #$30,d3
        cmpi.b #$20,d3
        bne.s .palette_bad
        btst #7,$ff(a0)
        beq.s .palette_bad
        move.b $f0(a0),d3
        or.b $9a(a0),d3
        or.b $19(a0),d3
        or.b $1a(a0),d3
        or.b $1b(a0),d3
        or.b $1c(a0),d3
        or.b $1d(a0),d3
        bne.s .palette_bad
        movem.l (sp)+,d3
        tst.l d2
        beq.s .wait
        bsr.w recovery_palette_nmi_prefix
        cmpi.l #1,d0
        bne.s .return
        move.w #11,6(a4)
        move.w #454,8(a4)
.return:
        rts
.palette_bad:
        movem.l (sp)+,d3
        bra.w .invalid
.wait:
        moveq #0,d0
        rts
.music:
        cmpi.w #$d501,10(a4)
        bne.w .invalid
        tst.w 4(a4)
        bne.w .invalid
        tst.l d2
        bne.w .invalid
        cmpi.b #$1e,(a4)
        bne.w .invalid
; Exact supported mapping obligation. Read bank offset from live mapper,
; never a cached bank pointer or selected-helper metadata.
        cmpi.b #3,3(a4)
        bne.w .invalid
        movem.l d3/a3,-(sp)
        moveq #0,d3
        move.b 3(a4),d3
        andi.l #7,d3
        lsl.l #7,d3
        lsl.l #7,d3
        lea (a5,d3.l),a3
        bsr.w recovery_music07_command
        movem.l (sp)+,d3/a3
        cmpi.l #1,d0
        bne.s .return
        move.w #12,6(a4)
        move.w #30,8(a4)
        rts
.invalid:
        moveq #-1,d0
        rts
