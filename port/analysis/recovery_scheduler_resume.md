# Recovery first scheduler resumption

This is new native recovery work, not recovered later gameplay or audio source.
The helper executes the bounded original `$FE8D` scheduler continuation after
one startup NMI and stops **before `$C584` executes**. It does not resume arbitrary
tasks, integrate input into the stable title, or change any delivered ADF.

## Original path and retained effects

The hash-checked European cartridge is the same private input used by the prior
nine helpers (SHA256 `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`).
The fixed-bank scheduler resets SP to `$FF`, clears `$90`, finds ready slot zero
(state 4), selects `$91=0`, writes task state 2 and restores SP from `$82=$BB`.
Its JSR to `$C162` writes `$FE/$CF` into original stack `$01BB/$01BA`.

The full original standard-controller algorithm is translated directly:

- Strobe `$4016` with 1 then 0; read eight interleaved bits from `$4016/$4017`.
- Preserve each original ROL store to `$14/$00/$15/$01`, including intermediate
  values derived from old RAM. Expansion bit one is explicitly zero.
- Preserve the two ORA/STA stores, derive new edges using previous held bytes,
  and sanitize opposing directions on both new-edge and held bytes.
- Return through the original stack, restore Y=`$08`, A/X=`$BF`, SP=`$BF`, and
  continue at `$C584`. The consumed original stack bytes remain in RAM.

The existing `rescue_update_controllers` primitive is intentionally not called:
its final RAM behavior is useful precedent, but this proof retains ordered
serial-input effects, intermediate RAM writes, and original status semantics.
In particular final carry is one exactly when player-one unsanitized edge bits
contain Up+Down or Left+Right. The final PLA/TAX sets N=1/Z=0; V/D/I are retained.
No general 6502 runtime interpreter is used in the native code.

## ABI and guarded scope

`port/src/recovery_scheduler_resume.s` exports `recovery_scheduler_resume`:

- A0: writable 2048-byte original-layout RAM.
- A1: writable eight-byte context: big-endian PC word, A/X/Y/P/SP/reserved bytes.
- A2: writable 74-byte journal: big-endian count word followed by eighteen
  `{address word, data byte, kind byte}` records, kind 0=read and 1=write.
- D0.b/D1.b: decoded controller one/two. Bits 7 through 0 are
  A, B, Select, Start, Up, Down, Left, Right. Upper register bits are ignored.
- Buffers must be valid, disjoint and exclusively owned during the synchronous
  call. The inputs are immutable snapshots for this one polling operation.
- D0=1 means completion, D0=-1 means unsupported/inert. D1–D7/A0–A6 are
  preserved; native stack balanced; native CCR scratch.

Before any RAM/context/journal mutation, require PC=`$FE8D`, A=0, X=`$BB`, Y=0,
SP=`$BB`, canonical P in `$A0/$A4/$A8/$AC`, task `$80=4`, saved SP `$82=$BB`, and
saved continuation bytes `$01BC–$01BF = 08 BF 83 C5`. Other task slots and RAM
can be arbitrary because this deterministic scan takes the first slot.
The caller must be continuing the original bank-6 resource context. This fixed
bank slice neither reads banked resources nor publishes mapper, PPU or APU
changes. Bank identity is not represented in the eight-byte context.

Journal records are complete before their count is incremented. Two writes and
sixteen reads describe logical controller polling, not cycle-accurate hardware
transactions. Native input is explicitly decoded standard pads without expansion
devices. No keyboard, platform input adapter, or Z/X mapping is introduced here.

## Verification

Run from the repository root with VASM and Python dependencies configured:

```
python port/tests/recovery_test_scheduler_resume.py
```

The standalone test assembles real 68020 code, executes it on machine68k
M68EC020, and compares against original ROM instructions executed by py65.
The instrumented original bus supplies standard serial pad bits and records
both strobe writes and every read alongside all original RAM writes.
It compares the full ordered event sequence, all 2048 RAM bytes, all eight
context bytes and the exact native journal, with buffer guards, native register
preservation, bounded execution, unexpected-write rejection and balanced stack.

Executed result: **66,560 standalone cases, 256 continuous compositions,
68,337 unsupported-input rejections and 66,560 completed-boundary rejections
passed**.

Coverage includes all 65,536 current/previous input pairs (complementary second
pad), 1,024 randomized independent two-pad/RAM cases, all four accepted I/D
status combinations, and 256 continuous ten-helper no-input compositions.
The continuous oracle performs the real `nmi()` at the existing chosen first
yield boundary, remaps actual cartridge banks, executes F0, the silent tick and
RTI, then runs the scheduler directly. Native buffers pass unchanged between
helpers; no captured state or game-state patches are inserted.

The test retains the prior named `architectural_status_view`: py65's raw virtual
B marker after RTI remains untouched, and only the comparison view clears B and
sets U. The earlier tail separately checks raw P against saved interrupt status
and checks unchanged saved frame bytes before the scheduler legitimately writes
its new JSR return into `$01BA/$01BB`. N/V/D/I/Z/C are not normalized.

Unsupported PC, context, ready state, saved SP and continuation bytes are tested
for inert rejection. Re-entering every completed standalone result is also
rejected without buffer mutation.

## Limits

This is a logical first scheduler resumption, not full boot, gameplay, arbitrary
scheduler support, cycle-accurate NMI/input timing, audible sound, title
integration, a speed claim or physical-Amiga validation. The next untranslated
task instruction is `$C584`. Existing helpers, probes, source inputs and stable
builds remain unchanged. No cartridge extracts or generated private traces are
part of this deliverable.
