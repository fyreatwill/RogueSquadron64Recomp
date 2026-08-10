# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s595 recap (read this first)

**Step 0 first**: `wc -c < docs/CURRENT-TRUTH.md` was 60008 at the end of s595
— over the 60000 maintenance trigger. If it's still over when you start,
THIS iteration is a MAINTENANCE iteration per ITERATION.md — do that before
anything below.

Item -361 (coalesce R2 guard fix, landed s593) is still awaiting its first
discriminating live re-verify. s595 consumed the queued `_c`/`_d` retries:

- `_d`: pre-engagement null (`case6=0`), same shape as prior ones.
- `_c`: **real progress** — reached `case6=1 hangar-sel=1`, full
  `FS_PIPE_INJECT` residual coverage (n=200+, E7→F3→FD, matches s588's H9d
  model exactly) — but the FULL_SYNC recovery cell `0x76B768` **never
  fired** in this run. Without recovery, thr-11 never destroys (H12c), sec4
  never gets its post-exit 2nd hit, and the run drifts until an unrelated
  crash (this time item -347's signature, see below).
- Tally: **7 consecutive non-discriminating attempts** for the R2 fix
  itself (`coalesce_guard2_r2=0` on every one). Per iron rule 8, s595
  redesigned instead of re-queuing blind: `HOLD_S` raised 90→210 (recovery
  is intermittent — s589/s592a fired, s591/s594_c did not — so give it more
  wall-clock exposure per run). Queued `s595_coalesce_r2_verify_e`/`_f`,
  currently sitting in `scratch/agent/soak_queue/` for the loop.

**Also s595: item -347 reframed.** Its 3rd occurrence (same
`last-guest-pc=0x80010134`, `transformLightByType+256`) turned out to be an
instrumentation-coverage artifact, not a recurring bug — `transformSceneLights`/
`transformLightByType` have zero `g_rs64_last_guest_pc` tracking (only
52/2499 functions do, all guard-campaign-associated), so the value freezes
at the caller's stub regardless of the true fault site. Filed, not
escalated, no guard written. New method-trap entry in CURRENT-TRUTH:
the "watch for the Nth occurrence" heuristic only has teeth when the
reporting function is in the guard-audited set — worth keeping in mind if
you're about to escalate any OTHER watch-listed breadcrumb
(-323/-324/-325/-326/-330/-332/-333) on repeat-count alone; none of those
were re-audited this session for their own instrumentation coverage.

## This iteration's work unit

**Item -361 continued: consume the queued s595 retries.**

1. Read `scratch/agent/SOAK-RESULTS.md` tail for `s595_coalesce_r2_verify_e`
   / `_f` lines first, then the full gate-summary line at the end of each
   `scratch/agent/soak_results/s595_coalesce_r2_verify_{e,f}_*.log`.
2. If a run shows `sec4>=2` (real post-exit reload) — this is the
   discriminating data point:
   - `coalesce_guard2_r2>0` AND `crash=ok` → **FIX CONFIRMED**. Check for a
     3rd `thr495FC_creates` (thr-12 for the mission, beyond the 2 early
     ones every run shows) or `sec2>0`. Close item -361's crash half; open
     thr-12/sec2 as the new frontier.
   - `coalesce_guard2_r2>0` AND `crash=CRASH` → bail value takes the wrong
     branch after all — recheck the exit-path register-use analysis in
     `PORTING-STATE.md` Session 593 against this run's actual crash PC.
   - `coalesce_guard2_r2=0` AND `crash=CRASH` at `0x8000247c` again → the
     patch did not take. Check `fixup_game_funcs.py`
     (`~/Documents/Tools/N64Recomp`) for the item -361 patch block, re-run
     the regen pipeline, verify the fixup report shows `x1` with no silent
     "REFUSING to run" sentinel.
   - `sec4>=2` but `recov76B768~=0` (reached post-exit sec4 WITHOUT
     recovery firing first) — new data point, note it; would mean sec4 and
     recovery are less coupled than H12c/H13c assumed.
3. If both `_e`/`_f` are again non-discriminating (pre-engagement null OR
   reached-but-no-recovery): this is 9 consecutive attempts. The `HOLD_S`
   axis has now been tried at 90 and 210 without closing the gap on its
   own — do NOT raise `HOLD_S` a 3rd time blindly. Switch redesign axis:
   either (a) a pre-hangar stabilization pass to cut the pre-engagement
   noise-death rate so more runs even reach case6, or (b) test whether a
   natural (non-force) double_start path reaches sec4 more reliably than
   `ROGUESQ_FORCE_CASE6_START` — both were listed as untried options as of
   s594 and neither has been attempted yet.

### Do NOT
- Treat a `sec4=1`-only, `case6=0`, or reached-but-no-recovery null run as
  evidence about the fix (iron rule 1) — only a run that reaches `sec4>=2`
  with the guarded code path live counts.
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-litigate the s354-366 arc's FIRST guard/bail — only the NEW `_R2_`
  site is open here.
- Chase item -347/-331/-306 reactively — all are filed breadcrumbs,
  watch-only (and -347 specifically is now reframed as likely
  non-diagnostic, see above).

### Exact commands (if no queue result to consume)
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=start_only HOLD_S=210 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s596_coalesce_r2_verify4 5 12
```
