# Additive bank-6 frame dispatcher and reached handlers

Helper 140, `recovery_player_frame_region`, is new static native 68020 logic, not
recovered later playable/audio source. Those historical sources remain missing.
No delivered ADF, frozen source, other project, emulator, firmware, publication,
Library item or target integration was changed by this module.

## Scope and integration contract

Half-open bank 6 ranges are 8000–80A7,81BC–81CC,8BC8–8C23,8E15–8E81 and 8F38–8FC6.
The first is the live frame object dispatcher. Three included table-selected
handlers,81BC/8BC8/8F38, were independently observed on the genuine 240-loop
Right/periodic-A original route.8E15 supplies the reached collision-response
continuations. This is partial frame work, not all bank 6 or complete gameplay.

Public entries:
8000,801F,8029,8033,8050,81BC,8BC8,8BD6,8C22,8E15,8E18,8E1A,8E32,
8F38,8F4C,8F7C,8F83,8F92,8F9A.

JSR writes both authentic 6502 return bytes with wrapped SP. Internal RTS routes
only to original statically listed return sites (including the explicitly
pushed 801F return); other popped PCs exit honestly. External fixed calls,
including F217/F328/F379/F0FB/F000/F066/F92B/F977, preserve their real call stack
and return PC for a separate helper. External branch 8192 and call 8C23 similarly
exit without fabricated work. Integration must supply these dependencies.

The original table-indirect jump at 801C reads the live RAM pointer and always
returns its actual target PC, even when that target is also translated by this
module. The parent must select the next helper from the resulting context.
There is no target-opcode read or runtime decoder. The original dispatch table
bytes remain in the approved immutable PRG input, not embedded native data.

## ABI, effects and admission

A0=RAM2048;A1=context 8 (big-endian PC,A,X,Y,raw P,SP,reserved);A2=counted
journal 60002;A4=runtime 12;A5=immutablePRG131072. D0=1 success/-1 inert rejection.
All other registers and native SP are preserved, in USER mode. Runtime control
must be 1E, bank 6, empty serial word at 4 and D501 magic at 10. This helper never
changes mapper/runtime state or silently services audio, video or scheduling.

The copied-state validation pass reserves 2060 bytes before native execution;
2304 stack bytes suffice, within the shared dedicated 4096 allocation. Each pass
has 20000 source-instruction budget and 15000 semantic resource-record budget.
Rejected admission/budget leaves caller RAM/context/journal/runtime unchanged.
Successful commit performs authentic ordered RAM effects and resource records.
Journal records are address-word/value/kind 0 with a leading count word. PRG
reads happen twice, once for validation and once for commit. Inputs, resources,
stack and buffers must be disjoint and inputs must remain unchanged between
passes. Full shared 134638-byte journal is sufficient.

Data-address logic supports 16-bit address wrapping, zero-page index wrapping
and RAM mirrors. None of the instructions in this bounded region exposes a
variable data pointer into mirrored RAM or IO, so those generic access-helper
branches are not separately claimed as exercised by its public API. Dispatch
pointer targets 0,2000,7FFF,FFFF are tested as external exits with no opcode read.
No invalid-pointer target is silently executed or changed to a supported PC.
Raw flag bits are preserved where 6502 operations preserve them. Binary 2A03
ADC/SBC ignores raw D;PHP/PLP have authentic B/U behavior.

## Validation and limits

The private test begins continuous original execution at FE24 through the
reviewed startup/menu/dialogue route and stage initialization. It supplies
Right/periodic A only through original controller reads, then compares each
admitted native slice against its original-first entry. Native output never
repairs or drives the original route. The test is isolated-slice evidence,
not persistent native reachability or target/hardware speed evidence.

Observed 240 loops, ending at the 241st C77B at logical NMI634:
3347 compared calls;3164 semantic resource reads;maximum 2 records and 70
original instructions per call. All 2048 RAM bytes, context 8, ordered RAM and
resource effects, resource addresses and journal tail agree. Visits include
240 calls 8000,1033 each 8BC8/8BD6,413 calls 81BC,136 each 8F38/8E18/8033,
106 each 8F83/8F9A,7 calls 8F7C and 1 call 8F4C.

The synthetic suite explicitly restores captured original entry fixtures only
for independent adversarial tests, then varies all 256 raw P/SP combinations.
All 2,816 synthetic variants pass; combined coverage is 123 of 226 translated instruction PCs.
Synthetic outer return bytes 1234 are not genuine route evidence. Boundary
checks stop at actual indirect exits and nonlisted popped return sites.
Public ROM-free checks pass all 65,517 nonentry PCs, cover all 256 raw flags and
stack wraps on inactive dispatch, four indirect targets without target fetch,
five runtime guards and a cyclic synthetic RTS stack exhausting the native
instruction budget without committed effects. Each call verifies USER mode,
register/SP preservation, full-width memory access bounds, unchanged code and
resources, guard bytes and untouched journal tail.

No PAL FPS, raster timing, full collision behavior, full-gameplay, rendered
pixels or audio fidelity is claimed. Parent integration and independent review
are separate requirements. A0/A1/A2/A4/A5 buffers and native stack must meet the
ABI; this is not an arbitrary hostile-host-pointer validation interface.

## Deliberate control-history research

The separate original-only control-route script supplies three fresh histories,
all with Right, via controller reads only. Each reaches 241 C77B entries at
logical NMI634. B pulses change at frame entries 1,15,30,45,...,240 (initial
press spans entries 1–14, later intervals 15 entries). These reach additional
untranslated bank6 table targets:8171/type00 (70 calls),8C4F/type3C (76),
81EB/type01 (34),8E81/type1C (56). B held through entry120 then released and
A held through entries1–60 and121–180, released in between and afterward,
add no table targets beyond the three included here. The script prints exact
pad-change frame/NMI/button values, preserving the actual read-boundary timing.
These observations are prospective translation scope, not native proof that
pickup/throw/jump work or visual evidence that the intended action occurred.
Current helper 140 is not expanded to claim those new handlers.

## Source-only reproduction

Only this six-file additive allowlist belongs to this module:

- port/src/recovery_player_frame_region.s
- port/tools/recovery_player_frame_generate.py
- port/tests/recovery_player_frame_test.py
- port/tests/recovery_player_frame_control_route.py
- port/analysis/recovery_player_frame_report.md
- port/analysis/recovery_player_frame_manifest.sha256

The generator is a separate specialization of the stage-object generator; its
predecessor is unchanged. Tests reuse the existing original-route bootstrap
and native instrumented harness. Set VASM to the approved vasmm68k_mot and
PYTHONPATH to the private py65/machine68k dependency directory, then run from
the repository root with PYTHONDONTWRITEBYTECODE=1:

    python port/tests/recovery_player_frame_test.py
    python port/tests/recovery_player_frame_test.py --rom
    python port/tools/recovery_player_frame_generate.py
    python port/tests/recovery_player_frame_control_route.py
    sha256sum -c port/analysis/recovery_player_frame_manifest.sha256

Public assembly is ROM-free. Private regeneration/testing verifies cartridge
SHA256 051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
Regeneration must be byte-exact. Do not publish cartridge, firmware, binaries,
assets, traces or fixture state. Restore only these additive files and separately
owned integration references, never reset or clean the shared checkout.
