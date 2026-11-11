# Recovery first-task yield boundary

This new helper follows the reviewed reset-to-dispatch checkpoint without altering any earlier helper, the stock-target probe, or stable title. It translates one synchronous task prefix, not an audio driver, asynchronous NMI engine, arbitrary scheduler, or complete boot.

## Original provenance and scope

Original PAL ROM SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Fixed PRG bank 7 maps to `$C000–$FFFF`; file offset is `16 + 7*16384 + CPU_address - $C000`.

`src/recovery_first_yield.s` translates:

- `$C574–$C580`: reset original SP to `$BF`, publish `$FF` to PPU control `$2000`, load `$F0` and call `$F377–$F391`.
- `$F377–$F391`: store `$D9=$F0`, save X=`$BF` at `$00`, read queue index `$DA`, store `$01=$F0`; enqueue only when `$DC+index` contains empty marker `$88`. On enqueue, write `$F0` and advance `$DA` modulo eight. A full slot is left unchanged and does not advance the index. Restore original X.
- `$C581–$C583`: call `$FF04` to yield.
- `$FF04–$FF1E`, including `$FEF7–$FEFC`: store `$93=1`, push X and Y, calculate task slot zero from `$91`, store timer `$81=1` and task state `$80=1`, save current SP=`$BB` into `$82`, and jump to `$FE8D`.

Execution stops **before** `$FE8D` resets SP and resumes scheduler scanning. It does not wait for a frame or execute any resumed task instruction.

Original return-stack RAM is retained exactly. First JSR pushes `$C580`; the second replaces that pair with `$C583`. The yield pushes X=`$BF` and original Y at `$01BD/$01BC`, then nested JSR writes `$FF0E` at `$01BB/$01BA`. Its RTS returns SP to `$BB`; the remaining saved continuation is intact for a later scheduler translation. On the composed reset path, saved Y is 8 and the eventual task return address corresponds to continuation `$C584`.

## Explicit PPU publication and ABI

Export: `recovery_first_yield`.

- A0: writable 2048-byte original-layout RAM.
- A1: eight-byte context: big-endian PC word, A, X, Y, P, SP, reserved byte.
- A2: writable six-byte journal: big-endian count word followed by one `{register address big-endian word, data byte, kind byte}` record. Kind 1 means write.
- All buffers must be valid, disjoint and exclusively owned during synchronous execution.
- Entry PC must be `$C574`, task selector RAM `$91` must be zero, and queue index `$DA` must be 0–7. Unsupported inputs return D0=-1 without changing any buffer.
- Success returns D0=1 at untranslated `$FE8D`. D1–D7/A0–A6 are preserved; CCR scratch; native stack balanced.

The one publication is `$2000 = RAM[$FF]`. Its record is populated before the journal count becomes one. No actual target MMIO occurs. In the normal composed reset path the value is `$90`, which would enable PPU NMI on the NES. This helper **does not inject that NMI**, emulate its timing, or claim that a live NES cannot interrupt this sequence. It proves the synchronous instruction/event sequence with asynchronous interrupts excluded, as required for a separate native adapter. Nor does enqueuing `$F0` produce audio playback.

Final context: PC=`$FE8D`, A=0, X=`$BB`, Y=0, SP=`$BB`; C=0, Z=0, N=1. Other P bits and reserved byte are preserved. The final N/Z derive from original TSX, not the prior TXA/TAY. Input SP is deliberately replaced by `$BF` at entry, regardless of its initial value.

Successful calls produce one PPU event and either 15 RAM stores for a full queue slot or 17 for an empty slot, with exact original ordering. This includes the stack stores, scratch locations and task-continuation state, not only the visible queue change.

## Independent original-ROM verification

With `VASM` naming `vasmm68k_mot` and py65/machine68k available on `PYTHONPATH`:

```
python port/tests/recovery_test_first_yield.py
```

The test hashes the private original ROM, executes actual original instruction bytes with py65, assembles five native helpers with `-m68020`, and executes them using machine68k M68EC020. It reuses the earlier read-only original-bus instrumentation and bounded host PPU event adapter; reference results still come directly from original ROM execution.

Verified coverage:

- 2304 standalone cases: all eight queue indices crossed with all 256 slot values, plus 256 explicit-empty cases covering every initial status, saved-Y and PPU-control byte. Original SP is also varied across all byte values; remaining RAM/context are randomized.
- Full RAM, full context, complete journal and the exact merged PPU/RAM event sequence, including same-value writes and all original stack stores.
- 256 continuous original runs from `$FE24` through the **first task yield** at `$FE8D`, compared against RAM → mapper → video → dispatch → first-yield calls. RAM/context pass directly between calls without patches. The original visits `$FE8D` during initial dispatch as well; the reference explicitly waits until `$C574` has been entered before treating `$FE8D` as the final boundary.
- Composition checks all 20 mapper publications and 2189 PPU events, preserves full event ordering, confirms the saved task continuation, and applies the PPU stream to randomized nametables from both initial latch states.
- 2304 inert completed-boundary rejections.
- 66038 unsupported-input rejections: 65535 other PCs, 255 nonzero task selectors and 248 invalid queue indices.
- Buffer guards, native register preservation, native stack balance, bounded execution and unexpected-write rejection. Invalid paths also preserve the entire pre-existing journal.

The tests above are host semantic evidence. Separate opt-in fifth-helper stock-A1200 target coverage is documented in `recovery_first_yield_target.md`; the older four-helper evidence alone does not cover this fifth helper.

## Next boundary and limitations

At `$FE8D` the original scheduler resets SP and scans task states. Task zero now waits with state 1 and timer 1; its readiness depends on future NMI/timer progress. Continuing requires an explicit native scheduling/event policy and independently verified timing-state transitions. Simply executing the polling loop or pretending the queued sound played would not supply that behavior.

The translation neither implements NMI/audio nor claims a complete reset-to-title, resource loading, playable game, or target speed. Only new source, tests and this analysis are added. ROM contents, extracted assets, snapshots and generated binaries remain private; test assembly output is temporary and automatically removed.
