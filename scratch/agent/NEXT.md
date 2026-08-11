# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s655 recap (read this first)

**Post-SKIP freeroll Outcome C (0 recovery-active):**
- s654 soak: 2× recovery_silent engaged; freelist 0x2/0x60 survived; killer
  SKIP on att2; thr11d unevaluable
- s655 in-session BUDGET=1200s: 5× recovery_silent + 1 pre-eng; arm_fl 5/5;
  freelist to_zero=0; **combined 0/7 recovery-active** post-SKIP vs ~1/3 pre-SKIP
- H-fl-survive-unblocks-thr11d **UNEVALUABLE** (recovery co-gate)
- **H-skip-suppresses-recov ACTIVE** (single-source correlation)
- Landed `ROGUESQ_ALLOW_WILD_W=1` A/B opt-out of SKIP_WILD_W (product default ON)

**Queued:** `scratch/agent/soak_queue/s655_allow_wild_w_recov_ab.sh`

## This iteration's work unit

**Primary: consume s655_allow_wild_w_recov_ab SOAK-RESULTS (or run if still queued).**

1. Posctrl: banner `[ost-wb] ALLOW_WILD_W=1` must fire; skip_wild may be 0
2. Count recovery-active among engaged attempts (hsel=1 + force6/case6)
3. Discriminators:
   - **A)** ≥1 recov768≥1 in ≤6 engaged → H-skip-suppresses-recov SUPPORTED
     (expect freelist to_zero 0x2/0x60 may return; note thr11d/fail136c if recov)
   - **B)** 0 recov over ≥5 engaged with ALLOW_WILD_W → H-skip-suppresses-recov
     REFUTED; drought independent of SKIP_WILD_W — pivot recovery inject path
4. If A and thr11d fires: also score H-fl-survive-unblocks-thr11d only if
   freelist still intact (SKIP_FL_HDR may keep header safe even with wild-W on)

## Hypotheses

| ID | Claim | Status |
|----|-------|--------|
| H-fb-skip-stops-stomp | SKIP stops freelist to_zero | CONFIRMED s654 |
| H-fl-survive-unblocks-thr11d | freelist intact → thr11d∧!fail136c | UNEVALUABLE s655 |
| H-skip-suppresses-recov | SKIP_WILD_W / fl survival lowers recov rate | ACTIVE (A/B queued) |
| H-shipn3-gate / Outcome A | B8→store→thr11d | CONFIRMED s637/s638 |

## Do NOT
- Score thr11d pipeline from recovery-silent-only freerolls
- Soft-skip thr12 without recovery-active thr11d evidence
- Re-open FB freelist-stomp without freelist to_zero under product SKIP (ALLOW=0)
- Treat 0/7 drought as causal CONFIRMED without A/B
- Raise HOLD_S past 210
- Merge -385 with -387/-384/-373/-386
- Leave ROGUESQ_ALLOW_WILD_W=1 on for product soaks (A/B only)

### Reference tags
`ROGUESQ_ALLOW_WILD_W`, `[ost-wb] ALLOW_WILD_W`, SKIP_WILD_W, 0x1F0D74,
arm_freelist, recov768, 0x76B768, thr11d_new, fail136c, -408, -409
