# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s587 recap (read this first)

| H | Result | Evidence |
|---|--------|----------|
| H8a E7 inject keeps syncs | **CONFIRMED** | r3: 388 dual syncs #5300–#5687 (238 sticky + 150 inject) |
| H8c mode-1 hangar flood | **REFUTED** | hangar e9_b 75/75; inject only @0x76DF60 |
| H8c broad last_fs | **CONFIRMED** (r1) | flood @0x4B8408 |
| In-place E9 rewrite | **REFUTED** | r2 UJ 2080 after inject; r3 non-mut UJ 0 |
| H8d force recovery makes inject redundant | **REFUTED for E7** | inject covers full E7 window before F3 |
| F3/FD residual | **OPEN** (-357) | inject stops at E7→F3; zero run 250 to hold-kill; fs stuck 4717 |

Landed: `ROGUESQ_FS_PIPE_INJECT` mode 1 non-mutating scratch `0x7FFF80` in
`src/rsp/dpc_bridge.cpp` (default OFF). Artifact: `s587_fs_pipe_inject_r3`.

## This iteration's work unit

**Item -357: residual F3/FD FULL_SYNC starvation after E7 inject.**

When sticky cell leaves PIPE (`E7→F3→FD`), `FS_PIPE_INJECT` no longer fires and
runner `syncs` dies again while GFX continues (r3 zero run #5688+).

### Hypotheses
- H9a: Task-end synthetic FULL_SYNC from scratch `0x7FFF80` whenever
  `g_task_rdp_fullsyncs==0` after dual has ever been seen collapses the F3/FD
  zero-tail (fix broken `rsp_force_fullsync` which re-submits last_fs=F3/FD).
- H9b: Only synth when slot head is F3/FD (not global zero-sync) avoids
  re-introducing hangar/action_queue issues.
- H9c: Force-path natural recovery cells (`0x76A838` s584 / `0x76B768` s586)
  still appear if hold is longer — inject did not block them; r3 kill was early.
- H9d: Extending PIPE inject to "any non-E9 at slot while last_fs==slot" is
  enough (treat F3/FD size-8 slot submits like PIPE).

### Discriminating measurement (one build, force dual, HOLD_S≥60)
1. Prefer H9a or H9d gated env (e.g. `ROGUESQ_FS_PIPE_INJECT=1` extended, or
   `ROGUESQ_FS_TASK_END_INJECT=1`).
2. Same-run: hangar late e9_b GREEN; dual E7 inject still 150; **post-F3
   `syncs≥1` for ≥200 tasks** (or zero-tail length ≪ s577's 772 / r3's 250).
3. UJ=0 CRASH=0; log synth count after F3 edge.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# after code + rebuild:
env PROBE_MODE=start_only HOLD_S=60 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE5_START=40 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s588_fs_f3_residual 5 12
```

### Outcomes
- post-F3 syncs recover + hangar green + UJ0 → ship candidate (consider default ON)
- recovery cells appear without extra inject (H9c) → inject E7-only is enough; longer hold
- UJ/hangar flood → tighten gate

### Do NOT
- Re-litigate H7/H8a E7 inject.
- Ship default-ON until F3 residual measured clean.
- Chase leave-path crashes.
