# RS64 recomp — autonomous iteration

You are continuing the Rogue Squadron 64 static-recomp investigation. You have
no memory of previous iterations; the docs are your memory.

## Read first, in this order — nothing else
1. docs/CURRENT-TRUTH.md   (state, config, next steps, superseded conclusions)
2. scratch/agent/NEXT.md   (the single next work unit, if it exists)
Do NOT read PORTING-STATE.md except to grep for a specific fact; it is 43
sessions long and roughly two dozen of its conclusions are superseded.

## Do exactly one work unit
A work unit is ONE experiment or ONE bounded change, chosen from the top of
CURRENT-TRUTH "Next steps" (or NEXT.md if present). Before building anything:
- Write down (in NEXT.md) the 2-4 competing hypotheses and the DISCRIMINATING
  measurement — the one whose outcome splits them. If you cannot name what
  each possible outcome would prove, redesign before running.
- Batch instrumentation: one build carrying every counter you will want, one
  run collecting all of them. Never spend a build-run cycle per counter.

## Iron rules (each one bought with multiple lost sessions)
1. A null result is WORTHLESS until the instrument passes a positive control
   in the same run ("mark everything" must visibly fire). A counter proving
   the branch ran is NOT a control.
2. No cross-run A/B on animating scenes. Phase-gate on VI transitions
   (PROBE_PHASE_WIDTH / PROBE_KEYS_FROM_PHASE=1), never a stopwatch. Toggle
   within a single run where possible.
3. Scope every counter and log budget to the phase. Run-lifetime budgets read
   as false zeros in later phases.
4. Two independent lines of evidence before any conclusion enters
   CURRENT-TRUTH. One source = label it "single-source" explicitly.
5. Check the boring thing first: build flags, env vars, stale schedules,
   "working as designed" — before instrumenting the exotic thing.
6. Regeneration order: make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
   cmake. New diagnostics in build/factor5_ucode/*.c or RecompiledFuncs/ go
   into the fixup scripts or they die at the next regen.
7. Kill runs with SIGKILL, never SIGTERM. Capture paths must not start with
   "." in the final component. Run the game from build/ with the ROM present.
8. Budget rule: if this is the 3rd consecutive iteration on the same
   hypothesis with no discriminating result, STOP experimenting. Write the
   hypothesis/evidence table into NEXT.md, pick the highest-information-value
   next probe, or go BLOCKED with a specific question.
9. NEVER run `git submodule update`, `git checkout -- lib/...`, `git clean`,
   or `git reset --hard` (all denied in .claude/settings.json). lib/ carries
   uncommitted patches. If you edit anything under lib/, run
   `./submodule-patches/export.sh` and commit the refreshed patches in the
   same iteration, or the work is lost at the next reset.

## Exit contract (the Stop hook enforces this)
Before you may stop, ALL of:
1. Append a dated session entry to PORTING-STATE.md: what ran, what it
   showed, what it rules out. Include failed experiments — a documented dead
   end is a result.
2. Update docs/CURRENT-TRUTH.md: next-steps reordered; any overturned
   conclusion moved to the superseded section WITH why it was believable.
3. Rewrite scratch/agent/NEXT.md for the next iteration: the single next work
   unit, exact commands, expected discriminating outcomes.
4. git add -A && git commit (message: "iter: <one-line finding>").
5. Write scratch/agent/STATUS: DONE (work unit finished), or BLOCKED (also
   write scratch/agent/BLOCKED.md: what you need, from whom, and what you
   already tried — specific enough that a human can act in 2 minutes).
Never end on a plan or a promise. If the experiment failed, run the fixed
version now, in this iteration.
