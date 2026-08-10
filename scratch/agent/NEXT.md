# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s631 recap (read this first)

**s631 (this session):** consumed the already-queued `s631_ltex_pool_aware_freeroll_hold210.sh`
soak (4th consecutive null on the `fail136c`/`maxfree_sel` discriminator — 0
`ltexmg` hits, 0/11 combined attempts across s628-s631). Per NEXT.md's own
plan, a 4th null should have triggered the aggregate-E8-drain-counter pivot.
Before building that, did an offline cross-reference of all 11 printed
`SCORE` lines (not just the final scored-or-rerolled one) across the 4 soak
logs on two fields: `recov768` (recovery cell fired) and `thr11d_new` (thr11
create+destroy pair completed — the established precondition for ever
reaching `loadLevelTextureCache`/`ltexmg`):

- Recovery is silent in 7/11 attempts.
- Of the 4 where recovery DOES fire, `thr11d_new` completes in only **1**
  (~25%). The other 3 are `I_thr11_live_no_destroy` / `_other_crash`.
- Raising `HOLD_S` 180→210 (s631's own pivot) did **not** fix this — s631's
  one recovery-fired attempt was still `I_thr11_live_no_destroy` at the
  wider window.
- The one `thr11d_new=1` sample (s629 attempt 4) was killed by a real SIGBUS
  crash before reaching `ltexmg`: `loadDatFile+692`←`loadLevelAssets`←
  `setupCutsceneLevel`←`cinematicLoopBody`←`mainGameLoop`. Matches the
  known stale-`last-guest-pc=0x800290d4` background-noise family (item
  -259) — 1× freeroll, not escalated (would need a 2nd occurrence in this
  specific window).
- Weak, unconfirmed (N=1) lead: that same attempt had `ship_store=2
  ship_zero_post=2` vs `=1` on all 3 no-destroy attempts — flagged as
  `H-shipcycle2`, not a claim yet.

**Conclusion: the aggregate-E8-drain-counter pivot is premature.**
`loadLevelTextureCache` is barely ever reached (needs `thr11d_new=1` first,
which is rare), so a finer malloc counter has nothing to discriminate yet.
The real bottleneck is upstream: thr11 destroy essentially never completes
within the observation window, and it isn't simply a function of dwell time
(HOLD_S widening didn't help). Enqueued two more copies of the same
freeroll recipe — `s632_thr11d_rate_accum_a.sh` and
`s633_thr11d_rate_accum_b.sh` (HOLD_S=210, otherwise mechanically identical
to s631) — to accumulate raw `thr11d_new=1` sample count. This is NOT the
same case as "don't queue a 4th identical HOLD_S retry" — that guidance was
about widening HOLD_S as a lever (now refuted); this is accumulating N on an
already-correct recipe (its own reroll logic already retries toward
`thr11d_new=1`), which is exactly what the soak queue exists for.

## This iteration's work unit

**Consume `s632_thr11d_rate_accum_a.sh` and `s633_thr11d_rate_accum_b.sh`**
(already queued; the loop runs up to 2 per iteration, so both may already
have results in SOAK-RESULTS.md by the time you read this).

1. For each soak, read the raw log (not just the SOAK-RESULTS.md summary
   line — it may be bare rc/dur with no inline verdict). Extract EVERY
   printed `SCORE` line (grep `SCORE` in the log), not just the final one —
   freerolled attempts still print diagnostic SCORE lines before rerolling.
2. Tabulate `recov768` (0 vs nonzero) × `thr11d_new` (0 vs ≥1) across ALL
   attempts from s628 through however many new soaks exist. Running total
   before this iteration: recovery fired 4/11, thr11d_new completed 1/4 of
   those.
3. If the combined sample now has **3+ `thr11d_new=1` occurrences**:
   - Check `H-shipcycle2`: does `ship_store=2`+ correlate with
     `thr11d_new=1` across the enlarged sample? If yes on 3+/3+ vs no on the
     no-destroy attempts, promote from "weak lead" to a real finding in
     CURRENT-TRUTH. If it breaks (a `ship_store=1` case with
     `thr11d_new=1`, or a `ship_store=2` case without), mark REFUTED.
   - For any `thr11d_new=1` attempt that ALSO reaches `ltexmg` (survives
     past the `loadDatFile` background-noise crash risk): finally read the
     `fail136c`/`maxfree_sel`/`reason` discriminator per the O1/O3 table
     below — this is the original -389/-390 question, still open.
   - If a 2nd `loadDatFile+692` crash appears specifically inside a
     `thr11d_new`-reached window (not just anywhere in the run): that upgrades
     from "known background noise, 1× freeroll" to a real blocker on this
     specific path — escalate (guard candidate), do not keep free-rerolling.
4. If the combined sample is STILL <3 `thr11d_new=1` occurrences after these
   2 soaks: enqueue 2 more identical-mechanics copies (new tags, e.g.
   `s634`/`s635`) rather than pivoting to a new instrument — the ~9%
   hit rate means this may take several more soak cycles. Do NOT spend a
   build/run cycle on new instrumentation until there's enough
   `thr11d_new=1` volume to have something to instrument.
5. Do NOT soft-skip thr12. Do NOT merge -385 with -387.

## Hypotheses (active)

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-ltexArg | (size=0x136C flags=0) | — | REFUTED s625 |
| H-ltexNullPool | (heads KSEG0 non-null) | — | REFUTED s625 |
| H-walk1 | uint32 MEM_* garbage | sane maxfree on posctrl | CONFIRMED s626 |
| H-ltexOOM | pool4 free ≥ need (global) | maxfree all pools | REFUTED s627 (global) |
| H-ltexOOM-sel | null = no free ≥ 0x1370 on E8 (pool "0" always empty this phase) | fail136c maxfree_sel < need | **UNFED — 0 data, 4 consecutive null soaks (s628-s631)** |
| H-ltexFree | null = freelist walk rejects free ≥ need | maxfree_sel ≥ need, mystery | **UNFED — same** |
| H-E8-consumer | narrow call-site can be identified draining E8 | — | REFUTED s631 (static) |
| H-thr11destroy-rate | thr11d_new completion rate is the real bottleneck, not HOLD_S dwell | recov768 vs thr11d_new across attempts | **SUPPORTED s631 (N=4, 1/4 hit) — needs more samples to firm up** |
| H-shipcycle2 | 2nd ship-store/zero cycle correlates with thr11d_new completing | ship_store≥2 on thr11d_new=1 attempts vs =1 on no-destroy | **WEAK LEAD, N=1 — not a claim yet** |
| H-recovwait1 | RECOV_WAIT=50 correct | — | CONFIRMED |
| H-dmarom1 | post soft-skip DMA (-387) | freeroll; not -385 root | 3× seen |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s628 maxfree/reason when unselected free counted
- Leave FORCE tools default-ON
- Raise HOLD_S past 210 (already at ceiling; s631 showed it doesn't move the
  thr11d_new rate anyway)
- Build the aggregate-E8-drain-counter instrument before `loadLevelTextureCache`
  is being reached with some regularity — premature per s631 analysis
- Escalate the `loadDatFile+692` crash off a single occurrence — needs a 2nd
  hit specifically inside a thr11d_new-reached window

### Reference tags
`[rs-malloc-diag]`, `ROGUESQ_LOG_RS_MALLOC_DIAG`, `fail136c`, `posctrl`, `ok136c`,
`maxfree_sel`, `nfree_sel`, `no_fit_unsel`, `no_fit_mystery`, H-ltexOOM-sel,
H-ltexFree, H-thr11destroy-rate, H-shipcycle2, `thr11d_new`, `ship_store`,
`ship_zero_post`, `loadDatFile+692`, `0x136C`, `0x1370`, pool E8/0/4,
`funcs_0.c` L_80001B18-B98
