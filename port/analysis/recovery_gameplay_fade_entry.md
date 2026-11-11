# Newly authored gameplay fade-entry continuation

This is a bounded static native 68020 translation, not recovered lost source, stage boot, rendered gameplay or a speed milestone. Existing player setup and all shared builders/probes/verifiers are unchanged.

## Exact boundary and prerequisites

The new `recovery_gameplay_fade_entry.s` enters at fixed-bank-7 CPU `$C700`, immediately after the existing player initializer. It executes the original nested call effects for `$C700` → `$E096` → `$C247` → `$C274`, initializes the palette-fade control state, copies 32 palette values, performs the first binary attenuation pass, stores the update marker and pushes the fade-loop count. It stops at `$C2A5`, **before** `JSR $FF04` frame synchronization.

The three original JSR return addresses are pushed high byte then low byte: `$C702`, `$E098`, `$C249`. Page-1 byte wrapping is preserved for every original stack value. The original PHA pushes 4 after those six bytes. No original RTS has been executed at this boundary. Stack S is entry S minus seven, modulo 256; live original stack data remains in the RAM image.

This is a meaningful first palette-fade pass, not a replacement for `$E096`. Its remaining work includes frame synchronization, additional fade iterations, the rest of `$C247`, stage/resource and hardware helper calls, and finally the player-position snapshots at `$C703`–`$C716`. The earlier bank-4 `$8000` initializer is still an unimplemented prerequisite of the wider stage-start path. Neither that initializer nor any intervening side effect has been skipped to reach this synthetic slice entry.

## ABI and effects

- A0: writable 2048-byte original RAM image.
- A1: writable eight-byte context: big-endian PC word, A, X, Y, raw P, S, reserved.
- A2: writable 512-byte ordered store journal. Each record is address word, value byte, zero byte. Buffers, code and native stack must not alias.
- Valid context PC: `$C700`. Every other context byte and RAM byte is arbitrary. No resource/ROM table, mapper, PPU or audio callback is needed before the stop.
- Success: D0 = 76, PC = `$C2A5`, A = 4, X = 16, Y = 255. All other native D/A registers are preserved; native CCR is scratch; native stack balances.
- Invalid PC: D0 = -1 with RAM, context and journal unchanged.

The journal covers exactly 76 architectural RAM writes (304 bytes); unused journal bytes remain untouched. It does not model cycle-level dummy bus writes or elapsed cycles. Status D/I/B/unused bits remain exactly as supplied. C/V come from the final binary palette subtraction, while the subsequent load of 4 clears N/Z. NES Ricoh 2A03 arithmetic ignores decimal adjustment without clearing D.

## Verification

The new source-only declarative contract uses invented states and no 6502 emulator, ROM or captured trace. It covers all 256 values in each of the 32 palette positions, every status byte with ten original stack-boundary values, and six inert invalid entries: **10,758 passing cases**.

The actual-ROM differential test pins private Europe input SHA-256 `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`. It executes actual instructions using py65 with a separately implemented Ricoh 2A03 binary SBC ALU. The override implements integer subtraction and binary flags, preserving other P bits; it never normalizes P or patches original RAM/context between slices. A separate bitwise full-adder truth table validates every A/operand/carry/D combination, **262,144 ALU cases**. ADC is not executed before this boundary.

The differential suite covers all 65,536 status/stack pairs and all 8,192 palette-position/value combinations. Another 4,096 compositions execute the unchanged player initializer at `$C6BD`, compare at `$C700`, and continue directly to `$C2A5`. Both reference and native original RAM/context stay live across this boundary; only the native journal and host calling frame are rearmed. No preceding bank-4 initialization is claimed.

Verified result: **73,728 standalone actual-ROM cases and 4,096 continuous compositions passed**, comparing **5,972,782 ordered stores**. The SBC truth-table and all 10,758 ROM-free cases also passed. The assembled native helper is **282 bytes**.

All tests compare full RAM, all context bytes, exact journal and untouched tail, ordered actual native RAM writes, buffer guards, native register preservation and balanced native stack. Every traced native read/write is globally whitelisted to explicit code, stop, RAM, context, journal and native-stack regions. Six explicit distant, out-of-range or crossing bad-read checks prove the whitelist is not merely an adjacent-guard check. The actual-ROM reference also rejects all reads outside RAM/fixed ROM and writes outside RAM.

## Reproduction and integration

From the project root, set `VASM` to the approved `vasmm68k_mot` and `PYTHONPATH` to the existing `rescue-recovery-inspection/.deps`, then run:

```sh
python port/tests/test_recovery_gameplay_fade_entry_contract.py
python port/tests/recovery_test_gameplay_fade_entry.py
```

The new helper remains separate from live title/gameplay integration. Its [source-only target probe](recovery_gameplay_fade_entry_target.md) now verifies six continuous synthetic player/fade compositions on an emulated stock PAL A1200. A future continuation must consume the live `$C2A5` context and original stack, implement the real frame synchronization contract, and return through the preserved call chain; it must not manufacture a return to `$C703`. No gameplay timing, full-stage, audible-output or physical-hardware claim is made. No proprietary input, assets, firmware or captured traces are added to source. Original and delivered media remain unchanged.
