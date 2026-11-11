# Actual bank5 queued NMI and 104 input frames

This additive wrapper handles actual bank5 FE8D, task80=1, with pending nametable flag19. It uses the frozen combined NMI98 routine and its existing journal134638 (metadata sentinelFFFF), then leaves ordinary audio processing at C0BF to the unchanged queued-command/music/SFX/RTI chain. No bank, task, input, return frame or resource state is fabricated. No other helper adaptation is added.

A separate read-only preflight uses the same finite-script admission as NMI98 before both event0 and event1. Supported event0 returns a genuine wait without modifying RAM, context, journal, runtime or effects. Event1 services the original NMI and publishes its actual ordered PPU/OAM/CHR effects. Cyclic or combined-over-budget queues reject on either event instead of becoming fake waits. Original F0/9A video suppression semantics retain pending requests; requests clear only when original work consumes them. F5/F6 nonzero remain explicit unsupported, never cleared.

The wrapper validates canonical status, runtime magic/control/serial state, enabled NMI and event0/1. Other PCs, banks, task states or absence of flag19 delegate to existing code. Runtime mapper changes are derived from the actual journal records. No APU command or audio work is skipped: NMI98 stops at C0BF, and the continuous comparison verifies the following ordinary audio helpers and eventual RTI.

## Qualification

Exact native composition: 217800 bytes, SHA256 c3fa0e31c4c42928f0d2440ec59e9b6a8e04a65c42b08ebb4d125c5a47957ff9. All previous source/manifests are unchanged. ABI, USER execution, preserved registers/SP, immutable code/resources, width-aware bounds and4096-byte stack guards remain active.

Public512 wait/service cases and private512 original-first wait/service cases pass. These paired cases span all SP bytes, canonical status combinations, finite nametable queues, optional1C/1D queues, palette updates, actual OAM DMA, CHR serial writes, timer changes and original F0/9A retained-video behavior. Full RAM/context, ordered PPU/mapper events, complete134638-byte journal including DMA and runtime fields match. Each suite also passes5125 inert/delegation checks: runtime/status/event/F5/F6 guards, cyclic and combined-over-budget scripts on both events, and exact-wrapper delegation for other banks/tasks/PCs. The private original prefix executes a real NMI from the incoming PC and stops at C0BF; later audio is proved by the continuous histories, not asserted as part of that prefix alone.

Both genuine Right01 and Right+A81 histories now pass104 completed frames,22041 accepted helper calls,498 logical NMIs,3708 ordered APU writes and7394 inert mutation guards. Queued nametable service and subsequent audio/RTI complete normally. Final camera state has RAMFC=73, FA=0, FD=0 and control90. This is host state/effect proof, not a measured target rendering or speed claim. Held A is input-delivery coverage, not proof of a fresh jump edge after player activation.

The next real unsupported boundary is fixed F328, context f32801090224b9a7, with actual mapper1E/00/10/06. Bank6 helper140 reaches it from8F38 via its original call. Native rejects inertly and both histories terminate at that same boundary; the intended240-frame goal is not reached. No140 raw-status mismatch or adaptation occurred. No further instruction was translated for this milestone.

Private evidence: port/build/recovery_bank_loader_video5_route_Osyo8h/{right,right_a}. summary.json records the bounded result; run.log, all input samples, per-RTI audio states and terminal snapshots remain private diagnostics, never production inputs. Session65330 completed exit0 because the harness successfully verified an explicit unsupported boundary; that does not mean the240-frame gameplay goal passed. Public/private module tests completed in recovery_bank_loader_video5_TeYjHb. No owned session remains active.

## Restore and replay

With approved VASM and machine68k PYTHONPATH, run bash port/tools/recovery_bank_loader_video5_public.sh for a new recursive source-only restore, hash verification, exact rebuild and public tests with cartridge/oracle access denied. Private module differential: python port/tests/recovery_bank_loader_video5_test.py --rom. Continuous replay requires an empty RECOVERY_PRIVATE_SNAPSHOT_DIR and PROBE_PAD=1 or129, then python port/tests/recovery_bank_loader_video5_rom.py default. The final JSON must report unsupported_boundary0xf328 and goal_reached false; do not treat a generic PASS banner as full gameplay completion.

Independent review remains required for this wrapper. No target builder, emulator capture, renderer, Paula backend, delivered disk or public repository was changed. NonzeroF6 and further object/player/sound behavior remain outside this checkpoint.
