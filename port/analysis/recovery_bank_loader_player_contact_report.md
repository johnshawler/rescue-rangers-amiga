# Fixed F92B player-contact scan, helper154

This additive static68020 module owns F92B–F976, with public entries F92B, F95A and F96C. The original internal JSR F949 and return F941 remain within the region. F696 and F6DC remain genuine pushed-stack external calls into existing collision helper151. No instruction interpreter, captured-state execution, bank substitution, sound/video suppression or new status normalization is used. All earlier sources and manifests are preserved.

## Contract and bounds

A0 RAM2048, A1 raw context8, A2 counted journal6, A4 runtime12, A5 immutable full PRG131072. D0=1 success or -1 inert preflight rejection; other native registers and SP preserved in USER mode. Runtime requires control1E, bank0–7, zero serial state and magicD501. Standalone preserves raw flags according to original instructions. The composed entry requires event0, task80=2, RAM91=0 and canonical incoming status, with no output normalization.

The34 static instruction PCs implement the original first/second player-contact checks. At most one semantic resource read occurs per slice, from the original FA18,Y or F9FC,Y fixed-bank address using the full RAM02 index on resumptions. Resource bytes are read live and are not embedded. After a read the region either exits through F6DC or returns through its genuine stack. Following an internal F941 return can lead to F696 but cannot add another resource read in that slice. Journal6 is exactly count2 plus one record4. All stores are RAM-only; there are no mapper, PPU, controller or APU effects in this module.

Two-pass copied-state validation uses an8192-instruction bound per pass and at most2304 bytes of disjoint native stack. An adversarial stack consisting of repeated internal F941 return addresses can cycle. The unchanged production bound rejects it without RAM/context/journal/runtime mutation; its one validation resource read is not a committed effect. An independent original-only16384-instruction trace stays in the region. A separate8-instruction diagnostic bound rejects a terminating state accepted by production. Neither failure is converted into a wait or partial success.

## Qualification

The main public model/native and private original-first suites each pass6144 accepted cases and65538 guards. They vary every raw P/SP/X byte and selected player states across all three public entries, including wrapped0000/FFFF external returns. The main private suite covers33 of34 owned PCs. An additional512 cases with genuine internal-return stack layout exercise F941 over all raw status/SP bytes, bringing combined original/native instruction coverage to all34. These are selected boundary cases, not exhaustive Cartesian RAM coverage.

Every private comparison checks full raw context, RAM, ordered RAM/resource effects, exact journal and untouched tail, validation plus committed resource reads, runtime/code/resource immutability, preserved native registers/SP, USER mode, width-aware access guards and2304-byte stack bounds. All65533 nonentry PCs reject before copied-state execution; five runtime guards are inert. Full composition adds768 model cases and8448 event/task/status/runtime guards, without invoking a status adapter.

Private evidence: port/build/recovery_bank_loader_player_contact_fbNfYw/{public,private}.log and recovery_bank_loader_player_contact_returns_9UkOai/{public,private}.log. The separate edges test proves production/reduced-budget failures. Offline generator reproduction is byte-identical. Native source SHA256a604c5db6f00915c4b0e1f32cb373cfe14917111b6eb1fc3564f0a4648c10c4d. Exact composite222684 bytes, SHA2560ff6d517c3d41786f4f2e144c24863753c0a3d4bff55a532ab8ecca8a8870346.

## Restore and private replay

With approved VASM and machine68k PYTHONPATH, run bash port/tools/recovery_bank_loader_player_contact_public.sh. It creates a fresh recursively hash-verified source-only tree, rebuilds the exact composite and runs public/negative tests while denying cartridge access and oracle/py65 imports.

Private comparisons: python port/tests/recovery_bank_loader_player_contact_test.py --rom; python port/tests/recovery_bank_loader_player_contact_returns.py --rom; python port/tests/recovery_bank_loader_player_contact_edges.py --rom.

For continuous held input, create an empty RECOVERY_PRIVATE_SNAPSHOT_DIR, set PROBE_PAD=1 or129, then run python port/tests/recovery_bank_loader_player_contact_rom.py default. The distinct player_contact_edge_rom.py supplies Right01 for the first five gameplay polls, Right+A81 for the next six, then Right01. Inputs flow only through the original controller path, from reset with no successful-chain state repairs. The generic harness PASS denotes compared bounded behavior, not completion: consult goal_reached and unsupported_boundary.

No target builder, renderer, sound backend, emulator capture, disk, input ROM, asset or public repository changed. Host semantic proof does not establish visible movement/jumping, frame rate or complete gameplay. Independent review is required for this extension.

## Genuine continuous boundary

The Right reset-history advances through F92B to134 completed frames/NMI528. At call24374, existing helper140 succeeds from context8f9a900902a5baa7 and produces raw f97740090234b9a7. The original raw status is also34, while the established published boundary convention expects24. RAM and all ordered effects agree. This is a post-success status ABI mismatch, not an inert unsupported rejection, and the240-frame goal remains false. No140 normalization was added.

The independent player_contact_raw_boundary.py replay takes the preserved before snapshot, executes13 original instructions beginning at PLP8F9A and compares the raw native result before any adapter. Full context/RAM, five ordered RAM effects, zero resource records, journal tail, runtime metadata and native bounds match. The diagnostic remains at port/build/recovery_bank_loader_player_contact_routes_wz7dTK/right/{run.log,diagnostic.json,before.*,after.*,input_history.json}. It can be replayed with python port/tests/recovery_bank_loader_player_contact_raw_boundary.py followed by that directory. This is diagnostic verification only, not authorization or implementation of a new status adapter.

The separate held Right+A reset-history reproduces exactly the same134-frame/NMI528/call24374 raw140 boundary, with preserved evidence under the sibling right_a directory. The release/press diagnostic is a separate replay and is not needed to establish this bounded freeze; no completed result for it is claimed here.
