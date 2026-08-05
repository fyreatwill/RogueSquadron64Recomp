# NEXT work unit

## s343 confirmed title-reach is restored, but found a NEW crash in `tickWrappingTimerAccumulatorList` one stage later — read this first

s343 (`HYPOTHESIS-ID m5-audio-destub-reapplydisplaymode-title-block`, CLOSED — confirmed, not
refuted) reverted `reapplyDisplayMode`'s gate back to force-zero (kept `setDisplayMode`'s reversal)
per s342's plan. **HA confirmed**: `phase width=1024 reached after 45.5s` (matches the 44.6-46.2s
baseline), 4 `[keys]` presses fired — title/menu genuinely reached for the first time since s328.
But the very next soak stage (12s "wait for SELECT YOUR CRAFT stable" window) died: signal 6
(abort), 36 `[CRASH]` lines, `last-guest-pc=0x80054744` — a compiler `break 7` div-by-zero trap
inside `tickWrappingTimerAccumulatorList` (a.k.a. `BREADCRUMB9`, PORTING-STATE s272-291), a
DIFFERENT signature from that function's previously-catalogued `0x80000004` near-null-pointer crash.
Full mechanism trace and root cause: `PORTING-STATE` Session 343, `docs/CURRENT-TRUTH.md` item -199.

**The open question**: this soak's gate config is byte-identical to s328's `step4gate2` baseline
(0/2 crashes across 2 soaks) — confirmed via direct `funcs_23.c` comparison. Single-source (1
observation this session). Two queued confirmation soaks
(`scratch/agent/soak_queue/s343_tickwrap_divzero_confirm{1,2}.sh`) should have run by now — **read
`scratch/agent/SOAK-RESULTS.md`'s tail for their verdicts before doing anything else.**

## The work unit: fold in the confirmation verdicts, then branch

**Step 1** (always do this first): `tail -10 scratch/agent/SOAK-RESULTS.md`, then read the full logs
at `scratch/agent/soak_results/s343confirm{1,2}_*.log` (`grep -a 'VERDICT\|crash_markers\|last_guest_pc'`
on each). Fold the verdicts into `docs/CURRENT-TRUTH.md` item -199 and this file's hypothesis
regardless of outcome.

**Branch A — both confirmations CRASH_DETECTED (2/2, now 3/3 combined with s343revert)**: this is a
real, reliably-reproducing regression, not the s328-baseline nondeterminism explanation. Land a guard
mirroring the established idiom (`fixup_game_funcs.py:939-949`, `musyxKeyOnVoice`'s break-6/7 → early
`return`; `evalCubicSplineAtTime`'s zero-width-interval → `f4.fl=0`): match
`do_break\(2147829572\);` in `tickWrappingTimerAccumulatorList`'s body and replace with a bail that
sets `hi = 0` (the `divu` remainder, consumed at `L_80054748: mfhi $v1`) then falls through to
`L_80054748`, instead of aborting — read `funcs_11.c:15310-15360` again first to confirm `hi`'s
downstream use before picking a substitute value; don't guess blind on a single crash observation
without also checking what `hi=0` does to the caller (this may need per-call-site testing, since the
comment at `main_overlay.txt:2031` says 3 callers in `funcs_11/32/33`). Regen, rebuild, one soak
past the SELECT YOUR CRAFT stabilization window to confirm the crash is gone and craft-select/mission
launch now progress further than ever reached in this arc.

**Branch B — both confirmations CLEAN (0/2)**: this crash is a rare flake (1/3 hit rate), similar to
`BREADCRUMB9`'s own historically low hit rate on its other signature — not worth a blind guard. Return
to M5-AUDIO-PLAN step 5 (crash-family #3/#4 rate comparison, `docs/M5-AUDIO-PLAN.md` §3) now that
title-reach is genuinely restored. Write FRESH soak recipes (do not resurrect
`soak_queue/cancelled/m5step5_rate_3..6.sh` — their `STICK_SCHEDULE`/`HOLD_S` values need re-checking
now that the phase they target is actually reachable) sized so the inner phase-gate timeout leaves
real margin under the loop's 600s hard cap.

**Branch C — mixed (1/2)**: treat as still-open: queue one more confirmation before deciding between
A and B (odd tie-breaks in a 2-observation sample aren't enough per Iron Rule 4 — need a 3rd before
concluding either way).

HYPOTHESIS-ID: m5-audio-destub-tickwrap-divzero-craftselect (1st iteration; new thread, pivoted from
the now-CLOSED m5-audio-destub-reapplydisplaymode-title-block).

## Environment notes (carried forward — see s327-343 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`.
- Current gate state (as of s343, unchanged unless Branch A is taken): fixup regex at
  `fixup_game_funcs.py` ~line 263 is `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode`
  (`0x8008EC88`, force-zeroed); `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed. Verify via
  `funcs_23.c: audio gate patched x1` in the fixup report and a direct grep of the regenerated
  `funcs_23.c` for both addresses.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> <VARS> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix
  is required — see project rule 10 / CLAUDE.md). Log lands at
  `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly (multi-MB files).
  `run_mission_keys.sh`'s wait-for-`VI=1024` phase gate has a HARDCODED 600s internal timeout
  independent of `HOLD_S`, separate from the loop's own 600s hard cap on queued recipes — size queued
  `HOLD_S` values with real margin under both.
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- `bash -n <script>` was denied by this session's permission gate even as a pure syntax check — if
  linting a soak-queue recipe, visual review is the workaround.
