# Genuine SFX duration multiplication and tick tail

An additive static 68020 helper advances the genuine Right/Left single-reset path
from bank3 PC8006 through the full duration multiplication, authentic RTS8298,
and stream-mask setup to PC81A3. It does not interpret 6502 opcodes. The pending
SFX request and original sound data remain intact. No command is skipped, queue
cleared, or state injected.

## Translation and ABI

The 8006 entry translates LDA0/STA C2, LDY8, eight iterations of ASL C2/ROL C1,
conditional binary ADC C4 and ADC0, DEY/BNE, and RTS8022. Ordered RAM writes are
preserved even when their values repeat. The product is C1:C2, not merely an
8-bit low product. A retains the original instruction sequence's accumulator,
Y ends zero, and raw P retains the exact last carry and overflow effects with
NZ from final DEY. Ricoh arithmetic remains binary even when raw D is set.

The 8298 entry translates LDY C1/INY/STY D5, INC C0, authentic JSR8358 and its
stream fetch/pointer advance/RTS, PHA/EOR CF, and both branches. A changed mask
is stored and JSR81A3 pushes the authentic82AB frame; unchanged masks execute
PLA/STA CF and RTS82AF to8060. It never stops just before a covered trivial RTS.
The changed-mask call is the genuine next boundary. Its 81A3 LDA CF begins
channel reconfiguration via81C0; that routine remains untranslated. The equal
mask path stops8060 before the separate phase-accumulation/channel-tick work.

A0 RAM2048, A1 rawcontext8 (PC.word,A,X,Y,P,SP,reserved), A2 journal6,
A3 immutable bank3[16384]. Caller provides valid disjoint buffers and live bank3.
D0=1 accepted or FFFFFFFF rejected. D1-D7/A0-A6 and native SP are preserved;
CCR is scratch. All raw P and wrapped emulated SP values are supported.
The 8006 entry requires the actual8297 return frame. The 8298 entry requires
actual805F frame and pointer8000..BFFF before any mutation. This conservatively
checks that frame even on the changed-mask branch, where it remains live.
Wrong PCs, frames or tail pointers reject without RAM/context/journal mutation
or resource reads. Multiplication needs no resource data or pointer validation.

Journal is count.word followed by address.word,value.byte,zero.byte. Unused
tail bytes stay untouched. Resource values are data, never host instructions.
No APU/PPU/controller/mapper write is added by this helper.

## Continuous original-ROM comparison

Right01 and Left02:1,208 helpers,41 NMIs,38 completed audio returns; rawcontext
81A302030024F1A7, mapper(30,31,31,3,()). The incomplete audio NMI remains live.
Duration1 times scale1 produces C1=00,C2=01. D5=01,C0=05. AF5F=02 is fetched
and D0/D1 advances AF60. CF=02; stack1F2..1F4 is AB,82,02: genuine call frame
and saved original mask. Older805F and C0F8 frames remain below it. Queue remains
03038888888888888888; cursor88 for Right and28 for Left.
The added slice produces28 ordered RAM writes and one resource read, no APU
writes. Neutral remains1,219 helpers/41 NMIs/39 returns,A06CFFFFFFA4BDA7.
Default16 remains1,196 helpers/40 NMIs/38 returns,C5F8F800FF27BFA7, both bank2.

Composite28,506 bytes, SHA256
5baf0e1aa0d6730ee3c2f35d1dc3015aebd920dfe45074339223f23f6fb5444a.
Standalone helper486 bytes. Frozen predecessor composite28,016 bytes, SHA256
98b9f24e5c552bb110cd94bee7f8204cab900175c54c6c1bcee4df094fadad50.
All four frozen continuous runs pass unchanged. All52 readable old manifest
file entries verify, including predecessor manifest
58b21442d22b9017021597497d7b52512ca55714a932764940201542325eacd8.

## Test coverage

The declarative suite passes425,984 accepted cases and375,806 inert rejects.
The same complete default suite passes in the independent source-only tree.
All425,984 accepted cases also pass the independent original-ROM oracle. Frozen stream, header
and initialized-tail original-ROM suites pass82,941,81,920 and65,536 cases.
The independent declarative contract models the arithmetic as a shifting
16-bit partial product and separately asserts exact unsigned8x8 multiplication.
Private --rom additionally executes original cartridge code with binary Ricoh
ADC and compares it to that model and to the assembled native helper.
Default mode imports only the existing ROM-free native header harness, not
private oracle modules, and never opens a cartridge. A separate source-only
copy contains exactly the new assembly/test and that public harness.

The tests cover all65,536 operand pairs under all four input C/D combinations,
all65,536 raw P/SP combinations at each entry, both tail branches and all16,384
bank addresses, including page crossing and BFFF. Every comparison checks full
RAM/raw context, ordered RAM/resource effects, resource addresses, journal
including untouched tail, immutable bank, ABI/native stack balance, stack
canaries, buffer guards and whitelist bounds. Out-of-range trace probes must
fail. Reject cases exhaust unsupported PCs, invalid tail pointers and each
incorrect return byte at every wrapped SP for both entries.

## Reproducing the checks

Install the documented native assembler and Python test dependencies. Set VASM
to the local vasmm68k_mot executable and add the dependency installation directory
to PYTHONPATH when it is not already on Python's search path. From the repository
root, run `python port/tests/recovery_test_sfx_duration_math.py` for the ROM-free
contract. With the hash-verified cartridge restored to the documented private
input path, add `--rom` for original-instruction comparison and run
`port/tests/recovery_test_resident_sfx_duration_math.py` with
`CHARACTER_INPUT=0,16,1,2` in separate invocations.

This is additive source development on the recovered baseline. It does not
recover the later missing gameplay/audio source or alter the delivered playable
ADF. Verification is host correctness only: no audible Paula, full-game
completion, target execution or stock-speed claim.
