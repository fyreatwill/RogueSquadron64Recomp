# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s658 recap (read this first)

**Outcome A CONFIRMED triple-source (H-wb-complete-not-stomp SUPPORTED):**

Landed `ROGUESQ_FL_HDR_RESTORE=1` (default OFF; needs ALLOW_FL_HDR):
snapshot 16B @ phys 0x1F3CC0 → writeback → restore. Logs
`HIT_WRITE_RESTORE` + `[fb-fl-hdr-restore]`.

Freeroll BUDGET=1200s, 6 attempts:
- att2/4/6 recovery-active with freelist header **restored** (recov768
  7932/7932/3058); thr11d_new=0 fail136c=0
- classic killer `1F0D74 w=1161` HIT_WRITE_RESTORE; restore match=1
  pre=0x2/0x60 mid=0/0 post=0x2/0x60; heartbeats 0x2/0x60 past 170s
- recovery-active **3/5 engaged** vs product SKIP 0/7, stomp ALLOW 1/3

**Refinement:** product SKIP drought = **writeback-skip** of freelist-range
wild CIMG, not freelist integrity. Freelist permanent survival *with*
writeback completion does **not** suppress recovery.

Product still: SKIP_WILD_W + SKIP_FL_HDR + last-line HIT_SKIP default ON.
FL_HDR_RESTORE default OFF (A/B only).

## This iteration's work unit

**Primary: productize freelist-header restore as freelist-range writeback path.**

Replace SKIP_FL_HDR hard-skip (and last-line HIT_SKIP) with always-on
snapshot/write/restore when range covers phys 0x1F3CC0. Decision points:

1. **SKIP_WILD_W policy:** keep allowlist (320/512/640/1024) ON, *or* allow
   wild widths through with header restore only. Prefer keep SKIP_WILD_W ON
   first (smaller blast radius) — only freelist-range *allowlisted* widths
   would need restore; but classic killer is w=1161 (wild). So productize
   must either:
   - (A) allow wild widths that hit freelist header (restore) while still
     SKIP_WILD_W for non-freelist wild; or
   - (B) turn SKIP_WILD_W off entirely and restore freelist when hit.
   Recommend **(A)**: if range covers freelist → allow writeback + restore
   header (even if wild width); else keep SKIP_WILD_W allowlist.

2. Posctrl freeroll under product defaults (no ALLOW_*):
   - HIT_WRITE_RESTORE or equivalent product log on killer
   - freelist 0x2/0x60 survives past 170s
   - recovery-active rate ≥ historical ~1/3 over ≥5 engaged
   - thr11d_new / fail136c scored (expect fail136c=0; thr11d may return)

Discriminators:
- **A)** recov ≥1/3 engaged + freelist intact + product defaults → productize LIVE
- **B)** recov still drought under product restore → residual other co-factor
- **C)** freelist still permanently stomped → restore not on product path

Do NOT leave ALLOW_* on product soaks. Do NOT soft-skip thr12 without
recovery-active thr11d evidence.

## Hypotheses

| ID | Claim | Status |
|----|-------|--------|
| H-fb-skip-stops-stomp | SKIP stops freelist to_zero | CONFIRMED s654 |
| H-skip-suppresses-recov | SKIP_WILD_W alone lowers recov | REFUTED s656 |
| H-fl-survive-suppresses-recov | freelist intact lowers recov (under permanent protect/skip) | SUPPORTED s657; **refined s658** — integrity alone not the gate |
| H-wb-complete-not-stomp | writeback completion (not fl zero) co-gates recov | **SUPPORTED s658** |
| H-shipn3-gate / Outcome A | B8→store→thr11d | CONFIRMED s637/s638 |

## Do NOT
- Score thr11d from recovery-silent-only freerolls
- Soft-skip thr12 without recovery-active thr11d evidence
- Leave ROGUESQ_ALLOW_WILD_W=1 / ALLOW_FL_HDR=1 / FL_HDR_RESTORE=1 as the
  only product path without default-ON productize
- Raise HOLD_S past 210
- Merge -385 with -387/-384/-373/-386

### Reference tags
`HIT_WRITE_RESTORE`, `FL_HDR_RESTORE`, `fb-fl-hdr-restore`, 0x1F3CC0,
0x1F0D74, recov768, thr11d_new, fail136c, -412, -408
