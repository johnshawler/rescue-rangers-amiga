# Fixed-bank main-frame dispatch through C940

Additive ID135 extends the frozen stage-loaded chain into the first authentic fixed-bank player-state dispatch. It statically translates C21E–C234, C2DC–C2F6, C77B–C925 and F379–F391. The table-indirect JMP at C923 reads live fixed-bank resources C926/C933 and returns the actual destination without reading or decoding instruction bytes. The initial genuine destination is C940. External calls remain explicit original pushed-stack exits. No player-action, collision, later game-loop or target-playability claim is made.

Entry symbol recovery_bank_loader_frame_dispatch composes the unchanged prior music dispatcher. ID135 journal60002 contains only semantic resources; RAM stores are direct. Common ABI remains RAM2048/context8/runtime12/fullPRG131072 and4096 disjoint native stack. Copied-state preflight enforces200000-label budget,15000 journal records, mapper control1E/bank0–7/serial0/magicD501. Original wrapped stack and raw flags preserved. Unsupported data reads reject inertly. No busyF6 branch is widened. F379 queues original sound rather than suppressing it.

## Proof and limitations

Continuous original-first default history from reset reaches C940 with14626 helper calls,394 logical NMIs and2849 APU writes. Final contextc940c90000a4bba7, mapper1E/00/10/05. Composite99220 bytes, SHA2564f82fd3deb3e357a08cc07583785c1327540c487b36b3ffb0e4e049fb66c88b7. Full RAM/context/runtime, ordered effects and resource reads match each boundary. Actual machine code runs USER mode with width-aware read/write bounds and4096 stack guards. This is logical-NMI host semantics, not asynchronous interrupt or target timing proof.

Standalone genuine-stage entry tests pass256 rawP/SP variants. Private tests across35 entry points pass560 raw-state variants, without excluding nonterminating cases. Public random-resource tests pass256 indirect dispatch models and1280 inert metadata/entry guards. These do not exhaust every gameplay branch or invalidPC. Public tests prove computed target data is never instruction-fetched. Developmental reference selector initially omitted an actual external RTS destination and was corrected; runtime source was unchanged by that correction. No assertion-failing developmental run is counted as qualifying proof.

The continuous private replay can optionally export diagnostic stage snapshots and completed-RTI APU states via RECOVERY_PRIVATE_SNAPSHOT_DIR. These exports are never production inputs or public deliverables. Default394 RTIs show noise00 at initial reset, then07/0D/81, with08 newly appearing atNMI379; target audio support is separately owned and not qualified here.

## Replay

Restore this manifest and recursive dependencies with SHA verification. Set VASM and machine68k PYTHONPATH, PYTHONDONTWRITEBYTECODE=1. Public: python port/tests/recovery_bank_loader_frame_public.py. Private continuous: python port/tests/recovery_bank_loader_frame_rom.py default, optionally setting RECOVERY_PRIVATE_SNAPSHOT_DIR to a newly created empty directory. For standalone tests first run frozen recovery_bank_loader_music_rom.py default with that environment variable to create genuine C77B snapshots; then run recovery_bank_loader_frame_contract.py SNAPSHOT_DIRECTORY and recovery_bank_loader_frame_variants.py SNAPSHOT_DIRECTORY. Private scripts require authorized original input ROM SHA051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411. Generators require that private source; only translated static logic is included publicly.

Scope ends atC940. IDs140 and150 and all target artifacts are excluded. Existing target builders, delivered disks and frozen source files remain untouched.
