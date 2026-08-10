# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s638 recap (read this first)

**Outcome A CONFIRMED (s637 soak att2 thr11d_new=1):** full live chain
`[mv-b8-set]` (acc≈0.997 thr=0.98 s0=0) → `[mv-ship-arm]` b8=1 → ship-store n=3 →
throttle-ret ret=1 → ship-zero n=3 → thr-destroy id=11 → sec4. Pure B8 path
(button never). First B8 ~93s post-hsel / ~76s post-recovery.

**fail136c raw FED:** E8 `i=55 @0x801F3CC0 flags=0x0 size=0x0` (s634 predicted
addr exact). Freelist walk stops; remaining free unreachable. Pool4 free ≥ need
but unselected. This is the thr12 / -385 root residual when thr11d fires.

**thr11d rate:** 3/9 recovery-fired. Offline Outcome B: s634 564s HOLD no
ship-store n=3 → HOLD not the lever.

**Enqueued:** `s638_b8_fail136c_freeroll.sh` — free B8 no-destroy + more raw dumps.

## This iteration's work unit

**Primary: freelist zero-node at `0x801F3CC0` (-391 / -385) — who writes flags=0 size=0.**

Product rank: every thr11d path dies at null `rs_malloc(0x136C)` because E8 walk
hits this node. Fix or guard here unblocks thr12; B8 rate only multiplies attempts.

1. **Consume any new SOAK-RESULTS** (s638 freeroll): fold thr11d / no-destroy /
   fail136c raw; if instrumented no-destroy, classify B8 Outcome B/C.

2. **Static freelist writer audit (one build if instrument needed):**
   - `rs_malloc` / free / coalesce / `heapFreeListDequeue` sites that store
     size/flags at freelist headers (funcs_0.c / fixup-known names).
   - What legitimate node layout looks like (flags 1 free, 2 alloc, term bit 0x8).
   - Hypotheses for `flags=0 size=0` at mid-arena:
     | ID | Claim | Discriminator |
     |----|-------|---------------|
     | H-zero-free | free path zeros header then fails to set size | write-trace at free site hits 0x801F3CC0 |
     | H-oob-store | unrelated store stomps freelist (OOB DMA / list) | last writer host/guest PC ≠ free/malloc |
     | H-split-bug | block-split leaves zero residual node | split site creates size=0 neighbor |
     | H-never-init | uninit slab used as freelist | first touch is walk not free |

3. **Instrument plan (batch in ONE build if static insufficient):**
   - Rate-limited log on freelist header stores when addr in E8 arena
     (~0x80154690..0x807xxxxx) and new size==0 or flags==0.
   - Same-run positive control: mark a deliberate free of a known node and
     show the instrument fires with sane flags/size.
   - Do NOT soft-skip thr12 create; do NOT coalesce past zero nodes without
     root evidence.

4. **If freelist blocked on static-only dead end:** fall back to `[mv-acc]`
   sample (acc vs thr every N frames post thr11-create) for H-b8rate — one build.

## Hypotheses (active)

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-walk1 | uint32 MEM_* garbage | sane maxfree on posctrl | CONFIRMED s626 |
| H-ltexOOM-sel | null = no free ≥ 0x1370 on selected | fail136c maxfree_sel < need | AMBIGUOUS (corrupt masks true free) |
| H-E8-corrupt | E8 freelist size insane mid-run | raw @0x801F3CC0 | **CONFIRMED s638 flags=0 size=0** |
| H-walk-model-bug | diag next≠game next | static compare | REFUTED s634 |
| H-zero-free / H-oob-store / H-split-bug | who writes zero node | write-trace | **ACTIVE** |
| H-shipcycle2 | thr11d needs post-create ship-zero n=3 | event order | STRUCTURAL s634 |
| H-shipn3-gate | n=3 = runModelViewerLoop B8→throttle | static+dynamic | CONFIRMED s637 |
| H-b8rate / Outcome A | thr11d path = b8→arm→store→thr | live chain | **CONFIRMED s638** |
| H-b8rate residual | no-destroy = acc never crosses thr | 0 mv-b8-set post id=11 | offline SUPPORTED; live pending freeroll |
| H-recovwait1 | RECOV_WAIT=50 correct | — | CONFIRMED |
| H-dmarom1 | post soft-skip DMA (-387) | freeroll | 4× seen |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s628 maxfree/reason when unselected free counted
- Leave FORCE tools default-ON
- Raise HOLD_S past 210
- Spend session on pure thr11d rate soaks without freelist or acc instruments
- Force ship-zero / B8 / destroyPlayerShipRecord without control plan
- Re-open "which destroyPlayerShipRecord caller" — closed s637
- Coalesce-past or skip zero freelist nodes as a product "fix" without writer ID

### Reference tags
`[mv-b8-set]`, `[mv-ship-arm]`, `[ship-store]`, `[ship-zero]`, `[throttle-ret]`,
`[rs-malloc-diag]`, fail136c, `0x801F3CC0`, `0x801F3C90`, flags=0 size=0,
`rs_malloc`, freelist, H-E8-corrupt, H-zero-free, thr11 id=11, -385, -391, -393
