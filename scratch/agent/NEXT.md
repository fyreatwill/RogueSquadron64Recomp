# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## Single work unit

**Post-sec2 mission progress under product multi-header restore** (item -420).

s668 CLOSED thr11d multi-hold LIVE and dissolved -385 null-malloc under
headers: thr11d → ok136c → thr12 → **section 2** dual-source, crash=0,
packTlut=0. thr12 churns (id=12 destroy at sec2 boundary, id=13 recreate
then destroy by HOLD end). Do **not** re-soak thr11d rate.

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-sec2-mission-live | after sec2, mission cutscene/gameplay VI+content advance within HOLD | sec2 fires but VI/content stuck at pre-mission menu profile for full HOLD |
| H-thr12-churn-normal | thr12 destroy at sec2 is expected service-worker teardown, not a stall | thr12 dies and no replacement stays live while sec2 content should run |
| H-packtlut-next | packTlut / HMT load (-373) is the next post-sec2 loader and should fire | sec2 holds with 0 packTlut and no other mission-load markers |

## Discriminating measurements (ONE freeroll, product defaults)

1. Product defaults only (headers restore ON, drop OFF). Same force6+inject
   engage path as s668.
2. BUDGET≥1200, target ≥2 recovery-full HOLDs that reach sec2 (s668 rate ~2/3).
3. Per sec2-reaching HOLD, score:
   - time of sec2 vs thr12 create/destroy ids
   - last thr12 still live? duration of thr12 after sec2
   - packTlut / parseHmt / loadTexture / craft-shadow counts post-sec2
   - VI width/origin transitions post-sec2 (if logged) or phase markers
   - crash / fail136c / ok136c post-sec2
   - any `[missing-func]` / new crash families

## Outcomes

- **A)** Mission phase markers / content advance post-sec2 → score residual
  (packTlut, input, stability) as next bottleneck
- **B)** sec2 loads but thr12 dies immediately and no mission loaders fire →
  thr12 lifetime / registerServiceWorker residual
- **C)** sec2 never reached this freeroll (recov drought) → re-run budget only;
  do not reopen thr11d

## Command sketch

```bash
# Reuse s668 recipe skeleton; extend score_attempt for post-sec2 markers.
# Tag prefix s669_postsec2_
BUDGET_S=1200 TARGET_RECOV_FULL=2 \
  zsh scratch/agent/s669_postsec2_scored_freeroll.sh \
  >scratch/agent/s669_logs/wrapper.stdout 2>&1
```

## Do NOT

- Productize `DROP_GARBAGE_CIMG` (s666 CLOSED REJECTED).
- Spend another session on thr11d multi-hold rate (-419 CLOSED).
- Chase single trackResourceList freeroll noise until 2nd same stack.
