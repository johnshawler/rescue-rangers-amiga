# Pending SFX27 dequeue and table dispatch

This additive host-only slice reuses the unchanged recovery_nmi_audio_entry
helper for the genuine nonempty C0BF queue, then adds a static 68020 translation
of bank3 8003 through 810B. It stops at 810D before the sound-header read.
There is no runtime 6502 interpreter, injected cursor, skipped sound, or forced
queue clear: the existing helper translates the original C0E7 consumed-slot
write, C0ED consumer advance, wrapped PHA/PLA and C0F0 JSR in original order.

The new helper accepts PC8003/A27 when the immutable bank3 command count exceeds
27 hex. This bounded direct-index path has no subtract/wrap loop. It increments
C0 as the original busy flag, pushes 80E5 through the actual wrapped 6502 stack,
reads the command count and table low/high bytes, and writes C1/C2. A nonzero
pointer ends at 810D with Y=0; a zero pointer ends at the original 8151 RTS
boundary without changing Y. Neither boundary executes its next instruction.
All raw P bytes, SP bytes, C0 overflow, and arbitrary pointer bytes are supported.
Out-of-bank pointers can be returned, but are never dereferenced by this helper.
Future header code must validate its own resource range before accessing them.

## Continuous single-reset results

The original-ROM and assembled-native runs retain one RAM/context initialization,
original external controller edges, scheduler, NMIs, video and prior music:

- Right 01: cursor88; 1,203 calls, 41 logical NMIs, 38 completed later audio
  returns; context 810DFF4E0026F4A7. Mapper (30,31,31,3,()).
- Left 02: cursor28; otherwise the same counts and final context/mapper.
- Neutral: unchanged 1,219 calls, 41 NMIs, 39 audio completions;
  A06CFFFFFFA4BDA7, bank2.
- Start after release/default confirmation: unchanged 1,196 calls, 40 NMIs,
  38 audio completions; C5F8F800FF27BFA7, bank2.

Both direction runs now retain DA/DB/ring bytes 03038888888888888888.
Consumer DB advanced from 2 to 3 by the original dequeue; sound27 is not pending
in the ring because execution has genuinely entered its handler. The audio NMI
is still incomplete. Busy C0 remains incremented, the nested 80E5 return frame
is live, and the original C0F2 caller frame remains beneath it.
The resource table supplies AF5B from 8A52 then 8A51. The exact next unsupported
instruction is 810D LDA (C1),Y, which would read bank3 AF5B (ROM byte0F).
The header, priority comparison, SFX state initialization and subsequent sound
channel execution are NOT translated in this slice. Alternate-character
confirmation and its fifteen-pair swap are not claimed continuously reachable.

Composite: 26,980 bytes, SHA256
4530c81299c7a6c2bc4799fdcada9a50b2ddf7b11568f2b571daec1d95871706.

## Contract and verification

New helper: A0 RAM2048, A1 raw context8 (PC.word,A,X,Y,P,SP,reserved),
A2 journal14, A3 immutable bank3[16384]. Valid disjoint buffers and live bank3
mapping are caller preconditions. D0=1 accepted / FFFFFFFF inert reject;
D1-D7/A0-A6 preserved, native stack balanced, CCR scratch.
Journal is count.word plus address.word/value.byte/zero.byte records. Resource
count is read once in preflight and again at its original semantic position;
only the three original semantic reads are journaled. Wrong PC/A rejects before
resource access; a short count rejects after that one read. Rejections preserve
RAM/context/journal/resources and ordered effects. Journal tails are preserved.
The reused C0BF helper keeps its F5=0, DB<8, nonempty-slot preconditions and
22-byte ordered mapper journal. No mapper busy path is bypassed.

New tests independently describe the dispatch and dequeue transitions, then
compare those contracts against assembled native code and the original ROM:
8,192 synthetic cases, 8,192 ROM cases, and 131,869 inert rejection cases.
Coverage includes every raw status/stack value, count boundary, every wrong PC,
every wrong command, all valid consumer indices, all nonempty command bytes,
busy rejection, invalid consumer indices, empty rejection, C0 overflow,
zero/nonzero and out-of-bank pointer values, reserved context, immutable resource
bounds, full RAM/context, ordered RAM and hardware effects, exact journals/tails,
register ABI, memory whitelist, buffer guards and native stack canaries.

All four new continuous runs compare every accepted boundary, raw context view,
full RAM, ordered effects, hardware journals, mapper snapshots and resource reads.
All four frozen predecessor continuous runs were rerun and preserve their earlier
26,800-byte composite SHA e742111ae4dc5ec05cc3c821038ff450aefa80b8453ef5817b159e809960fc21.
The prior manifest SHA d7c931e5c8de4dae091af5d3f14fa5088020dbd3ade917985fcbde2ec26401b6
and all 38 readable file entries across existing analysis manifests verify.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to the inspection .deps.
Run recovery_test_pending_sfx27_dispatch.py with and without --rom;
run recovery_test_resident_pending_sfx27.py with CHARACTER_INPUT=0,16,1,2.
Frozen regression commands are recovery_test_character_cursor_sound_request.py
with and without --rom, recovery_test_nmi_audio_entry.py, and the four
recovery_test_resident_character_cursor_sound.py inputs.

Only new uniquely named source/test/report/manifest files were added. Existing
source, tests, reports, manifests, README, aggregate runners, Git/index, ADFs,
checkpoints and deployments were not changed. No operation was denied or pending.
This is host correctness, not audible Paula, playable gameplay or stock-speed
proof. The later playable/audio source remains missing.
