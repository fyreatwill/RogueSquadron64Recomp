# NEXT (s7621)
HYPOTHESIS-ID: g6-upstream-features

G6a (s7617) and G6b (s7618-s7620, F6 panel) are landed and wait on the owner's hands. Take G6c far-object stand-ins.
NOTE: docs/CURRENT-TRUTH.md is ~59.9 KB; if Step 0 prints >60000 this iteration is MAINTENANCE instead.
Step 1 (this unit, offline, no game run): write docs/G6C-STANDINS-PLAN.md.
  - `git show origin/main:src/game/static_standins.cpp`, `git show origin/main:rogue_squadron.toml | grep -n -A12 -i stand`,
    `git show origin/main:src/game/toml_hooks.c`, `git show origin/main:src/game/hook_helpers.cpp` (only the parts the hooks call).
  - List every guest structure/address it reads or writes; for each, verify the address in OUR build (grep our symbol names /
    RecompiledFuncs for runInMissionFrame, selectMeshLod 0x80058264, 0x800FAC68) and mark same/different.
  - Map each toml hook onto our generated function + a fixup/apply script registered in RS64_REPLAY (docs/REGEN-VERIFY.md).
  - Gate: ROGUESQ_STANDINS=1 and draw distance > 1; dd1 untouched.
Hypotheses for the design question "can it be ported without HLE matrices?": H-portable (it only touches the game's own
visibility bucket + object templates, renderer-independent) vs H-hle (it needs RT64 HLE state we lack under LLE). The
plan doc must state which, citing the upstream lines.
Step 2 (next unit): implement hook 1 behind the flag with an in-run positive control.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; never launch under lldb.
