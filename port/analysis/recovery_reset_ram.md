# Recovery reset RAM boundary

This newly written recovery module extends the reproducible early title/menu source. It does not recover the lost later gameplay/audio source and is not integrated with the title boot. Existing captured title resources remain required.

## Verified original boundary

Original PAL cartridge SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Fixed 16 KiB PRG bank 7 maps to `$C000–$FFFF`; file offset is `16 + 7*16384 + address - $C000`.

The reset vector is `$FFE0`. Its SEI, mapper-reset write via INC `$FFE1`, CLD and jump lead to `$FE00`. `$FE00–$FE23` initializes the stack, disables display, waits for four PPU vblank set/clear pairs, and writes APU controls. These hardware operations are **not** translated by this helper. The original arrives at `$FE24` with Y=0. No promise that the hardware initialization has occurred is inferred from a RAM buffer.

`src/recovery_reset_ram.s` directly translates `$FE24–$FE42`, stopping before `$FE43`:

- `$FE24–$FE29`: clear zero page in original byte-write order: offset 0, then 255 down to 1.
- `$FE2B–$FE36`: increment zero-page pointer high byte `$01`, clear the next page in ascending byte order, repeat through page 7. The final `$01` is **7**, not zero. All of page one is cleared, including the former 6502 stack contents.
- `$FE38–$FE3D`: write `$88` to sound request queue offsets `$E3` down to `$DC`.
- `$FE3F–$FE41`: write `$1E` to `$FE`.

The slice makes exactly 2064 ordered byte writes to game RAM. There are no calls, original stack accesses, MMIO writes, bank changes, opcode fetch/dispatch loops, or ROM dependencies in the native helper. Native stack storage is separate from original-layout game RAM.

## ABI and failure contract

A0 points to writable 2048-byte original-layout RAM. A1 points to a distinct writable eight-byte context:

| Offset | Meaning |
| --- | --- |
| 0–1 | Original boundary PC, big-endian word |
| 2 | Original A |
| 3 | Original X |
| 4 | Original Y |
| 5 | Original P status bits |
| 6 | Original SP |
| 7 | Reserved, preserved |

The caller must supply valid, disjoint buffers and prevent concurrent access. Only PC=`$FE24` and Y=0 are accepted. Other register bytes may be arbitrary. The context records the boundary, not an emulated CPU engine or an instruction interpreter.

Return D0=1 means this bounded slice completed and reached **untranslated boundary `$FE43`**. Context PC becomes `$FE43`, A=`$1E`, X=`$FF`, Y=0, C=1, N=Z=0; other P bits, SP, and reserved byte are preserved. D1–D7/A0–A6 are preserved, CCR is scratch, native stack is balanced.

Return D0=-1 rejects any other input PC or nonzero Y without modifying either buffer. In particular, calling again with the completed context fails explicitly and does not silently reset RAM again. There is no success result implying a complete boot or title-ready state.

## Independent executable tests

Run from the project root with `VASM` set to `vasmm68k_mot` and `py65`/`machine68k` available on `PYTHONPATH`:

```
python port/tests/recovery_test_reset_ram.py
```

The test hashes the supplied original ROM, independently executes its instructions with py65, assembles this source with `-m68020`, and executes native machine code with machine68k M68EC020. Native memory tracing compares **every ordered RAM byte write**, including same-value writes, with the original instruction-level stores. The py65 trace is semantic instruction writes, not electrical 6502 dummy read-modify-write bus cycles. The helper has only private RAM writes and makes no bus-timing claim.

Coverage:

- 1536 original-ROM differential cases: all 256 initial P patterns across four full-RAM patterns, plus 512 deterministic randomized full-RAM states and varied A/X/SP/reserved context.
- 1536 repeated-call rejection checks at the completed boundary.
- 65790 invalid-context checks: every other 16-bit PC and every nonzero Y at the valid PC.
- Each case checks all 2048 RAM bytes, eight context bytes, RAM/context guards, preserved native registers, balanced native stack, and absence of unexpected native writes. Successful cases check all 2064 RAM stores in order. Source ROM execution rejects an escaped/unexpected boundary and is bounded by an instruction limit.

No snapshots, ROM excerpts, PRG/CHR assets, generated fixtures, or binary files are added by this deliverable. Assembly output is held in an automatically removed temporary directory. The test requires the private original ROM at `input/rescue-rangers-europe.nes`.

## Next boundary and limitations

At `$FE43`, the original loads bank 6 and calls mapper helper `$FF53` at `$FE45`. Subsequent code configures MMC1, CHR banks, hides sprites, clears nametables, and starts scheduler setup. These are **not** implemented or validated here. A future integration must independently provide correct hardware/mapper/resource semantics and preserve their ordering; it must not simply continue execution or declare the captured title fixtures removed.

This is host differential correctness evidence for one RAM-only slice, not target-emulator boot validation, a playable game, audio support, a PAL frame-budget test, or a stock-Amiga performance claim.
