# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s625 recap (read this first)

**H-ltexOOM instrument LIVE on recovery-active class-D; H-ltexArg + null_pool REFUTED;
free-byte walk untrusted (-388).**

### Scored SCORE (s625b att2)
- force6=1 thr11d_new=1 sec4_post=1 cshadow_a=3 ltex=1 **ltexmg=1** thr12=0
- **diag_pos=8 diag_fail136c=1 diag_ok136c=1** class_hint=M1_ltexmg_no_thr12
- fail136c: `size=0x136C flags=0x0 need=0x1370` heads KSEG0 non-null
  `head4=0x8062B800 head0=0x800B1EF0 headE8=0x80154690` reason=corrupt maxfree=GB garbage
- Same headE8 + garbage maxfree also on early **successful** posctrl/ok136c → walk model bug
- Residual **-387** again: `do_rom_read+608` ← submitDmaSlot ← processAssetLoadStep

Full: CURRENT-TRUTH -388/-385/-387; PORTING-STATE Session 625.

## This iteration's work unit

**Refine `[rs-malloc-diag]` to raw per-node header dump (fix free-byte interpretation).**

1. In fixup_game_funcs.py (and apply to funcs_0.c — fixup refuses re-run while sentinel set):
   replace free-bit/maxfree aggregation with raw dump of first ≤16 nodes per pool:
   `node=i flags=0x.. size=0x..` (and stop on flags&8, OOB next, or cap).
2. Same-run positive control still required: posctrl≥1 AND fail136c≥1 on class-D.
3. Discriminating outcomes:
   - **O1** at fail136c, all free nodes (flags&1) have size < 0x1370 and sizes look sane
     (≤ remaining RDRAM) → true heap pressure / fragmentation (H-ltexOOM)
   - **O2** size fields already garbage on early posctrl success → walk still wrong OR
     metadata layout differs; re-derive node stride from a known-good success (ptr−0x10)
   - **O3** heads/nodes KSEG0 early, garbage only at fail136c → progressive freelist
     corruption (H-ltexFree); find who wrote size words
   - **O4** posctrl silent → instrument miss
4. Optional batch: log `t0`/pools-tried at L_80001C60 (which pool failed).
5. Do NOT soft-skip thr12. Do NOT merge -385 with -387.
6. Soak: reuse s625 recipe (BUDGET≥900, RECOV_WAIT=50, freeroll non-class-D,
   `ROGUESQ_LOG_RS_MALLOC_DIAG=1`).

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ltexmg1 | (CONFIRMED) guard LIVE | ltexmg≥1 ∧ ltex_null=0 |
| H-ltexArg | (REFUTED s625) wrong size/flags | size=0x136C flags=0 |
| H-ltexNullPool | (REFUTED s625) heads null | heads KSEG0 non-null |
| H-ltexOOM | null = no free block ≥ 0x1370 | raw free sizes all < need, sane |
| H-ltexFree | null = freelist metadata corrupt | raw size words garbage only at fail |
| H-walk1 | (OPEN) free-byte walk mis-models nodes | garbage maxfree on success too |
| H-recovwait1 | (CONFIRMED) | RECOV_WAIT=50 |
| H-dmarom1 | (2× s624+s625) post soft-skip DMA | still freeroll; not root of -385 |

## Do NOT
- uint32 KSEG0 MEM bases (use S32)
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -387/-384/-373/-386
- Trust maxfree/totfree from s625 walk without raw node dump
- Leave FORCE tools default-ON
- Raise HOLD_S past 210

### Reference tags
`[rs-malloc-diag]`, `ROGUESQ_LOG_RS_MALLOC_DIAG`, `fail136c`, `posctrl`, `ok136c`,
`0x136C`, `0x8010FEFC`, `0x8010FF00`, `0x8010FF18`, `headE8`, H-ltexOOM, H-ltexFree, H-walk1
