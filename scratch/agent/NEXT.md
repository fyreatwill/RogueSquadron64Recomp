# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## Single work unit

**Post-sec2 FULL_SYNC plateau / menu return** (item -421).

s669 CLOSED -420 Outcome A: post-sec2 outdoor content LIVE ~195–200s
(VI 512 0x620000↔0x690000, present swap FIRE) then thr12→menu sec3;
packTlut=0. **H-postsec2-fs-plateau CONFIRMED** dual-source (rdpFs
frozen, syncs=0 ~5866–5894, E9 starved). Do not re-soak thr11d or
re-score post-sec2 presence.

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-mission-dl-no-e9 | mission-phase DLs legitimately lack E9 FULL_SYNC (game emits none) | oracle/retail or DL dump shows E9 in same outdoor window |
| H-inject-misses-mission | `FS_PIPE_INJECT` only covers hangar post-exit shape; mission outdoor tasks never get inject | inject counters fire for thr13 tasks OR arming inject for this phase moves rdpFs |
| H-menu-return-fs | rdpFs plateau causes state machine to abort mission → sec3 | rdpFs advances and sec3 return disappears / packTlut fires |
| H-menu-return-input | start_only HOLD never presses Start after cutscene; menu return is input-starved abort | extra post-sec2 Start/A keeps sec2 + reaches packTlut |

## Discriminating measurement (ONE iteration, batch arms)

Build/run **two arms in one session** on product defaults (headers ON, drop OFF):

1. **Arm A — FS inject visibility:** same force6+inject path as s668; add
   counters for inject hit rate **during thr13 post-sec2 only** (phase-gated
   from sec2 line). Posctrl: inject must log ≥1 sample in pre-sec2 recovery
   window (known-good). Score: inject_n post-sec2, rdpFs delta, syncs>0.
2. **Arm B — post-sec2 Start pulse:** same engage, but after sec2 (or after
   outdoor VI 0x620000 first present) inject Start×2 or A×2 via probe keys
   phase-gated. Score: sec3 return time, packTlut, thr12 lifetime vs s669
   baseline ~195s.

Target ≥1 recovery-full sec2 hold per arm (BUDGET≥1200 each; can run
sequentially if only one game instance, or sequential in one wrapper).

## Outcomes

- **A)** inject_n=0 post-sec2 while posctrl pre-sec2 inject>0 → H-inject-misses-mission;
  extend inject to mission outdoor task shape
- **B)** inject fires but rdpFs still flat → H-mission-dl-no-e9 / different fix site
- **C)** Start pulse prevents sec3 return or fires packTlut → H-menu-return-input;
  residual is input schedule not FS
- **D)** both arms still menu-return + packTlut=0 → guest path for thr12→sec3 teardown
  (instrument destroy call site)

## Command sketch

```bash
# Arm A: reuse s668 skeleton; phase-gate inject counters; tag s670_fs_postsec2_
# Arm B: PROBE post-sec2 keys; tag s670_input_postsec2_
# Offline baseline: python3 scratch/agent/s669_postsec2_offline_score.py
```

## Do NOT

- Productize `DROP_GARBAGE_CIMG` (s666 REJECTED).
- Re-soak thr11d multi-hold rate (-419 CLOSED).
- Re-prove outdoor present post-sec2 (s669 CLOSED).
- Chase packTlut SIGBUS (-373) until the loader actually fires (still 0).
