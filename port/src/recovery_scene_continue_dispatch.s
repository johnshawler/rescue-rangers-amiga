; Additive state-selected scene preparation over unchanged active-SFX runtime.
; Same RAM/context/journal134638/runtime12/resource131072 ABI; stack >=1KiB.
; IDs73 post entry,74 palette,75 hide,76 scene fade,77 scene resume,78 clear.
; No completed RTI IDs added. FF53 remains explicit unsupported boundary.
recovery_scene_continue_dispatch:
 cmpi.w #$c5f8,(a1)
 beq.w .post
 cmpi.w #$9000,(a1)
 beq.w .post
 cmpi.w #$f3c9,(a1)
 beq.w .post
 cmpi.w #$c274,(a1)
 beq.w .palette
 cmpi.w #$f3cf,(a1)
 beq.w .hide
 cmpi.w #$f3d2,(a1)
 beq.w .hide
 cmpi.w #$f3d5,(a1)
 beq.w .prepare
 cmpi.b #2,3(a4)
 bne.w recovery_state_menu_sfx
 cmpi.w #$c2a8,(a1)
 beq.s .fade_check
 cmpi.w #$fe8d,(a1)
 bne.w recovery_state_menu_sfx
 cmpi.b #4,$80(a0)
 bne.w recovery_state_menu_sfx
 movem.l d3,-(sp)
 moveq #0,d3
 move.b $82(a0),d3
 addq.b #3,d3
 cmpi.b #$d4,$100(a0,d3.w)
 bne.s .delegate
 addq.b #1,d3
 cmpi.b #$f3,$100(a0,d3.w)
 bne.s .delegate
 movem.l (sp)+,d3
 bra.w .resume
.fade_check:
 movem.l d3,-(sp)
 moveq #0,d3
 move.b 6(a1),d3
 addq.b #2,d3
 cmpi.b #$ce,$100(a0,d3.w)
 bne.s .delegate
 addq.b #1,d3
 cmpi.b #$f3,$100(a0,d3.w)
 bne.s .delegate
 movem.l (sp)+,d3
 bra.s .fade
.delegate:
 movem.l (sp)+,d3
 bra.w recovery_state_menu_sfx
.post:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #73,d6
 lea recovery_post_confirmation_entry(pc),a6
 bra.s .scratch
.palette:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #74,d6
 lea recovery_scene_palette_entry(pc),a6
 bra.s .scratch
.hide:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #75,d6
 lea recovery_scene_sprite_hide(pc),a6
 bra.s .scratch
.fade:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #76,d6
 lea recovery_startup_fade_continue(pc),a6
 bra.s .scratch
.resume:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #77,d6
 moveq #74,d7
 lea recovery_general_task_scheduler(pc),a6
 bra.s .validate
.prepare:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #78,d6
 move.w #4382,d7
 lea recovery_scene_continue_prepare(pc),a6
 bra.s .validate
.scratch:
 moveq #0,d7
.validate:
 cmpi.w #$d501,10(a4)
 bne.w .invalid
 tst.w 4(a4)
 bne.w .invalid
 tst.l d2
 bne.w .invalid
 cmpi.b #$1e,(a4)
 bne.w .invalid
 cmpi.b #2,3(a4)
 bne.w .invalid
 move.b 5(a1),d3
 andi.b #$30,d3
 cmpi.b #$20,d3
 bne.w .invalid
 cmpi.w #77,d6
 beq.s .invoke
 tst.b $91(a0)
 bne.w .invalid
 cmpi.b #2,$80(a0)
 bne.w .invalid
 tst.w d7
 bne.s .invoke
 suba.w #512,sp
 movea.l sp,a2
 jsr (a6)
 adda.w #512,sp
 cmpi.l #-1,d0
 beq.s .done
 moveq #1,d0
 bra.s .publish
.invoke:
 jsr (a6)
 cmpi.l #1,d0
 bne.s .done
.publish:
 move.w d6,6(a4)
 move.w d7,8(a4)
.done:
 movem.l (sp)+,d1-d7/a2-a6
 rts
.invalid:
 moveq #-1,d0
 bra.s .done
