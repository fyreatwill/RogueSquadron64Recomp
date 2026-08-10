# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s582 recap (read this first)

| Observation | Implication |
|-------------|-------------|
| Hangar control e9_b 30/30 | Walker OK (s581 held) |
| Plateau 132/132 e9_b=0, endB8 | **H-sync1 CONFIRMED** |
| 0 plateau probes e9_b≥1 & syncs=0 | **H-sync2 REFUTED** |
| Cutscene dual DLs: e9_b=0 but syncs=1 for ~230 tasks, then syncs=0 | **H-sync4** — LLE non-guest-E9 FULL_SYNC dies |
| rsp_force_fullsync unwired | Not the synthetic-halt path |

Authoritative guest FULL_SYNC presence: **e9_b**. Ignore lin_e9 alone for H-sync2.

## This iteration's work unit

**H-sync4: find LLE/bridge RDP 0x29 emission when guest e9_b=0, and why it stops.**

### Hypotheses
- H4a: Factor5 LLE ucode emits RDP FULL_SYNC from an internal path (not guest 0xE9)
  that later stops (halt/yield/state).
- H4b: Bridge synthesizes/counts 0x29 from a non-E9 command (mis-decode or filter).
- H4c: Guest 0xE9 exists outside the e9_b walk (walker gap #2) for cutscene DLs only;
  hangar control still green; e9_b false-neg on this DL shape.
- H4d: Hist/drain artifact — "syncs=1" not real FULL_SYNC submits (unlikely 230 consecutive).

### Discriminating measurement (same-run, one build)
1. At every RDP 0x29 submit in dpc_bridge (or equivalent), log: task#, submit_addr,
   byte0, and a cheap guest e9_b presence for current dl_ptr (or reuse LOG_DL_SYNC).
2. Force-exit recipe (reliable): `PROBE_MODE=start_only HOLD_S=45
   GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_FORCE_CASE5_START=40"`.
3. Split submits into: (A) hangar syncs=1 e9_b≥1, (B) cutscene syncs=1 e9_b=0,
   (C) plateau syncs=0.
4. Outcomes:
   - B submits with byte0=0xE9 at addr outside e9_b walk → H4c (walker gap)
   - B submits with byte0≠0xE9 or synthetic → H4a/H4b
   - B empty (no real 0x29) while hist says 1 → H4d
   - Plateau C has zero 0x29 submits (expected) — confirm edge coincides with last B

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# After adding ROGUESQ_LOG_RDP_FULLSYNC (or extending DL_SYNC) + rebuild:
env PROBE_MODE=start_only HOLD_S=45 \
  ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_FORCE_CASE5_START=40 ROGUESQ_LOG_RDP_FULLSYNC=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s583_hsync4_rdp29 5 12
```

### Do NOT
- Treat H-sync2 as open for the post-exit plateau.
- Chase leave-path crashes or item -347 until 3rd occ.
- Reopen s178 / thr-resume-skip.
- Use natural double_start as the only vehicle (2/2 crash this session); force is OK
  for H-sync4 discrimination.
