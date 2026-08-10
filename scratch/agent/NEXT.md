# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s634 recap (read this first)

**s634 ran `s634_thr11d_rate_accum_c` (new binary with !rsm_sane print-gate):**
4 attempts, recovery-fired 3×, thr11d_new **0/3**. Rate update s628–s634:
**2/8 (25%)** recovery-fired reach thr11d_new. 0 fail136c — bad_size raw-node
print still unfed.

**H-shipcycle2 STRUCTURAL (dual-source offline):** correlated s633
(`thr11d_new=1`) vs s634 att1 (`thr11d_new=0`, full 564s HOLD) event order
post-`[hangar-sel]`:

| step | both paths | thr11d_new=1 only |
|------|------------|-------------------|
| ship n=2 store/zero | yes | yes |
| destroy thr11 id=10, create id=11 | yes | yes |
| ship n=3 store/zero | **never on no-destroy** | yes |
| destroy id=11 → level-tex-* | no | yes |

SCORE `ship_store` is post-hsel only: =2 means n=2+n=3; =1 means only n=2.
Every no-destroy recovery-fired sample has ship_store=1; both thr11d_new=1
have ship_store=2. HOLD_S is not the lever (564s with id=11 live, no n=3).

**Freelist walk model dual-source OK** (game `next=node+size+0x10` matches
diag; predicted bad-node `0x801F3CC0`). Not a walker-model bug.

s635 remains queued for passive accumulation. Do not spend this session
babysitting another identical thr11d rate soak.

## This iteration's work unit

**Gate analysis for ship cycle n=3 / `destroyPlayerShipRecord` after post-exit
thr11 create** (item -392). Discriminating question: what condition makes
ship-store n=3 fire on thr11d_new=1 paths and never on no-destroy paths?

1. **Static:** list every caller of `destroyPlayerShipRecord` (known sites in
   `funcs_28/30/31/33/36.c` from s634 grep). For each, sketch the guard that
   decides whether to call free after hangar exit (state 8). Name the guest
   function + address for the path that fires at ship-zero n=3 host PC
   (`host=0x100d00b98` on s633 / `0x102e64b98` on s629 — use `atos`/`nm` or
   log host offset if available; guest ra may be zeroed).
2. **Dynamic from existing logs (no new run first):** in s633 and s629 att4
   thr11d_new=1 logs, dump ±50 lines around ship-store n=3 for guest
   breadcrumbs (`hangar-state`, section match, thr-create, cutscene tags,
   recovery). Diff against the same wall-clock window on s634 att1 after
   id=11 create (where n=3 never appears). The first tag present on thr11d=1
   and absent on no-destroy is the lead.
3. **If a single guest predicate is identified:** either (a) instrument it
   with a rate-limited fprintf in fixup (then one build + one soak), or
   (b) if it is already logged, just document the gate and enqueue a soak
   that waits for that tag. Do NOT force-write game state without a
   positive control plan.
4. **Consume s635** if the loop already ran it — fold SCORE into rates; if
   thr11d_new=1 with fail136c, read the !sane node print at E8 i=55
   (item -391). If still <3 thr11d_new samples and no n=3 lead, enqueue
   s636 copy for the loop and continue the gate analysis.

## Hypotheses (active)

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-ltexArg | (size=0x136C flags=0) | — | REFUTED s625 |
| H-ltexNullPool | (heads KSEG0 non-null) | — | REFUTED s625 |
| H-walk1 | uint32 MEM_* garbage | sane maxfree on posctrl | CONFIRMED s626 |
| H-ltexOOM | pool4 free ≥ need (global) | maxfree all pools | REFUTED s627 (global) |
| H-ltexOOM-sel | null = no free ≥ 0x1370 on E8 | fail136c maxfree_sel < need | **AMBIGUOUS N=1** (reason=corrupt, not clean no_fit) |
| H-ltexFree | null = freelist walk rejects free ≥ need | maxfree_sel ≥ need, mystery | UNFED clean |
| H-E8-corrupt | selected E8 freelist size field goes insane mid-run | !sane print flags/size at 0x801F3CC0 | **SUPPORTED N=1**; walk model OK; raw node unfed |
| H-walk-model-bug | diag next≠game next | static compare | **REFUTED s634** |
| H-thr11destroy-rate | thr11d rate is the bottleneck vs HOLD_S | recov vs thr11d across attempts | SUPPORTED 2/8; deprioritized |
| H-shipcycle2 | thr11d_new requires post-create ship-zero (n=3) | event order thr11d=1 vs =0 | **STRUCTURAL / CONFIRMED s634** |
| H-shipn3-gate | (open) a guest predicate gates ship n=3 | present on thr11d=1, absent on no-destroy | **ACTIVE** |
| H-recovwait1 | RECOV_WAIT=50 correct | — | CONFIRMED |
| H-dmarom1 | post soft-skip DMA (-387) | freeroll; not -385 root | 3× seen |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s628 maxfree/reason when unselected free counted
- Leave FORCE tools default-ON
- Raise HOLD_S past 210
- Spend the session on another pure thr11d rate-accumulation soak (enqueue only)
- Escalate scenegraph off recovery-active freeroll without scored class-D 2nd
- Force ship-zero / destroyPlayerShipRecord without a control plan

### Reference tags
`[ship-store]`, `[ship-zero]`, `destroyPlayerShipRecord`, `0x800B42A8`,
`[hangar-sel]`, thr11 id=11, ship n=3, H-shipn3-gate, H-shipcycle2,
`[rs-malloc-diag]`, `fail136c`, `stop=bad_size`, `0x801F3CC0`, thr11d_new
