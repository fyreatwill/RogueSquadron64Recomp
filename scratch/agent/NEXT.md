# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s580 recap (read this first)

Discriminating H-sync1 (guest omits 0xE9) vs H-sync2 (LLE drops) with
`ROGUESQ_LOG_DL_SYNC` **failed as designed** because the guest walk is incomplete:

| Observation | Implication |
|-------------|-------------|
| Boot clear DLs: 40/40 `syncs=1 raw_e9=1` | Instrument + simple-DL path OK (positive control) |
| Late hangar: 86/87 `syncs=1 raw_e9=0` | Walker **false-negates** 0xE9 on complex/chunked DLs (or LLE emits 0x29 without 0xE9; `rsp_force_fullsync` is **unwired**) |
| Post-exit r2 zero-sync probes all `raw_e9=0` | **Not discriminating** under walker gap |
| Post-exit r2 runners 282 syncs=1 / 235 syncs=0 | Dual population before sec2 all-zero plateau |

Do **not** claim H-sync1 from raw_e9=0 on complex tasks until late-hangar
`syncs=1 ⇒ raw_e9≥1` holds.

## This iteration's work unit

**Make raw_e9 a faithful absence probe on Factor5 complex DLs** (control gate), then
re-run one natural-exit capture to re-test H-sync1/2 on post-plateau tasks.

### Hypotheses (walker failure modes)
- H-walk1: treating 0xB5 as hard ENDDL pops too early; Factor5 chunk stream continues
  via 0x80 next-pointer / 0x108 layout and 0xE9 lives in a later chunk.
- H-walk2: G_DL branch=1 / multi-sub-DL graph misses sibling lists that LLE still runs.
- H-walk3: LLE emits RDP 0x29 without any guest 0xE9 (microcode auto-fullsync) —
  raw_e9 will stay 0 even with a perfect walk; then H-sync1/2 reframes around
  "why LLE auto-fullsync stops" not guest opcode.

### Discriminating measurement
1. Fix or replace the walk so that on **late hangar** tasks with `syncs=1`,
   `raw_e9 ≥ 1` (same-run control, ≥20 tasks s_n≥4000).
2. If after a correct walk raw_e9 is still 0 while syncs=1 → H-walk3 CONFIRMED;
   pivot to LLE-side emission probe (where does hist[0x29] get its byte?).
3. Only after control holds: natural exit, post-sec2 tasks with `syncs=0`:
   - raw_e9=0 → H-sync1 (guest omit)
   - raw_e9≥1 → H-sync2 (LLE drop)

### Exact commands
```bash
# 1) Source-read Factor5 chunk walk (docs/factor5-gbi.md + dpc_bridge / ucode dispatch)
# 2) Improve walk in main.cpp ROGUESQ_LOG_DL_SYNC (or dump LLE RDP ring source addr)
# 3) Rebuild + hangar-only control (no exit required):
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=start_only HOLD_S=20 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s581_dlsync_walk_control 5 12

# Late hangar control must show:
#   syncs=1 probes with raw_e9>=1 for ≥20 of first 30 late samples
# Failure (still raw_e9=0): implement H-walk3 LLE emission probe instead of more walk tweaks.
```

### Expected outcomes
- Walk fixed: late hangar control green → next session natural-exit H-sync1/2 retest.
- Walk cannot fix (H-walk3): instrument LLE at RDP 0x29 submit with guest DL cursor.

### Do NOT
- Claim guest omit from raw_e9=0 on complex DLs.
- Reopen thr-resume-skip / s178 producer-stop.
- Force-case5 as product fix.
- Chase leave-path noise or freelist residual.
