# SFX command-mask recovery milestone

This is new native 68020 recovery development from the preserved early source.
It does not recover the lost later gameplay/audio implementation. The target
remains the stock PAL A1200; expanded configurations are not substituted.
This milestone adds a real SFX state-changing command parser after the separately
preserved tick-entry checkpoint. Host correctness is not evidence of target
speed, target execution, audible audio, playability, or a finished game.

## Scope and contract

The new helper accepts bank 3 PC 82DC and X in 0..3. A0 points to 2048 bytes of
RAM, A1 to the eight-byte context, A2 to a 78-byte journal, and A3 to an immutable
16384-byte bank 3 resource view. Buffers must be valid, disjoint and exclusively
owned. Raw P and all 256 wrapped SPs are supported. D0 returns 1 for success or
FFFFFFFF for inert rejection; D1-D7/A0-A6 are preserved, native SP is balanced,
and CCR is scratch. The context's reserved byte is unchanged.

A preflight requires D0/D1 to address a mask in 8000..BFFE, a mask in 0..31,
and enough bytes through the final event byte without leaving the bank. It
validates the five inline callback destinations at 82FB..8304. Unsupported PC,
channel, pointer, mask, short stream or callback table is rejected before any
RAM/context/journal writes. Preflight can read the mask and callback table, but
those validation reads are not falsely published as original-game effects.
No resource contents are copied into the source as music profiles or streams.

The helper translates 82DC..82FA, the 8023 inline-table dispatcher, the 8358
stream-read routine, the five callbacks at 8667/86A5/8652/869F/8699 (including
instrument-pointer preparation at 867C), and 8305..8309. It preserves the real
82E2, 82E9, 82F0, 82FA and 8307 stack frames, saved shifted masks, destructive
dispatch return-address pops and temporary pointer writes. Callbacks are not
replaced with direct final-state assignments. Every original RAM write and
semantic resource read remains in order, including overwritten stack bytes.
The assembly is fixed native control flow, not an opcode interpreter.

The parser finishes all selected supported callbacks, reads the next event
byte and publishes PC 830B for a zero event or PC 831B for a nonzero event.
It deliberately does not execute either event action. The alternative SFX
envelope at 86B2 remains unsupported. The frozen music-envelope implementation
is never invoked with an unsupported SFX channel.

Accepted calls write the journal count and exactly its used records
(address word, value byte, kind zero for resources); every unused tail byte is
preserved. Maximum semantic resource events are 19. There are no new APU,
mapper, PPU or controller effects in this helper.

## Continuous evidence

The narrow tick-entry checkpoint advances Right/Left from 1,214 to 1,215 helpers
and adds no live-path writes. This second helper advances both to 1,216 helpers,
41 NMIs and 38 completed audio returns. It adds 62 ordered RAM writes and
13 semantic resource events. Three real callbacks change instrument selection,
prepare its resource pointer, and update channel control. The event stream
advances by five bytes. The eleven additional physical resource reads are
preflight validation, not semantic game events or fabricated bus effects.

The final context is 831B3A023A25F3A7. The caller's genuine 8079 frame and the
original C0F8 NMI frame remain live, and the pending mixed music/SFX NMI is
not completed. No queued request is forced complete. Neutral stays at
A06CFFFFFFA4BDA7 after 1,219 helpers, 41 NMIs and 39 completed returns;
confirmation stays at C5F8F800FF27BFA7 after 1,196 helpers, 40 NMIs and 38 returns.

All four extended continuous runs pass, as do all four narrow-checkpoint and
all four frozen phase-dispatch regressions. Original instructions run first and
choose their own boundaries. Only the initial reset state is loaded into the
native machine; no reference RAM/context is injected into the successful chain.
Continuous comparisons normalize the architectural status view by clearing B
and setting U. This does not change real stack bytes. Standalone comparisons
preserve and compare the complete raw status byte, including D/B/U.

The continuous helper-65 trace hashes (full RAM/context/effects/read sequence)
are 39c572dfd2755c26cfd0f2fb67243a1f9666063efb63c8cb253bc2d8b87ed4dd
for Right and a839dfade01af94dbe2d9dfec6676a1b1eefa2f606c7dd25d25012c2ab52fdd2
for Left. Full traces can be reproduced privately; only compact hashes and
results are kept here.

Standalone binary: 1708 bytes, SHA256
dbd4c928c62246b0b9cd95ec0ba961f7551f44d1ab2fbb748849dde48068ed2c.
Composite: 32562 bytes, SHA256
f073ee5e8cefcd71d8f2e02ef8ac90374adef368c4ca9837a691567590387174.
The narrow predecessor has its own manifest and unchanged 884-byte binary.
All 488 inventoried predecessor files remain byte-identical.

## Test coverage and reproduction

The standalone harness checks complete RAM and raw context, exact ordered
RAM/resource effects, validation versus semantic reads, the entire journal and
untouched tail, immutable resources/code, native ABI/stack/canaries, buffer
guards and global read/write whitelists. Deliberate out-of-range trace probes
must fail. Rejections are checked for atomicity across RAM, context and journal.

Coverage includes every raw P/SP pair, all masks and channels, zero/nonzero
events, page crossing, exact bank-end bounds, every SP/channel on unchanged,
changed and wrapping instrument commands, all unsupported PCs and pointers,
all unsupported channels/masks, and every wrong byte value at each of the ten
callback-table positions. Cartridge mode independently executes original
instructions for 65,536 accepted cases across valid bank-data locations. The
final expanded declarative suite has 77,713 accepted cases and 117,794 inert
rejects. Its source-only isolated copy denies cartridge opens and all private
reference imports. Final test completion is recorded in the manifest.

From the repository root, set VASM to an installed vasmm68k_mot executable,
make machine68k available on PYTHONPATH, and set PYTHONDONTWRITEBYTECODE=1:

- `python port/tests/recovery_test_sfx_command_mask.py`
- `python port/tests/recovery_test_sfx_command_mask.py --rom`
- `CHARACTER_INPUT=0 python port/tests/recovery_test_resident_sfx_command_mask.py`
- Repeat the continuous command with CHARACTER_INPUT=16, 1 and 2.
- Repeat all four inputs with recovery_test_resident_sfx_tick_entry.py and
  recovery_test_resident_sfx_phase_dispatch.py.

For detailed private traces, add `PRIVATE_TRACE_DIR=/tmp/sfx-private-traces` to
the extended continuous invocation. This optional output includes before/after
RAM, comparison/raw context, ordered effects, resource reads and journal bytes
for helpers 64 and 65. The harness rejects a trace directory inside this project.
Do not publish the private output. No captured state is input to the native chain.

Only explicit --rom and continuous tests require
input/rescue-rangers-europe.nes, SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
The default standalone source/test pair requires no cartridge or private modules.
For isolation, copy just that pair into matching port/src and port/tests folders
outside this project, then run it under a Python audit hook rejecting opens of
.nes files or input paths and imports beginning recovery_test_, recovery_music_
or verify_recovery_. The isolated wrapper itself runs the copied test as main.

## Remaining boundary and exclusions

The exact live unsupported instruction is bank 3 PC 831B, LDA $0704,X, with
X=2. It starts the nonzero event action. Zero events stop at 830B, before their
channel-duration/state action. SFX envelope 86B2 and completion of the pending
NMI remain future work. No event, callback, instrument data, queue or frame was
skipped to produce the checkpoint. No predecessor, README, aggregate script,
Git/index, publication, ADF, or other project was changed. No extracted resources,
private cartridge bytes, music profiles or captured RAM are public artifacts.
