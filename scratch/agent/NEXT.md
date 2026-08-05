# NEXT work unit

## s332 closed the previous hypothesis — start here

s332 runtime-REFUTED `HYPOTHESIS-ID m5-audio-destub-waitformusyx-secondspin-hang` (CURRENT-TRUTH item
-189, full detail `PORTING-STATE` Session 332): the `[waitmusyx-spin2]` diagnostic fired exactly once,
with `flag=0` — the loop falls through immediately and never blocks. The `reapplyDisplayMode` VI=640
graphics-task-submission stall (first found s329, still fully reproduces — s332's soak hit it again at
2.2s with 0 crashes across 1.28M log lines) is **not** caused by that spin loop. Root cause is still
open. Gate is back at the full force-zero baseline (`audio gate patched x2`), tree rebuilt clean.

## New hypothesis thread: is `reapplyDisplayMode` (or its guard) even reached during the stall?

s330's own source-read named this as the fallback if the spin-loop hypothesis didn't pan out (it
didn't): `reapplyDisplayMode`'s call (`funcs_0.c:1752`) is gated by a 3-condition guard
(`funcs_0.c:1703-1731`) re-evaluated every frame. Nobody has yet measured, at runtime, whether that
guard actually trips true during the stall, whether the call happens every frame once it does, or
whether `reapplyDisplayMode`'s own body ever returns. s330 also established (source-read, not yet
runtime-checked) that `runVideoFrameTick` contains no direct call into graphics-task submission — the
real producer runs on a separate native `gfx_thread` (`rt64_state.cpp:2945`) — so a game-thread stall
ANYWHERE in its per-frame tick (not necessarily inside `reapplyDisplayMode` itself) could starve that
thread by simply never returning to the code that signals/advances it.

## Hypotheses (pick the discriminating probe)

1. **Guard never trips**: `funcs_0.c:1703-1731`'s 3-condition guard never evaluates true during this
   soak's timeline, so `reapplyDisplayMode`'s call site is never reached at all, and the real stall
   has nothing to do with `reapplyDisplayMode` — it's elsewhere in `runVideoFrameTick`'s per-frame
   body, or even outside the game thread entirely. Discriminator: a fire-once-then-counting marker
   right at the call site (`funcs_0.c:1752`) — if it NEVER fires during a stalled soak, this wins.
2. **Guard trips, call happens, but `reapplyDisplayMode`'s own body (`funcs_23.c:9805-10097`) hangs
   internally** — entry fires but exit never does, or the call count freezes after some N. This
   would mean the game thread is parked *inside* `reapplyDisplayMode` itself, not downstream of it.
   Discriminator: paired entry/exit (or per-call) counters on the function body — entry count
   climbing while exit count stays flat (or both freeze together at some N) confirms this.
3. **`reapplyDisplayMode` runs to completion every frame with no internal hang, and the stall is
   genuinely downstream/elsewhere** — either later in `runVideoFrameTick`'s own body (after the
   `reapplyDisplayMode` call returns), or entirely outside the game thread (the native `gfx_thread`/
   `vi_thread` machinery itself wedges independent of anything the game thread does). Discriminator:
   if hypotheses 1 and 2 are both refuted (call site fires steadily, entry/exit counts both climb
   together with no growing gap), the stall must be downstream — next step would be a per-frame
   top-of-`runVideoFrameTick` counter cross-referenced against the native `gfx_thread`'s own
   task-submission attempt counter (already exists as `[vi-fs-decision]` in the log) to see whether
   the GAME thread is still ticking frames at all vs. genuinely stopped.

## The work unit

1. Add 2-3 diagnostics (`N64Recomp/fixup_game_funcs.py`, same convention as
   `[waitmusyx-spin2*]` — single shared env var e.g. `ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1`,
   default off, hard-capped prints):
   - a fire-once-then-periodic marker at `reapplyDisplayMode`'s call site (`funcs_0.c:1752`,
     inside the 3-condition guard's taken branch) — settles hypothesis 1.
   - paired entry (function top) and return (every return point, or at minimum the common
     fall-through) counters on `reapplyDisplayMode`'s own body (`funcs_23.c:9805-10097`) — settles
     hypothesis 2 (entry count vs exit count divergence).
   - OPTIONAL if budget allows: a per-frame counter at `runVideoFrameTick`'s own top (may already
     exist via `[synth-entry]`'s sibling instruments from the s310 AUDIOTICK_TRACE family — check
     before adding a duplicate) to have a same-run reference for "is the game thread still ticking
     frames at all" independent of the audio-gate diagnostics.
2. Regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → cmake — delete `RecompiledFuncs/*.c`
   first), narrow the audio-gate force-zero regex to `reapplyDisplayMode`'s site only again
   (`0x8008EB40`-only match, same B40-only narrowing s329/s332 used — confirm `audio gate patched x1`
   in the fixup report), rebuild.
3. Soak once with `scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`HOLD_S=600`, plus the new
   env var). Expect the same VI=640 phase-timeout INCONCLUSIVE symptom at 600s; the new diagnostics'
   fire pattern is the actual result.
4. Whichever hypothesis wins, close it in the same iteration (do not leave it open) — this is a
   reachability/location probe, not a fix attempt; a fix should wait for a confirmed stall location.
5. Revert the gate to the full force-zero baseline (`audio gate patched x2`) and rebuild clean before
   ending, per every prior session's convention.

## Environment notes (carried forward — see s327-332 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=600 ROGUESQ_LOG_<NEWVAR>=1 zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>`
  (the `env` prefix is required — see project rule 10, a bare `VAR=1 zsh ...` is denied by the
  permission prefix-matcher). Run it via Bash `run_in_background: true`, then block on it in the
  SAME turn — a `Monitor` call alone does NOT satisfy the Stop-hook gate if the turn ends before the
  soak completes; the gate re-fires on every attempted stop while `scratch/agent/STATUS` is
  `WORKING`. The pattern that worked in s332: launch in background, then a **foreground** Bash call
  `while kill -0 <PID> 2>/dev/null; do sleep 5; done` with a timeout comfortably over 600s (get the
  PID from the background launch's own stdout, e.g. `pid <PID> out=...` printed by
  `run_mission_keys.sh`). Log lands at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't
  read it directly (s332's was 1.28M lines / 60+ MB).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim. `cd <dir>` as its own standalone Bash call, then a separate command in that directory,
  avoids the "compound cd + redirection" approval prompt a single `cd x && cmd > file` triggers.

HYPOTHESIS-ID: m5-audio-destub-reapplydisplaymode-reachability (1st of 3 iterations — new thread,
opened this session after item -189 closed the prior one).
