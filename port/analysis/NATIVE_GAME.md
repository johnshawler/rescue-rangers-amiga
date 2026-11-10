# First native Rescue Rangers game-code translation

This is executable native game-state code, not a 6502 emulator and not a complete game port. The production source has five direct Motorola routines with no 6502 interpreter, opcode dispatcher, ROM instruction fetch, or runtime translation. They are assembled for 68020 (the selected instructions also happen to fit the 68000 subset).

## Source provenance

User-supplied Chip 'n Dale Rescue Rangers (Europe) ROM SHA-256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
The routines come from fixed PRG bank 7, mapped at CPU `$C000–$FFFF`. File offset = `16 + 7*16384 + CPU_address - $C000`. The byte-annotated disassembly is in `native-game-original-disassembly.txt`.

- `$C162–$C1B9`: two-controller sampling, new-press edges, held state, invalid simultaneous direction suppression. `$C162–$C18D` hardware serial reads and merge are replaced with host-supplied stable standard-controller bytes. The reference test still executes the original full routine with a serial input bus.
- `$C0A1–$C0BE`: NMI frame-counter increment, `$90=$FF` ready marker, four independent timer slots. This is only the RAM-mutating timer slice, ending immediately before `$C0BF`; it is not the whole NMI.
- `$C21E–$C234`: hide unused sprite entries by setting OAM Y bytes to `$F8`, including the special cursor-4 handling of sprite zero.
- `$C235–$C246`: initialize object slots 2 through 15, clearing `$04D0+slot` and setting `$0590+slot=$FF`, leaving player slots 0 and 1 untouched.
- `$C2DC–$C2F6`: original four-byte shift-register random-state update and its `$00` scratch write. Feedback is bit 1 of `$E4 XOR $E5`, shifted through `$E4–$E7`.

## Callable ABI

Source: `src/native_rescue_game.s`.

All five functions take A0 pointing at an ordinary writable 2048-byte RAM image with original NES offsets. All data and address registers are preserved; CCR is scratch. These do not access Amiga or NES hardware.

- `rescue_update_controllers`: D0.b = player 1, D1.b = player 2, in NES byte order: A, B, Select, Start, Up, Down, Left, Right from bit 7 to bit 0. `$14/$15` become newly pressed inputs and `$16/$17` held inputs, with the original impossible-direction handling. `$00/$01` become zero because the host adapter has no expansion-port input. Standard controllers only; expansion serial bit 1 is not modeled.
- `rescue_nmi_timers`: no additional arguments. Four slots at `$80,$84,$88,$8C`; state 1 decrements its following timer byte, and becomes state 4 only when that decrement yields zero. Byte wraparound preserved.
- `rescue_hide_sprites`: `$97` is the first unused OAM byte cursor and must be divisible by four. An invalid cursor also makes the original loop nonterminating; the translation retains that precondition. Cursor zero hides all 64 entries.
- `rescue_initialize_objects`: no additional arguments.
- `rescue_random_step`: no additional arguments. Does not initialize a seed.

`rescue_game_selftest` also takes A0. It is intentionally destructive to test-state locations, invokes all five routines, and returns D0=0 on success or D0=-1 on failure. Other registers are preserved, CCR scratch. Run against dedicated scratch RAM, or restore/reinitialize game RAM afterwards. It is a small on-target smoke check, not the differential test suite.

## Differential proof

Run `python port/tests/test_rescue_game.py` from the lab root (or use the absolute path). Dependencies: `py65` and `machine68k`; the test discovers the installed `/tmp/rescue-py65` and `/tmp/nes-sprite-test-deps` copies. Set `VASM` to override the default existing sibling-project assembler path. No sibling project files are changed.

The test asserts the ROM hash, executes the actual original 6502 instruction bytes with py65, assembles the native source using `vasmm68k_mot -m68020 -Fbin`, and executes the resulting machine code with machine68k's M68EC020 core. It compares all 2048 RAM bytes, checks native RAM boundary guards and register preservation, and verifies balanced native stack returns. Reference execution stops immediately before the original RTS or the end of the NMI slice; the host 6502 return stack is not part of the game-state ABI.

Coverage: all 65,536 current/previous controller combinations (second controller complementary), another 1,024 random-RAM controller cases; 2,048 timer cases covering every countdown value in every slot and randomized states; 1,088 sprite cases covering all 64 legal cursor values plus random states; 1,024 object-initialization cases; 66,560 PRNG cases covering every feedback-byte pair and randomized RAM. Total: 137,280 differential cases, plus 16 native boot selftests.

## Limits

No playable game loop, world rendering, collision, enemies, scoring, level loading, audio, MMC1 behavior, PPU behavior, or full reset/NMI implementation is implied. The controller host adapter supplies already-decoded input and does not reproduce serial bus timing or expansion devices. Host tests are semantic correctness evidence, not Amiga hardware speed measurements. No frame-rate or full-port performance claim is made. PAL cadence must be chosen by the platform integration, not inferred from these primitives.
