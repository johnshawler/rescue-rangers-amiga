# Resident startup title resources through C5CB

New static 68020 helpers extend the verified C5BB boundary through bank
selection, the real bank-2 resource loader, palette/OAM setup and rendering
enable. Existing sources, tests, targets, aggregate scripts, README and disks
are unchanged. The prior bank-only checkpoint is retained separately.

## Contracts

All helpers use A0 for 2048-byte RAM and A1 for the original eight-byte CPU
context. A2 points to their journal. Loader/setup additionally use A3 for an
immutable 16384-byte bank-2 view. Buffers must be valid, disjoint and exclusively
owned for the invocation. D0=1 succeeds; D0=-1 rejects without mutation.
D1-D7/A0-A6 are preserved and native stack is balanced; native CCR is scratch.
No resource, cartridge instruction bytes, captured states or assets are embedded
in the sources. These are static native semantic translations, not an opcode
interpreter. Resource preflight parses data only.

- `recovery_startup_bank_select.s`: C5BB -> C5C0 through FF53. Journal22.
  Accepts only F6=0; nonzero deferred work rejects before any mutation. Requires
  empty MMC1 latch and PRG mode 3. Preserves live F5 as mapper-event metadata,
  all original stack/RAM writes, incoming X/Y/SP and raw status bits. Exit
  status is `(P & 0x7c) | 2`. Does not change F6 or service deferred audio.
- `recovery_startup_resource_load.s`: C5C0 -> C5C5 through loader8000,
  including nested 8037 pointer-page crossings. Journal32770. Requires bank2
  mapping. Before mutation, validates the entire data stream stays inside the
  supplied bank and consumes at most 4094 bytes including its zero terminator.
  The initial two pointer reads plus at most 4094 stream reads bound semantic
  reads to 4096 and combined resource/PPU events below 8192. Unterminated,
  truncated, out-of-bank and over-budget streams reject inertly. Preflight
  reads are explicitly checked separately from semantic reads. Resource data
  must remain immutable between validation and execution. Every original
  semantic read, RAM write, status-read event and PPU write stays ordered.
  Count semantics are exactly signed DEC/BPL: counts 00..80 write count+1
  bytes, counts 81..FF write one byte. Original wrapped page-one JSR effects,
  pointer increments and count decrements remain visible. Exit A=0, X=2,
  Y=stream offset modulo 256, status `(P & 0x7d) | 2`, SP unchanged.
- `recovery_startup_title_setup.s`: C5C5 -> C5CB through setup8820 and C158.
  Journal566. Requires bank2 mapping. Reads 16 palette bytes and 124 sprite
  bytes directly from the live bank, performs ordered palette/OAM writes,
  publishes 1B=9F then 1A=9F, decrements rendering-disable depth and writes
  FE/PPU mask 1E. Exit A=1E, X=7C, Y=FC, P masked by 7D, SP unchanged.

Journal records are a big-endian count word followed by address.word,
value.byte and kind.byte. Bank helper kind is live F5. Loader/setup kind0
means resource read, kind1 PPU write, and loader kind2 PPU status read whose
unused result is normalized to zero. Unused journal tail is not modified.
These calls do not model asynchronous interrupt interleaving. The caller
must supply the documented mapper state; the resident test verifies it from
ordered mapper history, without rewriting latch state.

## Focused validation

Use approved VASM and inspection PYTHONPATH, then run:

- `python port/tests/recovery_test_startup_bank_select.py` and `--rom`
- `python port/tests/recovery_test_startup_resource_load.py` and `--rom`
- `python port/tests/recovery_test_startup_title_setup.py` and `--rom`
- `python port/tests/recovery_test_resident_startup_resources.py`

Bank and setup each pass 256 public and 256 actual-ROM randomized full-RAM
cases covering all raw incoming status bytes and wrapped SP values. Bank has
65,790 inert guards; setup has 65,535. Resource loader passes 256 public count
cases plus an exact 4094-byte maximum stream, and 65,543 inert guards. Its
actual-original suite passes 256 unmodified-ROM cases plus 256 cases executing
the same original instructions against synthetic legal resource data, covering
every signed count and page crossing without changing original loader code.
Tests compare full RAM/context, ordered effects, complete used journal and
untouched tail, preserved registers/native SP, resource immutability, buffer
canaries and global access whitelists. Private tests vary PPU status results.
The reference uses the independently truth-table-tested Ricoh CPU; incoming
raw status is never normalized or patched in standalone comparisons.

## Continuous resident composition

`recovery_test_resident_startup_resources.py` is a new composition, leaving
prior compositions intact. It loads native RAM/context exactly once at reset.
Native and reference proceed independently across every intermediate boundary;
no reference state is injected. Two immutable bank views are loaded once.
F6 naturally equals zero at C5BB in both machines, and the mapper naturally
arrives there as control1E, CHR0=00, CHR1=10, PRG06 with an empty serial latch.

Result: 537 native calls, 18 actual reference NMIs, 16 later active audio
calls; 10075 RAM writes, 3975 PPU events, 205 mapper writes, 324 controller
events, 1280 semantic resource reads and 114 APU writes. Final context is
C5CB/1E/7C/FC/24/BF/A7. Mapper is 1E/00/10/02 with empty latch. Both CHR
requests remain 9F; F0=0 and FE=1E. The new loader contributes 356 semantic
reads and 354 PPU events. Setup contributes 140 reads and one PPU write.

Native code/resource requirements for this host composition: 22556-byte
composite, 2048-byte RAM, 8-byte context, at most 32770-byte journal, two
16384-byte immutable bank views, and native stack. Journal capacity is a
conservative public bound, not an optimized Amiga allocation. This work does
not claim target Amiga execution, a new ADF, fixture-free displayed title,
playability, real-time speed or audible Paula output.

## Next honest dependency

C5CB now has the original outstanding yield call to FF04, eventually resuming
C5CE and entering fade-in C26E. NMI processing must consume the genuine live
CHR requests 1A/1B=9F, preserve mapper/stack/audio state and process any genuine
nonempty video queues. The existing narrow idle-NMI helper cannot simply be
called while ignoring those requests. Nothing here drains or zeros queues,
clears deferred audio or fabricates task readiness. Later active-audio command
02/CF callback branches remain unsupported. Deferred FF53 work and arbitrary
interrupt interleaving remain separate explicit dependencies.
