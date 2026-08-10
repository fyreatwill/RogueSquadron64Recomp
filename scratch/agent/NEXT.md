# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s627 recap (read this first)

**s627 scored class-D fail136c** (loop freeroll, attempt 1):
- thr11d_new=1 ltexmg=1 fail136c=1 posctrl=8 ok136c=1 cshadow_a=3
- fail136c flags=0 need=0x1370; pool4 free 0x6A3C0/0x6A3E0 ≥ need but **unselected**
- flags=0 path: E8 then pool0 only (rs_malloc L_80001B70)
- Global H-ltexOOM **REFUTED**; size-corruption O3 **REFUTED**
- `no_fit_mystery` was diag artifact (counted pool4 free)
- ok136c ptr=`0x80261E20` past s626 dump cap → free on selected can live past i=15
- -387 do_rom_read SIGBUS 3× after soft-skip (still freeroll while -385 open)

**s628 instrument LIVE** (rebuilt): cap 256, free-always print, `maxfree_sel`/
`nfree_sel`, reason `no_fit` | `no_fit_unsel` | `no_fit_mystery`.

## This iteration's work unit

**Consume s628 freeroll for selected-pool maxfree_sel — close H-ltexOOM-sel vs mystery.**

1. Ensure binary has s628: `strings build/RogueSquadron64Recomp | grep maxfree_sel`
2. Run / consume `scratch/agent/soak_queue/s628_ltex_pool_aware_freeroll.sh`
   (BUDGET=1200, RECOV_WAIT=50, force+inject + RS_MALLOC_DIAG).
3. On scored class-D with fail136c≥1 ∧ posctrl≥1:
   - **O1 / H-ltexOOM-sel:** `reason=no_fit` or `no_fit_unsel`, `maxfree_sel < need`,
     free sizes on sel pools sane → null is selected-pool pressure (next: who
     consumes E8/0, or expand pool / free leaks)
   - **O3 / H-ltexFree-walk:** `reason=no_fit_mystery`, `maxfree_sel ≥ need` →
     freelist walk rejects free blocks (flags/size/order bug) — instrument walk
   - Same-run control: posctrl `maxfree_sel` >> need + free= lines; fail136c `nsel=2`
4. Do NOT soft-skip thr12. Do NOT merge -385 with -387.

If s628 SOAK-RESULTS already has scored fail136c with maxfree_sel, skip re-run —
offline-analyze and close O1 or O3.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ltexmg1 | (CONFIRMED) guard LIVE | ltexmg≥1 ∧ ltex_null=0 |
| H-ltexArg | (REFUTED s625) | size=0x136C flags=0 |
| H-ltexNullPool | (REFUTED s625) | heads KSEG0 non-null |
| H-walk1 | **(CONFIRMED s626)** uint32 MEM_* garbage | sane maxfree on posctrl |
| H-ltexOOM | (REFUTED s627 *global*) pool4 free ≥ need | maxfree all pools |
| H-ltexOOM-sel | null = no free ≥ 0x1370 on E8/0 | fail136c maxfree_sel < need |
| H-ltexFree | null = freelist walk rejects free ≥ need | maxfree_sel ≥ need, mystery |
| H-recovwait1 | (CONFIRMED) | RECOV_WAIT=50 |
| H-dmarom1 | (3×) post soft-skip DMA | freeroll; not -385 root |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s628 maxfree/reason when unselected free counted
- Leave FORCE tools default-ON
- Raise HOLD_S past 210

### Reference tags
`[rs-malloc-diag]`, `ROGUESQ_LOG_RS_MALLOC_DIAG`, `fail136c`, `posctrl`, `ok136c`,
`maxfree_sel`, `nfree_sel`, `no_fit_unsel`, `no_fit_mystery`, H-ltexOOM-sel,
H-ltexFree, `0x136C`, `0x1370`, pool E8/0/4
