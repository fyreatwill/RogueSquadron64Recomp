# NEXT work unit

## s344 folded in the tickwrap-divzero confirmations (1/3 total, PARKED not guarded) and reopened M5-AUDIO-PLAN step 5 — read this first

s343 found a NEW crash (`tickWrappingTimerAccumulatorList` div-by-zero, `last-guest-pc=0x80054744`) one
soak stage past the restored title screen. s344 read the 2 queued confirmation soaks' FULL raw logs
(not just the recipes' own naive "any `[CRASH]` = confirmed" summary) and found: confirm2's crash was a
completely DIFFERENT, already-catalogued, unrelated bug (`emitAllocatedDLCommand`/`submitSceneNodeRender`
SIGBUS family, `last-guest-pc=0x80008928`, x0=RDRAM-host-base pattern) — not a real confirmation.
confirm1 ran fully clean through the entire hold window. **Net: 1/3 total observations of the specific
div-by-zero signature** — not enough to land a guard (needs 2/2 matching), not a clean 0/2 either.
`HYPOTHESIS-ID m5-audio-destub-tickwrap-divzero-craftselect` is PARKED, not closed: if a future soak's
`last-guest-pc` is `0x80054744` again, reopen it and this time land the guard (idiom:
`fixup_game_funcs.py:939-949`, match `do_break\(2147829572\);` in `tickWrappingTimerAccumulatorList`,
bail setting `hi=0` before `L_80054748: mfhi $v1` — read `funcs_11.c:15310-15360` first to confirm `hi`'s
downstream use, and check `main_overlay.txt:2031`'s note about 3 callers across `funcs_11/32/33`).

s344 ALSO found and fixed a soak-recipe methodology bug: `[keys]` lines are emitted by the launcher
driver (`run_mission_keys.sh`) into its own `*_launcher.log`, never into the game's `run.log` — the
`s343_tickwrap_divzero_confirm{1,2}.sh` recipes grepped the wrong file, so both self-reported
`keys_lines=0` despite actually having driven the FULL key/stick schedule (confirmed by reading the
launcher logs directly). **Title-reach is now confirmed 3/3** across independent soaks
(s343revert/confirm1/confirm2), not 1/1 — a real strengthening, not just a repeat. Full detail:
`docs/CURRENT-TRUTH.md` item -200, `PORTING-STATE` Session 344.

## The work unit: drain the 4 queued step-5 recipes, then tally crash-family #3/#4 rates

**Step 1** (always do this first): `tail -10 scratch/agent/SOAK-RESULTS.md` — the loop drains up to 2
queued recipes between iterations, so some or all of `m5step5v2_rate_1..4` may already have verdicts.
For EACH one, read the printed `last_guest_pc`/`last_pc_symbol`/`title_reached` fields (now included in
every verdict, no need to re-open the raw log) — this recipe generation fixes both bugs s344 found, so
trust its own field reporting Instead of re-deriving it from scratch.

**Step 2 — classify each crash by family, don't just tally rc**: per `docs/M5-AUDIO-PLAN.md` §3,
crash-family #3 is `waitForAnyAudioSlot` pre-title SIGSEGV (historical ~12-21% of pre-scene soak
deaths — check `pc-symbol` for `waitForAnyAudioSlot`, and note whether `title_reached` was ever printed:
family #3 kills BEFORE title). Family #4 is the post-cutscene stall (not a crash marker at all — check
the tail `vi_width`/`[vi-fs-decision]` lines for `pairs=0 stalled=1` persisting to the end of a clean-rc
run). Any OTHER `pc-symbol` (like s344's `emitAllocatedDLCommand` hit) is background noise from an
unrelated, already-catalogued family — note it, don't fold it into either family's rate.

**Step 3 — decide if 4 soaks is enough for a rate comparison**: M5-AUDIO-PLAN step 5 explicitly warns
against treating 1-2 clean runs as conclusive. If the 4 queued recipes give a clear signal (e.g. 0/4
family #3, 0/4 family #4-stall) that's still a small sample against ~12-21% historical family #3 base
rate — write 2-4 MORE recipes (`m5step5v2_rate_5..8.sh`, same template) before concluding a rate change,
per budget rule 8 (this is a NEW hypothesis-id iteration count, not a continuation of the parked
divzero thread — don't conflate the two when checking the 3-strikes rule).

HYPOTHESIS-ID: m5-audio-destub-step5-crashrate-comparison (REOPENED s344, 1st iteration since reopen;
originally opened s341, voided by s342's title-unreachability finding, now viable again).

## Environment notes (carried forward — see s327-344 for full detail)

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
  x1` in the fixup report. No rebuild needed for the queued `m5step5v2_rate_*` recipes.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). It arms EVERY diagnostic env var unconditionally already — no extra
  vars needed. Log lands at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it
  directly (200+ MB files). **`[keys]` lines land in the LAUNCHER's stdout/stderr
  (`scratch/agent/soak_results/<label>_launcher.log` for queued recipes), NOT in the game's own
  `run.log` — grep the right file** (s344's fix; the `m5step5v2_rate_*.sh` recipes already do this
  correctly).
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- Any soak recipe testing for a SPECIFIC crash must check `last-guest-pc`/`pc-symbol` against that
  crash's own signature, not just "did `[CRASH]` fire" — RS64 has ~20+ independent, already-catalogued
  crash families that can fire nondeterministically at any point (s344's method-trap finding,
  `docs/CURRENT-TRUTH.md` Method traps section).
