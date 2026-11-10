# Recovery reset mapper-publication boundary

This separate recovery helper continues the original reset RAM boundary, but does not integrate with the stable title or alter `recovery_reset_ram.s`. It is newly written source, not recovered later gameplay/audio code.

## Original source and exact scope

PAL original SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Fixed PRG bank 7, CPU `$C000–$FFFF`; file offset `16 + 7*16384 + CPU_address - $C000`.

Translated entry `$FE43` through `$FE66`, stopping before `$FE67`:

- `$FE43–$FE47`: load PRG bank 6 and call `$FF53`. `$FF53–$FF74` stores `$F1=6`, `$F4=6`, increments `$F5` (byte wrap retained), serially publishes five writes to `$FFF0`, clears `$F5`, and tests `$F6`.
- `$FE48–$FE5C`: load `$1E`, publish five control writes to `$9FFF`.
- `$FE5D–$FE61`: load 0 and call `$FF1F–$FF38`, setting `$F2=0`, publishing five CHR0 writes to `$BFFF`, and clearing `$1A`.
- `$FE62–$FE66`: load `$10` and call `$FF39–$FF52`, setting `$F3=$10`, publishing five CHR1 writes to `$DFFF`, and clearing `$1B`.

The publisher retains all five original shifted A byte values, not only their low bits. Interpreted as MMC1 least-significant-bit-first serial commits, these are PRG=6, control=`$1E`, CHR0=0, CHR1=`$10`, in that order. Control `$1E` selects vertical mirroring, fixed-last-bank PRG mode and separate 4KiB CHR banks. The helper does not implement those mapping effects or read data through the selected banks.

The original `$F6 != 0` branch at `$FF72` leads to `$FF75`: temporarily publish bank 3, drain the audio request queue through banked `$8003`, call banked `$8000`, clear `$F6` and restore the requested bank. This helper explicitly rejects nonzero `$F6` **before any changes**, rather than assuming that untranslated audio path succeeds.

## Native ABI

`src/recovery_reset_mapper.s` exports `recovery_reset_mapper`:

- A0: writable 2048-byte original RAM.
- A1: eight-byte boundary context, identical layout to the RAM helper: big-endian PC word, A byte, X byte, Y byte, P byte, SP byte, reserved byte.
- A2: writable 82-byte publication journal. First word is a big-endian committed-record count; twenty four-byte records follow. Each record is `{address big-endian word, original data byte, contemporaneous RAM[$F5] byte}`.
- D0=1: bounded completion at original `$FE67`, **not full boot completion**.
- D0=-1: unsupported PC or nonzero `$F6`; all three buffers remain unchanged.
- D1–D7/A0–A6 preserved; CCR scratch; native stack balanced.

Requires input PC=`$FE43`, `$F6=0`; other context and RAM bytes may be arbitrary. Buffers must be valid, disjoint and exclusively owned during execution. No asynchronous interrupt injection is modeled. The real reset path established SEI and disabled PPU NMI before this boundary; invoking the helper for an arbitrary live-game bank switch is outside its scope.

On success, context PC becomes `$FE67`, A=0, C=0, Z=1, N=0. X, Y, other P bits, SP and reserved byte remain unchanged. All original game RAM writes are retained, including the six JSR return-address writes to original page one. These use the supplied original SP with byte wrapping. The final pair contains return address `$FE66`; native call-stack storage is separate.

## Publication is explicit data, not NES MMIO

The implementation never writes target addresses `$9FFF/$BFFF/$DFFF/$FFF0`. It builds a logical journal for a future native resource/mapping adapter. For every publication it first writes the full record, then increments the count. RAM `$F5` is incremented before the five PRG publications and cleared before the remaining fifteen. Even an initial `$F5=$FF` wraps to zero just as in the original.

Tests observe each committed record during native execution, checking the live RAM busy byte and merging publications with RAM writes into a single ordered event stream. The journal also stores the busy byte, so a future consumer must not infer that every record occurred under the final RAM state. Journal construction is synchronous; it is not a concurrently consumed queue, actual bank mapping, MMC1 serial-latch implementation, or timing model. A future adapter must account for reset/latch state and preserve the verified ordering when selecting native resources.

## Reproduce and verified coverage

With py65 and machine68k on `PYTHONPATH`, and `VASM` naming `vasmm68k_mot`:

```
python port/tests/recovery_test_reset_mapper.py
```

The test hashes the private original ROM, executes actual original 6502 instructions with a bus that records logical mapper writes without overwriting ROM, assembles native 68020 machine code, and executes it with machine68k M68EC020.

Verified:

- 2048 original-ROM/native differential cases: all 256 flag bytes, all 256 SP values (including wrap), all 256 initial busy bytes across four hostile full-RAM patterns; plus 1024 randomized full-RAM/context cases.
- Every case compares all 2048 RAM bytes **including page-one stack effects**, all context bytes, all journal bytes, and one ordered stream of 34 events: 14 RAM stores and 20 mapper publications. Each commit checks contemporaneous `$F5` and independently decodes the four MMC1 five-bit values.
- 2048 inert repeated-call rejections at the completed boundary.
- 65790 inert invalid-context rejections: all 65535 other 16-bit PCs and all 255 nonzero deferred-audio bytes at the valid PC.
- RAM/context/journal guards, preserved native registers, balanced native stack, unexpected-write rejection and bounded execution are checked.

These are instruction-semantic writes, not physical 6502 RMW dummy-write cycles or MMC1 cycle timing. Original ROM/PRG/CHR, snapshots, binaries and extracted dumps are not part of these source files. Assembler output is temporary and automatically removed.

## Next unsupported boundary

`$FE67` calls original sprite-hiding helper `$C21E` (a bounded translation already exists in the early source); following `$FE6A` begins nametable clear setup and calls `$C1BA`. This deliverable stops before either. It neither creates the native CHR/nametable resources nor proves a reset-to-title boot, and it does not remove captured-title fixtures.

No full gameplay, audio, live mapper scheduling, target boot, stock-Amiga speed, or frame-budget claim follows from these host differential tests.
