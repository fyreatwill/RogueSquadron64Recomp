# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s620 recap (read this first)

**s619 soak folded: class-D LIVE; primary residual null rs_malloc in thr12 parent.**
- a1 freeroll: mat3inv/scenegraph; thr11d_new=0 recovery_silent
- a2 scored BASE_CTRL_PASS force6 old=5→6 recov768=7948
- **thr11d_new=1 sec4_post=1** (reconfirmed) thr12=0 sec2=0
- **cshadow_a=3 ltex=1** → class-D path ENTERED (asset-guard soft-skips)
- matfree=0 → **H-matfree1 SUPPORTED** (-384 stays 1× freeroll)
- Crash: `loadLevelTextureCache+2576` si_addr=0x380001054
  ← load_cutscene ← cinematicLoopBody
  guest 0x80048250 fill after **rs_malloc(0x136C)=NULL** (s0=0, s1=0xFFF)
- New residual **-385**; guard landed `[level-tex-malloc-guard]` → L_8004840C
- Soft-skip returns before registerServiceWorker → thr12 still not created when null
- Soak enqueued: `s620_ltex_malloc_guard_classd`

Full: CURRENT-TRUTH -385; PORTING-STATE Session 620.

## This iteration's work unit

**Consume s620 soak; live-verify level-tex-malloc-guard; classify thr12 vs OOM.**

1. Fold `scratch/agent/SOAK-RESULTS.md` line for `s620_ltex_malloc_guard_classd`.
   If absent/cancelled, requeue from done/ or rewrite.
2. **Require BASE_CTRL_PASS** (case5_n0_state ∈ {5,6}, not 255/110).
3. On recovery-active scored attempt, prefer **post-hsel** metrics only:
   thr11d_new, sec4_post, thr12_post, cshadow_*, ltex, **ltexmg**, ltex_null,
   ship_store, ship_zero_post, scenegraph=, readacct=, matfree=
4. Classify:
   - **M1** ltexmg≥1 ∧ ltex_null=0 → guard LIVE-VERIFIED (-385)
   - **M2** ltex_null=1 → guard miss / binary stale — rebuild path wrong
   - **M1+thr12** ltexmg≥1 ∧ thr12_post≥1 → unexpected (guard skips worker);
     investigate alternate thr12 create path
   - **G** thr11d_new+sec4 + cshadow, thr12=0, ltexmg=0 — never reached fill
     (different crash earlier)
   - **K2** matfree=1 on scored → escalate -384
   - **H/J** scenegraph/readacct on scored → escalate -382/-383
   - **E** recovery_silent (free-reroll)
5. If M1 confirmed and thr12 still 0: next unit is **why rs_malloc(0x136C) is
   null** (instrument heap free head / first malloc size / return at 0x80048240
   — one build with positive control), not more soft-skips past thr12 create.
6. Do NOT remove state==5 gate. Do NOT reintroduce uint32 KSEG0 MEM bases.
7. Do NOT raise HOLD_S past 210.
8. Do NOT merge -385 with -384 or -373.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-thr11d1 | (CONFIRMED) thr11d_new under force6+recov | — |
| H-kseg3 | (CONFIRMED) S32 base → case5-entry matches hangar | — |
| H-force6c | (CONFIRMED) force old=5→6 writes real hangar | — |
| H-matfree1 | (SUPPORTED s620) freelist 1× freeroll noise | 0 more matfree scored |
| H-matfree2 | 2nd same host stack → escalate -384 | matfree on scored |
| H-Dshadow1 | (partial) asset-guard fires; walk not primary death | cshadow_a ∧ thr12 blocked at malloc |
| H-ltexmg1 | null-malloc guard LIVE on class-D entry | ltexmg≥1 on scored |
| H-ltexOOM | rs_malloc null = heap pressure not bad size | free-head / size log |
| H-ship1 | thr11 destroy needs post-hsel ship ret=1 | SUPPORTED |
| H-ship1z | (REFUTED) ship-zero hard-blocks thr11d_new | — |
| H-recov1 | thr11d/sec2 requires 76B768 | SUPPORTED |
| H-force6b | FORCE_STATE6 only safe at state==5 | keep gate |
| H-sg1 / H-readacct1 | freeroll noise | 0 on scored |

## Do NOT
- `uint32_t base = 0x800D0000` (or any zero-extended KSEG0) in MEM_* patches
- Remove state==5 FORCE_STATE6 gate
- Raise HOLD_S past 210
- Soft-skip thr12 creation without fixing the null alloc
- Single-chase packTlut before 2nd occ same host stack
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON
- Trust thr11d_post or whole-run thr11c/sec4 as thr11d_new/sec4_post
- Merge -385 with -384/-373 on last-guest-pc

### Reference tags
`[level-tex-malloc-guard]`, `[level-tex-cache]`, `[craft-shadow-asset-guard]`,
`[craft-shadow-walk-guard]`, `loadLevelTextureCache`, `0x80048248`, `0x80048250`,
`0x80048240`, `rs_malloc`, `0x136C`, `registerServiceWorker`, `0x800495FC`,
`0x8006F2CC`, `0x76B768`, thr11d_new, sec4_post, thr12_post, ltexmg
