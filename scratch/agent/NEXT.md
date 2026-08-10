# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s607 recap (read this first)

Folded `s606_handoff_76ba90_dual_target` (208s, rc=1): **class E0**.
Engagement force6+case6+hangar-sel+ace80 OK; thr11 create@+719; inject
n=450; **recov76B768=0 recov76BA90=0**; thr11_destroy=0; crash@+25786
`findOrCreateMaterial+776` / guest `0x8000e29c` (`si_addr=0x39500e10d`).
Stack: emitMaterialTexturedDL ← drawSubtitleText ← runModelViewerLoop.
Post-hsel fullsync only sticky `0x76DF60` E9. Same crash PC as s605
(**2nd occ**) but s605 had recov768~=7920 — material death is
**independent of 76B768**. H-handoff1 refined (not post-768-only). Do not
single-chase `0x8000e29c`. Queued `s607_handoff_material_noise_reroll`.

Full: CURRENT-TRUTH -372; PORTING-STATE Session 607.

## This iteration's work unit

**Fold in the `s607_handoff_material_noise_reroll` soak result and act.**

1. Read SOAK-RESULTS.md line + discard_stats (`pre_eng`, `matnoise`) +
   scored gate fields:
   `force6, case6, hangar-sel, recov76B768, recov76BA90, last_768_rel,
   first_a90_rel, thr11_destroy, thr11_destroy_rel, sec4_post, crash,
   crash_pc, crash_rel, class_hint`.
2. Classify (recipe header A–H):
   - **A** thr11_destroy + sec4_post + g2 + ok → -361 confirm 1/2.
   - **B** thr11_destroy + sec4 + crash `0x8000247c` → r2 path.
   - **C** thr11_destroy + sec4 + other crash → file breadcrumb.
   - **D** 76BA90 + thr11_destroy=0 → handoff not sufficient.
   - **E** last_768>0, no 76BA90, non-material crash → gap variant.
   - **F** survive HOLD, thr11_destroy=0 (s602-like).
   - **G** budget exhaust / only noise (rc=2) — report matnoise rate.
   - **H** 76BA90 + thr11_destroy (any) → handoff sufficiency hit.
3. If A/B/H: queue one confirm soak only. Do NOT raise HOLD_S past 210.
4. If G with high matnoise rate (≥3 discards): note force6×material
   correlation vs s602 (no force6, 0 material) as single-source only —
   do not open a reactive material guard; consider one dual-arm recipe
   (force6 on/off attempts) only if matnoise blocks all progress.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-handoff1 | (REFINED s607) Material/FS crash aborts thr11 pipeline before handoff; not 76B768-gated | crash with or without recov768; thr11_destroy=0 |
| H-handoff2 | 76BA90 handoff required before thr11 destroy | thr11_destroy only when first_a90_rel >= 0 |
| H-handoff3 | thr11 destroy independent of 76BA90 once 768 dies | thr11_destroy with recov76BA90=0 |
| H-force6a | (CONFIRMED s606) state=6 force unlocks case6+hangar-sel | force6∧case6∧hsel |
| H-matnoise | 0x8000e29c is intermittent cutscene noise (not always force6-caused) | non-noise scored attempt exists under same force6 env |

## Do NOT
- Raise HOLD_S past 210.
- Treat thr10 destroy as the sec4 gate — only post-create thr11 destroy.
- Single-chase `0x8000e29c` / findOrCreateMaterial (2nd occ filed; need
  3rd + idiom-class shape before any guard).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-arm default stick schedule.
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON.
- Chase waitForAnyAudioSlot+244 (item -362).

### Reference tags
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[beginframe-s0-guard]`, `[state-write] site=0x800ACE80`,
`[buttons-hangar] site=0x800ACE94`, `[thr-create]`/`[thr-destroy]`
entry=`0x8006F2CC`, `[rdp-fullsync] ... addr=0x0076B768` /
`addr=0x0076BA90`, `[fs-pipe-inject]`, `[overlay] start-match: section 4`,
`[coalesce-heap-r2-guard]`, `[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`,
`findOrCreateMaterial`, guest `0x8000e29c`.
