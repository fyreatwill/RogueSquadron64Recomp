# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s592 recap (read this first)

| H | Result | Evidence |
|---|--------|----------|
| H13a path-to-sec4 intermittent | **SUPPORTED (path-gate)** | s592 0/2 never armed case6/hangar-sel/inject |
| H13b thr-12 soon after sec4 | untested | no post-exit sec4 |
| H13c initScene blocks thr-12 systematically | untested | s589 still sole sec4 data point |
| H13d thr-12 indep of thr-11 destroy | untested | |

s592 crashes (pre-exit hangar noise):
- s592: `reserveAndEmitDLEntry+18192`/`0x8000ce54` state=6
- s592_r2: `beginFrameDLChunk+46800`/`0x8000afa0` state=5 (**-338 4th**)

Artifact: `scratch/s73_post_a_scene/s592_sec4_thr12/ANALYSIS.md`.
Queued: `scratch/agent/soak_queue/s592_sec4_thr12_{a,b}.sh` (loop between iters).

## This iteration's work unit

**Item -361 continued: land post-exit sec4, then thr-12 vs crash.**

Consume any new SOAK-RESULTS lines first. If a queued soak already hit
sec4 + thr-11 destroy, skip re-running and analyze thr-12 offline only.

If no sec4 yet: run 1 force attempt (do not babysit a 3rd same-session retry if
a queue is armed — prefer offline analysis of a/b results). If a/b not yet run
by the loop, run one manually:

### Hypotheses (unchanged)
- H13a: keep retrying until sec4 (s589 shape).
- H13b: thr-12 within ~few hundred thr-resume of sec4 if no crash.
- H13c: initScene/coalesce systematically blocks thr-12 on force (≥2/2 sec4 holds).
- H13d: thr-12 independent of thr-11 destroy once sec4 loaded.

### Discriminating measurement
1. Positive controls same-run: case6-force; hangar-sel+state8; inject n>0;
   recovery @0x76B768 (expect thr-11 destroy when recovery fires).
2. Post hangar-sel **second** `start-match: section 4` (post-exit; ignore early
   cinematic sec4).
3. After that sec4: thr-create `entry=0x800495FC` (any id) vs CRASH before it.
4. Wall/task delta sec4→thr-12 if thr-12 appears.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Prefer consume SOAK-RESULTS; only if empty/failed:
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s593_sec4_thr12 5 12
```

### Outcomes
- sec4 + thr-12 + no crash → pipeline clear; next = sec2 / in-mission
- sec4 + thr-12 + later crash → thr-12 not the gate; follow thr-12→sec2
- sec4 + crash before thr-12 (s589 repeat) ≥2/2 → H13c; open coalesce/initScene
  audit only with same-run sec4 positive control
- still 0 sec4 after queue a+b + one more → escalate path reliability (hangar
  pre-exit crash rate); optional -338 source-trace only as systematic class

### Do NOT
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Reactive single-crash chase on -338 / reserveAndEmitDLEntry without sec4.
- Default-ON FS_PIPE_INJECT without thr-12/sec2 on a surviving path.
