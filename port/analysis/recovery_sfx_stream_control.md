# Native SFX stream control and sound shutdown

This is an additive host-qualified continuation of the recovered early title/menu
baseline. It does not recover the lost later playable/gameplay/audio source.
The target remains native PAL A1200, 68020/AGA, 2 MiB Chip RAM, no Fast RAM
preferred and at most 8 MiB optional Fast. No delivered disk is changed.

## Result

Both real Left and Right character-cursor histories now reach genuine sound
shutdown and continue through 22 subsequent completed NMI returns. The original
cartridge and native state remain equal through 2,442 native helpers, 78 NMIs
entered and 75 completed returns. The terminal context is
`83A00E2A00A4F2A7`, PRG bank 3, at music command 0E.

Shutdown itself is helper 1,766, within NMI 56, with 53 prior completed returns.
The helper enters at `8235FE0300A5F2A7` and performs the actual wrapping-stack
return to `806000FF0427F4A7`. The stream pointer and sound-active mask become
zero. Four ordered APU writes are emitted: 4004=30, 4001=08, 4005=08, 4015=0F
(hexadecimal). The preexisting 16 envelope calls and their 34 direct SFX APU
writes are unchanged. Returns 54 through 75 occur after shutdown without
reinitializing native RAM, replaying captured state or skipping audio work.

The final 83A0/0E stop is a **composition boundary**, not a claim that this command
lacks a translation. The existing `recovery_music_active_command0e.s` contract
accepts the terminal X=2A state, stream pointer A3A6, counter zero. A separate
isolated compatibility check of both terminal snapshots passes against that
existing native helper, its model and original instructions, reaching
`839DA32A00A4F2A7`. That isolated check is not counted as continuous execution.
The helper is deliberately not added to this composition, and no music guard is
relaxed. Further music/title-loop integration is separate work.

## Original semantics and static implementation

The high bit does not unconditionally mean sound completion. At 8235 the
original stores Y into CE, loads D7 and shifts it right. If D7 bit 0 is set,
it performs a genuine JSR with return address 823E and stops here at the
uncomposed header-table dispatch entry 80FB. This accepted bounded prefix
preserves its CE write, flags and wrapping stack pushes; it does not invent
header results or mark the sound complete.

If D7 bit 0 is clear, the original jumps to 8197, clears CE/D0/D1/D7/D8, then
executes channel shutdown at 81A3. A nonzero CF causes the complemented channel
mask to be processed by 81C0, with 80BB channel-volume writes, music-envelope
refresh markers, the three final APU writes and restoration of the saved mask
before clearing CF. CF=0 skips that channel loop. Both paths finish through the
real outer RTS at 81B2. All 55 original instructions in this bounded translation
are separately annotated, audited and exercised.

The source is static translated 68020 game code, not a generic 6502 interpreter.
Native subroutine linkage is separate from the emulated wrapping 6502 stack.
Internal original JSR frames are pushed and popped in original order. Internal
returns are invariant because neither channel state nor APU effects can alias
the stack page; the final outer RTS uses its actual RAM bytes, even when its
destination coincides with an internal instruction or the entry point.

## Standalone contract

`recovery_sfx_stream_control.s` accepts only original PC 8235, with arbitrary
A, X, Y, all 256 raw P values, all 256 SP values and arbitrary 2,048-byte RAM.
No assumption about the current stream byte is used. CF and D7 may each be any
byte. Every other PC is rejected atomically before touching RAM, context or
journal. There are no resource reads or unvalidated resource pointers.

A0 points to RAM (2,048 bytes), A1 to the eight-byte context and A2 to a 30-byte
journal. A3 is unused. The caller supplies valid, disjoint, exclusively owned
buffers and selects PRG bank 3. The composite checks the live serial mapper.
D0 returns 1 or -1; D1–D7 and A0–A6 are preserved; native CCR is scratch.
The journal contains a two-byte count followed by at most seven four-byte APU
records. Its unused tail remains caller-owned and unchanged. Rejection leaves
the entire journal unchanged. Resource data and executable code remain immutable.

Raw status is exact in standalone tests, including B/U and decimal bits.
This subset contains no ADC or SBC instruction. Original test CPU arithmetic
still uses Ricoh binary ADC/SBC despite D for consistency with predecessor
proofs. Continuous comparisons retain the established architectural B/U
normalization; that normalization is not substituted for raw standalone tests.

## Qualification

- Main ROM-free suite: 133,376 accepted cases and 65,535 inert rejections.
- Main original-cartridge suite: the same 133,376 accepted cases and 65,535
  inert rejections; accepted native results match original CPU execution and
  the separate declarative model.
- Directed original audit: 512 additional accepted original/native/model cases,
  every one of the 55 static original instructions executed, and all original
  instruction annotations checked against the approved cartridge.
- Source-only isolation: main ROM-free suite and static audit run from a fresh
  temporary tree with cartridge reads and private reference imports denied.
- Six new continuous histories: neutral, confirm, Left and Right at the default
  checkpoint, plus the two extended shutdown histories.
- Twenty unchanged predecessor histories: four inputs each through tick-entry,
  command-mask, event-action, active-control and envelope compositions.
- All 760 frozen predecessor files retain their recorded hashes, including all
  envelope files and its manifest. The approved ROM and delivered Z/X disk
  retain their original hashes.

The main suite exhausts the raw P/SP product, the CF/SP product, every invalid
entry PC, and nine coincidental final return destinations across every SP.
Tests compare full ordered RAM and APU effects, full RAM/context, journal
contents and untouched tail, register ABI, native stack balance, canaries,
immutable code/resource buffers and read/write bounds. Original execution is
stopped by executing the actual outer RTS or JSR, not by a coincidental target PC.

Neutral and confirm retain the prior endpoints: respectively 1,219 helpers,
41 NMIs, 39 returns, `A06CFFFFFFA4BDA7`; and 1,196 helpers, 40 NMIs, 38 returns,
`C5F8F800FF27BFA7`. Default Left/Right retain 1,429 helpers, 46 NMIs and 44 returns,
`FE9000100026FFA7`, bank 2. Extended histories stop before executing command 0E.

## Reproduction

From the repository root, configure VASM to a vasm m68k Motorola-syntax assembler
and PYTHONPATH to installed machine68k and py65 dependencies. No emulator or
firmware is needed for these host tests.

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_test_sfx_stream_control_isolated.py
python port/tests/recovery_test_sfx_stream_control.py --rom
python port/tests/recovery_test_sfx_stream_control_audit.py --rom
for input in 0 16 1 2; do
  CHARACTER_INPUT=$input python port/tests/recovery_test_resident_sfx_stream_control.py --rom
done
for input in 1 2; do
  CHARACTER_INPUT=$input AUDIO_RETURN_CAP=118 \
    python port/tests/recovery_test_resident_sfx_stream_control.py --rom
done
for checkpoint in tick_entry command_mask event_action active_control envelope; do
  for input in 0 16 1 2; do
    CHARACTER_INPUT=$input python port/tests/recovery_test_resident_sfx_${checkpoint}.py --rom
  done
done
```

Private cartridge comparisons require `input/rescue-rangers-europe.nes`, SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Set PRIVATE_TRACE_DIR to a directory outside the project to retain optional
private RAM/context/effect captures. Public files contain no cartridge image,
firmware, extracted assets or captured RAM.

## Remaining limits

Every continuous comparison starts at FE24 **after NES hardware warmup**, not
the reset vector. No reset-vector warmup proof is claimed. The odd-D7 80FB
header dispatch is only reached, not translated here. The preexisting 8249 and
8152 boundaries remain. The 83A0/0E integration boundary is intentional.
The frozen music guards and envelope behavior remain unchanged.

Host equivalence does not establish audible Paula output, stock-machine
performance, target execution or playability. Z=B and X=A remains the user
mapping. The delivered ADF and all original inputs remain unchanged.
