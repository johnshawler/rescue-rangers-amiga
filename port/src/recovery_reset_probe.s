; Independent diagnostic probe. MUSIC07 and its continuations include private data.
; Exercises newly translated FE24 through first task dispatch, then stops.
; Boot enters user mode: use custom interrupt/DMA shutdown, no privileged SR write.
        lea     $dff000,a5
        move.w  #$7fff,$9a(a5)
        move.w  #$7fff,$96(a5)
        move.w  #$7fff,$9c(a5)
        move.w  #$0200,$100(a5)
        lea     probe_stack_end(pc),sp
        lea     probe_report(pc),a6
        lea     probe_ram(pc),a0
        lea     probe_context(pc),a1
        move.l  a0,16(a6)
        move.l  a1,20(a6)
        lea     probe_mapper(pc),a2
        move.l  a2,24(a6)
        lea     probe_video(pc),a3
        move.l  a3,28(a6)
        lea     probe_stack(pc),a3
        move.l  a3,32(a6)
        move.l  sp,36(a6)
        ifd MUSIC_FIRST_CHANNEL
        lea     probe_event_fetch08(pc),a3
        move.l  a3,120(a6)
        lea     probe_event_instrument08(pc),a3
        move.l  a3,124(a6)
        lea     probe_event_fetch18(pc),a3
        move.l  a3,128(a6)
        lea     probe_event_command18(pc),a3
        move.l  a3,132(a6)
        lea     probe_event_fetch09(pc),a3
        move.l  a3,136(a6)
        lea     probe_event_command09(pc),a3
        move.l  a3,140(a6)
        lea     probe_event_fetch_rest(pc),a3
        move.l  a3,144(a6)
        lea     probe_event_rest(pc),a3
        move.l  a3,148(a6)
        lea     probe_event_snapshots(pc),a3
        move.l  a3,152(a6)
        endc
        ifd MUSIC_CHANNEL_SETUP
        lea     probe_stream_fetch05(pc),a3
        move.l  a3,92(a6)
        lea     probe_command05(pc),a3
        move.l  a3,96(a6)
        lea     probe_stream_fetch06(pc),a3
        move.l  a3,100(a6)
        lea     probe_command06(pc),a3
        move.l  a3,104(a6)
        lea     probe_stream_fetch07(pc),a3
        move.l  a3,108(a6)
        lea     probe_stream_command07_volume(pc),a3
        move.l  a3,112(a6)
        lea     probe_snapshots(pc),a3
        move.l  a3,116(a6)
        endc
        ifd MUSIC_FETCH
        lea     probe_music_fetch(pc),a3
        move.l  a3,84(a6)
        endc
        ifd MUSIC_COMMAND04
        lea     probe_music_command04(pc),a3
        move.l  a3,88(a6)
        endc
        ifd MUSIC07
        lea     probe_music_entry(pc),a3
        move.l  a3,72(a6)
        lea     probe_music_apu(pc),a3
        move.l  a3,76(a6)
        lea     probe_music_resource(pc),a3
        move.l  a3,80(a6)
        endc
        ifd PALETTE_NMI
        lea     probe_palette_nmi(pc),a3
        move.l  a3,68(a6)
        endc
        ifd SCHEDULER_RESUME
        lea     probe_controller(pc),a3
        move.l  a3,64(a6)
        endc
        ifd NMI_RETURN
        lea     probe_restore(pc),a3
        move.l  a3,60(a6)
        endc
        ifd AUDIO_RESET
        lea     probe_apu(pc),a3
        move.l  a3,56(a6)
        endc
        ifd AUDIO_ENTRY
        lea     probe_nmi(pc),a3
        move.l  a3,48(a6)
        lea     probe_audio_entry(pc),a3
        move.l  a3,52(a6)
        endc
        ifd FIRST_YIELD
        lea     probe_yield(pc),a3
        move.l  a3,44(a6)
        endc
        bsr.w   recovery_reset_ram
        cmpi.l  #1,d0
        ifd AUDIO_ENTRY
        bne.w   probe_fail
        else
        bne.s   probe_fail
        endc
        addq.l  #1,12(a6)
        bsr.w   recovery_reset_mapper
        cmpi.l  #1,d0
        ifd AUDIO_ENTRY
        bne.w   probe_fail
        else
        bne.s   probe_fail
        endc
        addq.l  #1,12(a6)
        lea     probe_video(pc),a2
        bsr.w   recovery_reset_video
        cmpi.l  #1,d0
        ifd AUDIO_ENTRY
        bne.w   probe_fail
        else
        bne.s   probe_fail
        endc
        addq.l  #1,12(a6)
        bsr.w   recovery_reset_dispatch
        cmpi.l  #1,d0
        ifd AUDIO_ENTRY
        bne.w   probe_fail
        else
        bne.s   probe_fail
        endc
        addq.l  #1,12(a6)
        ifd FIRST_YIELD
        lea     probe_yield(pc),a2
        bsr.w   recovery_first_yield
        cmpi.l  #1,d0
        ifd AUDIO_ENTRY
        bne.w   probe_fail
        else
        bne.s   probe_fail
        endc
        addq.l  #1,12(a6)
        endc
        ifd AUDIO_ENTRY
        lea     probe_nmi(pc),a2
        bsr.w   recovery_first_nmi_prefix
        cmpi.l  #1,d0
        bne.w   probe_fail
        addq.l  #1,12(a6)
        lea     probe_audio_entry(pc),a2
        bsr.w   recovery_nmi_audio_entry
        cmpi.l  #1,d0
        bne.w   probe_fail
        addq.l  #1,12(a6)
        endc
        ifd AUDIO_RESET
        lea     probe_apu(pc),a2
        bsr.w   recovery_audio_reset_command
        cmpi.l  #1,d0
        bne.w   probe_fail
        addq.l  #1,12(a6)
        endc
        ifd NMI_RETURN
        lea     probe_restore(pc),a2
        bsr.w   recovery_silent_tick_rti
        cmpi.l  #1,d0
        bne.w   probe_fail
        addq.l  #1,12(a6)
        endc
        ifd SCHEDULER_RESUME
        lea     probe_controller(pc),a2
        moveq   #0,d0
        moveq   #0,d1
        bsr.w   recovery_scheduler_resume
        cmpi.l  #1,d0
        bne.w   probe_fail
        addq.l  #1,12(a6)
        endc
        ifd RESUMED_TASK_SETUP
; Independently check the new helper's preserved native register ABI.
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_resumed_task_setup
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_setup_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_setup_abi_fail
        dbra    d0,probe_setup_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
        bra.s   probe_setup_abi_done
probe_setup_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_setup_abi_done:
        endc
        ifd PALETTE_NMI
        lea     probe_palette_nmi(pc),a2
; Independently check the new helper's preserved native register ABI.
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_palette_nmi_prefix
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_palette_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_palette_abi_fail
        dbra    d0,probe_palette_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
        bra.s   probe_palette_abi_done
probe_palette_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_palette_abi_done:
        endc
        ifd MUSIC07
        lea     probe_music_entry(pc),a2
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_nmi_audio_entry
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_music_entry_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_music_entry_abi_fail
        dbra    d0,probe_music_entry_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
        bra.s   probe_music_entry_abi_done
probe_music_entry_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_music_entry_abi_done:
        lea     probe_music_apu(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music07_command
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_music_apu_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_music_apu_abi_fail
        dbra    d0,probe_music_apu_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
        bra.s   probe_music_apu_abi_done
probe_music_apu_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_music_apu_abi_done:
        endc
        ifd MUSIC_FETCH
        lea     probe_music_fetch(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_tick_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_music_fetch_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_music_fetch_abi_fail
        dbra    d0,probe_music_fetch_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
        bra.s   probe_music_fetch_abi_done
probe_music_fetch_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_music_fetch_abi_done:
        endc
        ifd MUSIC_COMMAND04
        lea     probe_music_command04(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_command04
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_music_command04_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_music_command04_abi_fail
        dbra    d0,probe_music_command04_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
        bra.s   probe_music_command04_abi_done
probe_music_command04_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_music_command04_abi_done:
        endc
        ifd MUSIC_CHANNEL_SETUP
        lea     probe_stream_fetch05(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_stream_fetch05_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_channel_abi_fail
        dbra    d0,probe_stream_fetch05_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Snapshot comparison data only; no write to emulated context or RAM.
        move.l  a4,-(sp)
        lea     probe_snapshots(pc),a4
        move.l  (a1),0(a4)
        move.l  4(a1),4(a4)
        move.l  (sp)+,a4
        lea     probe_command05(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_command05
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_command05_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_channel_abi_fail
        dbra    d0,probe_command05_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Snapshot comparison data only; no write to emulated context or RAM.
        move.l  a4,-(sp)
        lea     probe_snapshots(pc),a4
        move.l  (a1),8(a4)
        move.l  4(a1),12(a4)
        move.l  (sp)+,a4
        lea     probe_stream_fetch06(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_stream_fetch06_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_channel_abi_fail
        dbra    d0,probe_stream_fetch06_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Snapshot comparison data only; no write to emulated context or RAM.
        move.l  a4,-(sp)
        lea     probe_snapshots(pc),a4
        move.l  (a1),16(a4)
        move.l  4(a1),20(a4)
        move.l  (sp)+,a4
        lea     probe_command06(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_command06
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_command06_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_channel_abi_fail
        dbra    d0,probe_command06_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Snapshot comparison data only; no write to emulated context or RAM.
        move.l  a4,-(sp)
        lea     probe_snapshots(pc),a4
        move.l  (a1),24(a4)
        move.l  4(a1),28(a4)
        move.l  (sp)+,a4
        lea     probe_stream_fetch07(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_stream_fetch07_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_channel_abi_fail
        dbra    d0,probe_stream_fetch07_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Snapshot comparison data only; no write to emulated context or RAM.
        move.l  a4,-(sp)
        lea     probe_snapshots(pc),a4
        move.l  (a1),32(a4)
        move.l  4(a1),36(a4)
        move.l  (sp)+,a4
        lea     probe_stream_command07_volume(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_command07_volume
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_stream_command07_volume_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_channel_abi_fail
        dbra    d0,probe_stream_command07_volume_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Snapshot comparison data only; no write to emulated context or RAM.
        move.l  a4,-(sp)
        lea     probe_snapshots(pc),a4
        move.l  (a1),40(a4)
        move.l  4(a1),44(a4)
        move.l  (sp)+,a4
        bra.s   probe_channel_done
probe_channel_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_channel_done:
        endc
        ifd MUSIC_FIRST_CHANNEL
        lea     probe_event_fetch08(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_fetch08_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_fetch08_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),0(a4)
        move.l  4(a1),4(a4)
        move.l  (sp)+,a4
        lea     probe_event_instrument08(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_event_instrument08
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_instrument08_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_instrument08_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),8(a4)
        move.l  4(a1),12(a4)
        move.l  (sp)+,a4
        lea     probe_event_fetch18(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_fetch18_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_fetch18_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),16(a4)
        move.l  4(a1),20(a4)
        move.l  (sp)+,a4
        lea     probe_event_command18(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_event_command18
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_command18_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_command18_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),24(a4)
        move.l  4(a1),28(a4)
        move.l  (sp)+,a4
        lea     probe_event_fetch09(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_fetch09_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_fetch09_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),32(a4)
        move.l  4(a1),36(a4)
        move.l  (sp)+,a4
        lea     probe_event_command09(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_event_command09
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_command09_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_command09_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),40(a4)
        move.l  4(a1),44(a4)
        move.l  (sp)+,a4
        lea     probe_event_fetch_rest(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_stream_fetch
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_fetch_rest_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_fetch_rest_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),48(a4)
        move.l  4(a1),52(a4)
        move.l  (sp)+,a4
        lea     probe_event_rest(pc),a2
        lea     probe_music_resource(pc),a3
        movem.l d1-d7/a0-a6,-(sp)
        bsr.w   recovery_music_event_rest
        cmpi.l  #1,d0
        bne.w   probe_fail
        movem.l d1-d7/a0-a6,-(sp)
        move.l  sp,a3
        lea     56(sp),a4
        moveq   #13,d0
probe_event_rest_abi:
        move.l  (a3)+,d1
        cmp.l   (a4)+,d1
        bne.w   probe_event_abi_fail
        dbra    d0,probe_event_rest_abi
        movem.l (sp)+,d1-d7/a0-a6
        lea     56(sp),sp
        addq.l  #1,12(a6)
; Comparison snapshot only, never emulated-state patching.
        move.l  a4,-(sp)
        lea     probe_event_snapshots(pc),a4
        move.l  (a1),56(a4)
        move.l  4(a1),60(a4)
        move.l  (sp)+,a4
        bra.s   probe_event_done
probe_event_abi_fail:
        moveq   #-2,d0
        bra.w   probe_fail
probe_event_done:
        endc
        move.l  sp,40(a6)
        clr.l   8(a6)
        move.w  #$0070,$180(a5)
probe_stop:
        bra.s   probe_stop
probe_fail:
        move.l  d0,8(a6)
        move.l  sp,40(a6)
        move.w  #$0700,$180(a5)
        bra.s   probe_stop

        include "recovery_reset_ram.s"
        include "recovery_reset_mapper.s"
        include "recovery_reset_video.s"
        include "recovery_reset_dispatch.s"
        ifd FIRST_YIELD
        include "recovery_first_yield.s"
        endc

        ifd AUDIO_ENTRY
        include "recovery_first_nmi_prefix.s"
        include "recovery_nmi_audio_entry.s"
        endc

        ifd AUDIO_RESET
        include "recovery_audio_reset_command.s"
        endc

        ifd NMI_RETURN
        include "recovery_silent_tick_rti.s"
        endc

        ifd SCHEDULER_RESUME
        include "recovery_scheduler_resume.s"
        endc

        ifd RESUMED_TASK_SETUP
        include "recovery_resumed_task_setup.s"
        endc

        ifd PALETTE_NMI
        include "recovery_palette_nmi_prefix.s"
        endc

        ifd MUSIC07
        include "recovery_music07_command.s"
        endc

        ifd MUSIC_FETCH
        include "recovery_music_tick_fetch.s"
        endc
        ifd MUSIC_COMMAND04
        include "recovery_music_command04.s"
        endc
        ifd MUSIC_CHANNEL_SETUP
        include "recovery_music_stream_fetch.s"
        include "recovery_music_command05.s"
        include "recovery_music_command06.s"
        include "recovery_music_stream_command07_volume.s"
        endc
        ifd MUSIC_FIRST_CHANNEL
        include "recovery_music_event_instrument08.s"
        include "recovery_music_event_command18.s"
        include "recovery_music_event_command09.s"
        include "recovery_music_event_rest.s"
        endc
        even
probe_report:
        ifd MUSIC_FIRST_CHANNEL
        dc.b    'CDRMFC01'
        else
        ifd MUSIC_CHANNEL_SETUP
        dc.b    'CDRMCS01'
        else
        ifd MUSIC_COMMAND04
        dc.b    'CDRMC041'
        else
        ifd MUSIC_FETCH
        dc.b    'CDRRMFT1'
        else
        ifd MUSIC07
        dc.b    'CDRRM071'
        else
        ifd PALETTE_NMI
        dc.b    'CDRRPAL1'
        else
        ifd RESUMED_TASK_SETUP
        dc.b    'CDRRSET1'
        else
        ifd SCHEDULER_RESUME
        dc.b    'CDRRRES1'
        else
        ifd NMI_RETURN
        dc.b    'CDRRRTI1'
        else
        ifd AUDIO_RESET
        dc.b    'CDRRAPU1'
        else
        ifd AUDIO_ENTRY
        dc.b    'CDRRAUD1'
        else
        ifd FIRST_YIELD
        dc.b    'CDRRYLD1'
        else
        dc.b    'CDRRST01'
        endc
        endc
        endc
        endc
        endc
        endc
        endc
        endc
        endc
        endc
        endc
        endc
        dc.l    $ffffffff,0,0,0,0,0,0,0,0
        ifd FIRST_YIELD
        dc.l    0
        endc
        ifd AUDIO_ENTRY
        dc.l    0,0
        endc
        ifd AUDIO_RESET
        dc.l    0
        endc
        ifd NMI_RETURN
        dc.l    0
        endc
        ifd SCHEDULER_RESUME
        dc.l    0
        endc
        ifd PALETTE_NMI
        dc.l    0
        endc
        ifd MUSIC07
        dc.l    0,0,0
        endc
        ifd MUSIC_FETCH
        dc.l    0
        endc
        ifd MUSIC_COMMAND04
        dc.l    0
        endc
        ifd MUSIC_CHANNEL_SETUP
        dc.l    0,0,0,0,0,0,0
        endc
        ifd MUSIC_FIRST_CHANNEL
        dc.l    0,0,0,0,0,0,0,0,0
        endc
        dcb.b   16,$5a
probe_ram:
        dcb.b   2048,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_context:
        dc.w    $fe24
        dc.b    $17,$33,0,$24,$fd,$a7
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_mapper:
        dcb.b   82,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_video:
        dcb.b   8754,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        ifd FIRST_YIELD
probe_yield:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd AUDIO_ENTRY
probe_nmi:
        dcb.b   298,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_audio_entry:
        dcb.b   22,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd AUDIO_RESET
probe_apu:
        dcb.b   30,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd NMI_RETURN
probe_restore:
        dcb.b   22,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd SCHEDULER_RESUME
probe_controller:
        dcb.b   74,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd PALETTE_NMI
probe_palette_nmi:
        dcb.b   454,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd MUSIC07
probe_music_entry:
        dcb.b   22,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_music_apu:
        dcb.b   30,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd MUSIC_FETCH
probe_music_fetch:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd MUSIC_COMMAND04
probe_music_command04:
        dcb.b   14,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd MUSIC_CHANNEL_SETUP
probe_stream_fetch05:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_command05:
        dcb.b   18,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_stream_fetch06:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_command06:
        dcb.b   14,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_stream_fetch07:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_stream_command07_volume:
        dcb.b   14,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_snapshots:
        dcb.b   48,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
        ifd MUSIC_FIRST_CHANNEL
probe_event_fetch08:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_instrument08:
        dcb.b   22,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_fetch18:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_command18:
        dcb.b   14,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_fetch09:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_command09:
        dcb.b   14,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_fetch_rest:
        dcb.b   6,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_rest:
        dcb.b   10,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
probe_event_snapshots:
        dcb.b   64,$a5
        dcb.b   16,$5a
        dcb.b   16,$5a
        endc
probe_stack:
        dcb.b   4096,$ee
probe_stack_end:
        dcb.b   16,$5a
        ifd MUSIC07
        dcb.b   16,$5a
probe_music_resource:
; Data only. Builder validates private ROM and writes read-only ignored input.
        incbin  "recovery-music07-private-bank3.bin"
        dcb.b   16,$5a
        endc
