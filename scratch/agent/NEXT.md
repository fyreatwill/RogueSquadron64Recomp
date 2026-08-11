# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s656 recap (read this first)

**H-skip-suppresses-recov REFUTED (SKIP_WILD_W alone):**
- Loop soak s655_allow_wild_w: 2 engaged, 0 recov; posctrl ALLOW LIVE
- In-session BUDGET=1200s: 4 engaged (3 silent + 1 matnoise), 0 recov
- Combined ALLOW_WILD_W **0/6** recovery-active vs pre-SKIP ~1/3
- Under ALLOW_WILD_W, **SKIP_FL_HDR still blocks killer** (1F0D74 w=1161 +
  other ranges covering 0x1F3CC0); freelist 0x2/0x60 survives all silent
- Silent fullsync: 0x76DF60 side-slot live; recovery cell 0x76B768 **0×**
  (active control ~3974×)
- Landed `ROGUESQ_ALLOW_FL_HDR=1`; queued `s656_allow_fl_hdr_recov_ab.sh`

## This iteration's work unit

**Primary: consume s656_allow_fl_hdr_recov_ab SOAK-RESULTS (or run if still queued).**

1. Posctrl: both banners must fire:
   - `[ost-wb] ALLOW_WILD_W=1`
   - `[ost-wb] ALLOW_FL_HDR=1`
2. Expect skip_wild=0 skip_fl=0; fb_hit may return on killer; freelist
   to_zero 0x2/0x60 may return in historical ~165s window
3. Count recovery-active among engaged (hsel=1 + force6/case6)
4. Discriminators:
   - **A)** ≥1 recov768≥1 in ≤6 engaged → H-fl-survive-suppresses-recov
     SUPPORTED (note thr11d/fail136c if recov fires; freelist may stomp)
   - **B)** 0 recov over ≥5 engaged **with freelist to_zero LIVE** →
     drought independent of freelist state → pure recovery-inject pivot
     (why guest never emits FULL_SYNC at 0x76B768 post-hsel)
   - **C)** freelist still never to_zero despite both allows → incomplete
     opt-out; re-check writeback path / last-drawn-skip coupling

If sample size short (loop 600s cap ≈2–3 engaged): re-run in-session
BUDGET=1200s like s656.

## Hypotheses

| ID | Claim | Status |
|----|-------|--------|
| H-fb-skip-stops-stomp | SKIP stops freelist to_zero | CONFIRMED s654 |
| H-skip-suppresses-recov | SKIP_WILD_W lowers recov rate | **REFUTED s656** |
| H-fl-survive-suppresses-recov | freelist intact lowers recov rate | ACTIVE (A/B queued) |
| H-fl-survive-unblocks-thr11d | freelist intact → thr11d∧!fail136c | UNEVALUABLE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | CONFIRMED s637/s638 |

## Do NOT
- Score thr11d from recovery-silent-only freerolls
- Soft-skip thr12 without recovery-active thr11d evidence
- Leave ROGUESQ_ALLOW_WILD_W=1 or ROGUESQ_ALLOW_FL_HDR=1 on product soaks
- Re-claim SKIP_WILD_W as drought cause (REFUTED)
- Raise HOLD_S past 210
- Merge -385 with -387/-384/-373/-386

### Reference tags
`ROGUESQ_ALLOW_FL_HDR`, `ROGUESQ_ALLOW_WILD_W`, `[ost-wb] ALLOW_FL_HDR`,
SKIP_FL_HDR, SKIP_WILD_W, 0x1F0D74, arm_freelist, recov768, 0x76B768,
0x76DF60, thr11d_new, fail136c, -410, -408
