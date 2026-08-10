# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s588 recap (read this first)

| H | Result | Evidence |
|---|--------|----------|
| H9d residual non-E9 inject | **CONFIRMED** (drop-return) | r3: 570 continuous dual syncs E9→E7→F3→FD |
| Forward residual | **REFUTED** | r2 UJ 2078 at task ~5880 |
| H9c recovery cells | **REFUTED** this window | 0 at 0x76A838/0x76B768 |
| Hangar flood (mode-1) | **REFUTED** | e9_b 39/40; only miss non-slot fs |
| Dual sticky FULL_SYNC gap | **CLOSED** (-357) | inject n≈300+ covers residual |
| Post-dual empty | **OPEN** (-358) | #5863+ tris=0 syncs=0 ×2085; present FIRE pairs=2 |

Landed: `ROGUESQ_FS_PIPE_INJECT` residual drop+inject (default OFF).
Artifact: `s588_fs_f3_residual_r3`.

## This iteration's work unit

**Item -358: post-dual empty after full sticky inject.**

After H9d covers the sticky cell through FD, dual DLs go tris=0/syncs=0 for
~2k tasks while present keeps FIRE pairs=2 and rdpFs plateaus. Is this
cutscene end → mission load stall, a new FULL_SYNC path gap (slot no longer
size-8-submitted), or a crash-truncated hold (`0x80065e94`)?

### Hypotheses
- H10a: Longer clean hold (or natural leave) advances past empty into
  in-mission / new VI without more inject.
- H10b: Empty tasks still need task-end FULL_SYNC (H9a) because the sticky
  slot is no longer size-8-submitted (inject cannot fire).
- H10c: Empty is crash-bounded noise; dying at `0x80065e94` masks recovery.
- H10d: Visual still shows cutscene content via present swap despite runner
  tris=0 (runner hist incomplete).

### Discriminating measurement
1. Force-exit + `FS_PIPE_INJECT=1` + `HOLD_S=90` with PNG captures after
   dual plateau (phase-gate on VI 640@0x6A2900 + N seconds).
2. Count size-8 submits at `0x76DF60` during tris=0 window (expect 0 if H10b).
3. Same-run hangar e9_b GREEN; UJ=0; note whether rdpFs ever moves after #5863.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE5_START=40 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s589_post_dual_empty 5 12
# offline: slot submit count after last syncs>0; PNG content if harness dumps
```

### Outcomes
- mission/new VI advances → H10a; consider default-ON inject
- slot submits=0 + rdpFs frozen → try H9a task-end inject
- only crash death → file breadcrumb; retry hangarbay-controlled

### Do NOT
- Re-litigate H9d drop vs forward (forward UJ closed).
- Ship default-ON until post-dual characterized.
- Chase leave-path crashes reactively.
