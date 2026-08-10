# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s629 recap (read this first)

**s629 (this session): re-ran s628's pool-aware freeroll with an added filter**
(reroll recovery-active hits lacking `thr11d_new`+`level-tex-cache`, so the
loop doesn't waste a "scored" slot on non-class-D recovery-active hits). 4
attempts in 1234s, budget exhausted: 2 recovery-silent, 2 recovery-active-but-
no-class-D-ltex reroll. **0 `ltexmg` hits — 0 `fail136c` events.**

Combined with s628 (600s cap, 3 completed attempts, also 0 ltexmg): **2
consecutive null soaks, 7 attempts total, 0 data for the `maxfree_sel`
discriminator.** This is NOT evidence against H-ltexOOM-sel or H-ltexFree —
the instrument is correct and live (posctrl sane every attempt), the class-D
`fail136c` condition itself just hasn't recurred since s627 (which hit it
2/2 attempts). Read as a hit-rate problem, not a refutation.

Iron rule 8: this is 2 consecutive non-discriminating soaks on the same
narrow discriminator. `s630_ltex_pool_aware_freeroll_retry.sh` is already
queued (identical recipe, re-enqueued verbatim — RNG variance, not a design
flaw). **If s630 also comes back 0 ltexmg, that's 3 in a row — STOP
re-running this exact recipe next iteration.** Pivot options at that point:
widen `HOLD_S` past 180 (risk: exceeds -361's "do not raise HOLD_S past 210"
guardrail — cap any widen at 210), or attack the -385 null-malloc question
from the allocator-consumer side (who else drains E8/pool0 before
`loadLevelTextureCache` runs) instead of waiting for the class-D window.

## This iteration's work unit

**Consume `s630_ltex_pool_aware_freeroll_retry.sh` (already queued).**

1. If SOAK-RESULTS.md already has an s630 line with `ltexmg` hits, skip
   re-running — offline-analyze the scored `fail136c` block for
   `maxfree_sel`/`reason` and close O1 or O3 per the table below.
2. If s630 also comes back with 0 ltexmg (3rd consecutive null): do NOT queue
   a 4th identical retry. Write the hypothesis/evidence table into this file,
   and pick ONE of:
   - Widen `HOLD_S` to 210 (max allowed) in a new `s631` recipe — more dwell
     time per attempt may raise the class-D hit rate.
   - Investigate the allocator-consumer side: grep who else calls `rs_malloc`
     against pools E8/0 between hangar-sel and `loadLevelTextureCache`, to
     find what's consuming the free blocks class-D needs — this could explain
     an INDEPENDENT root cause (consumption pattern) instead of waiting on
     the RNG walk to reproduce fail136c.
3. On scored class-D with fail136c≥1 ∧ posctrl≥1:
   - **O1 / H-ltexOOM-sel:** `reason=no_fit` or `no_fit_unsel`, `maxfree_sel <
     need`, free sizes on sel pools sane → null is selected-pool pressure
     (next: who consumes E8/0, or expand pool / free leaks)
   - **O3 / H-ltexFree-walk:** `reason=no_fit_mystery`, `maxfree_sel ≥ need`
     → freelist walk rejects free blocks (flags/size/order bug) — instrument
     walk
   - Same-run control: posctrl `maxfree_sel` >> need + free= lines
4. Do NOT soft-skip thr12. Do NOT merge -385 with -387.

## Hypotheses (active)

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-ltexArg | (size=0x136C flags=0) | — | REFUTED s625 |
| H-ltexNullPool | (heads KSEG0 non-null) | — | REFUTED s625 |
| H-walk1 | uint32 MEM_* garbage | sane maxfree on posctrl | CONFIRMED s626 |
| H-ltexOOM | pool4 free ≥ need (global) | maxfree all pools | REFUTED s627 (global) |
| H-ltexOOM-sel | null = no free ≥ 0x1370 on E8/0 | fail136c maxfree_sel < need | **UNFED — 0 data, s628+s629 null** |
| H-ltexFree | null = freelist walk rejects free ≥ need | maxfree_sel ≥ need, mystery | **UNFED — 0 data, s628+s629 null** |
| H-recovwait1 | RECOV_WAIT=50 correct | — | CONFIRMED |
| H-dmarom1 | post soft-skip DMA (-387) | freeroll; not -385 root | 3× seen |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s628 maxfree/reason when unselected free counted
- Leave FORCE tools default-ON
- Raise HOLD_S past 210
- Queue a 4th identical freeroll if s630 is also null — pivot instead (see above)

### Reference tags
`[rs-malloc-diag]`, `ROGUESQ_LOG_RS_MALLOC_DIAG`, `fail136c`, `posctrl`, `ok136c`,
`maxfree_sel`, `nfree_sel`, `no_fit_unsel`, `no_fit_mystery`, H-ltexOOM-sel,
H-ltexFree, `0x136C`, `0x1370`, pool E8/0/4
