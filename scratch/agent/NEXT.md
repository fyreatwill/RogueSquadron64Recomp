# NEXT work unit

## s345 fixed the soak driver — read this first

s344's `m5step5v2_rate_1/2` both came back `rc=137` (SIGKILL at the loop's 600s hard cap), which
NEXT.md's own plan would have read as crash-family #3/#4 evidence. It wasn't: both launcher logs show
the driven scenario (title reach at ~45.8s, full `[keys]`/stick schedule through the 240s hold,
`done wall=301-302s`) completed cleanly — the SIGKILL landed on the recipe's OWN post-launcher `grep`
passes over an 8.2-8.7 GB `run.log` (vs. 76-233 MB for every earlier recipe in this family), which
never finished before the watchdog fired. Root cause: a known, already-catalogued self-inflicted
logging blowup (PORTING-STATE Session 209/210) — `ROGUESQ_LOG_RS_FREE_WALK`/`ROGUESQ_LOG_RS_MALLOC_WALK`
log once PER LIST NODE walked, not once per call, and `[rs-free-walk]` was 44.7% of a 200 MB sample of
this run's log, matching Session 209/210's 44-82% range and ~47x blowup almost exactly. Fixed
`scratch/s73_post_a_scene/run_s327waitpump.sh` (the shared driver) to make those 4 vars
default-overridable (`${VAR:-1}`, behavior-preserving for every other recipe) and queued
`m5step5v3_rate_1/2.sh` with them opted to 0. Cancelled `m5step5v2_rate_3/4.sh` unrun (would have
reproduced the same artifact). Full detail: `docs/CURRENT-TRUTH.md` item -201, `PORTING-STATE` Session 345.

## The work unit: drain m5step5v3_rate_1/2, confirm the fix, then resume step-5 classification

**Step 1**: `tail -10 scratch/agent/SOAK-RESULTS.md` for `m5step5v3_rate_1/2` verdicts (the loop drains
up to 2 queued recipes between iterations, so these may already be in). For each, read the printed
`runlog_bytes` field FIRST — this is the fix's own positive control:
- If `runlog_bytes` is back in the 76-233 MB band (roughly 80,000,000-250,000,000) and `rs_free_walk_lines`
  is low relative to total lines, the fix worked — proceed to Step 2 (real classification work) below.
- If `runlog_bytes` is still in the multi-GB range despite `ROGUESQ_LOG_RS_FREE_WALK`/`_GUARD`/
  `ROGUESQ_LOG_RS_MALLOC_WALK`/`_GUARD` being set to 0 in the recipe, the fix didn't fully address the
  blowup (maybe a 5th log var is the real dominant cost, maybe the `${VAR:-1}` edit has a bug) — read
  `scratch/s73_post_a_scene/run_s327waitpump.sh` lines ~107-118 to verify the edit took, then sample the
  new run.log's line-tag distribution the same way this session did (`head -c 200000000 <file> | grep -ac
  '\[TAG\]'` for whatever tag dominates) to find the NEW top offender.
- If `rc=137` again but `runlog_bytes` is normal-sized this time, that's a genuine game-side stall
  (family #4 candidate) for the first time this batch — treat as real signal, not artifact.

**Step 2 — classify each crash by family** (per `docs/M5-AUDIO-PLAN.md` §3, unchanged from s344's plan):
family #3 is `waitForAnyAudioSlot` pre-title SIGSEGV (check `pc-symbol`, note whether `title_reached`
printed — family #3 kills BEFORE title). Family #4 is the post-cutscene stall (check the tail
`[vi-fs-decision]` line for `pairs=0 stalled=1` persisting on an otherwise-clean-looking run). Any OTHER
`pc-symbol` is background noise from an unrelated, already-catalogued family — note it, don't fold it in.

**Step 3 — decide if this is enough for a rate comparison**: 2 fresh data points plus whatever came before
is still a small sample against the ~12-21% historical family #3 base rate. If `m5step5v3_rate_1/2` give a
clean signal, write 2-4 more recipes (`m5step5v3_rate_3..6.sh`, same template, same env overrides) before
concluding anything, per M5-AUDIO-PLAN's own explicit warning against treating 1-2 runs as conclusive.

HYPOTHESIS-ID: m5-audio-destub-step5-crashrate-comparison (3rd iteration since s344's reopen — s345 was
methodology repair, not a repeat of the same experiment; if step 2/3 above also comes back
inconclusive/uninformative, that's the 3rd strike and budget rule 8 requires a pivot preamble next time).

## Environment notes (carried forward — see s327-345 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed. Verify via `funcs_23.c: audio gate patched
  x1` in the fixup report. No rebuild needed for the queued `m5step5v3_rate_*` recipes (no code change,
  only the shared driver script's env-var defaults changed).
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). It arms EVERY diagnostic env var unconditionally EXCEPT the 4
  heap-walker vars (s345 fix — `ROGUESQ_LOG_RS_MALLOC_WALK`/`_GUARD`/`ROGUESQ_LOG_RS_FREE_WALK`/`_GUARD`
  now default to 1 but are overridable by pre-exporting 0, unlike every other var in the file). Log
  lands at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly (can be 76-233
  MB normally; check `runlog_bytes` before trusting a soak's post-processing to have actually finished
  if a recipe doesn't print that field). **`[keys]` lines land in the LAUNCHER's stdout/stderr
  (`scratch/agent/soak_results/<label>_launcher.log` for queued recipes), NOT in the game's own
  `run.log`.**
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- Any soak recipe testing for a SPECIFIC crash must check `last-guest-pc`/`pc-symbol` against that
  crash's own signature, not just "did `[CRASH]` fire" — RS64 has ~20+ independent, already-catalogued
  crash families that can fire nondeterministically at any point (s344's method-trap finding,
  `docs/CURRENT-TRUTH.md` Method traps section).
- **New method-trap (s345)**: `rc=137` (SIGKILL at the loop's 600s hard cap) does NOT necessarily mean
  the GAME hung — it can mean the RECIPE's own post-processing (sequential greps over a huge log)
  didn't finish in time. Always check the launcher log's own `done wall=Ns` line and the run.log's byte
  size before reading a 600s timeout as a game-side stall.
