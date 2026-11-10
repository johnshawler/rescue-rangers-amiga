# Recovery first-task dispatch boundary

New isolated source continues the reset recovery without changing the three earlier helpers or stable title. This is a bounded first dispatch, not an arbitrary scheduler and not recovered later gameplay/audio source.

## Original provenance and exact path

PAL original SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Fixed PRG bank 7 maps to CPU `$C000–$FFFF`; file offset `16 + 7*16384 + address - $C000`.

`src/recovery_reset_dispatch.s` translates entry `$FE7C` through the indirect jump at `$FEC2`, stopping **before executing `$C574`**:

- `$FE7C–$FE88` installs task address `$C574` in `$94:$93`, loads A=0 and calls `$FED5`.
- `$FED5–$FEE4` calls `$FEF9–$FEFC`, which doubles A twice and moves it to X. Here A=0, so X=0. It copies `$93/$94` to slot-zero `$82/$83`, and writes task state 8 to `$80`.
- `$FE89–$FE8F` writes `$FF=$90`, then resets the **original** SP to `$FF` through TXS. This is a control shadow RAM write, not a hardware PPU write.
- `$FE90–$FEA3` clears `$90` and scans from slot zero with Y=4. The newly installed state 8 necessarily selects slot zero immediately, regardless of previous RAM/task state.
- `$FEA6–$FEC4` sees `$90=0`, selects task number 0 in `$91`, reads the previous state 8 into Y, changes `$80` to 2, restores `$93/$94` from `$82/$83`, and jumps through `$0093` to `$C574`.

No task-state rejection is needed: under synchronous execution, this entry unconditionally installs the state/address that it then selects. Unsupported entry PCs are rejected. An asynchronous interrupt or external RAM mutation during the helper is outside its contract.

There are exactly 15 ordered RAM stores: two initial entry-address stores, four nested JSR stack-byte stores, three task setup stores, the `$FF` shadow store, `$90/$91` clears, the state-2 store, and two final dispatch-address stores. The original nested calls push return addresses `$FE88` and `$FED7` before SP is reset. All four bytes, including original stack-pointer wrap, are preserved in the native RAM image. No original stack RAM is excluded from comparisons.

## Native ABI

Export: `recovery_reset_dispatch`.

- A0 points to writable 2048-byte original-layout RAM.
- A1 points to eight-byte context: big-endian PC word; A, X, Y, P, SP and reserved bytes.
- Buffers must be valid, disjoint and exclusively owned during execution.
- Entry PC must be `$FE7C`. Other context bytes and initial RAM may be arbitrary.
- D0=1 returns at untranslated `$C574`. This is bounded completion, not game/task execution or a full boot result.
- D0=-1 rejects any other PC, including a repeated call after completion, without modifying either buffer.
- D1–D7/A0–A6, including unused A2, are preserved; CCR scratch; native stack balanced.

Final original context: PC=`$C574`, A=`$C5`, X=0, Y=8, SP=`$FF`; N=1, Z=0, C=1. V and the remaining P bits are preserved by this helper. Reserved byte remains unchanged. The assembled code directly performs the proven path; it has no opcode interpreter, scheduler polling engine, MMIO or journal output.

## Original-ROM proof and composition

With `VASM` pointing to `vasmm68k_mot` and py65/machine68k available on `PYTHONPATH`:

```
python port/tests/recovery_test_reset_dispatch.py
```

The test hashes and executes the private original ROM bytes with py65, assembles all four native helpers with `-m68020`, and executes the machine code using machine68k M68EC020. It reuses the earlier test's read-only original-bus instrumentation and bounded host PPU adapter; expected state still comes from original instructions, not a source-level native model.

Verified coverage:

- 2048 standalone differential cases: all 256 initial status bytes and all 256 original SP values across four hostile full-RAM patterns, plus 1024 independent randomized cases. Varied task RAM does not alter the guaranteed first dispatch.
- Every standalone case compares all 2048 RAM bytes, all eight context bytes and the exact 15-store sequence, including same-value stores and original stack wrap.
- 256 continuous original runs from `$FE24` to `$C574`, compared against sequential native RAM → mapper → video → dispatch calls. Every initial status byte and SP value is exercised. RAM/context pass directly between calls without patches or snapshots.
- Composition compares the complete ordered RAM/mapper/PPU event stream, 20 mapper publications, 2188 PPU events, and final RAM/context. The bounded PPU adapter also verifies cleared nametables from both initial address-latch states.
- 2048 inert completed-boundary rejections and 65535 inert other-PC rejections.
- Boundary guards, unexpected native writes, native register preservation, balanced stack and bounded reference/native execution.

The composed proof starts at `$FE24`, **after untranslated reset hardware warmup**. It preserves the journals as explicit data and does not implement native resource mapping or PPU hardware. It injects no NMI/IRQ. This is host semantic evidence, not a target-emulator boot result or a hardware speed measurement.

## Precise next boundary

At `$C574`, the original starts task execution by setting SP to `$BF`, then writes the `$FF` shadow to PPU control `$2000` at `$C579`, calls the audio-request entry `$F377` with `$F0`, and yields through `$FF04` at `$C581`. None of those instructions execute in this helper. Later PRNG seed/resource initialization is likewise outside scope.

This deliverable does not claim complete boot, title-resource generation, audio playback, playable gameplay, or recovery of lost later source. It adds only the new source/test/report. No ROM extracts, graphics, snapshots or binaries are included; temporary assembler output is automatically removed. No existing helper or stable-title file is modified.
