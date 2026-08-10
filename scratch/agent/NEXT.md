# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s613 recap (read this first)

Folded `s612_ship_store_gate` (rc=1, 289s, recovery-active):
- **class D** thr11d+sec4, thr12=0, sec2=0
- ctrl_ship_store=1; store_at_hsel=0x8015FD90; ship_ret1_post=1
- H-ship1c SUPPORTED; H-ship1 re-confirmed on G path
- Crash: loadCraftShadowTextures null load_asset walk (si_addr=0x380000000)
- thr12 parent = loadLevelTextureCache only

Landed always-on soft-skip `[craft-shadow-asset-guard]` / `[craft-shadow-walk-guard]`
+ `[level-tex-cache]` entry. Binary rebuilt. Queued `s613_class_d_shadow_guard`.

Full: CURRENT-TRUTH -378; PORTING-STATE Session 613.

## This iteration's work unit

**Fold in the `s613_class_d_shadow_guard` soak result and act.**

1. Read SOAK-RESULTS + gate for:
   `craft_shadow_asset, craft_shadow_walk, level_tex_cache, level_tex_post,
   thr495FC_post, sec2_post, thr11_destroy, shadow_crash, class_hint,
   ctrl_ship_store, recov76B768`.
2. **Positive control:** on thr11d+sec4 scored path, expect
   `craft_shadow_asset+walk ≥ 1` OR `level_tex_post ≥ 1` OR thr12.
   If all zero and same shadow crash → instrument dead; fix first.
3. Classify:
   - **A** guard fires + thr12 + sec2 → class D dissolved; escalate -373 if packTlut
   - **B** `D_guard_thr12_no_sec2` → past shadow; residual thr12→sec2 handoff
   - **C** `D_guard_no_thr12` → still not reaching loadLevelTextureCache
   - **D** `D_shadow_crash` / guard=0 → different fault or instrument miss
4. If C with guard fire: offline map who calls loadLevelTextureCache post-sec4
   (s607 window) and what state it needs; do not soft-skip further without 2nd path.
5. Do NOT raise HOLD_S past 210. Do NOT soft-skip mat3inv. Do NOT chase packTlut
   single occ. Do NOT treat last-guest-pc=0x800290d4 as fault site.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ship1 | thr11 destroy requires post-hsel isPlayerShipActive ret=1 | SUPPORTED multi-run |
| H-ship1b | ship ret=1 is cause (not mere co-symptom) of thr11d | E_store_no_thr11d weakens |
| H-ship1c | post-hsel re-arm is updateTextOverlayLookupEntry when CC864 live | SUPPORTED s612 store_at_hsel |
| H-Dshadow1 | null load_asset walk is primary class-D death before thr12 | guard fires ∧ thr12 appears |
| H-Dshadow2 | soft-skip alone insufficient; loadLevelTextureCache still gated | guard≥1 ∧ thr12=0 |
| H-thr12a | thr12 create ≡ loadLevelTextureCache entry | level_tex_post≥1 ↔ thr495FC_post≥1 |
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

### Reference tags
`[craft-shadow-asset-guard]`, `[craft-shadow-walk-guard]`, `[level-tex-cache]`,
`[ship-store]`, `[ship-zero]`, `[ship-active]`,
`loadCraftShadowTextures`, `loadLevelTextureCache`, `hudDisplayUpdateWorker`,
`0x800495FC`, `0x8006B764`, `0x8006B780`, `0x8004810C`,
`updateHangarBayScene`, `runModelViewerLoop`, `registerServiceWorker`,
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC` / `0x800495FC`,
`[rdp-fullsync] ... addr=0x0076B768`, `[overlay] start-match: section 2` / `4`.
