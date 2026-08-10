# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s609 recap (read this first)

Folded `s608_post_sec2_pipeline_confirm` (rc=137 hard cap):
- A1/A2 pre-eng free rerolls (A1: `setByteAcrossEntryList+176`/`0x800aafa8` 1× breadcrumb).
- Attempt 3 engaged offline-scored:
  `force6=1 case6=1 hangar-sel=1 ace80=1 inject_max_n=750 thr11_create=1
  recov76B768=0 thr11_destroy=0 sec4_post=0 sec2_post=0 crash=ok`
  class **F_recovery_silent_no_thr11_destroy**.
- Post-hangar-sel FULL_SYNC mono `0x0076DF60`×474 — never diversifies to
  `0x0076B768` (s607 control: ×46 + multi-cell family → thr11 destroy → sec2).
- **H-recov1 necessity SUPPORTED.** Item -373 stays 1×. Item **-374** filed.
- Queued `s609_recovery_cell_reroll` (mid-run free-reroll on recovery silence).

Full: CURRENT-TRUTH -374/-373/-361; PORTING-STATE Session 609.

## This iteration's work unit

**Fold in the `s609_recovery_cell_reroll` soak result and act.**

1. Read SOAK-RESULTS + discard_stats:
   `pre_eng, matnoise, recov_silent, attempts, force6, case6, hangar-sel,
   ace80, inject_max_n, recov76B768, thr11_destroy, sec4_post, sec2_post,
   crash, crash_pc, crash_sym, class_hint, post_fs_top`.
2. Classify scored (recovery-active only):
   - **A** sec2_post + survive HOLD → first in-mission hold; escalate M3 DoD.
   - **B** sec2_post + packTlut/`loadDebugAssets` stack → -373 **2nd occ**
     (escalate: entry-arg range instrument on packTlut / loadTextureToMemory;
     no reactive single-site guard without idiom class).
   - **C** sec2_post + different crash → file new breadcrumb; -373 stays 1×.
   - **D** thr11_destroy + sec4, sec2=0 → regression vs s608.
   - **E** recov≥1 but thr11 still live at EOF.
   - **F** budget exhaust: only pre-eng / matnoise / recovery-silent —
     report rates; if recovery-silent dominates (≥3), offline compare RDRAM
     recovery-cell *writer* conditions (why 76B768 never appears) as next unit.
3. If B: offline, identify which packTlut arg is OOB; plan **one** fixup
   instrument (arg range log+skip).
4. Do NOT raise HOLD_S past 210. Do NOT reopen H-handoff2/76BA90.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-recov1 | (SUPPORTED s609) thr11 destroy/sec2 requires 76B768 recovery cell | thr11_destroy∧sec2 only when recov768≥1 |
| H-sec2a | force6+inject+76B768 yields sec2 when material noise absent | sec2_post≥1 on recovery-active non-noise |
| H-sec2b | post-sec2 death is stable packTlut/HMT path (-373) | same host stack 2× |
| H-sec2c | VI width=24 is coupled precursor to -373 | VI24 co-occurs with -373 only |
| H-handoff2 | (REFUTED s608) 76BA90 required for thr11 destroy | — |
| H-handoff3 | (SUPPORTED s608) thr11 destroy after 76B768 alone | thr11_destroy ∧ recov76BA90=0 |
| H-matnoise | (SUPPORTED) 0x8000e29c intermittent under force6 | non-noise scored exists |
| H-force6a | (CONFIRMED) state=6 force unlocks case6+hangar-sel | force6∧case6∧hsel |

## Do NOT
- Raise HOLD_S past 210.
- Treat last-guest-pc=0x800025ac as -326 2nd occ without host `do_rom_read` stack.
- Single-chase packTlut before 2nd occ of the same host stack.
- Re-require 76BA90 for thr11 destroy (H-handoff2 closed).
- Score recovery-silent runs as pipeline failures (they are free rerolls).
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON.
- Chase waitForAnyAudioSlot+244 (item -362).

### Reference tags
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[state-write] site=0x800ACE80`, `[buttons-hangar] site=0x800ACE94`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC` / `0x800495FC`,
`[rdp-fullsync] ... addr=0x0076B768` / `0x0076BA90` / `0x0076DF60`,
`[fs-pipe-inject]`, `[overlay] start-match: section 2` / `section 4`,
`packTlutEntriesRgba5551`, `loadDebugAssets`, `loadTextureToMemory`,
`parseHmtMaterials`, `osViSetMode` width=24, `[CRASH][pc-symbol]`,
guest material noise `0x8000e29c`, `setByteAcrossEntryList`/`0x800aafa8`.
