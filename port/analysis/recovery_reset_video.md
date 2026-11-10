# Recovery sprite-hide and nametable-clear boundary

This is new recovery-only source. The proven reset RAM and mapper helpers and the stable captured-state title remain unchanged. No later gameplay/audio source is recovered by this work.

## Source provenance and boundary

Original PAL ROM SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Fixed PRG bank 7 maps to CPU `$C000–$FFFF`; file offset is `16 + 7*16384 + address - $C000`.

`src/recovery_reset_video.s` translates `$FE67–$FE7B`, including the called paths:

- `$FE67`: JSR `$C21E–$C234`. Read sprite cursor `$97`, hide original OAM Y bytes from that cursor through the end of page two by storing `$F8` at four-byte intervals. Cursor 4 also hides sprite zero first. Cursor 0 hides every sprite. No cursor is silently normalized.
- `$FE6A–$FE72`: select nametable high byte `$20`, tile fill 0 and attribute fill 0, then call `$C1BA–$C205`.
- `$FE73–$FE7B`: select high byte `$24`, same fills, then call `$C1BA–$C205` again.

The next unsupported instruction is `$FE7C`, which begins task entry/scheduler setup. This helper does not execute it.

Each original clear stores arguments to RAM `$00/$01/$02`, reads `$2002` to reset the PPU address latch, publishes `$FF & $FE` to PPU control `$2000`, sets the address through `$2006`, then emits 1024 zero writes through `$2007`. It subsequently emits a redundant 64-byte zero attribute clear. The original CMP before ADC sets carry, so `ADC #2` adds **three**: the attribute addresses are `$23C0` and `$27C0`, not `$22C0/$26C0`.

## ABI and explicit resource effects

`recovery_reset_video` arguments:

- A0: writable 2048-byte original-layout RAM.
- A1: eight-byte boundary context: big-endian PC word, A, X, Y, P, SP, reserved byte.
- A2: writable 8754-byte PPU event journal: big-endian count word followed by 2188 four-byte records `{register address big-endian word, data byte, kind byte}`. Kind 0 is a read; kind 1 is a write.

All three buffers must be valid, disjoint, and exclusively owned during synchronous execution. Native memory accesses target those buffers and the native stack, never NES or Amiga hardware registers.

The only read event is `$2002`. Its data byte is zero by definition because the original routine discards the returned status before making a decision or storing it. The event represents the latch-reset side effect; it does **not** assert actual PPU status was zero. Tests vary the original returned status independently. Journal records are populated before count increments; a future adapter must consume events in that committed order. This is not a concurrent queue or a PPU emulator on target.

Supported entry: context PC=`$FE67`, sprite cursor `$97` divisible by four, and bit 2 of `$FF` clear (PPU data increment by one). The last guard bounds this adapter to actual nametable clears; increment-by-32 execution is explicitly unsupported. The original nonmultiple-of-four sprite cursor never terminates; the helper rejects it rather than hanging. All these invalid cases return D0=-1 before modifying any buffer.

Success returns D0=1 at untranslated boundary `$FE7C`. Context A=`$C0`, X=Y=0, C=V=N=0, Z=1; remaining P bits, SP and reserved byte are preserved. D1–D7/A0–A6 are preserved, CCR is scratch and native stack is balanced. Original page-one JSR stores are included exactly with byte-wrapping SP; no original-stack RAM is excluded from comparisons. The three JSR pairs are `$FE69`, `$FE72` and `$FE7B`.

There are 2188 PPU events: two reads and 2186 writes. Each clear has 1094 events: one status read, one control write, four address writes, and 1088 data writes. The RAM side has twelve setup/JSR writes plus the cursor-dependent OAM writes (1–64). Thus total merged events vary from 2201 to 2264.

## Executed verification

With `VASM` pointing to `vasmm68k_mot` and py65/machine68k on `PYTHONPATH`:

```
python port/tests/recovery_test_reset_video.py
```

The test hashes the private original ROM, executes actual original 6502 instruction bytes, assembles all three independent native recovery helpers with `-m68020`, and executes their machine code with machine68k M68EC020. No ROM-instruction interpreter is present in target code.

Coverage:

- 1280 standalone original-ROM/native cases: all 256 initial P values, all 256 SP values, all 64 valid sprite cursors, all 128 supported control-byte values across four hostile RAM patterns, plus 256 randomized cases.
- 128 continuous original runs from `$FE24` to `$FE7C` compared against sequential calls to RAM, mapper and video helpers, passing RAM/context directly between helpers without patching them. This compares every RAM byte, every context byte, and the complete ordered RAM/mapper/PPU event stream, including original JSR stack writes.
- Each valid video case compares all 2188 journal events and a host-only resource adapter applies them to random two-nametable contents with both initial PPU address-latch states. It verifies exact destination order, all 2048 bytes cleared, and the two redundant attribute clears.
- 1280 completed-boundary inert rejection checks.
- 65855 inert unsupported-input checks: all 65535 other PCs, 192 invalid sprite cursors and 128 increment-by-32 control values.
- Full RAM/context/journal guards, preserved native registers, balanced stack, ordered writes, unexpected-write rejection and bounded reference/native execution.

The PPU resource adapter in the Python test is a deliberately bounded host verifier. It does not claim full PPU behavior, rendering, timing, arbitrary-address mapping or target integration. These event traces are instruction-level semantics, not electrical bus cycles.

## Limitations and next step

The composed proof begins **after** original reset hardware warmup at `$FE24`. It does not model asynchronous NMI/IRQ injection. The first two helpers establish the guard-compatible state on the ordinary reset path, but mapper journals are not yet wired to native CHR/bank resources and the PPU journal is not wired into the title renderer.

At `$FE7C` the original sets task entry `$C574` in `$94:$93`, invokes scheduler initialization through `$FED5`, enables the PPU/NMI control shadow and enters scheduling. Resource/task translation and actual native boot integration remain separate work. No complete reset-to-title, playable gameplay, audio, ADF boot validation or hardware-performance claim is made.

Only source, tests and this analysis are added. ROM bytes, cartridge graphics, snapshots, extracted dumps and binaries remain private; test assembly output lives in an automatically removed temporary directory.
