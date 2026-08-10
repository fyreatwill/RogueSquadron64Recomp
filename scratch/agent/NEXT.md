# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s590 recap (read this first)

| H | Result | Evidence |
|---|--------|----------|
| H11a case6 edge is section-2 gate | **REFUTED** | FORCE_CASE6 3→5→6→8 + hangar-sel + VI640; 0 sec2 |
| H11b FULL_SYNC/thr health | **SUPPORTED** | thr-11 never finishes (s590); late thr-11→sec4→crash (s589) |
| H11c hangar-sel val=0 hard block | weak | s577 val=0 yet sec2 |
| Section-2 pipeline | **MAPPED** | thr-11 destroy→sec4→thr-12→sec2 (s577) |
| Inject recovery 2nd | **CONFIRMED** | 0x76B768 ×3853 on s590 |

Code: `ROGUESQ_FORCE_CASE6_START` at ACE94 (fixup + funcs_28.c).
Artifact: `scratch/s73_post_a_scene/s590_section2_case6/ANALYSIS.md`.

## This iteration's work unit

**Item -360: thr-11 (saveServiceWorker) stalls post-exit; thr-12 never starts.**

Section 2 only after thr-11 completes → sec4 → thr-12. Force/case6+inject
reach hangar exit but thr-11 does not finish (or finishes then dies before
thr-12). Discriminate wait-on-message vs RDP/FULL_SYNC vs crash-before-done.

### Hypotheses
- H12a: thr-11 blocks on a mesg/event that never arrives under dual sticky
  (even with inject), so destroy is delayed until recovery+long hold.
- H12b: thr-11 runs guest code that crashes (`findLookupEntryByKey` /
  freelist noise) before overlay DMA; section 4 never issued.
- H12c: thr-11 completes only when `rdpFs`/present stays healthy for a
  minimum window; inject recovery is too late / thr-11 already wedged.
- H12d: thr-12 create is gated on a flag set inside thr-11 epilogue that
  force path corrupts (sec4 alone insufficient — s589 had sec4, no thr-12).

### Discriminating measurement
1. Arm always-on sparse thr-11 progress: create time, each run_next (or
   every N guest PCs inside saveServiceWorker), destroy, and any
   `[overlay] start-match` in same run. Prefer existing thr-create/destroy
   logs + wall timestamps from `update_screen` / process epoch.
2. Same binary: case6+inject HOLD_S≥90 (s589 shape) vs natural if it
   survives; compare thr-11 create→destroy wall seconds and whether
   thr-12 appears within 30s of sec4.
3. Positive controls: hangar e9_b late40; case6-force-start; inject n>0;
   recovery @0x76B768 if dual sticky hits.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Offline first if thr-11 guest body not yet instrumented: compare s577/s589/s590
# thr-11 create/destroy line timestamps via proc_start_epoch + nearest [vi] line.
# Then optional thin instrument in saveServiceWorker entry/exit only if offline
# cannot split H12a/b/c.
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_RDP_FULLSYNC=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s591_thr11_pipeline 5 12
# Offline: thr-create-id id=11 → thr-destroy id=11 → section 4 → thr-create id=12 → section 2
```

### Outcomes
- thr-11 destroy + thr-12 + sec2 on case6+inject long hold → pipeline was
  time-bounded; product hold recipe + default-ON inject path reopens
- thr-11 destroy + sec4 but no thr-12 → H12d; instrument thr-11 epilogue flags
- thr-11 never destroy, crash inside thr-11 guest → H12b; file breadcrumb only
  if new signature; else thr-11 wait instrument
- thr-11 never destroy, no crash, inject recovery live → H12a/c; mqdiag or
  thr-11 mesg wait probe next

### Do NOT
- Re-open H11a case5 vs case6 as section-2 gate.
- Reactive leave-path / findLookupEntry crash chases.
- Default-ON FS_PIPE_INJECT without thr-12/sec2 on a surviving path.
