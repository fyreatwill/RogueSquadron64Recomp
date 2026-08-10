# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s626 recap (read this first)

**H-walk1 CONFIRMED.** s625 free-byte walk garbage (maxfree ~GB on successful
posctrl) was `uint32` guest addresses passed to `MEM_*` without `S32()` sign-
extension. s626 dumps raw ≤16 nodes/pool with S32; early posctrl shows sane
sizes (`maxfree_sane=0x4E6290`, free block at `0x80156D50`). O2 REFUTED.
Class-D fail136c not hit this session (recovery freeroll) — O1 vs O3 still open.

### Evidence (s626 att1 posctrl, instrument LIVE)
```
pool=E8 i=2 addr=0x80154B10 flags=0x2 size=0x2230 sane=1
pool=E8 i=3 addr=0x80156D50 flags=0x1 size=0x4E6290 sane=1
summary event=posctrl nnodes=6 nfree=2 maxfree_sane=0x4E6290 reason=ok
```
ok136c also sane (`maxfree_sane=0x6A3E0`). Generic flags=0x4 fails: head4=NULL
while pool0 free 0x3CE00 — reason string not pool-aware yet (cosmetic).

Code: `../N64Recomp/fixup_game_funcs.py` + `funcs_0.c` s626 heap-diag.
Env: `ROGUESQ_LOG_RS_MALLOC_DIAG=1`.

## This iteration's work unit

**Consume s627 freeroll (or re-run) for class-D fail136c raw free sizes — O1 vs O3.**

1. Ensure binary still has s626 diag (`grep maxfree_sane` in funcs_0.c / run log).
2. Run / consume `scratch/agent/soak_queue/s627_ltex_fail136c_freeroll.sh`
   (BUDGET=1200, RECOV_WAIT=50, same force+inject + RS_MALLOC_DIAG).
3. On scored class-D with fail136c≥1 ∧ posctrl≥1:
   - Dump free nodes (flags&1) on pools the flags=0 path uses (E8 then 0).
   - **O1** all free sizes < need=0x1370 and sane → H-ltexOOM (heap pressure)
   - **O3** free sizes ≥ need on selected pool, or size words garbage only at
     fail → H-ltexFree / other (check head4 for flags&4 noise separately)
4. Optional batch (only if fail136c already in hand): pool-aware reason string
   so flags=0x4 head4=NULL is `null_pool4` not `no_fit_mystery`.
5. Do NOT soft-skip thr12. Do NOT merge -385 with -387.

If s627 SOAK-RESULTS already has scored fail136c, skip re-run — offline-analyze
the raw `pool=` lines and close O1 or O3.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ltexmg1 | (CONFIRMED) guard LIVE | ltexmg≥1 ∧ ltex_null=0 |
| H-ltexArg | (REFUTED s625) | size=0x136C flags=0 |
| H-ltexNullPool | (REFUTED s625) | heads KSEG0 non-null |
| H-walk1 | **(CONFIRMED s626)** uint32 MEM_* garbage | sane maxfree on posctrl |
| H-ltexOOM | null = no free block ≥ 0x1370 on selected pool | fail136c free sizes all < need, sane |
| H-ltexFree | null = freelist metadata corrupt at fail | free sizes ≥ need OR garbage only at fail |
| H-recovwait1 | (CONFIRMED) | RECOV_WAIT=50 |
| H-dmarom1 | (2×) post soft-skip DMA | freeroll; not -385 root |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust pre-s626 maxfree/totfree numbers
- Leave FORCE tools default-ON
- Raise HOLD_S past 210

### Reference tags
`[rs-malloc-diag]`, `ROGUESQ_LOG_RS_MALLOC_DIAG`, `fail136c`, `posctrl`, `ok136c`,
`maxfree_sane`, `pool=`, H-walk1, H-ltexOOM, H-ltexFree, `0x136C`, `0x1370`
