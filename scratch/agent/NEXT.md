# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s611 recap (read this first)

Folded `s610_recov_mat3inv_reroll` (rc=0, 567s):
- discard_stats: pre_eng=1 matnoise=0 recov_silent=0 mat3inv=0 attempts=2
- Scored a2 class **E true stall** (not budget-truncated):
  `force6=1 case6=1 hangar-sel=1 ace80=1 inject_max_n=500
  recov76B768~=70 thr11_create=1 thr11_destroy=0 sec2_post=0
  mat3inv_entry=68 mat3inv_abnormal=0 crash=ok`
- Hold reached hold_160 (~283s); recovery ~hold_93 — past s607 destroy
  wall (game gone hold~65).
- **H-ship1 SUPPORTED:** thr11 destroy co-requires post-hsel
  `[ship-active] ret=1` (`isPlayerShipActive` @ `0x800B4264`, global
  `0x800CC85C`). Controls s592_a + s607: n=20 ship=0x8015FD90 ~655–787
  lines before thr11d. s610 + all scanned thr11-live stalls: zero
  post-hsel ret=1.
- Store site: `updateTextOverlayLookupEntry` @ `0x800B40D0`; zero in
  `destroyPlayerShipRecord`.
- Queued `s611_ship_ret1_gate` (ship_ret1 scoring + E_noship/E_ship_stall).

Full: CURRENT-TRUTH -376/-375/-361; PORTING-STATE Session 611.

## This iteration's work unit

**Fold in the `s611_ship_ret1_gate` soak result and act.**

1. Read SOAK-RESULTS + gate line for:
   `ship_ret1_post, ship_n20, ship_last, first_ship_ret1_rel,
   thr11_destroy, sec2_post, class_hint, mat3inv, recov76B768`.
2. Classify scored:
   - **A/B/C** sec2 paths (same as before; escalate -373 on B).
   - **D** thr11d+sec4 no sec2.
   - **G_thr11d_with_ship** thr11d + ship_ret1≥1 → H-ship1 co-occurrence
     reconfirmed; continue pipeline (sec2 / -373).
   - **E_noship** thr11 live + ship_ret1=0 → H-ship1 still holds; next
     code unit = instrument non-null store at `0x800B40D0`
     (`updateTextOverlayLookupEntry`) + callers post-hsel (who should
     re-arm ship and does not under force6).
   - **E_ship_stall** thr11 live + ship_ret1≥1 → **H-ship1 REFUTED** as
     necessity; pivot off ship gate, offline other post-ret1 events
     before thr11d in s607 window.
3. If ≥2 E_noship with recovery: instrument store (fixup_game_funcs.py)
   — one build, log every non-null write to `0x800CC85C` with ra.
4. Do NOT raise HOLD_S past 210. Do NOT soft-skip mat3inv (still 1×).
5. Do NOT treat last-guest-pc=0x80022160 as fault site.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ship1 | thr11 destroy requires post-hsel isPlayerShipActive ret=1 | thr11d only when ship_ret1_post≥1; E_ship_stall refutes necessity |
| H-ship1b | ship ret=1 is cause (not mere co-symptom) of thr11d | store fires then thr11d; store-without-thr11d weakens |
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

### Reference tags
`[ship-active]`, `isPlayerShipActive`, `0x800CC85C`, `0x800B40D0`,
`updateTextOverlayLookupEntry`, `destroyPlayerShipRecord`,
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC`,
`[rdp-fullsync] ... addr=0x0076B768`, `[fs-pipe-inject]`,
`[overlay] start-match: section 2` / `section 4`,
`mat3x3InverseInto`, `packTlutEntriesRgba5551`, `0x8000e29c`.
