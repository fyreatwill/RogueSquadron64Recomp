# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## Single work unit

**thr11d multi-hold freeroll under product multi-header restore**
(item -419). s667 closed fail136c residual (H-headers-fail136); thr11d
was 0/2 recovery-fired holds with thr11 live and ship_store max n=2 —
UNEVALUABLE vs historical 4/10 thr11d rate / s659 3/3 under 16B restore.

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-headers-thr11d | thr11d_new rate under headers ≈ s659 (≥1/3 of recovery-fired full HOLDs) | thr11d_new=0 on ≥5 recovery-fired full HOLDs |
| H-headers-shipn3 | ship n=3 / B8 still fires under headers when recovery fires | ship_store n=3 never appears on recovery-fired holds |
| H-headers-recov-rate | recovery-fired rate under headers ≥1/3 engaged | 0 recovery-fired over ≥6 engaged |

## Discriminating measurements (ONE freeroll, product defaults)

1. Product defaults only: NO `DROP_GARBAGE_CIMG`, NO `FL_HDR_RESTORE=0`.
2. BUDGET_S≥1800 (or multi-pass until ≥5 recovery-fired full HOLD_S=210).
3. Per recovery-fired full HOLD score: thr11d_new, ship_store max n,
   `[mv-b8-set]`, fail136c (expect 0), next_ok, freelist 0x2/0x60 hb.

## Outcomes

- **A)** thr11d_new ≥1 on ≥1/3 recovery-fired → headers product thr11d LIVE; push thr12 (-385)
- **B)** recovery fires but thr11d=0 and ship n≤2 always → residual is ship/B8 gate (-393), not freelist
- **C)** recovery drought returns → headers regression; bisect vs s667

## Command

```bash
# Prefer reusing s667 recipe with higher budget:
# edit BUDGET_S=1800 (or env override if supported), or:
zsh scratch/agent/s667_headers_restore_scored_freeroll.sh
# Better: copy to s668 with BUDGET_S=1800 MAX_ATTEMPTS=16
```

Enqueue long soak to soak_queue if only re-running; score offline.

## Do NOT

- Productize `DROP_GARBAGE_CIMG` (s666 CLOSED REJECTED).
- Chase single trackResourceList freeroll noise (att4 s667) until 2nd same stack.
