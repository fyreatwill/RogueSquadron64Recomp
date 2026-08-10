# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s631 recap (read this first)

**s631 (this session):** s630 (consumed at session start) confirmed the 3rd
consecutive null soak on the pool-aware `maxfree_sel`/`reason` discriminator —
s628, s629, s630 all show 0 `ltexmg` hits, 0 scored `fail136c` events, 10
combined attempts. Instrument itself is still live and correct (posctrl sane
every scored attempt: `maxfree_sel=0x4E6290`). Per NEXT.md's own stop
condition and iron rule 8, did **not** queue a 4th identical retry. Instead:

1. **Enqueued `scratch/agent/soak_queue/s631_ltex_pool_aware_freeroll_hold210.sh`**
   — identical recipe to s629/s630, `HOLD_S` widened 180→210 (the `-361`
   guardrail ceiling — do not go higher) for more per-attempt dwell time,
   on the theory that a longer post-hangar-sel window raises the probability
   of reaching the class-D `fail136c` call before an attempt's reroll
   boundary.
2. **Static analysis of `rs_malloc`'s pool-selection logic** (`funcs_0.c`
   L_80001B18-B98, addresses `0x80001B44`/`0x80001B88` in
   `~/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c`): traced the MIPS.
   For any call with `flags&4==0` (this includes the `0x136C` level-tex-cache
   call, `flags=0`), the code checks pool "0"'s head global
   (`MEM_W(0x80110000, -0x100)`); if that head is NULL it falls through
   unconditionally to pool E8 (`MEM_W(0x80110000, -0xE8)`) as the *sole*
   candidate — `t0=1`, one pool tried. **Every posctrl dump so far shows
   `head0=0x00000000`** — pool "0" is structurally empty through this whole
   phase, not selected-per-call. Conclusion: there is no narrow "who else
   drains E8" call-site set — every default-flags `rs_malloc` call anywhere
   in the hangar-sel..`loadLevelTextureCache` window is a candidate consumer.
   Static call-site enumeration is therefore low information value; do NOT
   spend a session grepping for E8 consumers by call site.

## This iteration's work unit

**Consume `s631_ltex_pool_aware_freeroll_hold210.sh` (already queued,
`HOLD_S=210`).**

1. If SOAK-RESULTS.md already has an s631 line with `ltexmg` hits (fed
   discriminator): offline-analyze the scored `fail136c` block for
   `maxfree_sel`/`reason` per the O1/O3 table below and close one of
   H-ltexOOM-sel / H-ltexFree.
2. If s631 ALSO comes back with 0 ltexmg (4th consecutive null, this time
   with the widened window): **stop widening HOLD_S — 210 is the guardrail
   ceiling, do not go higher.** Pivot to the other track named in the s631
   static-analysis note above: instrument aggregate E8 pool
   bytes-allocated / bytes-freed across the WHOLE hangar-sel..ltex window
   (not per-call maxfree at the moment of the 0x136C call) — batch this into
   the *same* `rs-malloc-diag` instrument (add a running counter, do not
   open a new instrumentation axis) so the next soak still only needs one
   build+run cycle. This tests whether E8 is being progressively exhausted
   by many small allocations over the window (aggregate-drain hypothesis,
   currently untested) vs. genuinely has enough headroom at the moment of
   the failing call (which would revive H-ltexFree — freelist-walk bug —
   as the leading explanation since call-site consumer-hunting is a dead
   end per above).
3. On scored class-D with fail136c≥1 ∧ posctrl≥1:
   - **O1 / H-ltexOOM-sel:** `reason=no_fit` or `no_fit_unsel`, `maxfree_sel <
     need`, free sizes on sel pools sane → null is selected-pool (E8)
     pressure — next: build the aggregate E8 drain counter (see step 2) to
     find the consumption pattern, since call-site enumeration is a dead end.
   - **O3 / H-ltexFree-walk:** `reason=no_fit_mystery`, `maxfree_sel ≥ need`
     → freelist walk rejects free blocks (flags/size/order bug) — instrument
     the walk itself (which node/flag causes rejection).
   - Same-run control: posctrl `maxfree_sel` >> need + free= lines.
4. Do NOT soft-skip thr12. Do NOT merge -385 with -387.

## Hypotheses (active)

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-ltexArg | (size=0x136C flags=0) | — | REFUTED s625 |
| H-ltexNullPool | (heads KSEG0 non-null) | — | REFUTED s625 |
| H-walk1 | uint32 MEM_* garbage | sane maxfree on posctrl | CONFIRMED s626 |
| H-ltexOOM | pool4 free ≥ need (global) | maxfree all pools | REFUTED s627 (global) |
| H-ltexOOM-sel | null = no free ≥ 0x1370 on E8 (pool "0" always empty this phase) | fail136c maxfree_sel < need | **UNFED — 0 data, s628/s629/s630 null (3× in a row)** |
| H-ltexFree | null = freelist walk rejects free ≥ need | maxfree_sel ≥ need, mystery | **UNFED — 0 data, s628/s629/s630 null (3× in a row)** |
| H-E8-consumer | narrow call-site can be identified draining E8 | — | **REFUTED s631 (static)** — pool "0" structurally empty ⇒ every default-flags alloc in-window is a candidate; no narrow set to grep |
| H-recovwait1 | RECOV_WAIT=50 correct | — | CONFIRMED |
| H-dmarom1 | post soft-skip DMA (-387) | freeroll; not -385 root | 3× seen |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s628 maxfree/reason when unselected free counted
- Leave FORCE tools default-ON
- Raise HOLD_S past 210 (s631 is already at the ceiling)
- Queue another identical HOLD_S=210 freeroll if s631 is also null — pivot to
  the aggregate E8 drain-counter instrument instead (step 2 above)
- Spend a session grepping rs_malloc call sites for "who uses E8" — refuted
  as low-value by the s631 static-analysis finding (every default-flags call
  is a candidate; the set isn't narrow)

### Reference tags
`[rs-malloc-diag]`, `ROGUESQ_LOG_RS_MALLOC_DIAG`, `fail136c`, `posctrl`, `ok136c`,
`maxfree_sel`, `nfree_sel`, `no_fit_unsel`, `no_fit_mystery`, H-ltexOOM-sel,
H-ltexFree, H-E8-consumer, `0x136C`, `0x1370`, pool E8/0/4, `funcs_0.c` L_80001B18-B98
