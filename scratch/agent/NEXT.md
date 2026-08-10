# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s637 recap (read this first)

**H-shipn3-gate CONFIRMED (dual-source s629+s633 vs s634):** thr11d_new path is
entirely inside `runModelViewerLoop`:

1. sp+0xB8 set when float `0x800D0120+0x90*s3+4` > `*0x800A79B8` (site 0x800CA1E0)
   — post-hsel newbtn is zeros, so not A/START
2. L_800CA51C: if ship null → `updateTextOverlayLookupEntry` → **ship-store n=3**
3. `accumulateShipThrottleCharge` (needs gPlayerShip) → ret=1 after 7 thresholds
4. L_800CA578 → `destroyPlayerShipRecord` → **ship-zero n=3** → thr11 id=11 dies → sec4

n=2 destroy = `gracefulMenuShutdown` (different caller). HOLD_S not the lever.

**Instruments live in binary:** `[mv-b8-set]` (always when B8 fires),
`[mv-ship-arm]` (rate-limited at L_800CA51C with s0/b8/ship/s3).

**s635/s636 soaks:** no new thr11d_new; rate still **2/8** recovery-fired.

**Enqueued:** `s637_mv_b8_shipn3_gate.sh` — consume its SCORE first.

## This iteration's work unit

**Consume s637 soak (or run it if not yet done) and classify B8 residual (-393).**

1. **Fold SOAK-RESULTS** for `s637_mv_b8_shipn3_gate`:
   - Count recovery-fired thr11d_new vs no-destroy.
   - On thr11d_new=1: require `[mv-b8-set]` then `[mv-ship-arm]` (b8=1 or s0=1)
     then ship-store n=3 then throttle-ret ret=1 — **positive control**.
   - On no-destroy: is `[mv-b8-set]` count post thr11-create **0** (acc never
     hits thr) or >0 with arm skipped / ship non-null?

2. **Discriminators (pick one):**
   | outcome | proves |
   |---------|--------|
   | A thr11d: b8-set→arm b8=1→store n=3→thr ret1 | control green; path as modeled |
   | B no-destroy: 0 mv-b8-set after id=11 create | float acc stuck (f28/s3/table) |
   | C no-destroy: mv-b8-set>0 but 0 store n=3 | arm entered with ship already set, or isPlayerShipActive blocks |
   | D thr11d without any mv-b8-set | store via s0=1 (button path) — unexpected post-hsel |

3. **If B (acc stuck):** static-read who writes s3 / the 0x800D0120 table and
   f28 (frame dt); instrument one rate-limited `[mv-acc]` sample of acc vs thr
   every N frames post-hsel (one build). Do not force B8 without control plan.

4. **If A only (no no-destroy sample):** enqueue another copy; do not spend
   session babysitting. Optionally offline-read s634 no-destroy for any
   pre-existing B8-adjacent tags (there were none before instruments).

## Hypotheses (active)

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-walk1 | uint32 MEM_* garbage | sane maxfree on posctrl | CONFIRMED s626 |
| H-ltexOOM-sel | null = no free ≥ 0x1370 on E8 | fail136c maxfree_sel < need | AMBIGUOUS N=1 |
| H-E8-corrupt | E8 freelist size insane mid-run | !sane print at 0x801F3CC0 | SUPPORTED N=1; raw unfed |
| H-walk-model-bug | diag next≠game next | static compare | REFUTED s634 |
| H-shipcycle2 | thr11d needs post-create ship-zero n=3 | event order | **STRUCTURAL s634** |
| H-shipn3-gate | n=3 = runModelViewerLoop B8→throttle | static+dynamic dual-source | **CONFIRMED s637** |
| H-b8rate | residual thr11d rate = B8 never fires | mv-b8-set post id=11 on no-destroy | **ACTIVE** |
| H-recovwait1 | RECOV_WAIT=50 correct | — | CONFIRMED |
| H-dmarom1 | post soft-skip DMA (-387) | freeroll; not -385 root | 3× seen |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s628 maxfree/reason when unselected free counted
- Leave FORCE tools default-ON
- Raise HOLD_S past 210
- Spend the session on pure thr11d rate soaks without the new B8 tags
- Force ship-zero / destroyPlayerShipRecord / force B8 without control plan
- Re-open "which destroyPlayerShipRecord caller" — closed s637

### Reference tags
`[mv-b8-set]`, `[mv-ship-arm]`, `[ship-store]`, `[ship-zero]`, `[throttle-ret]`,
`runModelViewerLoop`, `0x800CA1E0`, `0x800CA51C`, `0x800CA578`,
`accumulateShipThrottleCharge`, `gracefulMenuShutdown`, thr11 id=11,
H-shipn3-gate, H-b8rate, fail136c, `0x801F3CC0`
