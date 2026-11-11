# Fixed-bank player action family, helper 150

New static native 68020 logic, not recovered historical playable source.
No target, delivered disk, original cartridge, predecessor source, other project,
publication or Space item is changed. Parent integration and independent review
remain separate. No playable-game, pickup/throw-completion, PAL-speed, rendered
pixel, audible-output or hardware claim is made.

## Bounded original logic

Half-open fixed-bank ranges C940–CBA2, CBAC–CC9F, D50F–D5FC, D604–D657 contain
533 statically translated original instructions. C940 is the real state-zero
entry selected by C8EE's original state tables. CBAC is its vertical/collision
state path; D510/D559 contain stage-dependent movement checks; D604 checks a
carried-object action. The module includes directional and B-button decisions,
but external movement/collision/object dependencies remain untranslated here.
Data tables, including D5FC, remain only in the immutable approved PRG resource.
No production opcode fetch/decoder or captured-state/effect replay is present.

41 public instruction-aligned entries:
C940,C946,C94C,C96B,C9D0,CA1F,CA31,CA4E,CAA2,CAC6,CADA,CAE4,CB70,CB73,
CB78,CB8E,CB9F,CBAC,CBB3,CBCC,CBD9,CC09,CC18,CC21,CC60,CC6D,D50F,D510,
D559,D57A,D583,D588,D59A,D5A5,D5B0,D5B8,D5C3,D5CE,D5D2,D604,D62F.

Every JSR writes authentic wrapped 6502 stack bytes. External calls expose their
actual PC and stack, including F0FB/F000/F066/F31D/D40B/D3E7; integration must
supply these dependencies. RTS routes only to static original JSR return sites;
other popped targets are honest exits, even when also public entries. External
branches/jumps expose their actual target. C940 first calls CBAC, whose reached
F0FB dependency is not bypassed. D6A3 and C8EE remain outside ownership.

## ABI and admission

A0 RAM2048, A1 context8 (big-endian PC,A,X,Y,raw P,SP,reserved), A2 journal60002,
A4 runtime12, A5 immutablePRG131072. D0=1 success/-1 inert rejection. Other
registers and SP are preserved in USER mode. Runtime guards require control1E,
bank0–7, zero serial word at4, and D501 at10. Fixed-code execution accepts each
valid mapped bank because D58A can read live banked data. No mapper change occurs.

A copied-state preflight reserves2060 stack bytes.2304 bytes suffice within the
4096 target stack contract. Both passes have20000 source-instruction and15000
resource-record limits. Rejection leaves caller RAM/context/journal/runtime
unchanged. Commit preserves ordered RAM writes and resource records. Inputs and
resources must remain immutable across both passes; buffers and stack must be
disjoint. Journal records are address-word/value/kind0 with count-word prefix;
the shared134638-byte journal is sufficient. Reads occur twice, once each pass.

16-bit address wrapping, zero-page indexing and RAM mirrors are preserved.
Binary 2A03 arithmetic ignores raw decimal D. NZ and arithmetic preserve other
raw flag bits; PHP/PLP retain original B/U semantics. Reserved context survives.

## Evidence and reproducibility

Private test starts with continuous original execution from FE24, then follows
240 original main loops using Right/periodic A controller input. Native slices
are compared against original-first states and never repair or drive the oracle.
889 slices pass, maximum63 original instructions; genuine route observes zero
resource reads within this bounded module. Entries visited: C940103, CBD9222,
CC60122, CBAC116, CADA218, CC18104, CC214. Logical NMI634 at241st C77B entry.
This is isolated-slice evidence, not persistent native-game-loop evidence.

12,288 synthetic raw-P/SP variants independently restore captured fixtures or
explicit zero-RAM synthetic entries. Together with48 pointer/bank variants (12,336 total), they cover350/533
instruction PCs. Pointer variants exercise RAM mirrors, mapped/fixed PRG and
16-bit wrap across all8 mapped banks.
Synthetic fixtures/outer1234 return bytes are not genuine reachability evidence.

Public tests reject all65,495 nonentry PCs, test all256 raw-P/SP RTS variants,
invalid runtime guards, unsupported IO/data pointers, valid mirrored/PRG pointers
and a cyclic genuine RTS continuation that exhausts the instruction budget
without committed effects. Every call checks full-width bounds, USER mode,
register/SP preservation, code/resource immutability, guards and journal tail.
The synthetic resource-record limit is not claimed exhausted independently.

Run public restored-source checks:
`bash port/tools/recovery_player_action_public.sh`
with pinned VASM and machine68k on PYTHONPATH. This copies source/test dependencies
to a fresh temporary tree without inputs and forbids private ROM/oracle imports
and reads. Python hooks are regression guards, not an OS security boundary.
`--quick` skips only the nonentry sweep. Private checks:
`python port/tests/recovery_player_action_test.py --rom`.
Offline approved-ROM regeneration through
`port/tools/recovery_player_action_generate.py` reproduces native source exactly.
Native binary16950 bytes; SHA256
`1ba76c5231764e9a2133fa28df40023bd1d1b2545a92f8cba704a1f5e251f805`.
