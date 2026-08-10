# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s591 recap (read this first)

| H | Result | Evidence |
|---|--------|----------|
| H12a thr-11 mesg/audio wait | **REFUTED primary** | infinite recv loop; external stop; audio-drain only at thr-10 restart iters=1 |
| H12b thr-11 guest crash | partial noise | s590/s591 die thr-11 live; s589 thr-11 completes |
| H12c FULL_SYNC health gates thr-11 destroy/sec4 | **SUPPORTED** | s577 Δ266; s589 Δ2851+recovery→sec4; s591 0 recovery→no destroy |
| H12d thr-12 flag beyond sec4 | untested | s589 sec4 then initSceneForMission crash pre thr-12 |
| thr-11 is progress worker | **REFUTED** | save service; destroy ↔ sec4 scene transition |

Artifact: `scratch/s73_post_a_scene/s591_thr11_pipeline/ANALYSIS.md`.

## This iteration's work unit

**Item -361: post-sec4 thr-12 create vs `initSceneForMission` crash.**

Need a force run that reproduces s589 (thr-11 destroy + sec4). Then
discriminate: does thr-12 appear on a crash-free sec4 hold, or is thr-12
gated beyond sec4?

### Hypotheses
- H13a: recovery is intermittent; retry case6+inject HOLD≥90 until sec4 (s589 shape).
- H13b: once sec4 lands, thr-12 creates within ~same gap as s577 (~few hundred thr-resume) unless crash intervenes.
- H13c: `initSceneForMission`/`coalesceFreeHeapBlocks`/`0x8000247c` systematically blocks thr-12 on force path (not intermittent noise).
- H13d: thr-12 create is independent of thr-11 destroy timing once sec4 is loaded.

### Discriminating measurement
1. Arm always-on: thr-create/destroy, overlay start-match, inject, recovery cell.
2. Same recipe as s589/s591 until **post-exit sec4** observed (positive control for H13a).
3. From sec4 line: wall/task delta to thr-12 create (entry 0x800495FC id≥12) vs crash.
4. Positive controls: case6-force-start; hangar-sel+state8; inject n>0; if recovery @0x76B768 then expect thr-11 destroy.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Prefer 1–2 force soaks until sec4 (do not babysit if queueing):
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s592_sec4_thr12 5 12
# Offline gate: post hangar-sel [overlay] section 4; thr-destroy id=11; thr-create entry=0x800495FC after that
```

Optional soak_queue recipe if first attempt fails recovery (s591 shape): same env, tag `s592_sec4_thr12_retry`.

### Outcomes
- sec4 + thr-12 + no crash → pipeline clear; next = sec2 / in-mission
- sec4 + thr-12 + later crash → thr-12 not the gate; follow thr-12→sec2
- sec4 + crash before thr-12 (s589 repeat) ≥2/2 → H13c; open coalesce/initScene audit only if same-run sec4 positive control
- no sec4 after 2 recovery-fail runs → recovery reliability is the work unit (back to H10a rate)

### Do NOT
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Reactive single-crash chase on findLookupEntry / trackResourceList without sec4.
- Default-ON FS_PIPE_INJECT without thr-12/sec2 on a surviving path.
