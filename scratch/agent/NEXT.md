# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s596 recap (read this first)

s596 was a MAINTENANCE iteration (`docs/CURRENT-TRUTH.md` was 60008 bytes at
start, over the 60000 trigger). Compacted 683→483 lines (-200 net, exactly
the ADVANCED threshold), 60008→43625 bytes. No conclusions changed — pure
de-duplication against `PORTING-STATE.md`/`PROJECT-OVERVIEW.md`. Full detail:
`PORTING-STATE.md` Session 596.

Before compacting, s596 also consumed the queued `s595_coalesce_r2_verify_e`/
`_f` soaks (both had already run between iterations):
- `_e`: pre-engagement null (`case6=0 hangar-sel=0 sec4=0`), process died
  before reaching VI 1024.
- `_f`: `sec4=1` only — confirmed boot-only overlay-preload noise floor
  (s594), not a real post-exit reload; never reached case6/hangar-sel.

**Tally: 9 consecutive non-discriminating attempts** (s593-s596) for the
item -361 `coalesceFreeHeapBlocks` R2 guard fix — `coalesce_guard2_r2=0` on
every single one; the guarded code path has never executed in a live
re-verify since the fix landed s593. `HOLD_S` has now been tried at both 90
and 210 without closing the gap.

## This iteration's work unit

**Item -361: switch the redesign axis. Do NOT raise `HOLD_S` a 3rd time.**

Two untried options, per s594/s595's own analysis (neither attempted yet):

**(a) Pre-hangar stabilization pass** — most non-discriminating attempts
die on already-catalogued background noise (item -331 2nd occ, item -306,
item -347) *before* the force-exit env even engages. If the pre-engagement
noise-death rate can be cut, more runs will survive to reach `case6=1`.
Start by tallying exactly which breadcrumb killed each of the 9 nulls
(grep `scratch/agent/soak_results/s59{3,4,5}_coalesce_r2_verify_*` +
their linked `scratch/s73_post_a_scene/*/run.log` for the crash line) to
see if one single noise family dominates — if so, that's the one worth a
targeted guard, not a blind stabilization sweep.

**(b) Natural (non-force) double_start path** — `ROGUESQ_FORCE_CASE6_START`
may itself be adding fragility (it forces a state transition the natural
game logic wouldn't take at that exact moment). Test whether a natural
double_start leave sequence reaches sec4 more reliably than the forced
path. This was listed as untried in every session since s590.

Pick ONE, design the discriminating measurement (what result distinguishes
"this redesign helped" from "still noise-gated"), write it into this file's
next revision, then either run it directly (if fast) or queue it to
`scratch/agent/soak_queue/` for the loop to consume.

### Do NOT
- Raise `HOLD_S` past 210 — already tried twice (90, 210) with no effect on
  the recovery-cell-firing rate.
- Treat a `sec4=1`-only, `case6=0`, or reached-but-no-recovery null run as
  evidence about the fix (iron rule 1) — only a run that reaches `sec4>=2`
  with the guarded code path live counts.
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Chase item -347/-331/-306 reactively — all are filed breadcrumbs,
  watch-only.

### Reference: exact command used for prior attempts
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=start_only HOLD_S=210 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s597_coalesce_r2_redesign 5 12
```
For option (b), drop `ROGUESQ_FORCE_CASE6_START` and drive a natural
double_start leave sequence instead (see `PROBE_KEYS`/leave-sequence recipes
referenced in items -359/-590 for the natural path shape).
