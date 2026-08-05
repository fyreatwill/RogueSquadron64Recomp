# NEXT work unit

## s341 queued the M5-AUDIO-PLAN step 5 soak batch — read this first

s341 (`HYPOTHESIS-ID m5-audio-destub-step5-crashrate-comparison`, 1st iteration, CURRENT-TRUTH item
-197, full detail `PORTING-STATE` Session 341) verified the s340 gate promotion is already baked into
the current build (no rebuild needed) and queued 6 self-contained soak recipes to
`scratch/agent/soak_queue/m5step5_rate_1.sh` .. `_6.sh` rather than spending a session babysitting
repeat soaks. Each recipe runs the existing `run_s327waitpump.sh` driver (already arms
`ROGUESQ_AUDIO_UCODE=1` and the `_VOICE_ACTIVE_GATE`/`_VOICE_TRIGGER_CHAIN`/`_AUDIO_DRAIN` instruments
as a same-run positive control) at `HOLD_S=300`, then exits 1 iff a `[CRASH]` marker fired anywhere in
the run, else 0. The loop runs up to 2 of these between iterations, appending one verdict line each to
`scratch/agent/SOAK-RESULTS.md` and moving the recipe to `soak_queue/done/`; full logs land in
`scratch/agent/soak_results/`.

## The work unit: fold the soak batch's verdicts into the step 5 rate comparison

1. **Read `scratch/agent/SOAK-RESULTS.md`** (read list #3, tail -20) for how many of the 6
   `m5step5_rate_N` recipes have run and their `rc` values. `rc=1` means a `[CRASH]` marker fired
   somewhere in that run — a family #3 candidate if it fired before title (check the log). `rc=0`
   means no crash marker; it does NOT mean "no stall" (family #4 is a stall, not a crash marker).
2. **For every completed run, regardless of rc**, open its full log in
   `scratch/agent/soak_results/m5step5_rate_N_<timestamp>.log` (the recipe's own stdout, which
   includes its printed `last_vi:`/`last_vi_fs_decision:`/`last_drain_or_dma:` summary lines) —
   these alone may be enough; if more detail is needed the underlying game log is at
   `scratch/s73_post_a_scene/m5step5rateN/run.log` (grep, don't read directly — multi-MB). Check
   whether VI progressed normally (0->320->640, ~2.2s, matching s340's baseline) and whether the
   post-mission-launch hold shows the audio/DMA counters still incrementing at the tail (live) or
   frozen (a family #4 stall candidate).
3. **If all 6 have run**: compute the observed family #3 rate (crashes with a pre-title `[CRASH]`
   marker / 6) and compare against the ~12-21% historical baseline (docs/M5-AUDIO-PLAN.md §3). Check
   whether any run shows a genuinely frozen (not just benign-plateaued per s339/s340's characterization)
   VI/audio state for family #4, historically "every soak died earlier" before reaching this phase.
   - If 6 runs isn't enough for a confident read (wide baseline range, small N), queue another batch
     of the same recipe (copy `m5step5_rate_1.sh`'s pattern, bump the label/filename) rather than
     switching approach — this is explicitly a "budget accordingly" multiple-soaks question, not a
     3-strikes-and-pivot one, per the M5-AUDIO-PLAN's own framing.
   - If a clear rate difference from baseline emerges (HB: increase, or HC: decrease per the prior
     framing in CURRENT-TRUTH item -197/PORTING-STATE Sessions 340-341), characterize the specific
     crash signature and its numerator/denominator before writing it into CURRENT-TRUTH — this is the
     actual payoff/risk the whole M5 plan was measuring.
   - If the rate looks unchanged from baseline (HA): step 5 closes, M5-AUDIO-PLAN moves to step 6
     (validate real PCM reaches SDL, not just that the guest stopped hanging — see
     `docs/M5-AUDIO-PLAN.md` §4 step 6 for what's needed there).
4. **If none of the 6 have run yet** (loop hasn't reached a between-iteration slot, or all queued
   recipes are still pending): do NOT re-run the recipes inline — the loop drains the queue
   automatically between iterations regardless of what this session does. Pull forward other backlog
   instead (e.g. the sanctioned fixup_game_funcs.py BREADCRUMB10+ backport mentioned in
   CURRENT-TRUTH's USER DIRECTIVE item 30) while the queue drains in the background across iterations.

HYPOTHESIS-ID: m5-audio-destub-step5-crashrate-comparison (2nd iteration if this is picked up
again without new soak data since s341; unchanged from s341 — same investigation thread, no pivot).

## Environment notes (carried forward — see s327-341 for full detail)

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
  is required — see project rule 10 / CLAUDE.md). Log lands at
  `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly (multi-MB/million-line
  files).
- The soak driver's own "wait for VI width 1024" phase gate times out at 600s and exits 5
  (INCONCLUSIVE) for any scene that doesn't reach the title screen within the hold — this is NOT a
  crash signal by itself; check the log directly for crash/SIGSEGV/SIGTRAP/fatal/abort markers and
  the `[vi-fs-decision]`/`[dma-ring-consumer]`/audio-synth counters to confirm liveness before calling
  a phase-timeout a stall.
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- Scratch files outside the three allowed working directories (e.g. `/tmp/...`) are blocked by the
  sandbox — write throwaway analysis/poll scripts under `scratch/` in this repo instead.
- `bash -n <script>` was denied by this session's permission gate even as a pure syntax check (not a
  destructive command) — if a future iteration needs to lint a soak-queue recipe before enqueuing it,
  visual review is the workaround; don't assume plain `bash` invocations are freely permitted.
