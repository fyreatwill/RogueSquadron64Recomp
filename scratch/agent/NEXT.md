# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s618 recap (read this first)

**s617 freeroll classified: thr11d_post was false positive; true crash is readAccount.**
- BASE_CTRL_PASS force6 old=5→6 recov768=7952 recovery-active scored
- scenegraph=0 → H-sg1 SUPPORTED (-382 stays 1× free-reroll soft-park)
- thr11c_post=1; thr11d_post=1 counted destroy of **old** thr11 id=10; **new id=11 never destroyed** (thr11d_new=0)
- sec4_post=0 thr12=0 cshadow=0; ship_store=1 ship_zero_post=1
- Crash local-symtab `rebuildActiveDisplayObjectList+540` is **WRONG**
- nm/atos: `readAccountForSelectionScreen+604` (guest `0x800B85B4`);
  si_addr=0x3811c000e x9=0x811c000e; last-guest-pc=0x80022160 STALE
- Caller: `menuControllerInput` jump-table **case 1** (local s6=6 ≠ hangar state 6)
- New residual **-383** (1× free-reroll)
- Soak enqueued: `s618_readacct_freeroll_classd` (thr11d_new + readacct freeroll)

Full: CURRENT-TRUTH -383/-382; PORTING-STATE Session 618; PROJECT-OVERVIEW §27.

## This iteration's work unit

**Consume s618 soak; classify thr11d_new vs readacct 2nd-occ vs class-D.**

1. Fold `scratch/agent/SOAK-RESULTS.md` line for `s618_readacct_freeroll_classd`.
   If absent/cancelled, requeue from done/ or rewrite.
2. **Require BASE_CTRL_PASS** (case5_n0_state ∈ {5,6}, not 255/110).
3. On recovery-active scored attempt, prefer **post-hsel** metrics only:
   thr11c_post, **thr11d_new** (not thr11d_post), sec4_post, thr12_post,
   cshadow_*, ltex, ship_store, ship_zero_post, scenegraph=, readacct=
4. Classify:
   - **G** thr11d_new≥1 ∧ sec4_post≥1 ∧ (cshadow|thr12|sec2) → class-D A–D path
   - **H** scenegraph=1 on scored (2nd same host stack) → escalate -382
   - **J** readacct=1 on scored (2nd same host stack) → escalate -383
     (site audit: menuControllerInput case 1 / getAccount* / KSEG0 idiom)
   - **I** thr11c_post≥1 thr11d_new=0 no crash / other crash → ship-zero / handoff
   - **A–D** craft-shadow class-D as s615 when guards fire
   - **E** recovery_silent (free-reroll already)
5. Cross-check any local-symtab `rebuildActiveDisplayObjectList+540` with
   `nm -n build/RogueSquadron64Recomp | grep readAccount` / atos before acting.
6. Do NOT remove state==5 gate. Do NOT reintroduce uint32 KSEG0 MEM bases.
7. Do NOT raise HOLD_S past 210 / soft-skip mat3inv/readacct/scenegraph without 2nd.
8. Do NOT treat thr11d_post (any thr-destroy after hsel) as thr11d evidence.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-kseg3 | (CONFIRMED s617) S32 base → case5-entry matches hangar | — |
| H-force6c | (CONFIRMED s617) force old=5→6 writes real hangar | — |
| H-sg1 | (SUPPORTED s618) scenegraph SIGBUS free-reroll noise | 0 more hits |
| H-sg2 | 2nd same host stack → escalate -382 | scenegraph on scored a* |
| H-readacct1 | readAccount OOB is free-reroll noise | 0 more after freeroll |
| H-readacct2 | 2nd same host stack → real residual | readacct on scored a* |
| H-Dshadow1 | null load_asset walk primary class-D death | guard fires ∧ thr12 |
| H-ship1 | thr11 destroy needs post-hsel ship ret=1 | SUPPORTED multi-run |
| H-ship1z | post-hsel ship-zero blocks thr11d of new thr11 | thr11c_post≥1 thr11d_new=0 |
| H-recov1 | thr11d/sec2 requires 76B768 | SUPPORTED |
| H-force6b | FORCE_STATE6 only safe at state==5 | keep gate |

## Do NOT
- `uint32_t base = 0x800D0000` (or any zero-extended KSEG0) in MEM_* patches
- Remove state==5 FORCE_STATE6 gate
- Raise HOLD_S past 210
- Soft-skip mat3inv / scenegraph / readAccount without 2nd same host stack
- Single-chase packTlut before 2nd occ same host stack
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON
- Trust thr11d_post or whole-run thr11c/sec4 as thr11d_new/sec4_post
- Trust local-symtab rebuild+540 without nm/atos

### Reference tags
`[case5-entry]`, `[case5-force-state6]`, `[craft-shadow-asset-guard]`,
`[craft-shadow-walk-guard]`, `[level-tex-cache]`, `[ship-store]`, `[ship-zero]`,
`readAccountForSelectionScreen`, `menuControllerInput`, `0x800B85B4`,
`rebuildActiveDisplayObjectList` (mislabel only), `0x8006F2CC`, `0x76B768`,
`si_addr=0x3811c000e`, thr11d_new, sec4_post.
