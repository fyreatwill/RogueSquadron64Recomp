# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s619 recap (read this first)

**s618 freeroll classified: thr11d_new LIVE; new residual buildMaterialFreeList.**
- a1 freeroll: scenegraph 1st (same host stack as -382); thr11d_new=0
- a2 scored BASE_CTRL_PASS force6 old=5→6 recov768=7952
- **thr11d_new=1 sec4_post=1** (first LIVE) thr12=0 cshadow=0 sec2=0
- ship_store=2 ship_zero_post=2 → H-ship1z hard-block REFUTED
- scenegraph=0 readacct=0 on scored → -382/-383 stay 1× freeroll
- Crash: `buildMaterialFreeList+260` si_addr=0x380000000
  ← advanceVideoFrame ← initSceneForMission ← cinematicLoopBody
  last-guest-pc=0x800025ac STALE
- New residual **-384** (1× free-reroll)
- Soak enqueued: `s619_matfree_freeroll_classd`

Full: CURRENT-TRUTH -384; PORTING-STATE Session 619; PROJECT-OVERVIEW §27.

## This iteration's work unit

**Consume s619 soak; classify matfree 2nd vs thr12/class-D vs pipeline hold.**

1. Fold `scratch/agent/SOAK-RESULTS.md` line for `s619_matfree_freeroll_classd`.
   If absent/cancelled, requeue from done/ or rewrite.
2. **Require BASE_CTRL_PASS** (case5_n0_state ∈ {5,6}, not 255/110).
3. On recovery-active scored attempt, prefer **post-hsel** metrics only:
   thr11c_post, thr11d_new, sec4_post, thr12_post, cshadow_*, ltex,
   ship_store, ship_zero_post, scenegraph=, readacct=, **matfree=**
4. Classify:
   - **K2** matfree=1 on scored (2nd same host stack) → escalate -384
     (null-base guard at first clear-loop store; guest ~0x80021EB4 /
     base `0x80128F00` count `0x80128EF0`)
   - **G** thr11d_new≥1 ∧ sec4_post≥1 ∧ (cshadow|thr12|sec2) → class-D A–D
   - **H** scenegraph=1 on scored → escalate -382
   - **J** readacct=1 on scored → escalate -383
   - **L** thr11d_new+sec4 hold, crash=0, thr12=0 → freelist cleared / stall
   - **A–D** craft-shadow class-D when guards fire
   - **E** recovery_silent (free-reroll)
5. Cross-check local-symtab host with nm/atos before acting.
6. Do NOT remove state==5 gate. Do NOT reintroduce uint32 KSEG0 MEM bases.
7. Do NOT raise HOLD_S past 210 / soft-skip matfree/mat3inv/readacct/scenegraph
   without 2nd same host stack.
8. Do NOT merge -384 with -373 on last-guest-pc=0x800025ac (STALE).

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-thr11d1 | (CONFIRMED s619) thr11d_new under force6+recov | — |
| H-kseg3 | (CONFIRMED s617) S32 base → case5-entry matches hangar | — |
| H-force6c | (CONFIRMED s617) force old=5→6 writes real hangar | — |
| H-sg1 | (SUPPORTED) scenegraph free-reroll noise | 0 on scored |
| H-sg2 | 2nd same host stack → escalate -382 | scenegraph on scored |
| H-readacct1 | (SUPPORTED) readAccount free-reroll noise | 0 on scored |
| H-readacct2 | 2nd same host stack → escalate -383 | readacct on scored |
| H-matfree1 | freelist null-base free-reroll noise | 0 more after freeroll |
| H-matfree2 | 2nd same host stack → real residual / guard | matfree on scored a* |
| H-Dshadow1 | null load_asset walk primary class-D | guard fires ∧ thr12 |
| H-ship1 | thr11 destroy needs post-hsel ship ret=1 | SUPPORTED multi-run |
| H-ship1z | (REFUTED s619) ship-zero hard-blocks thr11d_new | — |
| H-recov1 | thr11d/sec2 requires 76B768 | SUPPORTED |
| H-force6b | FORCE_STATE6 only safe at state==5 | keep gate |

## Do NOT
- `uint32_t base = 0x800D0000` (or any zero-extended KSEG0) in MEM_* patches
- Remove state==5 FORCE_STATE6 gate
- Raise HOLD_S past 210
- Soft-skip matfree / mat3inv / scenegraph / readAccount without 2nd same host stack
- Single-chase packTlut before 2nd occ same host stack
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON
- Trust thr11d_post or whole-run thr11c/sec4 as thr11d_new/sec4_post
- Merge -384 with -373 on last-guest-pc=0x800025ac

### Reference tags
`[case5-entry]`, `[case5-force-state6]`, `[craft-shadow-asset-guard]`,
`[craft-shadow-walk-guard]`, `[level-tex-cache]`, `[ship-store]`, `[ship-zero]`,
`buildMaterialFreeList`, `0x80021EB4`, `0x80128F00`, `0x80128EF0`,
`initSceneForMission`, `advanceVideoFrame`, `readAccountForSelectionScreen`,
`0x800B85B4`, `0x8006F2CC`, `0x76B768`, thr11d_new, sec4_post, matfree
