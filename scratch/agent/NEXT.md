# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s614 recap (read this first)

Folded `s613_class_d_shadow_guard` (rc=2, 488s, **unscored**):
- pre_eng=1; force6=1 case6=0 hangar_sel=0 ace80=0 recov=0
- Root cause: `[case5-force-state6] n=40 old=3 new=6` — force wrote
  hangar state before camera-settle case5, so ACE80/case6/hangar-sel never ran
- Single attempt burned full BUDGET_S (no ENGAGE early-kill)

Landed **FORCE_STATE6 state==5 gate** (`[case5-force-state6-skip]` when old≠5/6)
+ soak `ENGAGE_WAIT_S=90` post `[case5-entry]`. Binary rebuilt.
Queued `s614_class_d_force_gate`.

Offline: s612 class-D craft-shadow crash (null walk, si_addr=0x380000000) is
still the residual after thr11d+sec4; guards at 0x8006B764/0x8006B780 are in
binary and would soft-skip that path — **live A–D classification still PENDING**.

Full: CURRENT-TRUTH -379; PORTING-STATE Session 614.

## This iteration's work unit

**Fold in the `s614_class_d_force_gate` soak result and act.**

1. Read SOAK-RESULTS + gate for:
   `force6, force_skip, craft_shadow_asset, craft_shadow_walk, level_tex_cache,
   level_tex_post, thr495FC_post, sec2_post, thr11_destroy, shadow_crash,
   class_hint, ctrl_ship_store, recov76B768, early=engage_timeout`.
2. **Engagement hygiene (s614):** if all attempts are `engage_timeout` /
   force_skip with hangar-state stuck ≠5 at case5-entry, do **not** re-chase
   FORCE_STATE6 — file as engagement flake and offline-map case5-entry
   state-read vs hangar-state discrepancy (s613 saw hangar-state=5 /
   case5-entry=3 same window). Prefer natural ACE80 path evidence from s612.
3. **Positive control:** on thr11d+sec4 scored path, expect
   `craft_shadow_asset+walk ≥ 1` OR `level_tex_post ≥ 1` OR thr12.
   If all zero and same shadow crash → instrument dead; fix first.
4. Classify scored path:
   - **A** guard fires + thr12 + sec2 → class D dissolved; escalate -373 if packTlut
   - **B** `D_guard_thr12_no_sec2` → past shadow; residual thr12→sec2 handoff
   - **C** `D_guard_no_thr12` → still not reaching loadLevelTextureCache
   - **D** `D_shadow_crash` / guard=0 → different fault or instrument miss
5. If C with guard fire: offline map who calls loadLevelTextureCache post-sec4
   (s607 window) and what state it needs; do not soft-skip further without 2nd path.
6. Do NOT raise HOLD_S past 210. Do NOT soft-skip mat3inv. Do NOT chase packTlut
   single occ. Do NOT treat last-guest-pc=0x800290d4 as fault site.
7. Do NOT re-ungate FORCE_STATE6 to write when old≠5.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ship1 | thr11 destroy requires post-hsel isPlayerShipActive ret=1 | SUPPORTED multi-run |
| H-ship1b | ship ret=1 is cause (not mere co-symptom) of thr11d | E_store_no_thr11d weakens |
| H-ship1c | post-hsel re-arm is updateTextOverlayLookupEntry when CC864 live | SUPPORTED s612 store_at_hsel |
| H-Dshadow1 | null load_asset walk is primary class-D death before thr12 | guard fires ∧ thr12 appears |
| H-Dshadow2 | soft-skip alone insufficient; loadLevelTextureCache still gated | guard≥1 ∧ thr12=0 |
| H-thr12a | thr12 create ≡ loadLevelTextureCache entry | level_tex_post≥1 ↔ thr495FC_post≥1 |
| H-force6b | FORCE_STATE6 only safe when hangar state==5; force from 3 blocks exit | s613 hang vs s614 skip+eng |
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
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC` / `0x800495FC`,
`[rdp-fullsync] ... addr=0x0076B768`, `[overlay] start-match: section 2` / `4`.
