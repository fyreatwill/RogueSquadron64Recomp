# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s605 recap (read this first)

Folded `s604_item338_item361_hold180_budgetfix` (600s, rc=137 hard-cap):
budget `START_FLOOR_S=100` **WORKED** (A3 started) but **0/3 engagement**
(0 ACE80 at hangar state=5). A1 `0x800ab068` hangarTickCameraOrbit; A2
`0x80054750` tickWrappingTimerAccumulatorList; A3 alive-stall c5≈186 no
ACE80. s603+s604 = 0/5 ACE80. Landed `ROGUESQ_FORCE_STATE6_AFTER` (default
OFF) at case5-entry; binary rebuilt; queued
`s605_force_state6_dual_target`.

Full: CURRENT-TRUTH -370; PORTING-STATE Session 605.

## This iteration's work unit

**Fold in the `s605_force_state6_dual_target` soak result and act.**

1. Read SOAK-RESULTS.md line + scored-attempt gate (if any):
   `case5-force-state6`, `case6-force-start`, `hangar-sel`,
   `beginframe_s0_guard`, `thr11_destroy`, `sec4_post`, `inject_max_n`,
   `recov76B768`, `coalesce_guard2_r2`, `crash`, `crash_pc`, `class_hint`.
2. Classify (recipe header):
   - **A** force6 + beginframe_s0_guard>=1 + no `0x8000afa0` → -338 confirm 1/2.
   - **B** thr11_destroy=1 + sec4_post>=1 + coalesce_guard2_r2>=1 + no crash
     at `0x8000247c` → -361 confirm 1/2; queue 2nd confirm.
   - **C** engaged (case6+hsel) + thr11_destroy=0 at HOLD end → recovery-cell
     pivot (H-recov*); do NOT raise HOLD_S past 210.
   - **D** thr11 destroy + sec4_post + other crash → file breadcrumb.
   - **E** force6 fires but case6=0 or hangar-sel=0 → state-byte write not
     enough for case6 path; instrument why ACE94 never runs.
   - **F** force6 never fires with case5-entry n>=40 → env/build miss
     (positive control fail); re-check binary + GAME_EXTRA_ENV.
   - **G** 0 engagement after ≥4 attempts with force armed → deeper block.
3. If B or A: queue one confirm soak only.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-force6a | Writing state=6 at case5 n=40 unlocks case6 + FORCE_CASE6_START | force6>=1 ∧ case6>=1 ∧ hangar-sel>=1 |
| H-force6b | Force unlocks exit but thr-11 still never destroys without recovery cell | thr11_destroy rate under force+inject vs s589 |
| H-recov1 | Recovery cell `0x76B768` required for cutscene advance that stops thr-11 | thr11_destroy: recov>0 vs recov=0 at equal HOLD |

## Do NOT
- Raise HOLD_S past 210.
- Re-characterize -338 from the 5 historical logs (done s600).
- Chase `waitForAnyAudioSlot+244` (item -362) or item -306 deep-hangar
  recurrence as a new single-crash guard (M3 = idiom-class audits only).
- Treat thr495FC_creates as post-exit thr-12 (boot-only).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-arm default stick schedule (no-sticks works when ACE80 settles).
- Leave FORCE_STATE6_AFTER default-ON (keep env-gated until 2/2 confirm).

### Reference tags
`[case5-force-state6]`, `[case5-entry]`, `[case6-force-start]`,
`[beginframe-s0-guard]`, `[hangar-sel]`, `[state-write] site=0x800ACE80`,
`[buttons-hangar] site=0x800ACE94`, `[thr-create]`/`[thr-destroy]`
entry=`0x8006F2CC`, `[rdp-fullsync] ... addr=0x0076B768`, `[fs-pipe-inject]`,
`[overlay] start-match: section 4`, `[coalesce-heap-r2-guard]`,
`[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`.
