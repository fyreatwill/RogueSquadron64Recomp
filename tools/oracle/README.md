# rs64_oracle — ask the real machine

Every "does the game really do X?" question on this project has been answered
with our own recompiled runtime as the witness. That runtime is the thing under
test, so those answers were never independent. This tool runs the **retail ROM
under mupen64plus** and reports what actually happens, giving the second source
that iron rule 4 asks for.

## Setup (once)

    tools/oracle/build_core.sh      # mupen64plus core with DEBUGGER=1 (+ binutils, brew mupen64plus)
    tools/oracle/build.sh           # the front-end

The core must be built from source: Homebrew's bottle has no `Debug*` symbols
and the oracle refuses to run against it.

## Use

    tools/oracle/build/rs64_oracle \
      --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom  ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 180 --watch-write 0x1F3CC0:0x1F3CD0

    [watch] write [0x001f3cc0,0x001f3cd0] flags=0x5 idx=0
    [hit] w addr=0x001f3cc0 pc=0x800b1234 prev_pc=0x800b1230 t=41.2s n=1
    [oracle] done: 3 hit(s) in 180.0s wall, 10794 VI (~179.9s emulated)

Exit status: 0 = hits, 3 = clean run with zero hits, 1/2 = setup error. The
VI count is emulated frames, so a run always reports how far the *game* got,
not just how long the wall clock ran.

## Three traps, all already paid for

**Addresses are PHYSICAL.** `r4300_write_aligned_word()` masks with
`0x1ffffffc` before the handler lookup, so the address that reaches the
breakpoint check has lost its KSEG0 prefix. A watch on `0x801F3CC0` never
fires — and reports a clean zero, which reads exactly like "the game never
writes here". The tool masks inputs with `0x1FFFFFFF` so both spellings work.

**Always run a positive control.** The first version of this tool reported zero
hits on a watch covering *all of RDRAM*, which is impossible; that is how the
physical-address trap was found. Before trusting any null, point a watch at
something that must fire:

    --watch-write 0x0:0x800000     # whole RDRAM: ~1.6M hits in 8 emulated seconds

Iron rule 1 applies to the oracle exactly as it applies to our own instruments.

**`m64p_breakpoint.endaddr` is INCLUSIVE.** `lookup_breakpoint()` tests
`address <= endaddr`. `--watch-write A:B` takes B half-open like everything
else and converts on the way in; if you touch that code, keep the conversion
or every watch quietly covers one extra word and attributes hits from outside
the range you asked about.

## Driving it

    --press 8:return,14:return,20:return --hold-ms 150

attaches `mupen64plus-input-sdl` and injects keys through
`CoreDoCommand(M64CMD_SEND_SDL_KEYDOWN/KEYUP, ...)`. Keys are names
(`return z x up down left right lshift lctrl space`) or raw SDL2 keycodes.
The key-to-button mapping is whatever `[Input-SDL-Control1]` holds in the
config; `--configdir DIR` materialises it so you can read it. The default has
controller 1 plugged in keyboard mode with `Start = key(13)` (Enter).

**Input is verified end-to-end**, not just delivered: the emulator is
deterministic, so two undriven 30 s runs agree to five significant figures on
writes per frame (2891.3, 2891.3 over all of RDRAM), while a run pressing
Start four times diverges to 2903.3 — 0.4% against 0.002% run-to-run noise.
Reproduce that A/B if you ever suspect the presses stopped landing.

What it still does not reach: blind Start presses get through boot, logos and
title, but not into the hangar or a mission — that needs a real menu
navigation schedule. Do not read a null as evidence about a phase the run
never reached; check the phase first.

The RSP plugin is Homebrew's `mupen64plus-rsp-hle`, which handles MusyX audio
tasks. Video and audio are left unattached and the core substitutes dummies
(input too, unless `--press` or `--input` attaches it). Graphics are therefore
not rendered at all — this instrument answers questions
about **memory and CPU**, not about pixels. For questions about what the
microcode is supposed to emit, read `docs/F5-UCODE-REFERENCE.md` instead.

## Questions worth asking it

- Does the retail game ever write the heap freelist header at physical
  `0x1F3CC0`, and from what PC? (items -405..-407 assume our writeback stomps
  something the game owns; the oracle can say whether the game itself ever
  touches it.)
- Is a given address ours or the game's, for any "who corrupted this?"
  question — the class that has eaten the most sessions on this project.
- What PC writes a structure we only see the aftermath of.
