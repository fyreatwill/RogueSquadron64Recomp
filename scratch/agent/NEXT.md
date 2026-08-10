# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s586 recap (read this first)

| H | Result | Evidence |
|---|--------|----------|
| H7a | **CONFIRMED** | E7→E9 #5309 and E9→E7 #5547 both `task_delta src=rsp_lle`; stop also `write lle_depth=1` + `slot_op_change op=27 src=rsp_submit` |
| H7b | **REFUTED** | 0 `intertask_delta` whole run |
| H7c | **REFUTED** | real RDRAM mutation under LLE before filtered PIPE submit |
| H7d | open | force path only |

Sticky: 238 E9 task_end, 0 mid-writes. Instrument GREEN. Artifact:
`scratch/s73_post_a_scene/s586_hsync4_writer_r2/run.log`.

## This iteration's work unit

**Product bridge response to sticky-cell PIPE overwrite (item -356).**

When Factor5 LLE writes E7 (PIPE_SYNC) into the shared 8-byte cell that was
sticky FULL_SYNC, dpc_bridge filters size-8 op 0x27 and runner `syncs` dies
while GFX continues. Writer is known (RSP); fix is bridge-side.

### Hypotheses
- H8a: Injecting one FULL_SYNC (or counting a synthetic sync) when filtering
  size-8 PIPE at `last_fullsync_addr` keeps dual-phase `syncs>0` past E9→E7
  without visual regression.
- H8b: Only inject when the filtered PIPE is the *sole* size-8 submit that
  task (avoids flooding mid-stream PIPEs).
- H8c: Broader "never filter size-8 PIPE" regresses hangar (action_queue flood).
- H8d: Force dual recovery at `0x76A838` already restores syncs later — inject
  only needed for open natural plateau (H6c); measure whether inject shortens
  zero-tail or is redundant on force path.

### Discriminating measurement (one build, one force dual)
1. Land gated fix: e.g. `ROGUESQ_FS_PIPE_INJECT=1` default OFF for A/B, or ON
   if already proven safe on hangar control in same run.
2. Same-run: hangar late e9_b/syncs GREEN (no flood), dual sticky E9 window
   still forms, then after E9→E7 edge runner `syncs` stays ≥1 (or zero-tail
   length collapses vs s586 baseline ~150 E7 tasks then F3/FD).
3. Log inject count + first/last inject task.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# after code + rebuild:
env PROBE_MODE=start_only HOLD_S=45 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE5_START=40 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s587_fs_pipe_inject 5 12
```

### Outcomes
- dual keeps syncs after E9→E7 + hangar control green → H8a/H8b path works
- hangar flood / present glitch → H8c, tighten gate
- inject fires but force still recovers only via 0x76A838 → measure natural next

### Do NOT
- Re-litigate H7a/b/c.
- Chase leave-path crashes.
- Ship inject without same-run hangar positive control.
