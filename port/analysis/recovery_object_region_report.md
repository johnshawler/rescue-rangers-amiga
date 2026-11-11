# Bounded bank5 object/sprite native region

This additive source translates original bank5 $8000–$81DF into native 68020
instructions. It is not a runtime 6502 decoder or captured-state/effect executor.
The offline generator consumes the approved private reference only to identify
this bounded instruction region. Public assembly contains native game logic,
not proprietary tables. All table data stays in the immutable external PRG view.

## Stable integration contract

Entry: `recovery_object_region`, reserved helper ID90. A0 points to disjoint
RAM2048; A1 context8 (big-endian PC, A, X, Y, raw P, SP, reserved); A2 counted
journal60002; A4 mapper/runtime12; A5 immutable PRG131072. D0 returns 1 on success
or -1 on inert rejection. D1–D7 and A0–A6 are preserved, including USER-mode native
SP. Native CCR is scratch. Reserve at least 2304 bytes disjoint native stack.
Publish runtime journal size60002, not a 65535 sentinel. Source is 5512 bytes,
binary SHA256 be69923025893d466d3c32e8ffcb77b914dbd12c97619d4fd663a84d72f76a21.

Admitted entry is PC8000, runtime control1E/bank5/empty latch/magicD501, with a
stacked top-level RTS destination outside8000–81DF. No canonical rawP assumption
is imposed. Genuine nested JSR/RTS/PHA/PLA/PHP/PLP use wrapped emulated SP and RAM.
The helper does not select a bank, manufacture a caller frame, or alter runtime.
F392 selection/return and other fixed-bank callers remain separate integration.

The wrapper first copies RAM/context into temporary native stack storage and
executes the same static native logic there. Invalid pointer domains, resource
budget exhaustion or execution budget exhaustion cause inert public rejection.
The private core's -2 is never public on this admitted contract. The caller must
keep RAM, context and resource unchanged between validation and committed passes;
interrupt interleaving that modifies these buffers is unsupported.

Each pass admits at most199999 original instruction labels before rejecting and
at most15000 resource reads. No dynamic path can run forever, overrun the journal,
or escape resource bounds. Zero-page indexed addresses wrap; indirect data reads
admit RAM mirrors0000–1FFF and PRG8000–FFFF, rejecting I/O/unmapped2000–7FFF. RAM
stores remain statically bounded by the translated addressing modes. Resources
8000–BFFF map bank5, C000–FFFF fixed bank7. Neither validation nor execution writes
code or PRG. A malicious top-level return inside the region rejects before running.

Validation resource reads are not semantic effects: A0 points to private native
stack RAM in that pass. In the committed pass A0 is the caller RAM, each resource
read publishes address.word/value.byte/kind0 in the counted journal. RAM stores
occur directly in original order interleaved with these resource events. There
are no APU, PPU, mapper or controller accesses in this translated region. Invalid
I/O addresses are rejected, never silently treated as reads. Unused journal tail
remains unchanged. A0 distinguishes validation reads in instrumentation only;
it does not influence game logic.

This doubles the translated work and adds a RAM/context copy. There is no stock
hardware speed claim. The explicit label budget adds further overhead. The
original stage, rendering and audio are not replaced by this helper.

## Verification

The final bounded implementation passed an original-first, continuously driven
FE24→FF53→F392→first-stage route followed by240 Right/A movement frames. It compared
242 authentic object calls:354758 original instructions,53781 semantic resource
reads, max276 reads/call, with genuine returns F3A2(1),C265(1),C83A(240). Comparison
covers all2048 RAM bytes, raw context, ordered RAM/resource effects and semantic
resource offsets. Native outputs never drive the reference and no captured state
is loaded. This proves these helper boundaries, not the full native game.

4096 additional private original-first probes use synthetic external table data,
coordinate/animation/clipping branches, every rawP and every SP. They cover1098006
original instructions and121089 semantic reads. These are branch probes, not an
expanded authentic route or arbitrary-game guarantee. The public suite uses no
ROM: unsupported-PC domain, mapper guards, all internal top-level return targets,
2560 supported inactive-object cases spanning all rawP/SP and both scan orders,
width-aware bounds, code/resource immutability and malformed-data/tiny-budget
transaction failures. Test hooks lowering budgets are test-only native source
mutations; target uses the fixed budgets above.

Final route session9099 and private-branch session70106 completed. Final public
session91462 passed2560 supported cases and66024 inert rejections, including the
complete unsupported-PC domain. Compact final public session77717 separately
passed the same2560 supported cases and495 selected inert checks. The test-only
10000→100000 native execute-iteration allowance does not affect exercised
results; the full session began before this timeout-only harness adjustment.
Independent review also passed78 pointer/stack/resource/budget probes and clean
source-only assembly plus generator equality on final source. Earlier sessions
10872/82893/24110 exercised the predecessor without transactional validation;
3513 exercised preflight before the explicit instruction budget. These are not
substitutes for final-source evidence. No actual emulator session, target disk,
public commit or publication was performed by this worker.

## Reproduce and restore

From repository root, set VASM to the pinned vasmm68k_mot, PYTHONPATH to the
private inspection .deps, and PYTHONDONTWRITEBYTECODE=1. Run:

    python port/tests/recovery_object_region_test.py
    python port/tests/recovery_object_region_branches.py
    python port/tests/recovery_object_region_route.py

The first command requires only machine68k/VASM and generic source. The last two
also require py65 and the privately approved input/rescue-rangers-europe.nes,
SHA256051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411,
and existing baseline oracle modules. Optional generator reproduction:

    python port/tools/recovery_object_region_generate.py

Restore only the source files listed in recovery_object_region_manifest.json
onto the preserved baseline and verify hashes. Add legally owned private inputs
only for private tests. Do not distribute ROM, generated binaries, RAM snapshots,
captures, journals, firmware or disks. Existing renderers, sound/keyboard helpers,
and delivered disk remain unchanged. Integration into the actual live target is
separate work and has not been qualified by these host tests.

The generator currently supports only instructions present in this one bounded
region and fails explicitly on other opcodes. Static flag/address emitters may
be reused for future work only after independently reviewing its new instruction
set, native scratch registers, bank/resource mapping, stack contract, call/return
edges and original-first tests. It is not a general production CPU backend.

## Release test hardening

Review found the first tiny-budget tests reused an already-invalid pointer fixture,
so those cases could pass without budget enforcement. The corrected test separates
malformed pointers from budget tests, explicitly proves two controls succeed, then
checks instruction budgets20/40 and resource caps1/5 reject those accepted inputs
inertly. Each native test-source substitution must occur exactly once. Focused
final check completed successfully (exec chunk1093cc, exit0): five inert rejection
cases and two accepted controls. Runtime source/generator/binary are unchanged.
The earlier exhaustive session91462 remains valid for its supported/entry/stack
scope, but its budget-fault claim is superseded by these strengthened checks.
No exhaustive sweep was repeated for this test-only change.

Focused reproduction:

    PYTHONPATH=port/tests:$PYTHONPATH python -c 'from recovery_object_region_test import transaction_checks; print(transaction_checks())'
