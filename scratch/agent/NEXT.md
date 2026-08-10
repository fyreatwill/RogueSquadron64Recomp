# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s584 recap (read this first)

| Observation | Implication |
|-------------|-------------|
| phys 0x76DF60 always size=8 DPC submit | shared **staging cell**, not ring/side buffer |
| task 5569 E9/syncs=1 → 5570 E7/syncs=0 | stop = **opcode rewrite**, not path death |
| 237 E9 then 150 E7 + 530 FD at same lo | H5b REFUTED (submits continue) |
| same dual dl_ptr pair through flip | H5c REFUTED |
| force recovers FULL_SYNC @ 0x76A838 task 6258 | s582/s583 "permanent" plateau death-truncated |
| e9_b=0 even on recovery | still side-slot pattern (H-sync4 family) |

Instrument stays: `ROGUESQ_LOG_FS_SLOT` + `ROGUESQ_LOG_DL_SYNC` + `ROGUESQ_LOG_RDP_FULLSYNC`.

## This iteration's work unit

**Why does LLE write PIPE_SYNC (E7) instead of FULL_SYNC (E9) into the staging
cell at the dual edge — and does natural hangar exit recover like force?**

### Hypotheses
- H6a: Guest dual DL stops containing a terminal FULL_SYNC emit path; LLE only
  ever forwards what the ucode writes — E7 is the legitimate end-of-batch op
  for that phase (lin_e9>0 at 5570 may be stale/unrelated).
- H6b: Ucode has a separate "emit FULL_SYNC to staging cell" epilogue gated on
  task flags / yield / DP complete that stops firing while geometry continues.
- H6c: Natural exit (s577) never reaches the force-path recovery phase
  (different cutscene branch / dies or freezes before 0x76A838).
- H6d: Recovery at 0x76A838 is VI/other synthetic — REFUTE already leans no
  (real kind=single E9 in s584); reconfirm e9_b=0 + real submit only.

### Discriminating measurement (prefer offline-first, one run if live)
1. **Offline on s584 log first:** correlate E9→E7 edge with runner fields
   (tris, cimg, depth, exit, dl_ptr), any overlay/section markers, and first
   0x76A838 single vs task #6258. Map whether lin_e9 at 5570 points inside
   dual DL or elsewhere.
2. If still open: one natural-exit soak (`PROBE_MODE=double_start` or real edge
   recipe from s577) with `ROGUESQ_LOG_FS_SLOT=1` + DL_SYNC + RDP_FULLSYNC —
   watch for E9→E7 and whether 0x76A838 ever appears.
3. Outcomes:
   - lin_e9 targets move out of live DPC path at edge → H6a
   - staging cell write of E7 with no guest E9 change → H6b
   - natural never recovers / never sees 0x76A838 → H6c
   - 0x76A838 not real guest E9 → H6d

### Exact commands (if live needed after offline)
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Prefer re-analysis of s584 before another force run.
# Natural recovery A/B (if offline insufficient):
env PROBE_MODE=double_start HOLD_S=45 \
  ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_FS_SLOT=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s585_hsync4_natural_recover 5 12
```

### Do NOT
- Re-litigate H5b/H5c or treat 0x76DF60 as a dedicated FULL_SYNC-only slot.
- Chase leave-path crashes / 0x8000b650 (known stale).
- Wire `rsp_force_fullsync` as product fix before knowing E9→E7 cause.
- Assume force-path recovery applies to natural s577 without measuring.
