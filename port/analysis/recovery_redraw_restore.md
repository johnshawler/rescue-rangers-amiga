# Restore and validate the dirty-composition helper

Apply only the additive paths in recovery_redraw_source_manifest.json to the
recovery/title-baseline-2026-11-10 baseline (remote checkpoint
 e703e77a9ca3e6ed23dab87f944eebf3b734432c; local eb6b8975).
The helper requires no private assets, C compiler, Amiga firmware or target capture.
Do not overwrite frozen sources or the delivered rescue-rangers-stock-zx.adf.

Set VASM to vasmm68k_mot and PYTHONPATH to a directory containing machine68k 0.5.1:

    export PYTHONDONTWRITEBYTECODE=1
    python port/tests/recovery_redraw_public_test.py

The test creates temporary assembly outputs and never modifies existing captures.
For private retained evidence, create a NEW output directory and fail if it exists:

    mkdir port/build/NEW_redraw_public
    "$VASM" -quiet -m68020 -Fbin -o port/build/NEW_redraw_public/invalidate.bin port/src/recovery_redraw_invalidate.s
    python port/tests/recovery_redraw_public_test.py > port/build/NEW_redraw_public/public-test.log

Generic dependency hashes are recorded in the manifest; verify them before running.
The test independently enforces hashes of its frozen background/sprite oracles.
Read recovery_redraw_contract.md before integration. The module adds no build-time
ROM dependency. Target instrumentation/stock timings, if provided by a live-menu
integration, belong to that integration's separate build and verifier, not this
public suite. No target measurement is implied by successful Musashi execution.

No generated binary, cartridge, firmware, OAM/CHR/trace dump, disk, audio or
screenshot belongs in the source-only deliverable. The additive allowlist includes
only assembly, synthetic tests and generic documentation/provenance. The manifest
itself is included by name and intentionally is not self-hashed.

Tested assembler: vasm 1.9, M68k backend 2.5, executable SHA256
`bbbf4e7edf2b2f7bc184624f23481a241a766e93c7d3d967470bb37faeecf7c3`.
Tested machine68k 0.5.1 CPython 3.12 extension SHA256
`a72eeab9cf05793d7e4e576bb5228da85eb212cf66ac37251c57c12d7702ec16`.
