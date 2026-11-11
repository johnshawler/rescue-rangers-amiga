# Fixed F328 horizontal targeting continuation

Helper152 is an additive static native translation of F328–F36B, including its two internal F345 calls. It reads the original player-slot activity/coordinate values, preserves the original byte/word arithmetic and direction-selection behavior, stores0580,X, and returns through the genuine original stack. F36C and later routines are outside this scope. There is no resource lookup, device effect, runtime opcode interpreter, captured-profile execution or raw-status normalization.

Standalone entry is F328 with any raw A/X/Y/P/SP byte. The common ABI remains A0 RAM2048, A1 context8, A2 counted journal2, A4 runtime12 and preserved registers. A5 is not read. Successful journal count is zero; all ordered RAM writes are captured independently. Runtime is unchanged by the raw module. The composition publishes152/2 and retains actual mapper state. It requires the existing canonical task context, event0, task80=2,91=0 and valid mapper/runtime metadata.

A copied-state preflight keeps failures inert. All dynamic RAM indices are bounded within the RAM view; no external resource or device path exists. The per-pass limit is512 static instructions. Top-level return addresses inside the owned F328–F36B range are explicitly unsupported and rejected before visible mutation. Internal F32D/F337 returns remain the exact original calls. Other external returns, including16-bit wrapping to0000, are preserved. The raw module needs2304 disjoint native stack bytes; the full composition retains4096.

## Qualification

Standalone public and private suites each pass1024 paired raw-P/SP/X/player-activity cases and66884 inert guards. Every raw P/SP/X byte and all four player-activity combinations are covered, with varied coordinates, A/Y inputs and external callers including0000/FFFF return wrapping. Private original-first comparisons cover all34 owned instruction PCs and both outcomes of all three conditional branches, with a maximum44 original instructions. These paired variants are not a Cartesian proof of all RAM combinations.

The guards include all65535 nonentry PCs, five runtime guards across256 cases, all68 in-region top-level return addresses, and a shortened8-instruction diagnostic preflight that rejects a case accepted by the normal512 limit. No production512-limit exhaustion is claimed. USER execution, exact register/SP preservation,2304-byte stack bounds, width-aware memory checks, immutable code/resources, raw arithmetic flags and the complete journal tail all pass. No resource reads occur.

Full-dispatch tests add256 model comparisons and2816 inert task/status/runtime/event guards. The genuine reached entry f32801090224b9a7 independently matches the original result8f4c02090125bba7 in33 original instructions with11 ordered RAM writes. This includes the real saved8F4B return, internal JSR/RTS writes and wrapped PHA/PLA behavior. No repair of state or status is used.

The offline generator reproduces the native source byte-for-byte. Source SHA256: 562028d7f29da668f4f15fd6f8aa1617c511524002f4860ce2d966fba1159f38. Exact composed binary:219238 bytes, SHA25681718774c14ed498e6aa747d5b6d21a75a86d8662b35c291ba87946c4d736fdb. Previous source and manifest hashes remain unchanged.

## Continuous input result

Both genuine reset-to-gameplay Right01 and Right+A81 histories pass the new helper and its actual8F4C continuation. They reach22043 accepted helper calls,104 completed frames,498 logical NMIs,3708 ordered APU writes and7394 inert mutation guards. The next unsupported boundary is fixed F977, context f97740090125b9a7, actual mapper1E/00/10/06. Existing helper140 calls it after F328 returns. Native rejects inertly, and the240-frame goal remains false. No140 status adapter was added.

Private evidence is port/build/recovery_bank_loader_target_choice_route_Kbbud2/{right,right_a}, including concise summary.json, exact input histories, per-RTI audio states and terminal snapshots. Those remain diagnostics, never production inputs. The current route harness exits successfully when an unsupported boundary is correctly verified; its generic PASS banner is not a claim that the gameplay goal completed. All owned sessions are finished.

## Restore and replay

Set approved VASM and machine68k PYTHONPATH, then run bash port/tools/recovery_bank_loader_target_choice_public.sh. It creates a fresh hash-verified source-only tree, rebuilds the exact composite and runs public/negative tests with cartridge/oracle imports denied.

Private standalone comparison: python port/tests/recovery_bank_loader_target_choice_test.py --rom. Genuine dispatcher comparison: python port/tests/recovery_bank_loader_target_choice_wrapper_test.py port/build/recovery_bank_loader_video5_route_Osyo8h/right. That fixture can be regenerated from reset using the preserved video5 ROM harness into a new empty private snapshot directory. To check generator reproducibility without overwriting source, import generate from recovery_bank_loader_target_choice_generate and compare its returned text with the frozen source.

Continuous replay: create an empty RECOVERY_PRIVATE_SNAPSHOT_DIR, set PROBE_PAD=1 or129, then python port/tests/recovery_bank_loader_target_choice_rom.py default. Expected current final JSON has unsupported_boundary0xf977 and goal_reached false.

Independent review is required for this new helper. No target builder, renderer, audio backend, emulator capture, delivered disk, input cartridge, asset or public repository was changed. Host semantic progress does not establish real-time speed, visible jump behavior or full-gameplay coverage.
