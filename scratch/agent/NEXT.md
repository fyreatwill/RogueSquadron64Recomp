# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## Single work unit

**Scored freeroll under product multi-header restore (drop OFF)** —
resume -414 after s666 rejected DROP_GARBAGE_CIMG productize.

Product path is restore (mode=headers, walk_cap=64KB). s661 freeroll was
INCONCLUSIVE (queue 600s cap before thr11d/fail136c scoring). s659 16B
restore: recov 3/3 thr11d 3/3 fail136c 2/3. Headers product should keep
recov while fixing next=node+size+0x10 zero_node.

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-headers-recov | Product headers restore retains recov_active ≥1/3 engaged | 0/N recovery-active under product defaults (drop OFF) |
| H-headers-fail136 | Headers restore zeros fail136c reason=corrupt / zero_node next | fail136c still fires with next_ok=1 after restore |
| H-headers-thr11d | thr11d_new rate under headers ≈ s659 3/3 when recov fires | thr11d_new=0 on recovery-active holds |

## Discriminating measurements (ONE build, product defaults)

1. No `ROGUESQ_DROP_GARBAGE_CIMG`, no `FL_HDR_RESTORE=0` (product restore ON).
2. Arm instruments: `ROGUESQ_LOG_FL_ZERO_WATCH=1`, `ROGUESQ_LOG_RS_MALLOC_DIAG=1`,
   force6+inject hangar path, HOLD_S≥210, BUDGET_S≥1200 (or queue soak).
3. Score per engaged recovery-active: thr11d_new, fail136c reason/maxfree,
   `[fb-fl-hdr-restore]` match=1 nhdr next_ok, freelist to_zero 0x2/0x60,
   HIT_WRITE_RESTORE on killer.

## Outcomes

- **A)** recov≥1/3 + thr11d_new≥1 + fail136c=0 → headers product LIVE; push thr12 (-385)
- **B)** recov OK but fail136c residual → deepen body/next header walk
- **C)** recov drought under product restore → regression vs s659; bisect

## Do NOT

- Productize `DROP_GARBAGE_CIMG` (s666 CLOSED REJECTED — recovery drought).
- Retire FL_HDR_RESTORE while drop is OFF (product freelist path).

## Recipe scaffold

`scratch/agent/s659_product_fl_restore_freeroll.sh` (or s660 headers variant)
with BUDGET_S≥1200. Enqueue to soak_queue if only re-running.

## Standing rules

- Editing `lib/rt64` → `./submodule-patches/export.sh` + commit same session.
- Kill with SIGKILL; run from build/ with ROM.
