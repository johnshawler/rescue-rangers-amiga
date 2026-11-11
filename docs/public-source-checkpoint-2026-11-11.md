# Public source and synthetic-test checkpoint

This additive checkpoint is based on the published recovery source, followed by
new code. It is not recovered later gameplay/audio source and is not a playable
disk release. No cartridge, firmware, captured game state, PCM, screenshot or
compiled game disk is included in this addition.

## Reproducible public scope

The two planner wrappers add the bounded `$8E` and `$06` noise mappings while
retaining existing planner behavior and rejecting unsupported inputs. The
integration generator, adapter/planner tests and linked-layout tests use compiled
68020 code and invented data. Temporary PRG/CHR placeholders are generated as
zero-filled buffers; finite noise buffers are generated algorithmically. The
embedded compiled-code and synthetic-wave digests do not identify private assets.

With the pinned recovery GCC 14 m68k toolchain, vasm and Python development
dependencies installed, run these separately from the assembler-only CI:

```sh
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
export VASM=/path/to/vasmm68k_mot
export PAULA_CC=/path/to/m68k-linux-gnu-gcc
python -m pip install -r requirements-dev.txt
bash port/tools/recovery_live_gameplay_public.sh
bash port/tools/recovery_live_gameplay_noise06_public.sh
```

The compiler must produce the expected original planner bytes; another GCC
version is not an equivalent validation environment. The `$8E` suite covers
11,776 planner inputs and 23,552 compiled calls. The `$06` suite covers 18,944
inputs and 37,888 calls. Both also exercise adapter writes/mute behavior, inert
rejection, input/register/stack/write bounds, 16 linked synthetic composition
frames and 163 journal-layout cases. Cartridge reads and original-code oracle
imports are prohibited in these runners. These are compiled synthetic runtime,
adapter and layout checks, not authentic game execution or target timing.

## Source snapshot and safe fresh restore

`port/analysis/public_source_inventory.txt` inventories the complete public
source snapshot, including its inherited historical documentation. It is not a
minimal dependency package. `port/analysis/public_source_checkpoint.json`
records sizes, executable flags and SHA-256 values for those public source
files. It does not record authentic asset/capture identities. The manifest
itself is the one excluded entry to avoid a self-hash cycle. The inventory's
fixed digest is checked independently by the tool. Existing historical public
reports and metadata remain unchanged; this is not a history-sanitization claim.

Only Python's standard library is required for the new contract checks:

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tools/public_source_checkpoint.py check --exact
python port/tests/public_source_checkpoint_test.py
python port/tools/public_source_checkpoint.py restore ../public-source-restored
python ../public-source-restored/port/tools/public_source_checkpoint.py check --exact
```

The destination must not exist, and its parent must already exist. Restore copies
only inventoried source files and the manifest, verifies the resulting closure,
and does not copy Git metadata or extra working outputs. Normal `check` tolerates
unlisted working outputs; `--exact` rejects extra files except a top-level `.git`
directory. It rejects missing, changed or empty files, invalid paths, duplicate or
incomplete manifest entries, changed inventory, unexpected file types and symlink
files/directories. Synthetic tests cover those errors and failed-restore cleanup.

The manifest and tool are reviewable consistency checks, not signed attestations
or protection against an attacker who can replace the tool and all its inputs.
Do not restore while another process is modifying the source or destination.
An intentional source change requires a reviewed snapshot update; do not regenerate
the manifest merely to suppress a validation failure.

The existing Python/assembler GitHub workflow runs this source contract and fresh
restore in addition to its established synthetic checks. It does **not** run the
two GCC 14 compiled suites above. A passing CI job is not their result.

## Separate private evidence and remaining limits

Separately verified private evidence records bounded 240-frame functional runs
for Right/X and neutral input. The earlier `$8E`-only neutral run stopped after
200 frames on unsupported audible `$06`, correctly muted, and remains a failed
240-frame attempt. The later `$06` wrapper does not reclassify that failure.
All 635 updates were late on each successful finite run; none establishes
playable speed. These facts are separate private observations, not assertions
proved by the public synthetic suites.

This addition cannot reproduce authentic cartridge-derived builds, original-first
target comparisons, actual input trajectories, final screenshots/Copper scanout,
private PCM intervals or private runtime-evidence identity checks. Finite-loop
noise is approximate; full-stream sound, NES phase/envelope/mixing fidelity,
visible motion, full-game behavior and physical-hardware performance are not
established by this source checkpoint. Original inputs, frozen private evidence
and previously delivered disks remain unchanged. No new playable disk is released.
