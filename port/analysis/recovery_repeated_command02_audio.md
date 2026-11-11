# Command02 and 75-call standalone music continuation

New static native68020 `recovery_music_active_command02.s` extends the reviewed
41-call standalone music composition without changing its existing sources.
The original command02 dispatch sets bit10 of the channel flags at0730+X.
It consumes no stream argument and returns to839D. Dispatch, original page-one
stack writes and C1/C2 effects are retained in their original order.

## Contract

A0 points to2048 bytes RAM; A1 to the8-byte big-endian PC,A,X,Y,P,SP,reserved
context; A2 to a10-byte journal; A3 to immutable16384-byte bank3 data.
Buffers, native code and native stack must be disjoint and exclusively owned.
Entry PC83A0, A02, X28..2B, canonical P (B clear,U set), including D=1,
and resource dispatch8487/8488 pointing to84BD are required. Invalid inputs
return D0=-1 without RAM/context/journal mutation. Success returns D0=1;
D1-D7/A0-A6 and native stack balance are preserved. Native CCR is scratch.
Two preflight resource reads precede the two ordered semantic dispatch reads.
Journal records are address-word,value-byte,kind-byte (resource kind0), after
a count word. No APU write is produced by this command itself.

There is no runtime CPU opcode decoder, captured-state initialization, or tone
generator. Music data remains data. The source contains no cartridge bytes or
extracted assets. VASM -m68020 output is738 bytes, SHA256
7dab1d5e44f18a946887448044a33f7eff46cfe6f59ba4fea3b760a1f835a023.

## Verification

- `recovery_test_active_command02_contract.py`:4096 ROM-free synthetic-resource
  cases and66744 inert guards, covering every PC, invalid command/channel/status
  values, both dispatch bytes, all SP values and D=0/D=1.
- `recovery_test_active_command02_rom.py`:4096 independent original-ROM cases.
- `recovery_test_repeated_command02_audio.py`:16 seeds times75 complete calls,
  26592 native helper calls and9328 ordered APU writes, all ending at C0F9.
- `recovery_test_repeated_command02_audio.py --prove-next-boundary`:16 independent
  bootstrap seeds,75 complete calls each, then the genuine command0E dependency
  at PC83A0 in call76.26736 native helper calls and9392 ordered APU writes include
  the verified partial call76. The dependency is reported, never skipped.

The repeated-call test keeps reference execution continuous and native buffers
resident after one initialization per seed. Only the caller's standalone C0F6
entry PC is selected for each invocation; no reference output is injected into
RAM or other context. Every helper boundary compares all2KiB RAM, complete
context, original ordered RAM/resource/APU effects, exact native resource reads,
immutable resources, journal contents, buffer guards, native ABI and access
whitelists. Raw reference status is not patched; its comparison view normalizes
virtual B and architectural U, matching the preceding reviewed proof.

This is a reference-bootstrap standalone audio proof, not authentic native
reset/frame continuity. It does not extend or alter the frozen resident533-call
startup proof. Unsupported CF callbacks, pending work, commands and genuine
boundaries remain rejected or explicit. No audible output, Paula rendering,
speed, stock target or playable-game claim is made.

Run with VASM set to vasmm68k_mot and PYTHONPATH containing machine68k and py65.
The ROM-free contract does not require py65 or a cartridge. Private ROM tests
verify Europe cartridge SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
The source-only manifest lists only the new deliverables; existing dependencies
remain at the reviewed checkout. No target, aggregate, old manifest, README,
Git index/branch, disk image, commit or publication is changed by this work.
