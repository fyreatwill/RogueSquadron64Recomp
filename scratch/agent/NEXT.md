# NEXT: RESUME bit1 writer versus lives decrement

Checkpoint close-out: do not rerun the prior guest-PC census. The next iteration's
single work unit is to instrument the already identified guest PC 0x800B1140
and add an explicit watch/log for the player lives byte 0x80130B10. Build once
and run the level-select mission recipe for 420 s; require mission origin,
`[mtm]`, and at least one real 3->2/2->1/1->0 lives decrement before using
the result.

Competing hypotheses and the discriminating measurement:

- H1: bit1 is posted by the player-slot settle writer at 0x800B1140 and the
  following mtm(1) decrements lives. Evidence: `[bit1ctx]` followed by a
  lives-byte decrement in the same mission phase.
- H2: bit1 is posted, but no lives decrement follows; the transition is not
  the death-settle chain. Evidence: bit1 hits plus live mtm/phase controls and
  unchanged lives.
- H3: the lives decrement occurs without a bit1 hit. Evidence: the lives
  control fires while the 0x800B1140 entry census is zero.

The split is one run: the bit1 entry, mask post, mtm, and lives lines share a
monotonic ordinal or timestamp. Do not infer H3 from absent host-symbol
breakpoints. Capture output under `scratch/agent/m6/<tag>/`, kill with SIGKILL,
and require the mission origin before counting any bit1 hit.

Expected commands after the static/ground-truth check:

```zsh
rg -n '800B1140|80130B10|requestMissionTransitionMode' RecompiledFuncs tools/fixup_game_funcs_vendored.py src/main
python3 tools/<new bit1-lives-fixup>.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env XENV='ROGUESQ_LOG_MTM=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_GODMODE=1 ROGUESQ_GODMODE3=2' zsh scratch/agent/<bit1-lives-soak>.sh
```

HYPOTHESIS-ID: g1-nonhealth-fail
