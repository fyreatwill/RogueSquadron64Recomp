# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s612 recap (read this first)

Folded `s611_ship_ret1_gate` (rc=2, 562s): **no recovery-active score**
(pre_eng=4 matnoise=1). a2 eng then material-noise before 76B768.

Landed gPlayerShip writer instrument (item -377):
- `[ship-store]` @ `0x800B40D0` (only non-null writer; when current is null)
- `[ship-zero]` @ `0x800B42A8`
- `[ship-store-skip]` @ non-null branch (rate-limited)
Binary rebuilt. Queued `s612_ship_store_gate`.

H-ship1 still SUPPORTED offline (s592_a+s607 thr11d have post-hsel ret=1;
s610 stall does not). H-ship1b (cause vs co-symptom) needs store timeline.

Full: CURRENT-TRUTH -377/-376/-361; PORTING-STATE Session 612.

## This iteration's work unit

**Fold in the `s612_ship_store_gate` soak result and act.**

1. Read SOAK-RESULTS + gate line for:
   `ctrl_ship_store, ship_store_all, ship_store_post_nz, ship_zero_post,
   store_at_hsel, first_store_post_val, ship_ret1_post, thr11_destroy,
   sec2_post, class_hint, mat3inv, recov76B768`.
2. **Positive control first:** `ctrl_ship_store` must be 1 (menu-path store
   before/at hangar). If 0 on a scored eng path → instrument dead; fix before
   any H-ship1b claim.
3. Classify scored:
   - **A/B/C** sec2 paths (same as before; escalate -373 on B).
   - **D** thr11d+sec4 no sec2.
   - **G_thr11d_with_ship** thr11d + (ship_ret1≥1 or ship_store_post_nz≥1)
     → log store→destroy gap; map host= to caller if possible.
   - **E_noship** thr11 live + ship_store_post_nz=0 → re-arm missing; offline
     which callers of updateTextOverlayLookupEntry should run post-hsel under
     force6 (`runModelViewerLoop` is prime) and do not.
   - **E_store_no_thr11d** thr11 live + store_nz≥1 → H-ship1b weakened
     (store without destroy); ship is co-symptom not cause.
   - **store_at_hsel val=0** → hangar-sel path copies null texture target;
     re-arm depends on a later call when `0x800CC864` is live.
4. If ≥1 E_noship with ctrl_store=1 and recovery: map host addresses of any
   post-hsel skip/store to callers (atos / nm on binary).
5. Do NOT raise HOLD_S past 210. Do NOT soft-skip mat3inv. Do NOT chase
   packTlut single occ. Do NOT treat last-guest-pc=0x80022160 as fault site.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ship1 | thr11 destroy requires post-hsel isPlayerShipActive ret=1 | thr11d only when ship_ret1_post≥1; E_ship_stall refutes necessity |
| H-ship1b | ship ret=1 is cause (not mere co-symptom) of thr11d | store fires then thr11d; E_store_no_thr11d weakens |
| H-ship1c | post-hsel re-arm is updateTextOverlayLookupEntry store when CC864 live | post-hsel ship-store val=0x8015FD90 on thr11d path |
| H-recov1 | (SUPPORTED) thr11 destroy/sec2 requires 76B768 | thr11_destroy∧sec2 only when recov768≥1 |
| H-sec2a | force6+inject+76B768 yields sec2 when noise absent | sec2_post≥1 on recovery-active non-noise |
| H-sec2b | post-sec2 death is stable packTlut/HMT path (-373) | same host stack 2× |
| H-mat3inv1 | post-exit cutscene hits singular/NaN det in mat3inv | mat3inv_abnormal≥1 same-run as Abort stack |
| H-mat3inv2 | (SUPPORTED) mat3inv Abort intermittent under force6 | free-reroll yields non-mat3inv scored path |
| H-handoff2 | (REFUTED s608) 76BA90 required for thr11 destroy | — |
| H-handoff3 | (SUPPORTED s608) thr11 destroy after 76B768 alone | thr11_destroy ∧ recov76BA90=0 |
| H-force6a | (CONFIRMED) state=6 force unlocks case6+hangar-sel | force6∧case6∧hsel |

## Do NOT
- Raise HOLD_S past 210.
- Soft-skip mat3inv det0 without 2nd occ + abnormal control.
- Single-chase packTlut before 2nd occ same host stack.
- Re-require 76BA90 for thr11 destroy.
- Score recovery-silent / mat3inv / matnoise as pipeline failures.
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON.
- Chase waitForAnyAudioSlot+244 (item -362).
- Treat class E as budget artifact without hold_N vs s607 hold~65.
- Claim H-ship1b without same-run ctrl_ship_store=1.

### Reference tags
`[ship-store]`, `[ship-zero]`, `[ship-store-skip]`,
`[ship-active]`, `isPlayerShipActive`, `0x800CC85C`, `0x800CC864`,
`0x800B40D0`, `0x800B42A8`, `0x800B4068`,
`updateTextOverlayLookupEntry`, `destroyPlayerShipRecord`,
`runModelViewerLoop`, `[case5-force-state6]`, `[case6-force-start]`,
`[hangar-sel]`, `[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC`,
`[rdp-fullsync] ... addr=0x0076B768`, `[fs-pipe-inject]`,
`[overlay] start-match: section 2` / `section 4`,
`mat3x3InverseInto`, `packTlutEntriesRgba5551`, `0x8000e29c`.
