# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s616 recap (read this first)

**FORCE_STATE6 KSEG0 base OOB root-caused and fixed.**
- s615 a2: hangar-state=5, case5-entry state=255, force_skip forever, recovery_silent
- Cause: `uint32_t base=0x800D0000` + `MEM_*` → rdram idx `0x1000CC3E7` (OOB);
  correct `S32` base → `0xCC3E7`
- s613 "force 3→6" never wrote real hangar (state stayed 5) — recharacterize -379
- Fix: `gpr base = S32(0x800D << 16)` in funcs_28.c + fixup; binary rebuilt
- Soak enqueued: `s616_force6_kseg0_base_fix` (not yet run by loop at session end)

Full: CURRENT-TRUTH -381; PORTING-STATE Session 616; PROJECT-OVERVIEW §27.

## This iteration's work unit

**Consume s616 soak (or requeue if missing); verify base fix + class-D A–D.**

1. Fold `scratch/agent/SOAK-RESULTS.md` line for `s616_force6_kseg0_base_fix`.
   If absent/cancelled, requeue the same script from soak_queue/done or rewrite.
2. **Positive control (must pass before trusting force/class-D):**
   - `[case5-entry] n=0 state=` ∈ {5,6} (or other 0..8), **not** 255/110
   - Prefer agreement with nearby `[hangar-state] state=`
   - If still garbage: binary not rebuilt / fix not linked — stop and fix build path
3. On recovery-active thr11d+sec4, score A–D (same as s615 NEXT):
   craft_shadow_asset/walk, level_tex_*, thr495FC_post, sec2_post, thr11_destroy,
   force6, force_old5, force_skip, recov76B768, ship_store
4. Classify:
   - **CTRL_FAIL** case5-entry still OOB → rebuild
   - **A** guard + thr12 + sec2 → class D dissolved
   - **B** `D_guard_thr12_no_sec2`
   - **C** `D_guard_no_thr12`
   - **D** shadow crash / guard=0
   - **E** eng + recovery_silent with CTRL pass → silence ≠ force-base; free-reroll
   - **F** recov + thr11 live (ship gate)
5. Do NOT remove state==5 gate. Do NOT reintroduce uint32 KSEG0 bases into MEM_*.
6. Do NOT raise HOLD_S past 210 / soft-skip mat3inv / single-chase packTlut.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-kseg1 | (CONFIRMED s616) uint32 base → OOB MEM | — |
| H-kseg2 | (CONFIRMED s616) s613 force never wrote real hangar | — |
| H-kseg3 | S32 base makes case5-entry match hangar-state | ctrl pass on s616 soak |
| H-force6c | with real base, force old=5→6 can write when stuck at 5 | force6=1 force_old5=1 |
| H-Dshadow1 | null load_asset walk primary class-D death | guard fires ∧ thr12 appears |
| H-Dshadow2 | soft-skip alone insufficient; loadLevelTextureCache gated | guard≥1 ∧ thr12=0 |
| H-ship1 | thr11 destroy needs post-hsel ship ret=1 | SUPPORTED multi-run |
| H-recov1 | thr11d/sec2 requires 76B768 | SUPPORTED |
| H-force6b | FORCE_STATE6 only safe at state==5 | keep gate |

## Do NOT
- `uint32_t base = 0x800D0000` (or any zero-extended KSEG0) in MEM_* patches
- Remove state==5 FORCE_STATE6 gate
- Raise HOLD_S past 210
- Soft-skip mat3inv det0 without 2nd occ + abnormal control
- Single-chase packTlut before 2nd occ same host stack
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON
- Score recovery-silent / mat3inv / matnoise as pipeline failures when free-reroll works

### Reference tags
`[case5-entry]`, `[case5-force-state6]`, `[case5-force-state6-skip]`,
`[craft-shadow-asset-guard]`, `[craft-shadow-walk-guard]`, `[level-tex-cache]`,
`[ship-store]`, `[ship-zero]`, `[ship-active]`,
`loadCraftShadowTextures`, `loadLevelTextureCache`,
`0x8006F2CC`, `0x800495FC`, `0x76B768`, `[hangar-sel]`, `[case6-force-start]`,
`site=0x800ACE80`, S32 KSEG0 base.
