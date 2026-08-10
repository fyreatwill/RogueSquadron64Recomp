# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s615 recap (read this first)

**Maintenance iteration** (CURRENT-TRUTH 60203 → 25368 bytes, −342 lines).
Migrated thr11→sec2 arc to PROJECT-OVERVIEW §27. Folded
`s614_class_d_force_gate` (rc=2, 564s, **unscored**):
- a1 force_skip pre_eng; a2 **natural engage** case6+hsel+ace80 with force6=0
  then recovery_silent; a3 pre_eng budget
- FORCE_STATE6 state==5 gate working (H-force6b partial); natural ACE80 without
  force-write; H-Dshadow1 still PENDING (no thr11d scored path)

Full: CURRENT-TRUTH -380; PORTING-STATE Session 615; PROJECT-OVERVIEW §27.

## This iteration's work unit

**Requeue + fold a recovery-active class-D soak; classify A–D on thr11d+sec4.**

1. Enqueue (or re-use) a self-contained soak that arms the same force6-gated
   recipe as s614 (`FORCE_STATE6_AFTER` with state==5 gate, `FS_PIPE_INJECT`,
   case6, ENGAGE_WAIT_S=90, RECOV_WAIT free-reroll, HOLD_S≤180/210).
   Prefer more attempts / same budget over longer HOLD.
2. On recovery-active thr11d+sec4, score:
   `craft_shadow_asset, craft_shadow_walk, level_tex_cache, level_tex_post,
   thr495FC_post, sec2_post, thr11_destroy, shadow_crash, class_hint,
   ctrl_ship_store, recov76B768, force6, force_skip`.
3. **Positive control:** thr11d+sec4 path must show
   `craft_shadow_asset+walk ≥ 1` OR `level_tex_post ≥ 1` OR thr12 — else
   instrument dead, fix first.
4. Classify:
   - **A** guard fires + thr12 + sec2 → class D dissolved; escalate -373 if packTlut
   - **B** `D_guard_thr12_no_sec2` → past shadow; residual thr12→sec2
   - **C** `D_guard_no_thr12` → not reaching loadLevelTextureCache
   - **D** `D_shadow_crash` / guard=0 → different fault or instrument miss
5. If only recovery_silent / pre_eng / matnoise: free-reroll is working; do **not**
   chase FORCE_STATE6 or raise HOLD. Optionally offline-map case5-entry vs
   hangar-state discrepancy only if force_skip dominates *and* natural ACE80
   also fails for 2+ engaged runs.
6. Do NOT raise HOLD_S past 210. Do NOT soft-skip mat3inv. Do NOT chase packTlut
   single occ. Do NOT re-ungate FORCE_STATE6 to write when old≠5.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ship1 | thr11 destroy requires post-hsel isPlayerShipActive ret=1 | SUPPORTED multi-run |
| H-ship1b | ship ret=1 is cause (not mere co-symptom) of thr11d | E_store_no_thr11d weakens |
| H-ship1c | post-hsel re-arm is updateTextOverlayLookupEntry when CC864 live | SUPPORTED s612 |
| H-Dshadow1 | null load_asset walk is primary class-D death before thr12 | guard fires ∧ thr12 appears |
| H-Dshadow2 | soft-skip alone insufficient; loadLevelTextureCache still gated | guard≥1 ∧ thr12=0 |
| H-thr12a | thr12 create ≡ loadLevelTextureCache entry | level_tex_post≥1 ↔ thr495FC_post≥1 |
| H-force6b | FORCE_STATE6 only safe when hangar state==5; natural ACE80 OK without write | s614 force_skip+eng partial |
| H-recov1 | (SUPPORTED) thr11 destroy/sec2 requires 76B768 | — |
| H-sec2a | force6+inject+76B768 yields sec2 when noise absent | sec2_post≥1 |
| H-sec2b | post-sec2 death is stable packTlut/HMT path (-373) | same host stack 2× |
| H-force6a | (CONFIRMED) state=6 force unlocks case6+hangar-sel | — |

## Do NOT
- Raise HOLD_S past 210.
- Soft-skip mat3inv det0 without 2nd occ + abnormal control.
- Single-chase packTlut before 2nd occ same host stack.
- Re-require 76BA90 for thr11 destroy.
- Score recovery-silent / mat3inv / matnoise as pipeline failures.
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON.
- Treat last-guest-pc=0x800290d4 as the craft-shadow fault site.
- Claim H-ship1b causal without E_store_no_thr11d.
- Force hangar state 3→6 (or any old≠5).

### Reference tags
`[case5-force-state6]`, `[case5-force-state6-skip]`,
`[craft-shadow-asset-guard]`, `[craft-shadow-walk-guard]`, `[level-tex-cache]`,
`[ship-store]`, `[ship-zero]`, `[ship-active]`,
`loadCraftShadowTextures`, `loadLevelTextureCache`, `hudDisplayUpdateWorker`,
`0x800495FC`, `0x8006B764`, `0x8006B780`, `0x8004810C`,
`updateHangarBayScene`, `runModelViewerLoop`, `registerServiceWorker`,
`[case6-force-start]`, `[hangar-sel]`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC` / `0x800495FC`,
`[rdp-fullsync] ... addr=0x0076B768`, `[overlay] start-match: section 2` / `4`.
