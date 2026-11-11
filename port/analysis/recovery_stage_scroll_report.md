# Native stage camera and map-update helper 160

This additive static 68020 module owns fixed-bank instruction ranges
D6A3–DB6D, DB6F–DBEC and DD1A–DF62 (exclusive ends). It covers camera movement,
one/two-player horizontal constraints, horizontal/vertical scroll bookkeeping,
and map-update orchestration. Original tables between the ranges remain private
immutable PRG resources. The generator is offline and hash-checked; the native
module never fetches or decodes 6502 instructions and never replays effects.

The frozen map helper 100 remains separate. DBEC is an authentic tail exit;
E06B and DF8A are authentic JSR exits. All original return addresses and stack
writes are preserved. Public entries and JSR continuations are enumerated in
`port/tests/recovery_stage_scroll_test.py`. Raw PHP/PLP pseudo-B behavior is
preserved, with no hidden canonicalization. Success-only legacy ABI adapters,
if used by integration, belong to the separately reviewed integration layer.

## Contract

A0: RAM 2048 bytes. A1: eight-byte PC/A/X/Y/P/SP/tag context. A2: counted
journal, at least 60,002 bytes. A4: runtime 12 bytes. A5: immutable full PRG,
131,072 bytes. D0 returns 1 on success or -1 on inert rejection. Every other
register and SP is preserved in USER mode. Reserve 4,096 native stack bytes;
the tested minimum preflight allowance is 2,304 bytes.

Caller pointers must designate valid disjoint RAM/context/journal/runtime/PRG,
code and native stack. RAM, context, runtime and resources must not change
concurrently during validation and execution. Host pointer validity is the
caller's responsibility. Supported runtime control is 1E, bank 0–7, zero mapper
serial state, and magic D501. CHR fields are preserved, not spoofed.

A bounded scratch execution validates before committing RAM/context/effects.
Instruction budget: 20,000 per pass. Resource-record budget: 15,000 per pass.
Unsupported 2000–7FFF data reads and non-RAM writes reject before publication.
RAM mirrors, 8/16-bit wrap, original stack wrap and Ricoh binary arithmetic are
preserved. The original cartridge and all fixture state remain unchanged.

## Verification

The unmodified terminal fixture from the continuous native loader/frame chain,
entry D6A3 with context D6A300001027BDA7 and mapper 1E/00/10/06, matches original
instructions exactly: 45 instructions, no resource reads, exit
C80AE40010A4BFA7. This validates the actual next native dependency without
patching the live state or synthesizing a return.

The continuous original-first 240-loop Right/periodic-A route matches 323 native
helper slices and 205 ordered resource reads. Maximum slice: 92 original
instructions and three resource records. Visits: D6A3 240, DAAD 83; 634 logical
NMIs. Camera X ranges from 0 to 166. A separate 240-loop Left/periodic-A route
matches 240 slices and 240 resource reads, maximum 96 original instructions,
with camera X remaining zero. An 800-loop Right/periodic-A route matches 1,054
slices and 608 resource reads through camera X=508, exercising a genuine
horizontal page crossing, with 1,228 logical NMIs.
These are standalone module comparisons with original execution between slices,
not a claim that the whole intervening gameplay chain is native.

Final-source private synthetic tests pass 11,768 raw-flag/stack, camera/page/player-count and
indirect resource/mirror/bank/wrap comparisons, covering 618 instruction PCs.

The test compares complete RAM/context, ordered RAM/resource events, exact
two-pass PRG read addresses, journal count and untouched tail. Native execution
checks USER mode, all preserved registers/SP, code/PRG immutability, buffer
canaries, bounded memory access and the minimum stack allowance. Test-only
compiled reductions exercise instruction/resource budget failure atomically.
The clean source-only restore passes all 65,493 invalid-PC rejections, 256
raw-P/SP cases, pointer/mirror checks, reduced budgets and runtime rejection.
The final strengthened-harness private replay and source-only quick restore
also pass; native assembly was unchanged during harness strengthening.
Exact offline generator reproduction passes.

The assembled module is 32,804 bytes, SHA-256
`db0f949c67b3eb4ff3528c0dd508feab82a334a57169704951a9b774ba82c582`.
It fits below the standalone harness's guarded data region; an explicit size
assertion prevents accidental overlap. Whole-chain integration requires its
separate relocated harness, because combined code exceeds the old layout.

No target/emulator run, publication, disk modification, timing, rendered-frame,
audio, or playable-stage claim is made. The qualified stock target checkpoint
remains stage-loaded C77B; further gameplay work remains host development.
