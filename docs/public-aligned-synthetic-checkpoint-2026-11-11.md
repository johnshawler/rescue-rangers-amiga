# Aligned renderer: public source and synthetic tests

This checkpoint contains an additive renderer, a source-preparation helper and
source-only tests. Its claims are limited to public source behavior and generated
synthetic results. It makes no runtime speed or playability qualification and
provides no playable disk.

## Renderer and source preparation

`recovery_aligned_background_draw.s` adds a horizontal fine-scroll-zero path that
copies visible pattern and palette bytes directly. Fine shifts 1 through 7 retain
the existing adjacent-byte merge loop. The renderer keeps the established
pixel/opacity ABI, 256-byte scratch allowance, register preservation, rejected
input behavior and 128-byte maximum stack allowance.

The renderer test reuses the existing independent synthetic pixel reference
against the new assembly source. Its 1,084 assembled calls cover all 512
horizontal origins in both user and supervisor mode, blank/rejected inputs,
wrapping, synthetic source mutations and sprite composition. There are 80
width-aware traced calls for ABI and access-bound checks. These are synthetic
correctness checks, not performance measurements.

The pure preparation helper uses the existing public background preparer and
replaces exactly one renderer call and one include in its generated device
source. Three preparation tests cover the two substitutions, repeatability,
missing/duplicate substitution rejection and its direct import contract. It does
not depend on unpublished target builders or evidence-processing tools.

## Python and assembler checks

Install the dependencies from `requirements-dev.txt` and provide vasm:

```sh
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
export VASM=/path/to/vasmm68k_mot
python port/tests/public_aligned_background_source_test.py
python port/tests/public_aligned_code_size_test.py
python port/tests/recovery_aligned_background_test.py
```

These commands run in the GitHub workflow after assembler setup. The 13 size
contract tests use invented buffers, sizes and symbols; they need no compiler.
The existing 43 source-contract tests retain fail-closed traversal, including
unreadable-directory errors.

The inventory and manifest describe a complete public source snapshot, not a
minimal dependency subset. Check or restore it into a new directory:

```sh
python port/tools/public_source_checkpoint.py check --exact
python port/tests/public_source_checkpoint_test.py
python port/tools/public_source_checkpoint.py restore ../aligned-synthetic-source
python ../aligned-synthetic-source/port/tools/public_source_checkpoint.py check --exact
```

The destination must not exist and its parent must already exist. Restore copies
only inventoried source and its manifest. It does not copy Git metadata or extra
working outputs. The source consistency checks are not signed attestations or
protection against replacement of the tool and all its inputs.

## Separate compiled synthetic integration

With the pinned recovery GCC 14 m68k toolchain and vasm available:

```sh
export PAULA_CC=/path/to/m68k-linux-gnu-gcc
bash port/tools/public_aligned_background_check.sh
```

This links the aligned renderer with the existing public adapter and planner,
using zero-filled fixture buffers and algorithm-generated noise waves. It runs
18,944 planner inputs / 37,888 compiled calls, adapter writes/mute/rejection
checks, keyboard and scanout contracts, 16 linked synthetic composition frames,
163 layout cases and the 1,084-call renderer suite. Original-code oracle imports
and cartridge reads are prohibited. This GCC 14 integration check is separate
from the Python/assembler GitHub job.

The runner enforces a conservative linked-code upper bound strictly below
393,216 bytes, three times the 128 KiB program-size budget basis. Five excluded
data/buffer spans are derived from synthetic symbols, generated fixture lengths
and public zero-buffer declarations. Each must be in bounds, nonoverlapping and
zero-filled. All remaining linked bytes count, including code, tables, padding
and other data, plus a full 1,024-byte bootblock. The public bootstrap is assembled
and must fit that block.

For the checked synthetic linkage, 870,384 payload bytes minus 583,150 excluded
zero-data bytes plus the 1,024-byte bootblock gives a 288,258-byte upper bound.
That is below the strict 393,216-byte ceiling. This is a conservative synthetic
linked-code bound, not an exact instruction-size total, runtime RAM measurement
or qualification of any other binary. The negative tests reject the exact ceiling,
overlaps, invalid offsets, missing symbols, changed excluded bytes, malformed
declarations and bootstrap overflow.

## Scope boundary

This addition contains no derived private-run timing, trajectory, memory,
state, PCM or capture summaries. It supplies no authentic asset or capture
identities and makes no runtime speed, playable-speed, hardware, full-game,
visible-motion or audio-output qualification. The source and synthetic tests do
not reproduce or attest authentic target builds or captured runs.

Previously published files and historical content remain unchanged except for
the explicit source-checkpoint bookkeeping and new README/workflow entries.
This narrower delta is not a removal or sanitation of historical repository
content. It is new source work, not recovery of missing later gameplay/audio
source.
