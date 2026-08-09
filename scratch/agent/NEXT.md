# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s578 recap (read this first)

**Item -7 post-exit body closed as characterization:**

| Hyp | s578 |
|-----|------|
| H-m1 in-mission within ~30s of state 8 | **REFUTED** (STAR WARS + desert only; no craft/HUD) |
| H-m2 cutscene before gameplay | **CONFIRMED** (section 4 then section 2; bumper → desert dive) |
| H-m3 s178 fs freeze post-exit | **CONFIRMED** (fs→4602 freeze after mission overlay; VI still presents) |
| H-m4 hangar-sel val=0 blocks mission | **REFUTED as hard block** |

Hangar leave works (s577 natural 6→8; s578 spaced alternate 6→7→8). DoD blocker is now
**cutscene plays then RDP `fs` freezes** — s178 family with hangar-exit as known trigger.

Leave-path intermittent crashes this session (do NOT chase reactively):
- `reserveAndEmitDLEntry+18192` / `0x8000ce54` (s578 first)
- `coalesceFreeHeapBlocks+4424` / `0x8000247c` (s578 retry + spaced; known noise)

Artifacts: `scratch/s73_post_a_scene/s577_item7_real_edge/` (full post-exit PNG+log),
`s578_item7_post_exit{,_retry,_spaced}/`.

## This iteration's work unit

**Reopen s178 graphics-task-submission stall with hangar-exit → mission-overlay as trigger.**

### Hypotheses
- H-stall1: game-thread stops invoking the per-frame GFXTASK producer after mission overlay
  (s178 original mechanism — "producer not called").
- H-stall2: producer still enqueues tasks but LLE/runner never completes them (RDP `fs` stuck
  while task counts keep climbing).
- H-stall3: FULL_SYNC / present path stops consuming completed tasks (`pairs=0` + `stalled=1`
  continuously) while producer+RDP still move.
- H-stall4: cutscene is *supposed* to end and hand off to gameplay, but a guest gate
  (overlay/function/state) never flips — stall is symptom of stuck cutscene state machine.

### Discriminating measurements (ONE build, ONE long post-exit capture)
1. After section-2 start-match: count GFXTASK submits / LLE entries / `processDisplayLists ENTER`
   per second before vs after `fs` plateau.
2. `[vi-fs-decision]` `stalled` / `pairs` / `rdpFs` around freeze — same shape as s178?
3. Guest hangar/menu state + any post-exit state-writes after state 8.
4. Positive control: hangar-sel + graceful-menu + section-2 start-match all fire in same run;
   if leave dies early, retry (spaced p2: `PROBES_OVERRIDE="p1:start:6 p2:start:15 ..."`)
   or accept s577 log re-instrument offline if only counters missing.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Prefer natural exit; space p2 so case 5→6 can complete (~15s)
env PROBE_MODE=double_start HOLD_S=45 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  PROBES_OVERRIDE="p1:start:6 p2:start:15 p3:start:3 p4:start:8" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s579_item7_stall 5 12 \
  > scratch/s73_post_a_scene/s579_item7_stall_driver.log 2>&1

# Offline on successful exit (or re-grep s577 if only analysis):
grep -E 'hangar-sel|graceful-menu|start-match: section|\[phase\]|stalled=1|fs=|processDisplayLists|submit_rsp|n_gfx|\[CRASH\]|last-guest-pc' \
  scratch/s73_post_a_scene/s579_item7_stall/run.log | tail -120
```

If submit/LLE counters are not already in the binary, add a **batched** rate-limited pair
(submit count + LLE enter + rdpFs) gated to post-graceful-menu, one build, one run. Prefer
extending existing runner/DPC logs over new guest probes.

### Expected outcomes
- H-stall1: submit/LLE drop to 0 at freeze while thr-resume healthy → producer stop (s178).
- H-stall2: submits climb, fs flat → runner/LLE completion bug.
- H-stall3: submits+fs move but present decisions all `pairs=0 stalled=1` → present path.
- H-stall4: guest state stuck mid-cutscene (no state-write after 8; section-2 never yields) →
  map cutscene completion gate (not a host RDP bug).

### Do NOT
- Chase 0x8000ce54 / 0x8000247c / -338 leave-path noise.
- Treat ROGUESQ_FORCE_CASE5_START as product fix (force skipped section 2 in s576).
- Reopen freelist residual / M5.
- Reactive single-crash chases mid-cutscene unless same guest-PC ≥3 with hangarbay control.
