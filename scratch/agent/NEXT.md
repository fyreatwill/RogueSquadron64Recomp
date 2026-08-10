# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s608 recap (read this first)

Folded `s607_handoff_material_noise_reroll` (311s, rc=1): **class C but past thr11→sec4**.
Engagement force6+case6+hangar-sel+ace80 OK; matnoise=0 attempt 1; inject n=400;
recov76B768~=92; **recov76BA90=0**; **thr11_destroy=1 sec4_post=1 sec2=1 sec2_post=1**;
thr12 lifecycle complete; crash post-sec2 at `packTlutEntriesRgba5551+2608` via
`loadDebugAssets` (item **-373**). last-guest-pc `0x800025ac` is **stale** — not -326.
**H-handoff2 REFUTED** (thr11 destroy without 76BA90). thr11→sec4 no longer primary M3
blocker. Queued `s608_post_sec2_pipeline_confirm`.

Full: CURRENT-TRUTH -373/-361; PORTING-STATE Session 608.

## This iteration's work unit

**Fold in the `s608_post_sec2_pipeline_confirm` soak result and act.**

1. Read SOAK-RESULTS + discard_stats + scored gates:
   `force6, case6, hangar-sel, ace80, inject_max_n, recov76B768, recov76BA90,
   thr11_destroy, sec4_post, sec2_post, thr495FC_creates, crash, crash_pc,
   crash_sym, class_hint, texdata/material guard fires`.
2. Classify:
   - **A** sec2_post + survive HOLD → first in-mission hold; escalate M3 DoD.
   - **B** sec2_post + same packTlut/`loadDebugAssets` stack → -373 **2nd occ**
     (escalate: entry-arg range instrument on packTlut / loadTextureToMemory;
     still no reactive single-site guard without idiom class).
   - **C** sec2_post + different crash → file new breadcrumb; keep -373 at 1×.
   - **D** thr11_destroy + sec4, sec2=0 → regression vs s608; investigate.
   - **E** material noise only (rc=2, high matnoise) — report rate; requeue.
   - **F** pre-eng only — report; requeue with same recipe.
3. If B: offline, identify which packTlut arg (a0/a1/a2/a3 / t0) is OOB from
   registers + source; plan **one** fixup instrument (arg range log+skip), not
   a multi-site sweep yet.
4. Do NOT raise HOLD_S past 210. Do NOT reopen H-handoff2/76BA90 as required.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-sec2a | force6+inject+76B768 yields sec2 when material noise absent | sec2_post≥1 on scored non-noise |
| H-sec2b | post-sec2 death is stable packTlut/HMT path (-373) | same host stack 2× |
| H-sec2c | VI width=24 is coupled precursor to -373 (same corruption wave) | VI24 co-occurs with -373; absent on other post-sec2 deaths |
| H-handoff2 | (REFUTED s608) 76BA90 required for thr11 destroy | — |
| H-handoff3 | (SUPPORTED s608) thr11 destroy after 76B768 alone | thr11_destroy ∧ recov76BA90=0 |
| H-matnoise | (SUPPORTED s608) 0x8000e29c intermittent under force6 | non-noise scored exists |
| H-force6a | (CONFIRMED) state=6 force unlocks case6+hangar-sel | force6∧case6∧hsel |

## Do NOT
- Raise HOLD_S past 210.
- Treat last-guest-pc=0x800025ac as -326 2nd occ without host `do_rom_read` stack.
- Single-chase packTlut before 2nd occ of the same host stack.
- Re-require 76BA90 for thr11 destroy (H-handoff2 closed).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON.
- Chase waitForAnyAudioSlot+244 (item -362).

### Reference tags
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[state-write] site=0x800ACE80`, `[buttons-hangar] site=0x800ACE94`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC` / `0x800495FC`,
`[rdp-fullsync] ... addr=0x0076B768` / `0x0076BA90`, `[fs-pipe-inject]`,
`[overlay] start-match: section 2` / `section 4`,
`packTlutEntriesRgba5551`, `loadDebugAssets`, `loadTextureToMemory`,
`parseHmtMaterials`, `osViSetMode` width=24, `[texdata-table-guard]`,
`[texdata-ptr-array-guard]`, `[material-array-ptr-guard]`,
`[CRASH][pc-symbol]`, guest material noise `0x8000e29c`.
