# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s606 recap (read this first)

Folded `s605_force_state6_dual_target` (399s, rc=1): **H-force6a CONFIRMED**
(force6→ACE80→case6→hangar-sel). thr11→sec4 RECHARACTERIZED: not "76B768
sufficient" (H-recov1 sufficiency REFUTED). Control s592_a timeline post
hangar-sel: thr10 destroy~+0.8k → thr11 create~+0.9k → inject~+9k →
76B768~+20k..+87k → **76BA90@+95599** → thr11 destroy@+96337 → sec4@+96340
→ item -361 R2 crash. s605: same through 76B768 die@+86k, then crash@+89961
at `findOrCreateMaterial+776` / guest `0x8000e29c` (NEW vs prior material
noise `0x80010b7c`) with **0× 76BA90**. Queued
`s606_handoff_76ba90_dual_target`.

Full: CURRENT-TRUTH -371; PORTING-STATE Session 606.

## This iteration's work unit

**Fold in the `s606_handoff_76ba90_dual_target` soak result and act.**

1. Read SOAK-RESULTS.md line + scored gate fields:
   `force6, case6, hangar-sel, recov76B768, recov76BA90, last_768_rel,
   first_a90_rel, thr11_destroy, thr11_destroy_rel, sec4_post, crash,
   crash_pc, crash_rel, class_hint`.
2. Classify (recipe header):
   - **A** 76BA90 + thr11_destroy + sec4_post + g2 + ok → -361 confirm 1/2.
   - **B** 76BA90 + thr11_destroy + sec4 + crash `0x8000247c` → r2 path.
   - **C** 76BA90 + thr11_destroy + sec4 + other crash → file breadcrumb.
   - **D** 76BA90 but thr11_destroy=0 → handoff not sufficient (pivot).
   - **E** last_768>0, no 76BA90, gap crash → H-handoff1; file if new PC;
     do not single-chase; if `0x8000e29c` 2nd occ, note recurrence only.
   - **F** 76B768 never dies / stuck mid-phase at HOLD end.
   - **G** engagement/force miss.
3. If A or B: queue one confirm soak only. Do NOT raise HOLD_S past 210.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-handoff1 | Gap crash (material/FS) aborts before 76BA90 handoff | crash_rel < first_a90_rel ∨ (no a90 ∧ crash in post-768 gap) |
| H-handoff2 | 76BA90 handoff is required before thr11 destroy | thr11_destroy only when first_a90_rel >= 0 |
| H-handoff3 | thr11 destroy is independent of 76BA90 once 768 dies | thr11_destroy with recov76BA90=0 |
| H-force6a | (CONFIRMED s606) state=6 force unlocks case6+hangar-sel | force6∧case6∧hsel |

## Do NOT
- Raise HOLD_S past 210.
- Treat thr10 destroy (hangar-exit churn) as the sec4 gate — only post-create
  thr11 destroy counts.
- Re-characterize -338 from the 5 historical logs (done s600).
- Chase `waitForAnyAudioSlot+244` (item -362) or single-crash material
  `0x8000e29c` as a new guard (M3 = idiom-class audits only; file recurrence).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-arm default stick schedule.
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON.

### Reference tags
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[beginframe-s0-guard]`, `[state-write] site=0x800ACE80`,
`[buttons-hangar] site=0x800ACE94`, `[thr-create]`/`[thr-destroy]`
entry=`0x8006F2CC`, `[rdp-fullsync] ... addr=0x0076B768` /
`addr=0x0076BA90`, `[fs-pipe-inject]`, `[overlay] start-match: section 4`,
`[coalesce-heap-r2-guard]`, `[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`.
