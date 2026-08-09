# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s579 recap (read this first)

Post-mission-overlay "fs freeze" was **mis-classified as s178**. Offline on full s577 log:

| Hyp | s579 |
|-----|------|
| H-stall1 producer stops | **REFUTED** (772 lle + 771 runner post-plateau) |
| H-stall2 LLE incomplete | **REFUTED** (all exit=1) |
| H-stall3 classic s178 present stall | **REFUTED** (0 stalled=1 after sec2; FIRE pairs=4) |
| H-stall3b FULL_SYNC starvation | **CONFIRMED** (rdpFs == Σ syncs = 4602; last 772 tasks syncs=0) |
| H-stall4 stuck cutscene / fixed draw | **SUPPORTED** (hold MD5 freeze; tris lock 42→51) |

Do **not** reopen thr-resume-skip / producer-stop tools for this symptom.

## This iteration's work unit

**Why does FULL_SYNC stop after mission overlay?** Guest DL omit vs LLE/runner drop.

### Hypotheses
- H-sync1: post-plateau guest DLs never contain FULL_SYNC (or Factor5 full-sync opcode) —
  cutscene/mission draw path omits it.
- H-sync2: guest DLs contain full-sync but LLE/runner histogram drops it before `syncs` count
  (translator / opcode map gap after overlay reload).
- H-sync3: full-sync is present and executed but `rdpFs`/runner `syncs` under-count (counter
  bug) — unlikely given rdpFs==Σsyncs exact match, keep as control only.

### Discriminating measurement (ONE build if needed, ONE exit capture)
1. On each `[runner] task` (or `[lle task]`), if post-graceful-menu / rate-limited: dump first
   ~32 words of raw DL at `dl_ptr` and count opcode byte `0xE9` (standard G_RDPFULLSYNC) plus
   any Factor5 alias already mapped as full-sync in our GBI table.
2. Same-run positive control: a pre-plateau task that logged `syncs=1` must show ≥1 full-sync
   opcode in the raw dump; if control dump is empty/wrong, instrument is broken.
3. Compare first 5 post-plateau `syncs=0` tasks: raw full-sync count 0 → H-sync1; raw ≥1 but
   runner syncs=0 → H-sync2.

### Exact commands
```bash
# 1) Find how runner counts syncs + Factor5 full-sync opcode mapping (source-read first)
rg -n 'syncs|FULL_SYNC|G_RDPFULLSYNC|0xE9' src lib/rt64 docs/factor5-gbi.md | head -40

# 2) Prefer offline if a prior run already dumps DL bytes; else one batched log line:
#    [dl-sync-probe] task=#N syncs=N raw_e9=N first_ops=...
#    Gate: after graceful-menu OR after section-2 start-match; first 20 + every 50th.

# 3) Natural exit re-capture only if new instrument needs a live log:
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=double_start HOLD_S=20 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  PROBES_OVERRIDE="p1:start:6 p2:start:15 p3:start:3 p4:start:8" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s580_item7_sync_probe 5 12 \
  > scratch/s73_post_a_scene/s580_item7_sync_probe_driver.log 2>&1

grep -E 'dl-sync-probe|hangar-sel|start-match: section 2|syncs=|\[CRASH\]' \
  scratch/s73_post_a_scene/s580_item7_sync_probe/run.log | tail -80
```

### Expected outcomes
- H-sync1: control tasks raw_e9≥1; post-plateau raw_e9=0 → guest omit; next is cutscene/mission
  state machine (why draw loop has no full-sync / completion gate).
- H-sync2: post-plateau raw_e9≥1 but runner syncs=0 → fix LLE/GBI full-sync recognition.
- H-sync3: raw and runner disagree with rdpFs — only if Σsyncs math breaks (should not).

### Do NOT
- Treat this as s178; do not arm thr-resume-skip chases.
- Chase 0x8000ce54 / 0x8000247c / -338 leave-path noise.
- Force-case5 as product fix.
- Reopen freelist residual / M5.
