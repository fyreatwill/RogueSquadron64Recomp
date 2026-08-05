# NEXT work unit

## s342 found `reapplyDisplayMode`'s gate reversal blocks title-screen reach entirely — read this first

s342 (`HYPOTHESIS-ID m5-audio-destub-reapplydisplaymode-title-block`, 1st iteration, CURRENT-TRUTH item
-198, full detail `PORTING-STATE` Session 342) found, by hand-reading the raw logs of the queued step-5
soak batch plus s340's own raw logs, that **every soak with `reapplyDisplayMode`'s gate reversed — alone
(s329) or combined with `setDisplayMode`'s (s340x2, s341x2) — has never reached the title screen: 0/5
across 3 sessions spanning weeks.** `setDisplayMode` reversed ALONE reaches title fine (45.4s baseline,
`scratch/s73_post_a_scene/step4gate2.log`). This means s340's "2/2 clean soaks" promotion-decision
validation never actually exercised menu navigation, craft select, or mission launch — only ~600s of
idling at the pre-title attribution/logo screen (0 `[keys]` lines in both its raw logs, confirmed s342).
M5-AUDIO-PLAN step 5 (crash-family #3/#4 rate comparison) cannot be measured while this holds — both
target families are defined relative to phases (pre-title death rate, post-cutscene stall) this build
cannot reach.

## The work unit: revert `reapplyDisplayMode`'s gate to force-zero, rebuild, re-validate title-reach

**Competing hypotheses**:
- HA: `reapplyDisplayMode`'s reversal is the sole cause — reverting ONLY its gate (keeping
  `setDisplayMode`'s reversal) restores title-reach to the ~45s baseline, matching `setDisplayMode`-alone
  behavior (`step4gate2`). This is the expected outcome given the clean 3-way isolation s342 already
  did (baseline OK, setDisplayMode-alone OK, reapplyDisplayMode-involved 0/5 OK).
- HB: reverting doesn't fully restore title-reach — some OTHER change since s328 (not the gate itself)
  is responsible, or there's a second, independent regression. Would falsify HA and reopen the search.
- HC: title-reach is restored, but a NEW failure appears further into the menu/mission-launch sequence
  once title is reachable again — the "H3: visual/behavioral regression not caught by a crash-free soak"
  possibility s340 flagged as unaddressed (`docs/M5-AUDIO-PLAN.md`), now actually testable for the
  first time since title was never reached before.

**Discriminating measurement**: does `phase width=1024 reached after ~N s` appear in the soak's own
launcher-log output (or equivalently, does `grep -c '\[keys\]' run.log` go from 0 to nonzero) within a
timeframe comparable to the 44.6-46.2s historical baseline? That single fact splits HA from HB. Getting
that far also gives HC a first chance to surface (any new crash/stall AFTER title, during menu nav or
mission launch, that wasn't previously observable because title was unreachable).

**Steps**:
1. Edit `~/Documents/Tools/N64Recomp/fixup_game_funcs.py`'s audio-gate regex (currently
   `r"0x8008E(?:NONE)"`, matching neither address — see the comment block above it, ~line 262) to match
   `0x8008EC88` only (`reapplyDisplayMode`'s address), so it gets force-zeroed again while
   `0x8008EB40` (`setDisplayMode`) stays unpatched/reversed. Follow the exact pattern s303/s307/s329
   used for single-site narrowing (grep those session comments in the same file for the regex form).
2. Regen: delete `RecompiledFuncs/*.c` first, then `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`
   -> `cmake --build` (full paths/commands in the Environment notes below). Confirm via the fixup
   report (`audio gate patched x1`, not x2) and by grepping the regenerated `funcs_23.c` directly for
   both addresses — `0x8008EC88` should show the force-zero patch, `0x8008EB40` should show the raw
   `= ctx->r2;` write.
3. Run ONE soak: `env HOLD_S=240 zsh scratch/s73_post_a_scene/run_s327waitpump.sh s342revert` (inline,
   not queued — this is a genuine new experiment needing a fresh look, not a repeat recipe). Read the
   launcher's own stdout for `phase width=1024 reached after Ns` (success) vs. `phase timeout
   (INCONCLUSIVE)` (HB, falsified). Cross-check `grep -c '\[keys\]' scratch/s73_post_a_scene/s342revert/run.log`
   — should be nonzero (4 schedule presses minimum) if title was reached.
4. If HA confirms (title reached, comparable timing): this closes the immediate blocker. Update
   CURRENT-TRUTH: `setDisplayMode`'s reversal remains the validated permanent default;
   `reapplyDisplayMode`'s reversal is NOT promoted (back to force-zero, this time genuinely tested
   against the "does the game still work" bar, not just "does it crash while idling pre-title"). Then
   step 5 (family #3/#4 rate comparison) can resume — but write FRESH soak recipes rather than reusing
   `soak_queue/cancelled/m5step5_rate_*.sh` (their `STICK_SCHEDULE`/`HOLD_S` values were sized for a
   phase this config can now actually reach, but the recipes' own post-processing logic needs the
   inner phase-gate timeout to leave real margin under the loop's 600s hard cap — the cancelled recipes
   never got there because title was unreachable, not because the margin math was checked).
5. If HB or HC: follow wherever the evidence leads; do not assume `reapplyDisplayMode` was the only
   variable without checking the diff between `step4gate2`'s era (s328) and now (build/harness drift is
   the boring-first check per Iron Rule 5).

HYPOTHESIS-ID: m5-audio-destub-reapplydisplaymode-title-block (1st iteration; new thread, pivoted from
the now-superseded m5-audio-destub-step5-crashrate-comparison).

## Environment notes (carried forward — see s327-342 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> <VARS> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix
  is required — see project rule 10 / CLAUDE.md). It wraps `run_mission_keys.sh`, whose own
  wait-for-`VI=1024` phase gate (lines 69-77) has a HARDCODED 600s internal timeout independent of
  `HOLD_S` — if reused for a queued soak_queue recipe, remember the loop's own 600s hard cap will race
  it and usually win (see `soak_queue/cancelled/README.md`), so an inline one-off run (this work unit)
  or a generous manual timeout is safer than queuing until title-reach is re-confirmed.
  Log lands at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly
  (multi-MB/million-line files). `proc_start_epoch.txt` in the same dir gives the real UNIX start
  time for cross-referencing against the log's own mtime to get wall-clock duration.
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- Scratch files outside the three allowed working directories (e.g. `/tmp/...`) are blocked by the
  sandbox — write throwaway analysis/poll scripts under `scratch/` in this repo instead.
- `bash -n <script>` was denied by this session's permission gate even as a pure syntax check — if
  linting a soak-queue recipe, visual review is the workaround.
- Some `bash` heredoc/multi-command blocks trip a sandbox "Contains simple_expansion" or "Contains
  command_substitution" false-positive on nested `$()`/`${}` even in read-only commands — split into
  separate single-purpose `Bash` calls rather than one large script block if this happens (s342).
