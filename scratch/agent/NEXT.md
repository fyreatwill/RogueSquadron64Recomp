# NEXT work unit

HYPOTHESIS-ID: direct-residual-gap-audit

## s567 recap (read this first)

**Item -346 FULLY CLOSED 2/2.** Loop confirm was WEAK (item-306 early death); same-session
manual retry CLEAN: hangarbay n=2700, full ~300s rc=0, 0 r6 fires, no 0x8000d6d0 crash.

Breadcrumb re-tally: no 3rd-hit escalations. `-332` still 2 occs (moderate, watch). `-347` 1 occ
(do not chase). Freelist WRITE campaign remains CLOSED; packing stays DEFERRED.

## This iteration's work unit

**Systematic DIRECT residual-gap audit** of the `-334/-340/-345/-346` model:

> After an existing freelist / sibling-ptr / heaplistdeq guard range-checks register R and
> skips a write, is there an *unguarded* `MEM_W(off, ctx->rR)` on the same base within the
> next few recomp instructions (including delay-slot duplicates)?

### Hypotheses
- H1: more residual same-base writes exist after recently landed guards (R2/R6/attr-write/
  sibling-ptr) → enumerate, guard the gap class, 1st live-verify.
- H2: residual is empty after -346 → document EMPTY re-scan (2 independent greps), pivot to
  next highest-info class (escalate -332 source-trace only if a 3rd controlled hit appears,
  else M3 DoD body item -7 / parked items).
- H3: packing-DEFERRED sites are real freelist bases after all → shape-check write-base
  provenance before any packing guard (s558/s562 already classified as DL cursor; only re-open
  with new contradictory evidence).

### Discriminating measurement
1. Enumerate candidate gaps with a single offline scan (no build yet):
   ```bash
   # Starting points: existing guard site guest PCs in fixup_game_funcs.py site tables
   # For each site S that guards MEM_W(off, rN), look ±16 lines in the matching funcs_*.c
   # for unguarded MEM_W(*, rN) or MEM_W(*, same-base-after-reload-from-stack).
   rg -n 'HEAP_FREE_LIST_DEQUEUE_R[0-9]_GUARD|HEAPLISTDEQ_ATTR_WRITE|SIBLING_PTR_WRITE' \
     tools/fixup_game_funcs.py | head -80
   ```
2. Classify every hit: ALREADY_GUARDED / NEEDS_GUARD / DEFERRED_PACKING / DEAD.
3. If NEEDS_GUARD nonempty: land one family (or extend an existing site list), one build,
   one hangarbay-driven soak (all passive breadcrumb envs armed).
4. If EMPTY: write the EMPTY table into PORTING-STATE + CURRENT-TRUTH, pick next unit.

### Expected outcomes
| Outcome | Proves |
|---|---|
| ≥1 NEEDS_GUARD + post-fix no-crash at that PC | H1 residual real; item -348+ |
| NEEDS_GUARD=0 after two independent scans | H2 residual empty; campaign truly closed |
| Packing site reclassified freelist with same-run bad_ptr co-fire | H3 reopen packing |

### Do NOT
- Chase item -347 / other single-occ breadcrumbs.
- Re-open freelist WRITE packing DEFERRED without new evidence.
- Guard without a same-base-as-existing-guard provenance link (no blind new families).
- Early-guard `goto` full epilogue unless every callee-save the epilogue restores is spilled.

## Iron-rule reminders
- Confirm free session number at START (next is s568).
- Weak early deaths on item -306: discard+retry.
- Kill with SIGKILL; run from build/ with ROM.
- One build, all counters; hangarbay n double-digit+ required for valid verify.
