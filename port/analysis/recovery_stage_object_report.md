# Additive native stage-object window

Helper 116, `recovery_stage_object_region`, statically translates bank 4
8040–8087 (initial object window), 8090–8192 (object scan and spawn), and fixed
F31D–F327 (spawn animation pointer initialization). Only 8040 and 8090 are
public entries. Internal JSR/RTS executes native logic with the original 6502
stack bytes and wrapped SP. An outer RTS exits at its actual popped return PC.
No opcode decoder, captured-effects replay, game tables or instruction bytes
are linked into this source. Offline generation verifies the private approved
cartridge SHA256. Unsupported IO pointers and exhausted bounds reject inertly.

## ABI and limits

A0=RAM2048, A1=context8 (big-endian PC, A/X/Y/raw P/SP/reserved), A2=counted
journal60002, A4=runtime12, A5=immutable PRG131072. D0=1 success or -1 inert
rejection; all other registers and native SP are preserved. USER mode only.
Runtime control byte0 must be1E, mapped bank byte3 must be4, serial-state word4
zero, and magic word10 D501. Runtime metadata is not modified. Helper has no
mapper/audio/PPU dependency or implicit scheduling. Full shared journal134638
and dedicated native stack4096 are sufficient.

Preflight copies RAM/context to2060 bytes of stack and executes the same native
logic before committing real effects. At least2304 stack bytes are required.
Each pass has20000 original-instruction budget and15000 resource-record limit.
Scratch rejection never changes caller RAM/context/journal/runtime. Immutable
reads during failed validation remain possible. Buffers, stack, code and PRG
must be disjoint; no writer may alter inputs between passes. This is a bounded
correctness checkpoint, not a target-speed result.

Resource reads are semantic live reads in original order, recorded as CPU
address word/value/kind0, preceded by word count. Fixed C000–FFFF uses bank7;
8000–BFFF uses guarded bank4. RAM mirrors use000–7FF. Pointers and arithmetic
wrap at authentic6502 widths. Binary2A03 ADC/SBC ignores the raw decimal flag
while preserving unrelated raw flags. Private test expects twice the semantic
resource reads because of validation plus commit. RAM writes are real writes,
observed independently from the resource journal.

The object tables at ($72),Y through ($7C),Y and spawn metadata through ($04),Y
are live immutable resources or authentic RAM, never embedded data. Native
logic writes initial window indices70/71, original pointer scratch, object
position/type/flags/animation arrays, and genuine6502 call stack state.

## Verification and reproduction

Set VASM to the approved vasmm68k_mot, PYTHONDONTWRITEBYTECODE=1, and PYTHONPATH
to the private py65/machine68k dependency directory. From repository root:

    python port/tests/recovery_stage_object_test.py
    python port/tests/recovery_stage_object_test.py --rom
    python port/tools/recovery_stage_object_generate.py

Public tests assemble without cartridge input, reject65534 nonentry PCs, cover
256 raw-flag/wrapped-stack fast returns, reject IO and invalid runtime fields,
and test bounded inert rejection of an endless malformed object scan. Every
native call checks USER mode, register/SP preservation, guard bytes, full-width
memory-access bounds, unchanged code/resources, and journal tail preservation.

Private tests start original execution at FE24 and reach stage initialization
at logical NMI377. Both real calls,8040 and8090, compare all RAM, context and
ordered effects. They consume93 semantic resource reads, at most89 per call,
and at most1055 original instructions. The native helpers return honestly to
the original callers; the enclosing original stage sequence reaches E106.
These are standalone original-first fixtures, not whole-native reachability.
A separate512-case synthetic test varies every raw flag and wrapping SP for
both reached inputs, with an explicit synthetic outer return and original
semantics as oracle. These cases are not called genuine route evidence. Together they exercise129
of170 translated instruction PCs; remaining branches are not fully qualified.

Parent integration and independent review remain separate. No target emulator,
firmware, published repository or delivered disk was changed. No full-game,
PAL FPS, accurate raster/NMI timing or audio-fidelity claim is made.

## Source-only allowlist

Only these five additive files belong to this module:

- port/src/recovery_stage_object_region.s
- port/tools/recovery_stage_object_generate.py
- port/tests/recovery_stage_object_test.py
- port/analysis/recovery_stage_object_report.md
- port/analysis/recovery_stage_object_manifest.sha256

The generator is a standalone specialization of the frozen map generator;
it does not modify or require changes to that predecessor. Tests reuse its
original-route bootstrap and semantic-read oracle. Reproduction must be
byte-exact. Never publish cartridge, firmware, assets, compiled binaries or
trace/state fixtures. Restore by removing only this allowlist and any separately
owned integration references, not by resetting or cleaning the shared checkout.
