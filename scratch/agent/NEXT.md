# NEXT work unit

HYPOTHESIS-ID: direct-residual-gap-audit

## s568 recap (read this first)

**Item -348 FIXED 1/2** — SIBLING_PTR DIRECT residual same-base gap class.

Dual offline scan (focus-family + all-PATCH MEM_W, WINDOW=24): 140 unique NEEDS_GUARD, all
SIBLING_PTR (102 TIGHT / 92 classic 0X0→0X4). Freelist R-numbered + ATTR residual EMPTY.
Packing not reopened. Applied 218 sites across 3 waves into `SIBLING_PTR_WRITE_GUARD`
(fixup table + surgical funcs_3/4). Float stores at `0x80017264`/`0x80017268` packing-adjacent
DEFERRED.

1st live-verify CLEAN: hangarbay n=2900, full ~300s rc=0, 0 CRASH, 0 sibling-ptr-write fires
(true-negative). 2nd confirm queued:
`scratch/agent/soak_queue/s568_sibling_residual_gap_confirm.sh`.

## This iteration's work unit

**Fold s568 2nd confirm from SOAK-RESULTS; close item -348 2/2 if CLEAN.**

If the queued confirm is WEAK (item-306 early death / hangarbay n single-digit): discard+retry
manually same session (same recipe as `s568_sibling_residual_gap_manual.sh`).

If CLEAN: mark -348 FULLY CLOSED 2/2, pivot the hypothesis slug — highest-info next:

### Hypotheses for pivot (after -348 closes)
- H1: another DIRECT residual class exists outside SIBLING (e.g. freelist *reads* already
  covered; or non-sibling write families) → re-run dual scan with broader FOCUS_TAGS, or
  escalate multi-occ breadcrumbs (-332 at 2 occs moderate).
- H2: residual-gap campaign truly empty → M3 DoD body item -7 (`PROBE_MODE=start_only HOLD_S=60`)
  or parked M4 items.
- H3: float-store residual at `0x80017264`/`68` is a real freelist-shaped crash sink → only if
  a hangarbay soak dies there with bad_ptr co-fire.

### Discriminating measurement (post-close)
1. Consume SOAK-RESULTS line for `s568_sibling_residual_gap_confirm`.
2. If CLEAN: breadcrumb re-tally from SOAK-RESULTS (watch -332 for 3rd occ); pick next unit.
3. Do NOT re-open packing DEFERRED without new same-run bad_ptr evidence.

### Do NOT
- Chase item -347 / other single-occ breadcrumbs.
- Re-open freelist WRITE packing DEFERRED without new evidence.
- Guard without a same-base-as-existing-guard provenance link.
- Early-guard `goto` full epilogue unless every callee-save the epilogue restores is spilled.

## Iron-rule reminders
- Confirm free session number at START (next is s569).
- Weak early deaths on item -306: discard+retry.
- Kill with SIGKILL; run from build/ with ROM.
- One build, all counters; hangarbay n double-digit+ required for valid verify.
