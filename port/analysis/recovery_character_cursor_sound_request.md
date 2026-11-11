# Native cursor resource and sound request

The additive static 68020 helper translates A07B through its real JSR F379,
F379 through its real wrapped-stack RTS, and A086 through its real JSR FF04.
The resource is read from caller-supplied immutable bank 2, never synthesized.
F379 is an enqueue request, not SFX execution. Its DC,X accesses are zero-page
indexed and wrap at FF; arbitrary DA values and aliases of 00/01/DA are retained.
An occupied slot leaves DA unchanged. An empty 88 slot accepts the actual A,
advances the producer modulo eight, restores X from 00 and returns through the
actual stack bytes. Final NZ comes from LDX, while comparison carry survives.

Continuous resident runs begin at reset with one RAM/context initialization.
All four previous inputs pass with original controller edges, scheduler, NMIs,
video, music and audio returns retained:

- Neutral: 1,219 calls, 41 NMIs, 39 later audio completions; A06CFFFFFFA4BDA7.
- Start after release: 1,196 calls, 40 NMIs, 38 audio completions;
  C5F8F800FF27BFA7, unchanged default-character confirmation.
- Right 01 after Start release: 1,201 calls, 41 NMIs, 38 audio completions;
  genuine cursor 88, then C0BF00100026F8A7.
- Left 02 after Start release: identical counts and final context, cursor 28.

Both direction runs retain DA/DB/ring bytes 03028888278888888888. The queue
consumer is genuinely pending at DB=2, with sound27 in DE. The last NMI has
entered C0BF but has NOT completed audio. No queue byte was cleared or bypassed.
The native composite is 26,800 bytes, SHA256
 e742111ae4dc5ec05cc3c821038ff450aefa80b8453ef5817b159e809960fc21.

## Exact remaining dependency

The previously supplied empty-queue C0BF helper is not applicable. Original
C0BF switches to bank3, reads DC,X, and on nonempty queue C0E4 pushes the request,
C0E5–C0ED clears the consumed slot and advances DB, C0EF pulls the request, then
C0F0 calls bank3 8003. The new composition stops before C0BF instead of dispatching
an empty-queue contract on a nonempty queue. Nonempty dequeue and SFX27 execution
are untranslated in this slice. Thus a genuine alternate cursor selection is
proved, but its later release/Start confirmation and fifteen-pair swap are NOT
claimed continuously reachable. They must wait for original audio execution.
No unsupported operation was attempted or denied; this is an implementation
boundary. Independently added music command0F remains untouched and is not used
as an excuse to skip the sound dependency.

## Contract and verification

A0 RAM2048, A1 raw context8 (PC.word,A,X,Y,P,SP,reserved), A2 journal6,
A3 immutable bank2[16384]. D0=1 accepted or FFFFFFFF inert wrong-PC rejection.
D1–D7/A0–A6 preserved; native stack balanced; CCR scratch. Journal is count.word
followed, only for A07B, by address.word/value.byte/zero.byte. Other entries clear
only the count; tails remain unchanged. RAM stores are observed in order by the
host harness. Valid disjoint buffers and live bank2 mapping are preconditions.
No generic opcode interpreter or embedded cartridge payload is introduced.

6,144 synthetic cases and 6,144 original-ROM cases cover all raw status bytes,
all Y resource indexes, zero-page ring-index wrap, aliases, empty/full slots,
stack wrap, arbitrary A/X/Y/return bytes and reserved context. All 65,533 invalid
PCs reject with RAM, context, resources and journal unchanged. Tests compare
full RAM/raw context, ordered RAM/resource effects, exact journal and tails,
resource read bounds, immutable resources, ABI, buffer and native-stack canaries,
and whitelist all native memory accesses. The resident comparison verifies every
accepted boundary and resource, mapper, ordered effect and journal continuously.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to the inspection .deps.
Run recovery_test_character_cursor_sound_request.py with and without --rom, then
recovery_test_resident_character_cursor_sound.py with CHARACTER_INPUT=0,16,1,2.
The prior character manifest and every file it covers remain unchanged; its
frozen queue predecessor is also verified. No existing source/test/report/manifest,
Git state, README, aggregate runner, ADF, checkpoint or deployment was modified.
Host correctness only: no target gameplay, audible output or PAL A1200 speed claim.
