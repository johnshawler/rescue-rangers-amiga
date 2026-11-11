# Source-only reproduction

Use the pinned 68020 assembler through VASM and the repository's Python test
dependencies (machine68k). From repository root:

    bash port/tools/recovery_stage_scroll_public.sh

This restores only the native assembly, the scroll test and its two shared
harness modules into a temporary tree. Import/read guards reject py65, private
oracle imports and cartridge input reads. These are regression guards, not an
OS security sandbox. No cartridge, binary, fixture or recorded effect is needed.
Use --quick to skip the exhaustive invalid-PC sweep, retaining other checks.

Private original comparisons additionally require py65 and the approved private
Europe cartridge with SHA-256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411:

    python port/tools/recovery_stage_scroll_generate.py
    python port/tests/recovery_stage_scroll_test.py --rom
    python port/tests/recovery_stage_scroll_test.py --rom --frames 800 --route-only
    python port/tests/recovery_stage_scroll_test.py --rom --pad 2 --route-only

Every private run checks that generator output matches checked-in assembly
exactly. --fixture accepts a private prefix for .ram.bin, .context.bin and
.runtime.bin files and compares a single authentic boundary without mutation.
Fixtures are host test material, never production-module inputs.

Publish only approved source/report/test files. Do not include cartridge,
source disassembly dumps, private fixture state or build outputs. Publication
is outside this task and presently blocked; do not use alternate upload routes.
