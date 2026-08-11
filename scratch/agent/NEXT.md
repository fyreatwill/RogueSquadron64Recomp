# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s657 recap (read this first)

**s656 soak = Outcome C incomplete opt-out:**
- ALLOW_WILD_W + ALLOW_FL_HDR both LIVE; skip_wild=0 skip_fl=0
- But `copyNativeToRAM` last-line hard-returned HIT_SKIP always
- Freelist 0x2/0x60 survived; 0/2 recovery-active

**s657 complete opt-out + freeroll Outcome A:**
- Gated last-line on ALLOW_FL_HDR → HIT_WRITE LIVE
- Freelist to_zero 0x2/0x60 returned (att3 full zeros @166352ms after
  classic killer `1F0D74 w=1161` HIT_WRITE)
- **1/3 recovery-active** (att3: recov768=7948 thr11d_new=1 fail136c=1
  reason=corrupt ltexmg=1 class M1_ltexmg_no_thr12)
- **H-fl-survive-suppresses-recov SUPPORTED**
  (product SKIP 0/7 + ALLOW_WILD 0/6 + incomplete ALLOW 0/2 vs complete 1/3)
- Product keeps SKIP_WILD_W + SKIP_FL_HDR + last-line HIT_SKIP default ON

## This iteration's work unit

**Primary: surgical freelist-header snapshot/restore to split co-factors.**

Under ALLOW_WILD_W=1 + ALLOW_FL_HDR=1 path in `copyNativeToRAM` when hit:
1. Snapshot 16 bytes at phys 0x1F3CC0 (or 8-byte flags+size)
2. Proceed with writeback (HIT_WRITE)
3. Restore header snapshot immediately after

Posctrl: HIT_WRITE fires AND freelist 0x2/0x60 survives past ~170s
(no freelist-shaped to_zero; heartbeats stay 0x2/0x60).

Discriminators on engaged freeroll (BUDGET≥1200, target ≥5 engaged):
- **A)** ≥1 recov768 with freelist header **restored/intact** after HIT_WRITE
  → writeback-completion (not freelist corruption) co-gates recovery
  → product path can explore non-destructive writeback variants
- **B)** 0 recov over ≥5 engaged with header restored + HIT_WRITE live
  → freelist corruption itself co-gates recovery (paradox; escalate)
- **C)** freelist still stomped despite restore → restore incomplete

Do NOT leave ALLOW_* on product soaks. Do NOT soft-skip thr12 without
recovery-active thr11d evidence.

## Hypotheses

| ID | Claim | Status |
|----|-------|--------|
| H-fb-skip-stops-stomp | SKIP stops freelist to_zero | CONFIRMED s654 |
| H-skip-suppresses-recov | SKIP_WILD_W lowers recov rate | **REFUTED s656** |
| H-fl-survive-suppresses-recov | freelist intact lowers recov rate | **SUPPORTED s657** |
| H-wb-complete-not-stomp | writeback completion (not fl zero) co-gates recov | ACTIVE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | CONFIRMED s637/s638 |

## Do NOT
- Score thr11d from recovery-silent-only freerolls
- Soft-skip thr12 without recovery-active thr11d evidence
- Leave ROGUESQ_ALLOW_WILD_W=1 or ROGUESQ_ALLOW_FL_HDR=1 on product soaks
- Re-claim SKIP_WILD_W as sole drought cause (REFUTED)
- Raise HOLD_S past 210
- Merge -385 with -387/-384/-373/-386

### Reference tags
`HIT_WRITE`, `ALLOW_FL_HDR`, freelist snapshot/restore, 0x1F3CC0, 0x1F0D74,
recov768, 0x76B768, thr11d_new, fail136c, -411, -408
