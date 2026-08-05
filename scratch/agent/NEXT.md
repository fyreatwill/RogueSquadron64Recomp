# NEXT work unit

## s346 was a MAINTENANCE iteration (Step 0 triggered) — read this first

`docs/CURRENT-TRUTH.md` hit 60,543 bytes, over the 60,000 threshold, so s346 compacted it
(670→470 lines) instead of running an experiment. The closed s297-337 M5 gate-reversal/VI=640-stall
investigation arc (3 Next-steps ranges, 86 lines) migrated to `docs/PROJECT-OVERVIEW.md` §9. While
reading SOAK-RESULTS.md for the maintenance pass, 2 new verdicts had already landed
(`m5step5v3_rate_1/2`, queued by s345): both confirm s345's `${VAR:-1}` log-blowup fix works
(`runlog_bytes` back to 57-62 MB, no more `rc=137` artifacts), but `rate_1` crashed at
`last-guest-pc=0x80010b7c`, `pc-symbol=allocOrEvictMaterialNode+944` — NOT a match for any
already-catalogued crash signature (checked against `tickWrappingTimerAccumulatorList`'s div-by-zero,
the `emitAllocatedDLCommand`/`submitSceneNodeRender` SIGBUS family, and `waitForAnyAudioSlot`). `rate_2`
ran clean the full 240s hold. s346 queued 2 more soaks on the identical template
(`scratch/agent/soak_queue/m5step5v3_rate_3.sh`/`_4.sh`) but did not run them (maintenance iteration).
Full detail: `docs/CURRENT-TRUTH.md` item -202, `PORTING-STATE` Session 346.

## The work unit: drain m5step5v3_rate_3/4, classify allocOrEvictMaterialNode, continue the rate count

**Step 1**: `tail -10 scratch/agent/SOAK-RESULTS.md` for `m5step5v3_rate_3`/`_4` verdicts (the loop
drains up to 2 queued recipes between iterations — these may already be in). For each:
- Confirm `runlog_bytes` stayed in the normal 50-70 MB band (if it didn't, the s345 fix regressed —
  that would itself be a surprising, checkable finding).
- Check `last_pc_symbol`. If it says `allocOrEvictMaterialNode+944` again, that's 2/4 — a real
  candidate crash family, not a fluke; read the full verdict log
  (`scratch/agent/soak_results/m5step5v3_rate_{3,4}_*.log`) and the matching `*_launcher.log` for
  exactly which stick input preceded it (rate_1's crash landed right at hold_10, the first scheduled
  stick press — check if that recurs). If it's a DIFFERENT symbol, or clean, note it as-is; don't force
  a pattern out of 2-4 points.

**Step 2 — source-read `allocOrEvictMaterialNode` if it recurs (≥2/4 hits)**: grep
`~/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_6.c` for the function, read it around the +944 byte
offset (compare against the function's disassembled structure — same technique s343 used for
`tickWrappingTimerAccumulatorList`'s `break 7` trap: find what conditional/pointer-deref sits at that
exact offset). Name says "alloc or evict a material node" — a plausible fit for a hangar/craft-select
scene doing per-frame material-slot churn; check whether this looks like an OOB array index, a null
deref, or a div/mod trap, same triage categories as every other crash family in the catalog.

**Step 3 — tally the rate**: after step 1/2, you'll have 4 real (non-artifact) data points total from
the v3 family (`rate_1` crash, `rate_2` clean, `rate_3`/`_4` TBD). Compare against M5-AUDIO-PLAN §3's
historical baselines (family #3 `waitForAnyAudioSlot` ~12-21% pre-title SIGSEGV rate; family #4
post-cutscene stall, historically "every soak died earlier"). If `allocOrEvictMaterialNode` is
confirmed recurring, it may be a NEW family #5 rather than #3/#4 — note that distinction explicitly,
don't fold it into the #3/#4 count. 4 points is still a small sample; write 2-4 more `m5step5v3_rate_N`
recipes (same template) before concluding a rate, per M5-AUDIO-PLAN's explicit warning against
over-reading small samples.

HYPOTHESIS-ID: m5-audio-destub-step5-crashrate-comparison (4th iteration since s344's reopen — s345 was
methodology repair, s346 was maintenance + passive fold-in, neither counts as a repeat of the same
experiment for budget rule 8; this next iteration IS the experiment, watch the 3-strike rule from here).

## Environment notes (carried forward — see s327-346 for full detail)

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
  x1` in the fixup report. No rebuild needed for this work unit unless step 2 lands a guard.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). It arms EVERY diagnostic env var unconditionally EXCEPT the 4
  heap-walker vars (s345 fix — `ROGUESQ_LOG_RS_MALLOC_WALK`/`_GUARD`/`ROGUESQ_LOG_RS_FREE_WALK`/`_GUARD`
  now default to 1 but are overridable by pre-exporting 0). Log lands at
  `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly; check `runlog_bytes`
  before trusting a soak's post-processing to have actually finished. **`[keys]` lines land in the
  LAUNCHER's stdout/stderr (`scratch/agent/soak_results/<label>_launcher.log`), NOT in the game's own
  `run.log`.**
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- Any soak recipe testing for a SPECIFIC crash must check `last-guest-pc`/`pc-symbol` against that
  crash's own signature, not just "did `[CRASH]` fire" — RS64 has ~20+ independent, already-catalogued
  crash families that can fire nondeterministically at any point (s344's method-trap finding,
  `docs/CURRENT-TRUTH.md` Method traps section).
- `rc=137` (SIGKILL at the loop's 600s hard cap) does NOT necessarily mean the GAME hung — it can mean
  the RECIPE's own post-processing didn't finish in time (s345's finding). Always check the launcher
  log's own `done wall=Ns` line and the run.log's byte size before reading a 600s timeout as a game-side
  stall.
