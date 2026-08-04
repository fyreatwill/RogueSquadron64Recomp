# NEXT work unit — M5-AUDIO-PLAN.md step 3: `waitForAnyAudioSlot` bounded-timeout guard

## Context (read `docs/M5-AUDIO-PLAN.md` §3-§4 first — this is a condensed pointer, not a re-derivation)

s300 executed M5 steps 1-2: confirmed `M_AUDTASK` dispatches continuously from boot regardless of the
audio-enable gate byte (both by source trace and a ground-truth `[audtask-dispatch]` counter), and
landed `factor5_ucode_b` behind a new `ROGUESQ_AUDIO_UCODE` env toggle (default off — `musyx_stub`
unchanged unless a human/soak sets it). 2 validation soaks with the toggle on: 0 crashes, 0 hangs,
~1,500+ real ucode dispatches, title+menu+hold all clean. Full detail: `PORTING-STATE` Session 300,
`docs/M5-AUDIO-PLAN.md` §4 step 2.

**Do not re-run steps 1-2's soaks** — they're done and their evidence is recorded. This session's work
is step 3 only.

## The work unit

`waitForAnyAudioSlot` (`N64Recomp/RecompiledFuncs/funcs_15.c:7217`) is a tight, uncapped spin:
`while (!anyAudioSlotActive()) { tickMusyXIfActive(); }`. It's currently benign because the stub
resolves the condition fast (empty voice state converges instantly). Real audio load with real timing
(now reachable via `ROGUESQ_AUDIO_UCODE=1`, and closer once step 4 reverses the gate) makes an actual
hang here more likely, not less — this is a pre-existing landmine independent of the de-stubbing plan,
not a hypothetical.

**Exact loop back-edge** (already-armed diagnostic exists at this site, `ROGUESQ_LOG_AUDIO_DRAIN=1`,
counter `g_audio_drain_iters`, resets to 0 at function entry, increments once per loop iteration —
`N64Recomp/fixup_game_funcs.py:2054-2138`):

```c
    // 0x800668CC: beq         $v0, $zero, L_800668C0
    if (ctx->r2 == 0) {
        // 0x800668D0: lui         $v0, 0x8013
        ctx->r2 = S32(0X8013 << 16);
            goto L_800668C0;   // <-- this is the spin. ctx->r2==0 means "no slot active yet".
    }
```

**Guard**: after `g_audio_drain_iters` (already file-scope, already incremented every iteration right
before this branch) exceeds a bounded cap, force the loop to exit instead of taking `goto
L_800668C0` — i.e. force `ctx->r2` nonzero (or skip the `goto` and fall through to the post-loop code
at `0x800668D0`) so `anyAudioSlotActive()`'s result is treated as "some slot became active" without
actually being true. Pick the cap generously (this loop's steady-state iteration count under the stub
was never measured — `ROGUESQ_LOG_AUDIO_DRAIN=1`'s heartbeat fires every 2000 iterations, so a first
soak with the guard's own fire-counter armed will show the real distribution; start with something
like 500,000 iterations — several orders of magnitude above any plausible legitimate convergence — and
tighten later if the heartbeat data supports it). Log every fire distinctly
(`ROGUESQ_LOG_WAITFORSLOT_GUARD` or similar, new env var per project convention) so a fire is never
silently indistinguishable from a normal exit.

Add the patch to `N64Recomp/fixup_game_funcs.py` near the existing `_audio_drain_loop_patch`
(~line 2087) — same file, same function, same regex-anchor style as every other guard in this file.
Regen: `cd N64Recomp && ./build/N64Recomp rogue_squadron.toml && python3 fixup_game_funcs.py` (no
`make_elf.py` needed, mapping unchanged), then `cmake --build build -j8` from repo root
(`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` prefix for Metal shader rebuilds).

## Validation soak

Per the plan: confirm the guard's own fire-counter stays at **0** in a normal soak (same-run positive
control that it isn't firing spuriously on legitimate convergence) while the existing pre-scene
`waitForAnyAudioSlot`-chain death rate (~12-21% historically, crash family #3) is otherwise unaffected
— this guard is a pure safety net, not expected to change steady-state behavior with the stub still
in place. Run with `ROGUESQ_AUDIO_UCODE=1` armed (step 2's toggle) so the guard gets exercised under
the same real-dispatch condition step 2 validated, not the degenerate stub-only path — the whole point
of landing this guard now is to be ready for step 4's gate reversal, where real timing makes a genuine
hang here plausible for the first time. Arm `ROGUESQ_LOG_AUDIO_DRAIN=1` and the new guard-fire log
alongside the existing full diagnostic set (see `scratch/s73_post_a_scene/run_dequeuearg1.sh` for the
established env-var block to copy).

**Discriminating outcomes**:
1. Guard fires 0 times, crash family #3's rate unchanged from baseline → guard is a correctly-inert
   safety net, ready for step 4. Proceed to step 4 next session.
2. Guard fires (even once) → this loop DOES sometimes fail to converge even under the current stub —
   a genuine, previously-undetected hang risk independent of de-stubbing. Worth its own investigation
   before step 4 (a hang crash family #3 has been silently masking, per M5-AUDIO-PLAN.md §3's
   speculation, becomes newly plausible).
3. Crash family #3's rate visibly drops with the guard armed → the guard itself is the fix for (part
   of) crash family #3, independent of anything else in this plan — note this prominently, it would be
   a real finding, not just risk-reduction plumbing.

## Environment notes (carried forward, all still valid)

- Build: `main.cpp` is this repo's own tree, not `N64Recomp`/`lib/` — a plain
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from repo root
  picks up `src/main/main.cpp` changes with no regen step. Confirmed working this session (s300).
- Soak driver: `scratch/s73_post_a_scene/run_mission_keys.sh` (`HOLD_S`/`PROBE_MODE` env-overridable,
  waits for VI width 1024 phase-gated not stopwatch-gated, self-SIGKILLs at the end, prints a
  `--- summary ---` block with `CRASH:`/`exit=2:`/`UnhandledJump:`/`missing-func:` counts). Launch
  with `run_in_background: true` (Bash tool) or expect auto-backgrounding past 120s; poll via
  `grep`/`tail` on the run's `run.log`, or arm a `Monitor` on the task's own stdout for `done wall=`/
  `CRASH:` lines rather than foreground-sleeping.
- `BREADCRUMB12`/`MATEXPIRY_GUARD` thread is DORMANT, not closed — still armed passively in every
  soak via the shared driver. If a 3rd `BREADCRUMB12` recurrence or a `[matexpiry-guard]` fire shows
  up in `scratch/agent/SOAK-RESULTS.md` at a future session start, fold it into the ledger per the
  decision tree in `PORTING-STATE.md` Session 297 — but do not make it this session's primary work
  unit unless it does.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step3
