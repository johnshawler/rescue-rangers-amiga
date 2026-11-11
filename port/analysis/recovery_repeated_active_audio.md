# Repeated active audio: native control, envelope, duration and command03

Five new static 68020 helpers compose the existing indexed parser into genuine
repeated music calls. Production code is static native assembly with translated
control flow, arithmetic and original stack effects. It contains no instruction
fetch/decode loop, general CPU interpreter, captured state initialization or tone
generator. The caller supplies the immutable private bank3 resource view; original
music data and lookup tables remain interpreted as data. No old helper is edited.

## Completed standalone proof

`recovery_test_repeated_active_audio.py` independently executes the actual Europe
ROM from reset, through the first real active music tick, to obtain test-only
initial state. It loads native RAM/context once per sequence and keeps those
buffers resident across every subsequent helper call. A caller starts each new
standalone audio invocation at C0F6; it does not modify RAM or other CPU fields.
The original reference continues from its own exact preceding output. This is
explicitly **not** a native reset or repeated game-frame proof.

- Default: 16 bootstrap seeds × 16 complete calls, 5,632 native helper calls,
  1,600 ordered APU writes (100 per sequence).
- `--ticks 41`: 16 seeds × 41 calls, 14,384 native helper calls and 4,928 APU
  writes (308 per sequence). All finish at original C0F9. At call41 the four
  durations are all04. A separate bounded exploratory execution reaches the
  first unsupported command02 at83A0 in call42. It is not skipped.
- The first16 per-call APU counts are
  12,4,2,2,2,4,0,0,0,20,8,8,8,16,8,6.
- Every boundary compares all2KiB RAM, context, ordered original RAM/resource/APU
  effects, exact native resource reads including preflight, immutable resources,
  ABI preservation, native stack balance, guards and global access whitelists.
  Production buffers are never replenished from reference output after bootstrap.
- The reference uses actual original instructions, two real initial NMIs and
  real mapper state. Raw reference status is not patched; a named context view
  clears virtual B and sets architectural U for comparisons.

Call9 genuinely encountered previously missing command03. Its new translation
was added rather than stopping after the initial envelope prefix. All41 calls
retain CF=0, so no CF callback claim follows from this proof. The control helper
rejects nonzero entry CF and pending D0/D1 work, rather than clearing or bypassing it.
Phase wrap runs the original double pass through its stacked8052 continuation.
Envelope processing includes instrument attack/decay/release, volume, triangle
rules, amplitude/pitch modulation, pitch conversion, glide and ordered APU output.

## New contracts

All entries use A0→2048-byte RAM and A1→8-byte context (big-endian PC,A,X,Y,P,SP,
reserved). Resource helpers use A3→immutable16384-byte bank3 view. Buffers/code/
native stack must be valid, disjoint, exclusively owned. D0 returns1 or -1 inert
rejection; all other native registers are preserved, native CCR is scratch.

- `recovery_music_active_control.s`: C0F6 or8085→8374,839D,or actual tick return.
  No journal/resources. Canonical D=0; entry CF,D0,D1 zero.8085 requires stacked
  channel0..3. All original RAM and page-one effects retained. The control
  helper follows at most one phase continuation: generated in this invocation,
  or validated at8085 by the complete wrapped savedCF00/return8051/outerreturn
  C0F8 structure. Other80BA RTS destinations, including8052 and8085, are
  published as natural boundaries, not followed. This structural rule does not
  claim the frame has authenticated provenance.839C follows only its channel
  return generated in the same invocation.
- `recovery_music_duration_prepare.s`:8374→837F or86B2; journal10. Original
  instrument lookup and call frames retained. See duration report for full guard.
- `recovery_music_active_envelope.s`:86B2→actual original RTS target, normally
  837F. Journal514 (count word plus128 records). Each record is address word,
  value byte,kind byte:0 resource,1 APU. Unused bytes are zero on success.
  Requires X28..2B, canonical D=0, stage(0704,X)&7<=4, C5 pointer8000..BFF8,
  threshold resource892E=0 and the five dispatch targets at86BF. The11
  preflight bytes are unjournaled; original semantic reads remain in order.
  These guards bound all reached resource reads and threshold-search loops.
- `recovery_music_duration_progress.s`:837F→839D or actual RTS; no journal.
  Gate expiry, duration subtraction and original stack writes retained.
- `recovery_music_active_command03.s`:83A0/A=03→839D; journal10. Does not
  consume a stream argument. Toggles bit08 of indexed channel flags. Supports
  canonical status including D=1 (no ADC/SBC), validates dispatch8489/848A.

## Standalone verification

- Active control:16,384 ROM-free and16,384 independent original-ROM cases;
  66,523 inert guards and16,128 bounded-return regressions in each suite.
  These cover all SP values, restoredCF0/1/128/255, caller8052/8085 returns,
  chained returns and each of the five structural frame bytes independently
  altered. The exact review reproducer now returns at8052 with restoredCF1
  and four RAM writes, without entering the unsupported callback.
- Envelope native:4,096 independent original-ROM cases. Additional independent
  structured domain model:16,384 original-ROM comparisons,16,384 ROM-free
  synthetic-resource/native comparisons and117,978 inert guards.
- Command03:4,096 ROM-free and4,096 original-ROM cases;66,744 inert guards.
- Each duration helper:65,536 ROM-free and65,536 original-ROM cases plus66,011
  inert guards. See `recovery_music_duration_progress.md` and
  `recovery_music_envelope_declarative.md` for their detailed coverage.

Assembled VASM `-m68020` binary sizes/SHA256:

- Control1484:42a12fb7fab0568f28c3e9784e9f71567d25973a0b113cfa98b2e3fe8173e97a
- Envelope4586:801f24d8f99cc4a70ba6d9de6f8516b6d161f7dbafef296fd864d418033cbe96
- Command03 738:4486e9c3775613ec4eb44a5fa41246e1ada2e081490634eb46396d8611762eaa
- Prepare358:fdcd8be0a20d0aaaa68c5a715338b06ac8b6e5e2e087c815752ad627185df3fa
- Progress288:56a95900a05e1698bee53be8804a7cbb6a4a04f6f5aade53379aed02340c2fd1

Run with VASM pointing to vasmm68k_mot and PYTHONPATH containing machine68k and,
for private ROM tests only, py65. The three contract suites and duration contract
suites use synthetic resources and do not need the cartridge or py65.

Private cartridge hash remains
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No ROM/firmware extracts, raw traces, captured initial state or new ADF are
published. No Paula renderer, audible output, game-speed measurement, full boot,
playable game, physical target or stock-target execution is claimed here.
The [resident reset/fade composition](recovery_resident_startup_fade.md)
provides the separate connected-runtime proof.
