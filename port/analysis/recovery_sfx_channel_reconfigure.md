# Genuine SFX channel reconfiguration and authentic return

This additive static 68020 helper continues the original bank3 PC81A3 path
through channel reconfiguration, the genuine nested calls and returns, and the
saved-mask restoration at82AC. It ends at8060 before the separate phase
accumulation and mixed music/SFX channel-tick loop. No generic instruction
interpreter, injected state, skipped command, forced queue clearing, or new ADF
is involved. This is new recovery-branch source development, not recovery of the
missing later playable/audio source.

## Translation and contract

The helper translates81A3..81B2,81C0..81EF, the called80BB..80CE volume reset,
and82AC..82AF. Nonzero CF is XORed with0F. For each channel X=3..0, a clear
mask bit invokes80BB, writes the original APU volume/control register, and marks
077C+X=FF when either0754+X or0750+X is nonzero. Each LSR CF is an observable
RAM write. The original saved mask, nested JSR return addresses, wrapped stack
writes, and all RTS pops are preserved. The routine then emits4001=08,
4005=08,4015=0F, returns to81AE, clears CF, returns to82AC, restores the caller's
saved mask to CF and consumes the actual805F frame. CF=0 takes the original
short path through both returns without channel/APU changes.

A0 points to2048 bytes of emulated RAM, A1 to the raw eight-byte context
(PC.word,A,X,Y,P,SP,reserved), A2 to a30-byte event journal, and A3 to the
immutable bank3 buffer. Buffers must be valid and disjoint, with bank3 active.
A3 is not read by this helper. Journal format is count.word followed by
address.word,value.byte,kind.byte; kind1 denotes an APU write. Maximum seven
records occupy30 bytes. Every accepted call sets the count, and unused journal
tail bytes stay untouched. Full raw P, including D and reserved bits, is supported.
D0 returns1 accepted or FFFFFFFF rejected; D1-D7/A0-A6 and native SP are
preserved, and CCR is scratch.

Preflight requires PC81A3, wrapped stack offsets+1/+2 equal AB/82 and+4/+5
equal5F/80. Offset+3 is an arbitrary saved mask. Wrong PCs or frames reject
before RAM/context/journal mutation or external effects. All256 emulated stack
positions, including wraparound, are supported. The nested calls never overwrite
the validated outer frames.

## Continuous original-cartridge comparison

Single-reset Right01 and Left02 runs reach806002FF0425F6A7 after1,209 helpers,
41 NMIs and38 completed audio returns. The incomplete NMI remains live. CF=02,
C0=05,D5=01,C1:C2=0001,D0/D1=AF60, and queue03038888888888888888 are preserved.
The genuine channel2 volume reset emits4004=30, followed by4001=08,4005=08,
and4015=0F. The cursor remains88 for Right and28 for Left. Mapper state remains
(30,31,31,3,()). The remaining original C0F8 frame is live at stack1F7/1F8.
Neutral00 remains1,219 helpers/41 NMIs/39 completed returns atA06CFFFFFFA4BDA7.
Confirmation16 remains1,196 helpers/40 NMIs/38 returns atC5F8F800FF27BFA7.

The added genuine slice produces14 RAM writes and4 APU writes, without resource reads.
Standalone helper398 bytes, SHA256
2ee6645f917604f4734cb8f4a38a34697851b0162286d678a613881d034f35bf.

Composite28,908 bytes, SHA256
45f5bf0ec7395adfaf1d324db22c377f1d65c33cba358b942e6102aa05b43b7b.
The frozen duration predecessor is28,506 bytes, SHA256
5baf0e1aa0d6730ee3c2f35d1dc3015aebd920dfe45074339223f23f6fb5444a.
Its manifest remains
f03d7c96491d0aca195f6eea7c1ea8d801873026d18cd46745e4f5832a64cdda.
All56 readable file entries in the preexisting analysis manifests verify.

## Verification and reproduction

The default standalone suite passes196,609 accepted cases and326,655 inert rejects.
The same complete default suite passes in an isolated source-only copy containing
only the two new source/test files. All196,608 accepted main cases pass the
independent original-ROM oracle. All four new continuous runs and all four frozen
predecessor continuous runs pass.

The standalone suite exhausts all65,536 raw P/SP combinations, all65,536
mask/saved-mask combinations and all65,536 mask/channel-activity combinations.
Each accepted case uses randomized full RAM, registers and journal tails.
Inert preflight checks exhaust all unsupported PCs and every incorrect byte at
all four frame positions across all256 wrapped SP values. Every comparison
checks full RAM/raw context, ordered RAM/APU effects, journal and untouched tail,
absence of resource reads, immutable bank, register ABI/native stack balance,
stack canaries, buffer guards and read/write whitelist bounds. Deliberately
out-of-range trace probes must fail. Private --rom checks the declarative model
and assembled native helper against the actual original instructions. Production
assembly is separate from both reference implementations.

Set VASM to the installed vasmm68k_mot executable and make the machine68k test
dependency available on PYTHONPATH. From the repository root run:

- `python port/tests/recovery_test_sfx_channel_reconfigure.py`
- `python port/tests/recovery_test_sfx_channel_reconfigure.py --rom`
- `CHARACTER_INPUT=0 python port/tests/recovery_test_resident_sfx_channel_reconfigure.py`
- Repeat the continuous command with CHARACTER_INPUT=16,1,2.
- Frozen regression: run recovery_test_resident_sfx_duration_math.py with the same four inputs.

The default standalone suite needs only its new Python file and new assembly
file under port/tests and port/src. It imports no private oracle modules and
opens no cartridge. --rom explicitly requires the hash-verified cartridge at
input/rescue-rangers-europe.nes and the existing private reference harness.
The continuous original-instruction tests also require that cartridge.

The exact next unsupported instruction is8060 CLC, followed by LDA CA/ADC C8,
phase accumulation, saved-mask setup and mixed music/SFX dispatch. This helper
does not claim that later SFX channel tick or NMI completion. Verification is
host correctness only, not audible Paula output, full-game completion, target
execution or stock-speed proof. This is additive source development on the
recovered baseline; it does not recover the missing later gameplay/audio source
or change the delivered Z/X ADF. The manifest records the frozen dependencies.
