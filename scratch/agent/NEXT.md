# NEXT work unit (s2122) — port-side key-on contract census

HYPOTHESIS-ID: m5-keyon-port-contract-census

## Work unit

Add one regeneration-persistent, opt-in diagnostic to the existing
`musyxKeyOnVoice` fixup block in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` (the
block near line 6119). Keep all eight early-return guards unchanged. In one
phase-keyed table, record for each of these exact sites:

    0x80090CEC, 0x80090D04, 0x80090D30, 0x80090D48,
    0x80090D74, 0x80090D8C, 0x80090DB8, 0x80090DD0

the `musyxKeyOnVoice` entry count, the site/guard count, the normal-tail
count, and the numerator/divisor register values immediately before the
corresponding divide. Also record slot `+0` transitions (`0x02` and `0x00`)
with the same phase key. Derive register names from a fresh generated body;
do not guess them from the retail PC list. The diagnostic must be disabled
unless `ROGUESQ_LOG_M5_KEYON_CENSUS=1`, rate-limit output, and add its source
to the fixup script rather than editing generated C.

## Competing hypotheses and single discriminator

- `H-PortKeyOnDead`: the port's qualified hangar route never enters this
  eight-site class. The positive LLE/audio controls and hangar VI fire, while
  all eight entry/guard/tail rows are zero.
- `H-PortKeyOnGuarded`: the port enters one or more sites and returns through
  the existing guards. The table identifies the exact site subset and operand
  values; normal-tail and slot transitions remain absent for those calls.
- `H-PortKeyOnNormal`: at least one site is entered and the function reaches
  its normal tail, with a corresponding slot transition. The early returns
  are not the admission boundary for that observed call path.
- `H-PortRouteMismatch`: the port reaches the class with a nonzero/invalid
  operand pattern or site subset that is absent from retail, so the next step
  is descriptor/route provenance rather than guard removal.

The single discriminator is the complete eight-site table from one run,
accepted only if the same run has positive `[audtask-dispatch]`/LLE controls,
title VI `1024 @ 0x00790400`, and hangar VI `512` with an
`0x006AB400` origin. A covered all-zero table parks the class. Any guard hit,
normal tail, or slot transition selects the exact port-only branch for the
next contract audit. No outcome authorizes removing or rewriting a guard in
this work unit.

## Exact commands

1. Inspect the fresh generated `musyxKeyOnVoice` body and add the complete
   table to the existing fixup block; verify the eight anchors and the new
   diagnostic marker before regeneration:

       rg -n -C 4 'musyxKeyOnVoice|0x80090CEC|0x80090DD0' \
         /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c
       rg -n 'musyxKeyOnVoice|M5_KEYON_CENSUS' \
         /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py

2. Regenerate in the required order, then build the Debug target:

       cd /Users/williambuckley/Documents/Tools/rogue_squadron64
       python3 tools/make_elf.py
       cd /Users/williambuckley/Documents/Tools/N64Recomp
       ./build/N64Recomp rogue_squadron.toml
       python3 fixup_game_funcs.py
       cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
       DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
         cmake --build build --config Debug --target RogueSquadron64Recomp

   If the generated-output sentinel refuses the fixup pass, clear only the
   generated `RecompiledFuncs/` outputs through the existing regeneration
   procedure and rerun this sequence; never hand-edit the generated files.

3. Run one qualified hangar capture. The existing driver launches from
   `build/`, kills the game with SIGKILL, and supplies the title-to-hangar
   schedule; pass the new diagnostic only to the game:

       cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
       env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1' \
         zsh scratch/s73_post_a_scene/run_mission_keys.sh s2122_keyon_port 30 12

Inspect only the positive LLE/audio controls, `[phase]` title/hangar rows,
the complete eight-site key-on table, and slot `+0` transitions. Do not
change the guards or infer a null result without both VI controls.
