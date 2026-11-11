# Shared native movement and collision helper 151

This additive static 68020 module translates fixed-bank movement, tile collision,
slope adjustment, player contact and bounded object-contact sweeps. It does not
interpret 6502 opcodes at runtime, replay saved effects, or substitute snapshots.
Original cartridge tables are read through the immutable full-PRG input only.
Raw PHP/PLP flag behavior is intentional: the first F0FB slice returns P=B4.
Legacy live helpers which require canonical B-clear contexts need a separately
qualified ABI adapter; this helper must not clear B to satisfy those guards.

Owned instruction ranges (exclusive ends): EA8F–EBFA, ED3A–EEAB, F000–F328,
F5A6–F7FE. Public entry points and real JSR continuations are listed in
`port/tests/recovery_player_collision_test.py`. F217 and F31D are admitted.
EA8F may expose genuine E817/F379/F3F5 calls; the object-contact sweep may expose
F7FE. Those are real original PC/stack boundaries, not synthetic returns. D6A3
scrolling and the player/frame orchestrators are outside this module.

## ABI and safety contract

A0 points to 2,048 bytes of RAM, A1 to the eight-byte PC/A/X/Y/P/SP/tag context,
A2 to a journal with capacity at least 60,002 bytes, A4 to the twelve-byte runtime
record, and A5 to 131,072 immutable PRG bytes. D0 returns 1 on success or -1 on
inert rejection. All other registers and SP are preserved in USER mode. Reserve
4,096 native stack bytes (minimum supported preflight allowance 2,304 bytes).

Buffers, native stack, code and immutable PRG must be valid and disjoint.
RAM/context/runtime/resources must not be changed concurrently during both passes.
Invalid caller host pointers are not made safe by this assembly interface.
Runtime control must be 1E, bank 0–7, mapper serial state zero and magic D501.
The helper preserves raw flags, 8/16-bit arithmetic wrap, original RAM mirrors,
original stack wrap, and ordered writes and resource reads. Decimal mode does
not alter Ricoh binary arithmetic. Two-pass execution first validates against
private copied RAM/context and suppresses published effects. Both instruction
(20,000) and resource-record (15,000) budgets are bounded. Unsupported 2000–7FFF
reads or non-RAM writes reject without publishing partial state.

## Verification

The original-first 240-loop route has passed 1,879 helper slices and 16,553
ordered resource reads. Maximum observed slice: 567 original instructions,
21 resource records. Logical NMI count: 634. Entry visits: F31D 9, F0FB 349,
F217 1,033, F000 218, F696 116, F066 126, F6DC 28. This route is a standalone
semantic qualification, not a claim that every intervening helper is native.

The first F0FB fixture exported by the continuous native chain was independently
compared against original instructions without changing its state. Entry context
F0FB06000124B5A7 and mapper 1E/00/10/05 produced CBD9000000B4B7A7 at CBD9 after
466 original instructions and 15 ordered resource reads. The fixture is private
test material and is never consumed by the production helper.

The final native binary is 55,038 bytes, SHA-256
59e9ebc4ee957e4291c93b394c6d59bcc331e6b95a3b7c5057667e553af0b4ed.
Final-source private qualification passed 26,416 synthetic raw-flag/stack and
pointer/mirror/bank/wrap comparisons, covering 769 original instruction PCs.
The clean source-only restore passed all 65,440 invalid-PC rejections, 256
raw-P/SP cases, pointer/mirror, reduced-budget and runtime rejection checks.
Exact generator reproduction passed. Hashes are recorded in the companion manifest.
The harness checks complete RAM, context, ordered effects, exact two-pass PRG
reads, register/SP preservation, USER mode, bounded writes and code/resource
immutability. Public tests also cover raw flags/SP wrap, indirect pointer holes,
RAM mirrors, PRG addressing, runtime rejection and deliberately reduced compiled
budgets. No target timing, audible output, display, emulator disk or playable-stage
claim is made. PAL stock A1200/68020 remains the intended target, with optional
Fast RAM limited to 8 MiB.

## Reproduction

Set VASM to the pinned `vasmm68k_mot` assembler and provide Python dependencies
from `requirements-dev.txt`. From repository root run:

    bash port/tools/recovery_player_collision_public.sh

The public recipe restores only the native source and three test/harness files
to a temporary tree. Python read/import guards reject cartridge and oracle
access. These guards are regression checks, not an OS sandbox. No ROM, fixture,
generated binary or recorded effect stream is required for public checks.

Private reference tests additionally require the approved cartridge, SHA-256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411:

    python port/tools/recovery_player_collision_generate.py
    python port/tests/recovery_player_collision_test.py --rom

The generator is an offline development tool and is not linked into the target.
Regeneration must reproduce the checked-in assembly byte-for-byte. Do not publish
the cartridge, fixtures or build outputs with the source checkpoint.
