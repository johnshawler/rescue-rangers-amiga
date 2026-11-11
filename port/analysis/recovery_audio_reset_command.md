# Recovery actual bank-3 startup reset/mute command

This new helper translates the actual original audio command `$F0` for the supported startup state, returning to the fixed-bank NMI at `$C0F3`. It does not play audio on Paula, translate the full audio engine, run the subsequent bank-3 `$8000` update, restore the interrupted bank, execute RTI or resume the scheduler. All seven prior helpers and probes are unchanged by this task.

## Actual cartridge sources and control flow

Original PAL ROM SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.

- PRG bank 3 maps to CPU `$8000–$BFFF`; file offset `16 + 3*16384 + address - $8000`.
- Fixed PRG bank 7 maps to `$C000–$FFFF`; file offset `16 + 7*16384 + address - $C000`.

`src/recovery_audio_reset_command.s` follows these original instructions:

1. `$8003` jumps to `$80E1`. Increment busy/state byte `$C0`, then JSR `$80E9` (return address `$80E5`). Command `$F0` branches through `$817D`.
2. Save original Y in `$C3`, mask the command to zero and call stack-based dispatcher `$8023`. It consumes JSR return `$8183` into `$C1/$C2`, reads the actual table entry at `$8184/$8185`, temporarily pushes its low byte, then dispatches to `$8194`. The native helper preserves every scratch and temporary-stack store, rather than only the final destination.
3. `$8194` calls `$81B3` (return `$8196`), which clears channel pointer pairs `$0754+X` then `$0750+X` for X=3 down to 0.
4. It falls through `$81C0`. With guarded `$CF=0`, each of four channels calls `$80BB` to emit the original mute/control write. `$CF` is shifted and stored on every iteration, then restored from the original stack. All writes are retained even when their value is already zero.
5. `$81E2–$81EF` emits the original sweep/reset/enable writes and returns to `$8197`.
6. Clear `$CE`, `$D0`, `$D1`, `$D7`, `$D8`. Because `$CF=0`, skip the conditional second mute pass and return through `$81B2` to `$80E6`.
7. Decrement `$C0`, restoring its entry value, and RTS through the validated original return frame to `$C0F3`.

No instruction at `$C0F3` executes. The NMI will still need to loop over its queue, call its bank-3 update, restore banking and return from interrupt.

## ABI, guards and explicit APU output

Export `recovery_audio_reset_command`:

- A0: writable 2048-byte original-layout RAM.
- A1: eight-byte boundary context `{big-endian PC word, A, X, Y, P, SP, reserved}`.
- A2: writable 30-byte APU journal: big-endian count word, then seven `{big-endian address word, data byte, kind byte}` records. Kind 1 means write.
- Buffers must be valid, disjoint and exclusively owned during synchronous execution.
- This is the statically selected **bank-3** implementation. The caller must have selected that bank/resource implementation; the helper is not a generic CPU-address dispatcher or runtime mapper.

Before any game-RAM/context/journal mutation, require:

- PC=`$8003` and A=`$F0`.
- `$CF=0`, the supported startup channel mask.
- Original stack bytes at `(SP+1) mod 256` and `(SP+2) mod 256` in page one are `$F2` and `$C0`, identifying the expected return frame `$C0F2`.

Unsupported cases return D0=-1 with all three buffers unchanged. Success returns D0=1 at `$C0F3`. All other native D/A registers are preserved; CCR scratch; native stack balanced.

Final original context: A=0, X=`$FF`, Y=`$0C`, SP=entry SP+2 modulo 256. C=0 from the final LSR of `$CF`; N/Z come from DEC restoring `$C0`, not from A=0. V/D/I/B/U and reserved context byte are preserved. `$C0` itself returns to its entry value, including increment/decrement wraparound. `$C3` retains entry Y; `$C1/$C2` end at `$94/$81`.

The exact ordered APU writes are:

| Register | Value |
| --- | --- |
| `$4000` | `$30` |
| `$4004` | `$30` |
| `$4008` | `$00` |
| `$400C` | `$30` |
| `$4001` | `$08` |
| `$4005` | `$08` |
| `$4015` | `$0F` |

Each record is populated before its count commits. These are explicit original APU resource effects for a future native audio adapter. They are not physical NES register writes on Amiga, immediate audible output, Paula emulation or proof of oscillator/envelope timing. The original `$4015=$0F` value is preserved exactly, not replaced with an invented all-channels-disabled value.

## Independent original-ROM verification

With `VASM` naming `vasmm68k_mot` and py65/machine68k available on `PYTHONPATH`:

```
python port/tests/recovery_test_audio_reset_command.py
```

The oracle loads **actual bank-3 instruction/table bytes and fixed-bank bytes** from the supplied hash-checked ROM. It does not substitute a reference command model. Standalone tests select bank 3 explicitly. Continuous tests decode the original five-write PRG publications and remap the real lower PRG window, including reset bank 6 and the NMI's temporary bank 3. This is a bounded adapter for the verified publication sequence, not a full MMC1 electrical/timing model.

The native source is assembled with `-m68020` and its machine code runs through machine68k M68EC020. The target has no general 6502 interpreter, opcode stream or embedded ROM/table dump.

Verified:

- 2048 standalone actual-ROM/native cases: all 256 initial status bytes, SP values, `$C0` values and saved-Y values across four hostile RAM patterns, plus 1024 independent randomized cases.
- All 2048 RAM bytes, all eight context bytes, the complete 30-byte APU journal, and all **48 ordered events**: 41 RAM/stack/scratch stores and seven APU writes.
- Exact stack-dispatch effects, all nested JSR/PHA/PLA stores, original stack wrap, clearing order, repeated zero stores, and `$C0` restoration.
- 256 continuous eight-helper paths: reset → first task yield → explicit hardware NMI → audio entry → actual `$F0` command return. RAM/context pass directly between helpers without patches. The oracle injects hardware NMI once at the selected first-yield boundary and executes real bank-3 code before stopping at `$C0F3`.
- Continuous paths preserve all 25 prior mapper publications, all prior PPU/DMA effects, seven new APU writes and final stack/context. The mapped bank remains 3 at the stop boundary; no bank restoration is implied.
- 2048 completed-boundary inert rejections and 66555 unsupported-input rejections: every other PC, all 255 other commands, all 255 nonzero `$CF` values, and every wrong byte in either required return-frame position.
- Buffer guards, native register preservation, native stack balance, bounded execution, unexpected-write detection and entire-journal preservation on invalid calls.

## Remaining scope

Nonzero `$CF` and every command other than `$F0` remain unsupported. In particular, conditional additional mute behavior, music/sound resource initialization, channel updates and the bank-3 `$8000` tick are not approximated. This helper returns from one supported command only.

At `$C0F3`, the original NMI jumps back to its queue scan. Subsequent empty-queue update, bank restore, register/status restore, RTI and scheduler continuation still require separate translations and tests. The tests described here provide host semantic proof. Separate eighth-helper stock-target coverage is documented in `recovery_audio_reset_target.md`; the earlier seven-helper evidence alone does not cover this command.

No ROM extracts, tables, audio assets, dumps or binaries are included in these new files. Temporary assembly output is automatically removed. There is no claim of a full boot, music playback, gameplay, hardware performance or physical-Amiga validation.
