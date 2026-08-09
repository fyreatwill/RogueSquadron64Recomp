# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s581 recap (read this first)

| Observation | Implication |
|-------------|-------------|
| Boot: 20/20 e9_a=e9_b=lin≥1 | Both walks OK on simple DLs |
| Late hangar first 30: e9_a=0/30, e9_b=30/30, lin=30/30, fs_b0=E9 | **H-walk1 CONFIRMED**; control GREEN |
| H-walk3 (no guest 0xE9) | **REFUTED** for hangar |
| e9_b overcounts (9–26) | Presence-only probe, not count==syncs |

Authoritative guest FULL_SYNC presence: **`e9_b≥1` or `lin_e9≥1`**. Ignore e9_a on complex DLs.

## This iteration's work unit

**Natural-exit H-sync1 vs H-sync2 discrimination** on the post-mission-overlay
FULL_SYNC starvation plateau (item -349 / -7 / -351).

### Hypotheses
- H-sync1: guest omits 0xE9 on post-plateau tasks (`syncs=0` and `e9_b=0` and `lin_e9=0`)
- H-sync2: guest still has 0xE9 but LLE drops it (`syncs=0` and `e9_b|lin≥1`)
- H-sync3: plateau tasks never reached / dual population only (no all-zero plateau this run)

### Discriminating measurement (same-run)
1. Positive control: late pre-exit hangar `syncs=1` ⇒ e9_b|lin≥1 for ≥20/30 samples.
2. Reach natural hangar exit (3→5→6→8, section 2) and hold past sec2.
3. On post-sec2 (or consec zero-sync after ever_sync) probes:
   - majority `syncs=0 & e9_b=0 & lin=0` → **H-sync1**
   - majority `syncs=0 & (e9_b≥1|lin≥1)` → **H-sync2**
4. Also log fs_addr sticky: if syncs=0, fs_addr may be from prior task — do not treat as this-task emission.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Natural exit path (s577 recipe): double_start spaced edges + long hold
env PROBE_MODE=double_start HOLD_S=45 \
  ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s582_hsync_plateau 5 12

# Offline:
#   late hangar control: first 30 t>=4000 syncs>0 with e9_b|lin
#   post hangar-sel / post sec2: syncs=0 probes → e9_b/lin contingency table
# Require hangar-sel + section 2 (or graceful-menu) for full plateau; if only
# dual-pop before sec2, still classify that dual population with e9_b.
```

### Expected outcomes
- H-sync1 → guest no longer emits 0xE9; fix is on game-side task builder / state after overlay.
- H-sync2 → LLE drops/filters FULL_SYNC; fix is ucode/bridge path for those DLs.
- No plateau → retry exit recipe (s577 real_edge); do not reopen walker.

### Do NOT
- Treat e9_a=0 as guest omit on complex DLs.
- Reopen thr-resume-skip / s178 producer-stop.
- Force-case5 as product fix.
- Chase leave-path noise or freelist residual.
