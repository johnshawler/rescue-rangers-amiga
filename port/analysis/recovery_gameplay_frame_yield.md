# Newly authored gameplay frame yield

This bounded static native 68020 translation continues the live gameplay fade entry at `$C2A5` through `JSR $FF04` to the original scheduler entry `$FE8D`. It also accepts direct `$FF04` entry for callers that already hold their original return frame. It does not execute the scheduler, synthesize a return, advance an interrupt, finish the fade loop, or initialize a playable stage.

## Contract and exact boundary

- A0 points to writable 2048-byte original RAM.
- A1 points to eight bytes: big-endian PC word, A, X, Y, raw P, S, reserved.
- A2 points to a writable 512-byte ordered store journal, address word/value byte/zero byte per record.
- All buffers, code and native stack must be disjoint. Execution is uninterrupted over this slice; asynchronous NMI injection is outside this contract.
- Entry PC is `$C2A5` or `$FF04`. Every RAM byte and other context byte is arbitrary. Other PCs return D0=-1 without changing RAM/context/journal.
- Success returns D0=10 for `$C2A5` or D0=8 for `$FF04`. All other native D/A registers are preserved, native stack balances, and native CCR is scratch. Unused journal tail stays untouched.

The C2A5 entry first pushes return `$C2A7`, high byte then low. Both entries store 1 into `$93`, push original X and Y, push nested return `$FF0E`, execute the task-index computation at `$FEF7`, and consume that nested return. They then store the wait count, wait state 1, and saved original stack pointer into the task slots. Original page-1 stack wrapping and zero-page indexed address wrapping are preserved. All 256 values of `$91` are translated exactly as bytes; acceptance does not assert that all are valid scheduler task IDs.

Final PC is `$FE8D`, before `LDX #$FF` and `TXS`. A/Y contain `($91_at_FEF7 * 4) mod 256`; X/S contain entry S minus four for C2A5, or minus two for FF04, modulo 256. C reflects bit 6 of the task byte, N/Z reflect final saved S, and V/D/I/B/unused bits retain their entry values. No implicit status normalization is performed. The caller's live frames and fade counter remain in original RAM, together with the consumed nested-call stack bytes. No hardware access occurs in this slice.

## Verification

The new ROM-free declarative test uses invented RAM/context and no ROM, trace, or CPU reference. It covers both entries across all task-byte/stack-byte pairs, with all status bytes represented, plus six inert invalid PCs. The separate private differential test executes actual hash-pinned Europe-ROM instructions using py65, across both entries and all status/stack pairs, rotating through every task byte.

The four-helper composition executes `$C6B5 → $C6BD → $C700 → $C2A5 → $FE8D`. Original and native RAM/context remain live at every boundary, with no patching, pending-state clearing or frame fabrication. The pre-existing resource initializer's explicit `$F6=0`, mapper-mode/serial-latch and immutable resource-view restrictions remain prerequisites, not conclusions about title-to-stage reachability. Only native host frames and journals are rearmed between helpers. The composition reuses the independently truth-table-validated Ricoh 2A03 SBC reference for the preceding palette slice.

All native reads/writes are globally whitelisted by the existing unchanged harnesses. Full RAM/context/journal, ordered native stores, untouched journal tail, buffer guards, preserved native registers and balanced native stack are compared. Existing negative distant and crossing read probes remain active; composition also retains immutable-resource read/write boundary probes. The actual-ROM buses independently reject unexpected original reads/writes.

Run from repository root with the approved VASM and inspection-dependency PYTHONPATH:

```sh
python port/tests/test_recovery_frame_yield_contract.py
python port/tests/recovery_test_frame_yield.py
python port/tests/recovery_test_frame_yield_composition.py
```

## Remaining dependencies

FE8D scheduler dispatch, interrupt-driven task readiness, general task resumption, restoration of saved X/Y and return to `$C2A8`, remaining fade iterations and original caller returns are not implemented here. Existing narrowly constrained scheduler-resume helpers are not a general adapter for this new state. No audio, palette, scheduler or pending-state value is cleared to force integration. There is no target integration, rendered-stage, audible-output, timing, physical-hardware or performance claim. No proprietary inputs/assets/traces are added to source; delivered media and existing source files remain unchanged by this work.

Verified final results: **131,072 actual-ROM cases**, **1,179,648 ordered stores**; **131,078 ROM-free cases** including six inert rejections; **4,096 continuous four-helper compositions**, **562,026 ordered effects**; **262,144 SBC truth-table cases** for the preceding fade reference. The helper assembles to **260 bytes**. Python syntax compilation passed for all four new Python files. Journals describe architectural stores, not cycle-level dummy bus writes or elapsed cycles.

## Subsequent integrated checkpoint

The helper-local limits above describe this component when introduced. The
[bounded resident runtime target](recovery_runtime_target.md) now verifies the
reset-generated idle/NMI/initial-music/RTI/task-resume path on an emulated
stock PAL A1200. Stage frame-yield compositions remain separate synthetic-entry
proofs. Public and private aggregate scripts include these helper suites.
There is still no complete native gameplay loop, audible output or speed claim.
