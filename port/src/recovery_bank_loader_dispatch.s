; Additive bank2 interstitial continuation; ABI of scene dispatch unchanged.
; ID79 mapper22,80 prefix6,81 loader32770,82 second0,83 assets154.
; All unsupported guards inert. F6 nonzero is explicitly unsupported atFF53.
recovery_bank_loader_dispatch:
 cmpi.w #$ff53,(a1)
 beq.w .restore
 cmpi.b #2,3(a4)
 bne.w recovery_scene_continue_dispatch
 cmpi.w #$9003,(a1)
 beq.w .prefix
 cmpi.w #$8000,(a1)
 beq.w .resource
 cmpi.w #$9034,(a1)
 beq.w .second
 cmpi.w #$9039,(a1)
 beq.w .assets
 cmpi.w #$9041,(a1)
 beq.w .assets
 cmpi.w #$f3e5,(a1)
 beq.w .enable
 cmpi.w #$f3ee,(a1)
 beq.w .fade_entry
 cmpi.w #$f3f1,(a1)
 beq.w .pop
 cmpi.w #$910c,(a1)
 beq.w .tail
 cmpi.w #$c2a8,(a1)
 beq.s .fade_check
 cmpi.w #$fe8d,(a1)
 bne.w recovery_scene_continue_dispatch
 cmpi.b #4,$80(a0)
 bne.w recovery_scene_continue_dispatch
 movem.l d3,-(sp)
 moveq #0,d3
 move.b $82(a0),d3
 addq.b #3,d3
 cmpi.b #$ed,$100(a0,d3.w)
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
 cmpi.b #$f0,$100(a0,d3.w)
 bne.s .delegate
 addq.b #1,d3
 cmpi.b #$f3,$100(a0,d3.w)
 bne.s .delegate
 movem.l (sp)+,d3
 bra.w .fade_continue
.delegate:
 movem.l (sp)+,d3
 bra.w recovery_scene_continue_dispatch
.enable:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #84,d6
 moveq #6,d7
 lea recovery_bank_loader_fade(pc),a6
 bra.w .validate
.fade_entry:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #85,d6
 moveq #0,d7
 lea recovery_bank_loader_fade_entry(pc),a6
 bra.w .validate
.fade_continue:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #86,d6
 moveq #0,d7
 lea recovery_startup_fade_continue(pc),a6
 bra.w .validate
.resume:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #87,d6
 moveq #74,d7
 lea recovery_general_task_scheduler(pc),a6
 bra.w .validate
.pop:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #88,d6
 moveq #0,d7
 lea recovery_bank_loader_fade(pc),a6
 bra.w .validate
.tail:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #89,d6
 moveq #0,d7
 lea recovery_bank_loader_fade(pc),a6
 bra.w .validate
.restore:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #79,d6
 moveq #22,d7
 lea recovery_bank_loader_restore(pc),a6
 bra.w .validate
.prefix:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #80,d6
 moveq #6,d7
 lea recovery_bank_loader_prefix(pc),a6
 bra.w .validate
.resource:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #81,d6
 move.w #32770,d7
 lea recovery_bank_loader_resource(pc),a6
 bra.s .validate
.second:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #82,d6
 moveq #0,d7
 lea recovery_bank_loader_second(pc),a6
 bra.s .validate
.assets:
 movem.l d1-d7/a2-a6,-(sp)
 moveq #83,d6
 move.w #154,d7
 lea recovery_bank_loader_assets(pc),a6
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
 cmpi.w #87,d6
 beq.s .view
 tst.b $91(a0)
 bne.w .invalid
 cmpi.b #2,$80(a0)
 bne.w .invalid
 ; Restore is qualified here only for the current interstitial bank2.
 cmpi.w #79,d6
 bne.s .view
 cmpi.b #2,2(a1)
 bne.s .invalid
.view:
 movea.l a5,a3
 adda.l #32768,a3
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
