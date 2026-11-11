; Newly authored static translation of fixed bank 7 $C6BD-$C6FF,
; including $F31D-$F327; stops BEFORE JSR $E096 at $C700.
; A0=2048-byte original RAM; A1=8-byte context: PC.w,A,X,Y,P,S,reserved.
; A2=256-byte ordered write journal, 4 bytes per event: address.w,value,0.
; Requires PC=C6BD and RAM[$50] in {0,1}. No resources or hardware used.
; D0=event count, or -1 with no mutations on invalid input.
; D1-D7/A0-A6 preserved, native CCR scratch. Context S and Y unchanged.
        xdef recovery_gameplay_player_init
recovery_gameplay_player_init:
        cmpi.w #$c6bd,(a1)
        bne.w .invalid
        cmpi.b #1,$50(a0)
        bhi.w .invalid
        movem.l d1-d7/a3,-(sp)
        movea.l a2,a3
        moveq #0,d5
        moveq #0,d4
        move.b $50(a0),d4
.player:
        moveq #0,d6
        cmpi.b #$0c,$54(a0,d4.w)
        bcs.s .carry_done
        moveq #1,d6
.carry_done:
        cmpi.b #$0c,$54(a0,d4.w)
        beq.w .next
        move.w #$4d0,d2
        add.w d4,d2
        move.b #$80,d3
        bsr.w .write
        move.w #$400,d2
        add.w d4,d2
        move.b #$d0,d3
        bsr.w .write
        move.w #$420,d2
        add.w d4,d2
        move.b $34c(a0,d4.w),d3
        bsr.w .write
        move.w #$510,d2
        add.w d4,d2
        move.b #$74,d3
        bsr.w .write
        moveq #0,d3
        move.w #$56,d2
        add.w d4,d2
        bsr.w .write
        move.w #$54,d2
        add.w d4,d2
        bsr.w .write
        move.w #$58,d2
        add.w d4,d2
        bsr.w .write
        move.w #$5c,d2
        add.w d4,d2
        bsr.w .write
; Original clears $5E (not $5E,X).
        move.w #$5e,d2
        bsr.w .write
        move.w #$430,d2
        add.w d4,d2
        bsr.w .write
        move.w #$410,d2
        add.w d4,d2
        bsr.w .write
; C6EC JSR F31D pushes return C6EE, including page-1 wrap at S=0.
        moveq #0,d7
        move.b 6(a1),d7
        move.w d7,d2
        ori.w #$100,d2
        move.b #$c6,d3
        bsr.w .write
        subq.b #1,d7
        move.w d7,d2
        ori.w #$100,d2
        move.b #$ee,d3
        bsr.w .write
        move.w #$550,d2
        add.w d4,d2
        move.b #$ab,d3
        bsr.w .write
        move.w #$560,d2
        add.w d4,d2
        move.b #$ff,d3
        bsr.w .write
.next:
        subq.w #1,d4
        bpl.w .player
        move.w #$4f0,d2
        move.b #$18,d3
        bsr.w .write
        move.w #$4f1,d2
        move.b #$30,d3
        bsr.w .write
        move.w #$99,d2
        move.b #$55,d3
        bsr.w .write
        move.w #$c700,(a1)
        move.b #$55,2(a1)
        move.b #$ff,3(a1)
        andi.b #$7c,5(a1)
        or.b d6,5(a1)
        move.l d5,d0
        movem.l (sp)+,d1-d7/a3
        rts
.write:
        move.b d3,(a0,d2.w)
        move.w d2,(a3)+
        move.b d3,(a3)+
        clr.b (a3)+
        addq.w #1,d5
        rts
.invalid:
        moveq #-1,d0
        rts
