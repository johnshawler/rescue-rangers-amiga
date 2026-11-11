# General four-task scheduler recovery

New static native 68020 translation of the hash-checked Europe cartridge's scheduler at FE8D, with the natural FE90 scan reentry. This is a bounded scheduler primitive for a persistent original-context runtime, not a complete runtime or playable game. Existing helpers, builders, aggregate scripts and delivered media were not modified.

## Contract

`recovery_general_task_scheduler` takes A0 = writable 2048-byte original RAM, A1 = eight-byte context (big-endian PC word, A/X/Y/raw P/S/reserved), A2 = writable 74-byte journal, and D0.b/D1.b = decoded standard controllers (A/B/Select/Start/Up/Down/Left/Right from bit 7 to bit 0). Upper input register bits are ignored. Buffers, code and host stack must be disjoint and exclusively owned during the synchronous call. No asynchronous NMI is injected inside a call.

The controller journal is a big-endian count word followed by up to eighteen records of address word, value byte, kind byte (0 read, 1 write). Records are complete before count publication. Unused tail is untouched. Non-polling successful calls write a zero count; unsupported PCs leave every buffer untouched.

Results in D0:

- 0: no eligible task after exactly one four-slot scan. Context is the original FE90 boundary after the backward jump. This is **not** a resume. RAM $90 is zeroed by the real scan entry; no task readiness is changed.
- 1: original saved-stack task resumed. Context is the original continuation after RTS, before executing its first instruction.
- 2: original fresh-task indirect dispatch, before executing the selected target instruction.
- -1: unsupported PC, inert rejection.

D1-D7/A0-A6 are preserved, host stack balances and host CCR is scratch. Entry FE8D resets original S to FF; entry FE90 retains S. All other original context bytes and RAM may be arbitrary. Acceptance is a translation contract, not a claim that arbitrary task states or target PCs are meaningful gameplay. Caller must dispatch returned original PCs to their corresponding static native code; there is no instruction decoder, dynamic CPU interpretation or ROM access in production.

## Retained original behavior

Slots at $80/$84/$88/$8C are scanned in order. Every unsigned state >=4 is eligible, not just state 4. Exactly state 8 selects a fresh task. The original $91 selection and state-2 store occur in their original order. Fresh vectors come from the selected slot's $82/$83 into $93/$94; no additional resource view or fabricated stack is needed. X remains the slot offset, Y the old state and A the vector high byte.

Other eligible states restore original S from the slot. Only task zero executes the original C162 standard-pad poll, including both JSR stack stores, both strobe writes, sixteen interleaved reads, intermediate ROL stores, previous-held edge derivation, direction sanitation and consumed RTS frame reads. Expansion bits are explicitly zero. Then the original Y and X are popped and the return address is consumed, wrapping S within page one. Return PC increments modulo 65536. Consumed stack bytes remain present in RAM.

Raw P is preserved without canonicalizing B/U. Only the original affected N/Z/C bits change; V/D/I/B/U retain their input bits. Carry for nonzero saved tasks follows the comparison against state 8; task-zero carry follows controller sanitation. The idle scan leaves Z set and C/N clear, with A equal to the fourth slot's state, X=16, Y=0. No timer, readiness, pending flag or interrupt is invented.

## Verification

With VASM set to the approved vasmm68k_mot and PYTHONPATH set to the inspection dependencies, run:

- `python port/tests/test_recovery_general_scheduler_contract.py`
- `python port/tests/recovery_test_general_scheduler.py`
- `python port/tests/recovery_test_general_scheduler_startup_composition.py`
- `python port/tests/recovery_test_general_scheduler_stage_composition.py`

The helper assembles to **542 bytes**. Executed results:

- **70,085 ROM-free declarative cases**, using invented state, independently expressed state operations and no ROM/reference CPU. Includes five inert invalid-PC cases.
- **70,080 independent actual-ROM differential cases**, with hash pinning to SHA256 051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411. Original instruction execution uses an explicit bus read/write whitelist and bounded instruction budget.
- **256 continuous existing startup compositions**, real first NMI, silent tick and RTI through the general scheduler to C584, without RAM patches or captured state. This reuses the existing startup reference sequencing. Its explicitly named architectural RTI comparison view remains unchanged: py65's virtual B marker stays untouched in the oracle, while the view matches the older native interrupt helpers. The new standalone scheduler tests separately compare raw P without that view.
- **4,096 synthetic stage-prefix/frame-yield compositions**, reaching FE8D and taking an honest empty scheduler scan, then a repeated FE90 scan. Stage prefix contributes 561,966 ordered effects; the scheduler effects are checked separately. The inherited preceding fade proof also executes all 262,144 binary SBC truth-table cases.

Standalone coverage includes each slot, every eligible state byte 4..255, wrapping saved-stack positions, representative fresh-pointer bytes and raw flag bits, all 256 raw status bytes on task-zero/idle paths, both scheduler entry PCs, and all 65,536 current/previous controller-one pairs with complementary controller-two inputs. Full RAM/context, ordered RAM/controller effects, exact journal/tail, guards, native register preservation and bounded balanced stack are compared. Native accesses are globally whitelisted; the standalone harness retains negative distant and crossing read checks.

The stage composition is deliberately an extension of the existing **synthetic** C6B5 contract, not a reset-generated stage entry. It starts with task zero selected and four initially inactive task slots, plus the existing stage initializer's F6=0 / mapper / resource prerequisites. These are declared initial test conditions, not inserted patches after a yield. Native and reference state are passed unchanged through resource initialization, player initialization, fade entry, FF04 and scheduling. The scheduler uses the same native RAM/context buffers after the preceding slices. Its only subsequent changes are original scheduler effects. State 1 and palette request $18=FF remain pending after both empty scans.

## Honest remaining boundary

The stage composition does **not** resume C2A8. Its wait state must first be advanced by actual NMI timer processing, with pending palette and any other queues handled, followed by sound processing, bank restoration and RTI. Repeated empty scans do not simulate that work. The existing first-NMI prefix explicitly rejects a pending palette; the palette-specific prefix can handle its documented restricted queue state but is not a general NMI implementation. Both existing prefix entry contracts are FE8D, while the bounded empty scheduler naturally returns FE90. A persistent runtime therefore also needs actual interrupt entry/resumption at that scan boundary; rewriting PC back to FE8D or clearing pending queues is not an adapter.

The broader reset/title path's later active music/NMI return and mapper-deferred-audio requirements remain integration dependencies. No NMI was skipped to make the stage test resume, no post-yield readiness was patched and no continuation frame was manufactured. There is no full boot, title integration, complete loader, playable stage, audible output, cycle timing, physical-Amiga or performance claim. No cartridge, firmware, extract, captured frame or raw trace is included in these new files.

## Subsequent integrated checkpoint

The helper-local limits above describe this component when introduced. The
[bounded resident runtime target](recovery_runtime_target.md) now verifies the
reset-generated idle/NMI/initial-music/RTI/task-resume path on an emulated
stock PAL A1200. Stage frame-yield compositions remain separate synthetic-entry
proofs. Public and private aggregate scripts include these helper suites.
There is still no complete native gameplay loop, audible output or speed claim.
