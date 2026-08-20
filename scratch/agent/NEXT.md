# NEXT work unit (s2000) — repair the M5 fixup anchor and regenerate

HYPOTHESIS-ID: m5-audio-ground-truth

## Single work unit

Make the existing `fixup_game_funcs.py` force-zero rule for guest
`0x8008EC88` tolerate the diagnostic `rs64_probe_submit_gate_store` line that
now appears between the instruction comment and `MEM_B`. Keep the rule anchored
to this one PC and require exactly one match. Then perform the documented
regeneration order and build. Do not run the game, enable `ROGUESQ_AUDIO_UCODE`,
flip another gate, or change the default audio dispatch in this unit.

## Competing hypotheses and discriminating measurement

- **H-probe-anchor:** only the intervening probe broke the old regex. After
  regeneration and fixup, the script reports one audio-gate patch and generated
  `funcs_23.c` has `0x8008EC88` followed by `MEM_B(...) = 0`; no unrelated gate
  store changes appear.
- **H-generator-layout:** N64Recomp's current output differs in more than the
  probe line. The optional-probe anchor still does not match or matches zero;
  the exact-count assertion selects a new address-anchored fixup design before
  any runtime test.
- **H-wrong-output-path:** the fixup script reports a match but the inspected
  `RecompiledFuncs/funcs_23.c` remains unchanged or still writes `1`. This
  selects a path/configuration error, not a guest-gate conclusion.

The discriminator is one post-fixup table: patch-report count, exact generated
`0x8008EC88` store value, and the count of changed `0x800A0F50` stores. A result
of exactly `1 / 0 / 0` selects H-probe-anchor; zero or multiple matches selects
H-generator-layout; a report/output disagreement selects H-wrong-output-path.

## Exact commands

```sh
rg -n -C 3 '8008EC88|rs64_probe_submit_gate_store' \
  ../N64Recomp/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs/funcs_23.c
(cd ../rogue_squadron64 && python3 tools/make_elf.py)
(cd ../N64Recomp && ../RogueSquadron64Recomp/build/N64Recomp rogue_squadron.toml)
(cd ../N64Recomp && python3 fixup_game_funcs.py)
rg -n -A 3 -B 2 '0x8008EC88' ../N64Recomp/RecompiledFuncs/funcs_23.c
cmake --build build --target RogueSquadron64Recomp
```

Record the exact patch count and generated store table in `PORTING-STATE.md`.
If the table selects H-probe-anchor, the following unit is M5 step 2: one
build with the default `musyx_stub` and opt-in `ROGUESQ_AUDIO_UCODE=1` arms,
phase-gated at title/hangar, measuring task exit, DMEM canary, slot transition,
and PCM sanity in the same run.
