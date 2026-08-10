# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s589 recap (read this first)

| H | Result | Evidence |
|---|--------|----------|
| H10a longer hold advances | **CONFIRMED** (when recovery fires) | 2288 post-dual syncs>0; 0x76B768×1988; fs 7010 |
| H10b need task-end inject | **REFUTED** | recovery cells carry FULL_SYNC after slot size-8 ends |
| H10c empty crash-bounded | **SUPPORTED** s588 shape | s588: 0 recovery + 0x80065e94 + empty×2085 |
| H10d visual despite tris=0 | **REFUTED** | black freeze real; content returns with live tris/syncs |
| Post-dual empty structural | **CLOSED** | not inevitable under H9d inject |
| Mission section 2 on force | **OPEN** (-359) | s588/s589 never load; s577 natural did |

Artifact: `scratch/s73_post_a_scene/s589_post_dual_empty/ANALYSIS.md`.

## This iteration's work unit

**Item -359: force path never loads mission overlay section 2.**

Dual FULL_SYNC sticky gap is product-fixed when inject+recovery run. M3 DoD
still blocked: force-exit cutscene never hands off to `.ovl.mission` (section
2 @0xA5D30). Natural s577 did.

### Hypotheses
- H11a: Force path skips a Start/state edge natural leave uses; section 2
  only after that edge (case 6→8 natural vs force case5).
- H11b: Section 2 is gated on FULL_SYNC/present health; s577 loaded it
  *before* dual sticky starvation; with inject, force should eventually
  load it if held longer / different key schedule.
- H11c: Force path corrupts a mission-entry flag (hangar-sel val=0 is
  symptom) so cinematic loops without mission DMA.
- H11d: Section 2 only loads from menu-overlay codepath that force never
  re-enters after VI 640 cutscene.

### Discriminating measurement
1. Same-run: arm inject + overlay logs; run **natural** `double_start` leave
   (not force) with HOLD_S≥45; count section-2 start-match and whether
   inject/recovery fire after exit.
2. If natural dies before section 2: force path with extra Start edges after
   state 8 (PROBES_OVERRIDE) and log any section-2 attempt.
3. Positive control: hangar e9_b GREEN; if section 2 loads, note task# and
   whether dual sticky had already started.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Prefer natural leave first (s577 recipe shape)
env PROBE_MODE=double_start HOLD_S=60 \
  GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_RDP_FULLSYNC=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s590_section2_natural 5 12
# Offline: grep '[overlay]' for section 2 / 0xA5D30 / 0x000A5D30 rom
# Compare to s577_item7_real_edge section-2 timing vs dual sticky onset
```

### Outcomes
- natural + inject loads section 2 → H11a/H11d force-incomplete; product
  leave must be natural edges (or force must synthesize them)
- natural never section 2 even with inject → H11b weaker; look at menu flags
- force+extra edges loads section 2 → H11a CONFIRMED; document edge recipe
- only crashes → breadcrumb; enqueue soak; do not reactive-chase

### Do NOT
- Re-open H10b task-end inject for post-dual.
- Default-ON FS_PIPE_INJECT without 2nd recovery confirm (can piggyback).
- Reactive leave-path crash fixes.
