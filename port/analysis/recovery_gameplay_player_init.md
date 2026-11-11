# Newly authored player initialization recovery

This is a new bounded static 68020 translation, not recovered lost source and not a playable-game or continuous-startup milestone.

## Implemented boundary

`port/src/recovery_gameplay_player_init.s` translates fixed PRG bank 7, CPU `$C6BD` through `$C6FF`, including the nested `$F31D`–`$F327` animation initializer. It stops at `$C700`, before the original `JSR $E096` instruction executes.

The actual ROM's stage setup path calls `$C6B5` from `$C614`. Before this slice, `$C6B5` selects bank 4 through `$FF53` and calls its `$8000` routine. This implementation does **not** perform or replace those prerequisites. At the slice entry, `$50` selects the highest player slot, zero or one. Players are processed descending. State `$0C` skips initialization. Other players receive the original object flags, initial vertical coordinate from `$034C+slot`, animation state, cleared motion/action fields and the `$F31D` animation pointer values. The original unconditional `$5E` clear is preserved; it is not changed into an indexed clear. Both horizontal starting positions and `$99` are then initialized.

Each original `JSR $F31D` writes the original return address `$C6EE` into the original stack page, including stack-byte wraparound. Returning leaves those bytes in RAM and restores the original S. The final original A, X, Y, status, S and continuation PC are represented explicitly. Status bits not changed by the original instructions remain unchanged; the last player comparison supplies carry, and the final load of `$55` clears N/Z. There is no generic opcode interpreter, ROM instruction fetch or runtime translation in the native source.

## Interface

- A0: writable 2048-byte RAM image using original NES offsets.
- A1: writable eight-byte context, big-endian PC word, then A, X, Y, P, S and reserved byte.
- A2: writable 256-byte journal buffer, separate from RAM/context/code/native stack. Each original architectural RAM store appends a four-byte record: big-endian address word, value byte, zero byte. Maximum 33 records (132 bytes). Unused journal bytes are unchanged.
- Valid entry: context PC `$C6BD`, RAM `$50` equal to zero or one. Other context bytes and all other RAM may vary. Resources/hardware callbacks are not needed by this slice.
- Success: D0 is the number of records; context PC becomes `$C700`. All other native D/A registers are preserved. Native CCR is scratch. Native stack balances.
- Invalid entry: D0=-1, with RAM, context and journal unchanged.

The journal records architectural writes as executed by the reference CPU, not cycle-level dummy bus writes or cycle timings. RAM buffers, context and journal must not alias. The host must consume the continuation explicitly rather than treating this boundary as a completed stage initializer.

## Actual-ROM differential verification

Private ROM input: `input/rescue-rangers-europe.nes`, SHA-256 `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.

`port/tests/recovery_test_gameplay_player_init.py` asserts that hash and executes the original ROM instructions with py65. It assembles the new source with the existing VASM `-m68020` toolchain and executes the resulting 340 bytes with machine68k's M68EC020 core. The test compares all 2048 RAM bytes, the full eight-byte context and every ordered original RAM write against the native journal. It also checks untouched journal tail, memory guards, native register preservation and balanced native stack return.

Verified result:

- 65,536 two-player cases covering every pair of player-state bytes, with randomized other RAM/context.
- 65,536 one-player cases covering every status-byte/stack-byte pair, including inactive-player cases and stack wraparound.
- 259 inert invalid-input cases: all 254 unsupported player counts and five wrong entry PCs.
- Total: 131,331 passing cases, including 131,072 actual-ROM differential cases and 2,841,216 compared ordered RAM-write events.

Every native read and write is checked against a complete address-region whitelist, including code, STOP, RAM, context, journal and bounded native stack. Five explicit invalid-read checks cover distant, guard and crossing accesses. Actual ordered native RAM stores are compared directly with the reference events, independently of the returned journal.

Run from the project root with the approved toolchain and dependencies:

```sh
PYTHONPATH=/workspace/scratch/43ecf79622a5/rescue-recovery-inspection/.deps \
VASM=/workspace/scratch/43ecf79622a5/amiga-recovery-tools/vscode-amiga-debug/bin/linux/vasmm68k_mot \
python port/tests/recovery_test_gameplay_player_init.py
```

No ROM, firmware, extracted assets or captured traces are added to public source.

## Remaining boundary

This standalone slice is not linked into the title or continuous reset/audio recovery. A separate source-only target probe now verifies six synthetic inputs on an emulated stock PAL A1200; see [the target report](recovery_gameplay_player_init_target.md). The next stage-initialization work must establish bank-4 `$8000` preconditions and translate or explicitly boundary the `$E096` call at `$C700`. After that call, the original code at `$C703`–`$C716` clears `$6E` and snapshots player positions into `$68/$6A` before returning. These dependencies cannot be skipped merely because this inner player setup passes. Collision, controls-to-movement, stage loading/rendering and the full frame loop remain outside this proof. No PAL game timing, physical-hardware runtime or performance measurement is claimed. Existing startup/audio helpers and delivered media remain unchanged.
