# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s617 recap (read this first)

**FORCE_STATE6 KSEG0 S32 base fix LIVE-VERIFIED (-381 CLOSED).**
- s616 soak: case5_n0_state=5, force6=1 force_old5=1, hangar 5→6→8
- Class-D A–D NOT reached: thr11 id=11 created post-hsel, never destroyed
- sec4 whole-run=1 was early cinematic only (sec4_post=0)
- New residual -382: traverseSceneGraphRecursive SIGBUS (guest 0x8000f421 /
  si_addr 0x38000f421) before thr11d — 1× free-reroll
- Soak enqueued: `s617_scenegraph_freeroll_classd` (not yet run at session end)

Full: CURRENT-TRUTH -382/-381; PORTING-STATE Session 617; PROJECT-OVERVIEW §27.

## This iteration's work unit

**Consume s617 soak; classify thr11d vs scene-graph 2nd-occ vs class-D.**

1. Fold `scratch/agent/SOAK-RESULTS.md` line for `s617_scenegraph_freeroll_classd`.
   If absent/cancelled, requeue from done/ or rewrite.
2. **Require BASE_CTRL_PASS** still (case5_n0_state ∈ {5,6}, not 255/110).
3. On recovery-active scored attempt, prefer **post-hsel** metrics only:
   thr11c_post, thr11d_post, sec4_post, thr12_post, cshadow_*, ltex,
   ship_store, ship_zero_post, scenegraph=
4. Classify:
   - **G** thr11d_post≥1 ∧ sec4_post≥1 ∧ (cshadow|thr12|sec2) → class-D A–D path
   - **H** scenegraph=1 on scored (2nd same host stack) → escalate -382 (node ptr audit)
   - **I** thr11c_post≥1 thr11d_post=0 no crash / other crash → ship-zero / handoff
   - **A–D** craft-shadow class-D as s615 when guards fire
   - **E** recovery_silent (free-reroll already)
5. Do NOT remove state==5 gate. Do NOT reintroduce uint32 KSEG0 MEM bases.
6. Do NOT raise HOLD_S past 210 / soft-skip mat3inv / single-chase packTlut.
7. Do NOT treat whole-run thr11c/sec4 as thr11d evidence.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-kseg3 | (CONFIRMED s617) S32 base → case5-entry matches hangar | — |
| H-force6c | (CONFIRMED s617) force old=5→6 writes real hangar | — |
| H-sg1 | scenegraph SIGBUS is free-reroll noise (1×) | 0 more hits after freeroll |
| H-sg2 | 2nd same host stack → real residual needing guard | scenegraph on scored a* |
| H-Dshadow1 | null load_asset walk primary class-D death | guard fires ∧ thr12 appears |
| H-ship1 | thr11 destroy needs post-hsel ship ret=1 | SUPPORTED multi-run |
| H-ship1z | post-hsel ship-zero blocks thr11d of new thr11 | thr11c_post≥1 thr11d_post=0 |
| H-recov1 | thr11d/sec2 requires 76B768 | SUPPORTED |
| H-force6b | FORCE_STATE6 only safe at state==5 | keep gate |

## Do NOT
- `uint32_t base = 0x800D0000` (or any zero-extended KSEG0) in MEM_* patches
- Remove state==5 FORCE_STATE6 gate
- Raise HOLD_S past 210
- Soft-skip mat3inv / scenegraph without 2nd same host stack
- Single-chase packTlut before 2nd occ same host stack
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON
- Trust whole-run thr11c/sec4 as post-hsel thr11d/sec4

### Reference tags
`[case5-entry]`, `[case5-force-state6]`, `[craft-shadow-asset-guard]`,
`[craft-shadow-walk-guard]`, `[level-tex-cache]`, `[ship-store]`, `[ship-zero]`,
`[scene-traverse-entry]`, `traverseSceneGraphRecursive`, `setupCameraMatrices`,
`runModelViewerLoop`, `0x8006F2CC`, `0x800495FC`, `0x76B768`, `0x8000f421`,
`si_addr=0x38000f421`, thr11d_post, sec4_post.
