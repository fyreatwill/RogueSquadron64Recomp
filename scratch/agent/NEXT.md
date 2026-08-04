# NEXT work unit — M5-AUDIO-PLAN.md step 4: reverse `initMusyXEngine`'s gate-byte site

## Context (read `docs/M5-AUDIO-PLAN.md` §4 step 4, and §1 for the 3 gate-byte sites — condensed
pointer, not a re-derivation)

s300 executed M5 steps 1-2 (confirmed `M_AUDTASK` dispatches continuously regardless of the gate,
landed `factor5_ucode_b` behind `ROGUESQ_AUDIO_UCODE`, default off). s301 executed step 3: landed and
validated the `waitForAnyAudioSlot` bounded-timeout guard (fire count 0/3 across 3 soaks, 7 legitimate
calls each converging in 1 iteration — the guard is a confirmed-inert safety net). Full detail:
`PORTING-STATE` Sessions 300-301.

**Do not re-run steps 1-3's soaks** — done, evidence recorded. This session's work is step 4 only.

## The work unit

Three sites force-zero the audio-engine-enable gate byte (`0x800A0F50`), added as a deliberate fix
(`N64Recomp/fixup_game_funcs.py:94-101`, comment: "force audio-engine-disabled (MusyX stubbed;
spin-wait wedges coop scheduler)"): `initMusyXEngine`, `setDisplayMode`, `reapplyDisplayMode`. Step 4
reverses these **one at a time**, starting with `initMusyXEngine` (earliest in boot, so a regression
is caught before menu/gameplay complexity compounds it) — i.e. remove/bypass that one force-zero patch
so the guest's own `sb $v0,...` write (real init success value) takes effect, while leaving the other
two sites force-zeroed for now.

**Why this specific site first**: `initMusyXEngine` runs once at boot, before the scheduler-wedge
failure mode (crash family #1) had its documented occurrence — reversing it first isolates whether
*this* site alone is sufficient/safe before touching the other two (which run on every display-mode
change, a much hotter path).

## Validation soak

Per the plan: watch specifically for crash family #1's exact signature (`waitForMusyXAudioTaskDone` /
`shutdownAudioEngine` hang, boot-time scheduler wedge) recurring — this is a confirmed historical
failure mode being deliberately re-exposed, not a hypothetical guess. Arm the full existing diagnostic
set (`scratch/s73_post_a_scene/run_waitforslotguard1.sh` is the current reference — copy its env-var
block, or use `run_dequeuearg1.sh`) plus `ROGUESQ_AUDIO_UCODE=1` (step 2's toggle — real ucode timing
is what step 4 exists to test against) and the step-3 guard's `ROGUESQ_LOG_WAITFORSLOT_GUARD=1`
(already in `run_waitforslotguard1.sh`).

**Discriminating outcomes**:
1. Crash family #1's exact signature recurs → the ucode from step 2 completes dispatch (`Broke`/
   return) but doesn't actually decrement the real countdown the guest spin-waits on — needs a
   source-level fix in the ucode's task-completion signaling, not a gate re-revert. Do NOT just
   re-force the gate zero and call it done — that's reverting step 4, not completing it.
2. 2 clean soaks, no family #1 recurrence → reverse `setDisplayMode`'s site next (same validation),
   then `reapplyDisplayMode` last — do NOT reverse all 3 in one session; one site, one validation soak
   per session per the plan's incremental design.
3. A different, new crash signature appears → do not immediately attribute it to family #1 or dismiss
   it as baseline noise (per s301's method: check whether the entry-diagnostics for the crashing
   function actually fired before the crash — a legitimate call vs. a corrupted-jump landing
   mid-function are distinguishable exactly the way s301 distinguished them). Note it in the ledger
   either way; don't guess.

## Environment notes (carried forward, all still valid)

- Regen order still applies if `N64Recomp/fixup_game_funcs.py` changes: `cd N64Recomp &&
  ./build/N64Recomp rogue_squadron.toml && python3 fixup_game_funcs.py`, then from repo root
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`.
- `N64Recomp/fixup_game_funcs.py` is NOT git-tracked in the `N64Recomp` tool checkout itself (confirmed
  s301 — `git status` there shows it `??`/untracked, same for `RecompiledFuncs/`) — the durable record
  is this project's own `PORTING-STATE.md`/`CURRENT-TRUTH.md` plus the physical file on disk in that
  checkout, not a git commit in `N64Recomp`. No `submodule-patches/export.sh` applies here — that's
  only for `lib/N64ModernRuntime` and `lib/rt64`, which this work does not touch.
- Soak driver: `scratch/s73_post_a_scene/run_waitforslotguard1.sh` (new this session; copies the
  established `run_dequeuearg1.sh` env-var block plus `ROGUESQ_AUDIO_UCODE=1` and
  `ROGUESQ_LOG_WAITFORSLOT_GUARD=1`). `HOLD_S`/`PROBE_MODE` env-overridable, phase-gates on VI width
  1024, self-SIGKILLs at the end, prints a `--- summary ---` block. Launch with
  `run_in_background: true`; poll via a `Monitor` grepping the run's own log for `summary|CRASH|done
  wall` rather than foreground-sleeping — this is what s301 used successfully. **One game run at a
  time** — do not launch soaks 2/3 until the prior one's process has actually exited.
- s301 found this project's baseline pre-scene/early-scene crash rate is high enough that even 2-3
  soaks in a row can each die to a *different* pre-existing, unrelated crash class before reaching a
  useful validation window (crash family #3's own SIGSEGV once, the `x0=0x0000000300000000`
  RDRAM-host-base signature once, in 3 soaks). Budget for this: don't treat a single soak's crash as
  informative about step 4's own change without first checking whether the crashing function's own
  entry diagnostics actually fired (the s301 method) — a crash with zero entry-diagnostic lines despite
  resolving inside an instrumented function's byte range is the corrupted-jump/wild-write signature, not
  a legitimate call through that code path.
- `BREADCRUMB12`/`MATEXPIRY_GUARD` thread remains DORMANT — still armed passively in every soak via
  the shared driver. Same decision tree as before (`PORTING-STATE.md` Session 297) if it recurs.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4
