# Recovery startup NMI prefix, stopped before audio dispatch

This new isolated helper models an explicit hardware NMI at the first-yield boundary and the guarded startup prefix of its handler. It does not skip the remaining handler or pretend a timer update alone completes an NMI. All five prior helpers, probes and stable title are unchanged.

## Original source and chosen interruption boundary

Original PAL SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Fixed PRG bank 7 maps to `$C000–$FFFF`; file offset is `16 + 7*16384 + address - $C000`. Original NMI vector `$FFFA/$FFFB` points to `$C000`.

The supplied context is the interrupted CPU state **before executing `$FE8D`**, after the first task yield. An explicit external NMI event is injected there. This is a chosen logical interruption boundary, not a claim that hardware timing guarantees the first NMI occurs there: `$C579` has already enabled NMI earlier in the task, and an actual edge could occur at another instruction. Other interruption PCs are unsupported.

`src/recovery_first_nmi_prefix.s` models hardware entry plus the executed startup path `$C000–$C0BE`, ending before `$C0BF`:

1. Hardware pushes interrupted PC high/low and status with B clear; I is set. Handler PHP then saves post-interrupt status with B/U set, followed by saved A, X and Y. All seven stack writes and byte-wrapping SP are included in original-layout RAM.
2. With `$F0|$9A=0`, publish PPU control `$FF & $78`, read `$2002`, disable rendering with `$2001=0`, reset OAM address with `$2003=0`, and request DMA from CPU page two with `$4014=2`.
3. Guarded pending palette/nametable/CHR flags are zero, so their update branches are not entered. Read `$2002` again, publish scroll `$FC/$FA`, mask `$FE`, and control `($FD & 1) | $FF`.
4. Increment frame byte `$92`, set `$90=$FF`, and execute the four original timer slots. State 1 decrements its timer and becomes state 4 only when the result is zero.
5. Stop at `$C0BF`, before bank-busy testing, PRG publication, audio calls, register restoration or RTI.

The timer code is only one part of this prefix; all preceding handler/hardware effects are retained.

## Exact guards and ABI

Export: `recovery_first_nmi_prefix`.

- A0: writable 2048-byte original-layout RAM.
- A1: eight-byte context: big-endian PC word, A, X, Y, P, SP, reserved byte.
- A2: writable 298-byte resource output. First word is the committed event count; ten four-byte records follow, each `{register address big-endian word, data byte, kind byte}`. Kind 0 is an unused-result read; kind 1 is a write. Bytes 42–297 hold the 256-byte OAM DMA source snapshot.
- Buffers must be valid, disjoint and exclusively owned during synchronous execution.

All input guards are checked before any output-buffer or game-RAM mutation:

- PC=`$FE8D`.
- Canonical status representation: B=0, U=1. Other status bits, A/X/Y and SP may vary. NMI is not blocked when I is set.
- PPU control shadow `$FF` has bit 7 set.
- `$F0`, `$9A`, `$18`, `$19`, `$1A`, `$1B`, `$1C`, `$1D` are all zero. These exclude rendering suppression and pending palette, nametable and CHR publications.

Invalid inputs return D0=-1 and leave all three buffers unchanged. Success returns D0=1 at the explicitly untranslated `$C0BF`. D1–D7/A0–A6 are preserved, CCR scratch, native stack balanced.

Final original X=`$10`, Y=0, SP=input SP minus seven modulo 256. A equals the fourth slot's original state, except a state-1 timer reaching zero leaves A=4. N=0/Z=1 come from final DEY; C is the final slot's CMP #1 result. I=1, V/D/U remain as appropriate from entry, B=0; reserved byte is preserved. The interrupt frame remains on the original stack because RTI has not executed.

## Hardware and DMA are explicit data

The ten records contain two `$2002` reads and eight writes. Read record data is zero because both returned status values are unused, not because PPU status is assumed zero. The oracle returns varied status values.

At the `$4014` publication the snapshot contains the exact current RAM `$0200–$02FF`, and original OAM address has just been set to zero. The test checks snapshot contents against live original-layout RAM at the native publication point and independently captures the original bus's DMA source at that point. This preserves the resource data, rather than asking a future adapter to infer it from potentially changed RAM.

These are logical register/resource events, not Amiga MMIO, a PPU implementation, cycle-accurate DMA, stall emulation or automatic NMI generation. A future native renderer must consume them explicitly. No mapper writes occur in this prefix.

## Independent verification

With `VASM` naming `vasmm68k_mot` and py65/machine68k on `PYTHONPATH`:

```
python port/tests/recovery_test_first_nmi_prefix.py
```

The test hashes the private original ROM, loads its actual fixed bank/vector and calls **py65's hardware `nmi()` entry**, then executes original instructions. It does not jump directly to `$C000` with an invented return stack. The assembled 68020 helper is executed with machine68k M68EC020.

Verified:

- 2048 standalone original-ROM/native cases: every original SP and timer byte across every timer slot, plus 1024 randomized states. All canonical status patterns and arbitrary saved registers are exercised.
- All 2048 RAM bytes, full context, all event records, DMA source bytes and exact merged interrupt-stack/handler-RAM/hardware event ordering.
- 256 continuous original reset→first-task-yield→explicit NMI compositions against all six helpers, with no RAM/context patches. The oracle passes the initial scheduler visit to `$FE8D`, reaches `$C574`, waits for the first task yield, then injects NMI exactly once. It stops at `$C0BF`.
- On the composed startup path: task zero changes to state 4/timer 0, queue slot `$DC` still holds `$F0`, queue read index `$DB` is still zero, and PRG shadow `$F1` still equals 6. This expressly demonstrates that audio dispatch was **not** skipped or consumed.
- 2048 completed-boundary rejections and 67895 invalid-input rejections: every other PC, every nonzero value in all eight excluded flags, every noncanonical P byte and every NMI-disabled control byte.
- Guards, native register preservation, stack balance, unexpected-write detection and bounded execution. Invalid calls preserve the full event/DMA output.

Host semantic evidence only. Existing target-probe evidence does not cover this new prefix.

## Actual remaining NMI and audio boundary

At `$C0BF`, original code reads `$F5`. A busy bank transition increments `$F6` and can defer audio; this path is not silently treated as complete. On the normal first-reset path `$F5=0`, it publishes PRG bank 3 through five writes at `$C0C9–$C0D9`, then examines queue `$DC+[$DB]`.

The queued startup `$F0` is nonempty: `$C0E4–$C0EF` saves it, marks the slot empty and advances `$DB`, then **`$C0F0` calls bank-3 `$8003`**. Empty queues instead reach **`$C0F6` calling bank-3 `$8000`**. Only after that processing does the handler restore bank `$F1`, restore registers/status, and RTI at `$C114`.

A next small extension could journal bank-3 publication and queue-consumption effects, stopping before executing the banked call and retaining its exact stack/context. Completing the first NMI needs actual bank-3 audio-entry translation, its hardware/resource effects, bank restoration and RTI proof; merely invoking the existing timer helper cannot establish it. Subsequent scheduler resume is likewise not implemented by this prefix.

No ROM extracts, fixtures, graphics or binaries are included in these source files. Test assembly output is temporary. No full boot, audio playback, gameplay, performance or physical-Amiga claim is made.
