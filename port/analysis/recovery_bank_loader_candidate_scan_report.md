# Fixed F977 candidate scan, helper153

This additive static68020 module owns F977–F9F1, with public entries F977, F9D7 and F9E4. It preserves the original candidate-slot scan, flags, ordered RAM stores, genuine external JSR stack pushes and RTS return. F696 and F6DC remain actual external calls into the already qualified collision module151. There is no runtime opcode interpreter, captured-state execution, bank substitution or new status normalization.

## Native contract

A0 RAM2048, A1 raw context8, A2 counted journal18, A4 immutable runtime12, A5 immutable full PRG131072. Success D0=1, rejected preflight D0=-1 with caller-visible state unchanged. Other native registers/SP are preserved in USER mode. Runtime requires control1E, bank0–7, zero serial state and magicD501. The standalone module preserves every raw status bit according to original instructions. The composition requires event0, active task80=2, RAM91=0 and canonical incoming status; no output mask is applied.

There are59 static instruction PCs. Each slice can perform at most four fixed-bank semantic resource reads: two candidate-type indexed reads followed by two masked-size indexed reads, after which it exits via the original F696 call. Reads are from the immutable current PRG, including the original F9D0/F9D5 bases, without embedding table bytes. Index arithmetic and addresses are preserved even when an index selects outside an apparent table. No PPU, mapper, controller or APU event belongs to this routine. The two-pass copied-state preflight journals only committed reads; validation reads are separately checked. Journal18 is exactly count2 plus four records4. Stores are RAM-only.

Each pass has an8192-static-instruction bound and uses at most2304 bytes of disjoint native stack. A candidate scan with X16 can skip the terminal Y16 comparison forever. The unchanged production bound rejects this case atomically; a private original-only16384-instruction trace verifies that the original remains inside the scan. This unsupported cyclic state is not represented as success or a scheduler wait. A separate8-instruction diagnostic bound rejects a terminating case accepted by production, proving causal preflight failure. The type3A path genuinely falls through the type60 setup because the preceding LDA08 makes BEQ false; the implementation does not simplify this behavior.

## Qualification

The main public/model suite and private original-first suite each passed3068 accepted cases and65542 inert guards. They cover all256 raw-P/SP/X values across the selected entry/activity combinations; four deliberately cyclic cases reject. They are not a Cartesian proof of all RAM states. The private suite covers51 of59 instruction PCs. An additional1024 candidate-type cases cover every selected type1/60/3A/other with all256 raw-P/SP and live table indices, also covering51 PCs independently. No assertion that either individual suite covers all59 is made.

Every accepted private case compares full RAM, raw context, ordered RAM/resource effects, exact journal including untouched tail, and validation/committed immutable reads. Exact register/SP preservation, USER mode, code/resource/runtime immutability, width-aware memory bounds and the2304-byte stack limit pass. All65533 nonentry PCs reject before copied-state execution. Runtime guards and actual cyclic-budget rejection preserve state. Full-composition public tests add768 cases and8448 task/event/runtime/status guards, with no raw-status adapter activation.

Evidence: port/build/recovery_bank_loader_candidate_scan_piPjSn/{public,private}.log, recovery_bank_loader_candidate_scan_branches_uRMTZc/{public,private}.log. Initial development caught a stale generator RTS-return list during assembly and a public-model assumption that every scan terminates; both were corrected before qualification. No frozen source changed.

Native source SHA2560d4b709255ee0a7ee6f79997c5d1b410bca4e5057433c2b5869f806d36323da0. Exact composite221230 bytes, SHA256b58b121286cb066ddd72c694214ecdca271d4e96f37ef4207f71dae120c72747. Offline generator reproduction is byte-identical.

## Restore and replay

Set approved VASM and machine68k PYTHONPATH, then run bash port/tools/recovery_bank_loader_candidate_scan_public.sh. This restores only recursively hash-verified source into a new directory, rebuilds the exact native composition and runs public/negative suites with cartridge access and oracle/py65 imports denied.

Private comparisons: python port/tests/recovery_bank_loader_candidate_scan_test.py --rom; python port/tests/recovery_bank_loader_candidate_scan_branches.py --rom; python port/tests/recovery_bank_loader_candidate_scan_edges.py --rom.

For continuous held-input histories, create an empty RECOVERY_PRIVATE_SNAPSHOT_DIR, set PROBE_PAD=1 or129, then python port/tests/recovery_bank_loader_candidate_scan_rom.py default. The distinct candidate_scan_edge_rom.py uses actual Right-only input for the first five gameplay visits, Right+A for visits6–11, then releases A. Inputs are delivered only through the original controller path. Neither diagnostic fabricates game state. The generic harness PASS means comparisons and unsupported-boundary rejection passed; inspect goal_reached and unsupported_boundary separately.

No target builder, renderer, sound backend, emulator capture, delivered disk, assets or published repository changed. Host semantic comparisons do not establish speed, visible jump behavior or full gameplay. Independent review remains required.

## Continuous verified boundary

Genuine Right and the distinct A release/press history both reach22045 accepted helpers,104 completed frames,498 logical NMIs,3708 ordered APU writes and7394 inert mutation guards. Actual F977 returns through the original bank6 continuation; the next unsupported fixed boundary is F92B, context f92b40091025bba7, mapper1E/00/10/06. It rejects inertly and goal_reached remains false for the240-frame goal. No140 status adapter was introduced.

The edge history records real helper138 samples Right01 on zero-based frames0–4, Right+A81 on5–10, then Right01 from11 onward. Evidence is port/build/recovery_bank_loader_candidate_scan_edge_EudfPy/{summary.json,input_history.json}; Right history is port/build/recovery_bank_loader_candidate_scan_route_EliDe8/right. This proves input delivery and compared continuation, not that a visible jump occurred. All saved snapshots and input histories are private diagnostics, never production inputs.

The separate held Right+A replay also reaches exactly the same reported counts and inert F92B boundary, recorded under recovery_bank_loader_candidate_scan_route_EliDe8/right_a.
