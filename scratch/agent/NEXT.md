# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s610 recap (read this first)

Folded `s609_recovery_cell_reroll` (rc=1, 535s):
- discard_stats: pre_eng=2 matnoise=0 recov_silent=0 attempts=3
- A1/A2: `setByteAcrossEntryList+176`/`0x800aafa8` (3× total)
- Scored a3 class **E recharacterized**:
  `force6=1 case6=1 hangar-sel=1 ace80=1 inject_max_n=450
  recov76B768~=48 thr11_create=1 thr11_destroy=0 sec2_post=0
  crash=CRASH host=mat3x3InverseInto←setupCameraMatrices←runModelViewerLoop`
- last-guest-pc=`0x80022160` **STALE** (tickTextureMaterialExpiry nop)
- Offline vs s607: first 76B768 same ~+63–67k post-hsel; s607 thr11d ~+7k
  after first 768; s609 death ~+4k after first 768 → **mid-window Abort**,
  not EOF thr11-stall. Item **-375** filed. -373 still 1×.
- Queued `s610_recov_mat3inv_reroll` (mat3inv free-reroll + MAT3INV log).

Full: CURRENT-TRUTH -375/-374/-373/-361; PORTING-STATE Session 610.

## This iteration's work unit

**Fold in the `s610_recov_mat3inv_reroll` soak result and act.**

1. Read SOAK-RESULTS + discard_stats:
   `pre_eng, matnoise, recov_silent, mat3inv, attempts, force6, case6,
   hangar-sel, ace80, inject_max_n, recov76B768, thr11_destroy, sec4_post,
   sec2_post, mat3inv_entry, mat3inv_abnormal, stack_mat3inv, crash,
   crash_pc, class_hint, post_fs_top`.
2. Classify scored (recovery-active, non-matnoise, non-mat3inv only):
   - **A** sec2_post + survive HOLD → first in-mission hold; escalate M3 DoD.
   - **B** sec2_post + packTlut/`loadDebugAssets` stack → -373 **2nd occ**
     (escalate: entry-arg range instrument on packTlut / loadTextureToMemory;
     no reactive single-site guard without idiom class).
   - **C** sec2_post + different crash → file new breadcrumb; -373 stays 1×.
   - **D** thr11_destroy + sec4, sec2=0 → regression vs s608.
   - **E** recov≥1 thr11 live at EOF without mat3inv stack → true stall;
     offline compare recovery→destroy gap vs s607.
   - **F** budget exhaust: only pre-eng / matnoise / recovery-silent / mat3inv
     — report rates. If mat3inv≥2 with `mat3inv_abnormal≥1` same-run, plan
     det0 soft-skip in fixup (identity write + return) as next code unit.
3. If B: offline which packTlut arg is OOB; plan **one** fixup instrument.
4. Do NOT raise HOLD_S past 210. Do NOT reopen H-handoff2/76BA90.
5. Do NOT treat last-guest-pc=0x80022160 as a fault site.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-recov1 | (SUPPORTED) thr11 destroy/sec2 requires 76B768 | thr11_destroy∧sec2 only when recov768≥1 |
| H-sec2a | force6+inject+76B768 yields sec2 when noise absent | sec2_post≥1 on recovery-active non-noise |
| H-sec2b | post-sec2 death is stable packTlut/HMT path (-373) | same host stack 2× |
| H-sec2c | VI width=24 is coupled precursor to -373 | VI24 co-occurs with -373 only |
| H-mat3inv1 | post-exit cutscene hits singular/NaN det in mat3inv | mat3inv_abnormal≥1 same-run as Abort stack |
| H-mat3inv2 | mat3inv Abort is intermittent noise under force6 | free-reroll yields non-mat3inv scored path |
| H-handoff2 | (REFUTED s608) 76BA90 required for thr11 destroy | — |
| H-handoff3 | (SUPPORTED s608) thr11 destroy after 76B768 alone | thr11_destroy ∧ recov76BA90=0 |
| H-matnoise | (SUPPORTED) 0x8000e29c intermittent under force6 | non-noise scored exists |
| H-force6a | (CONFIRMED) state=6 force unlocks case6+hangar-sel | force6∧case6∧hsel |

## Do NOT
- Raise HOLD_S past 210.
- Treat last-guest-pc=0x800025ac as -326 2nd occ without host `do_rom_read` stack.
- Single-chase packTlut before 2nd occ of the same host stack.
- Soft-skip mat3inv det0 without 2nd occ + same-run abnormal control.
- Re-require 76BA90 for thr11 destroy (H-handoff2 closed).
- Score recovery-silent or mat3inv runs as pipeline failures (free rerolls).
- Leave FORCE_STATE6_AFTER / FS_PIPE_INJECT default-ON.
- Chase waitForAnyAudioSlot+244 (item -362).
- Re-open s223 hangar mat3inv null as if it covered post-exit.

### Reference tags
`[case5-force-state6]`, `[case6-force-start]`, `[hangar-sel]`,
`[state-write] site=0x800ACE80`, `[buttons-hangar] site=0x800ACE94`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC` / `0x800495FC`,
`[rdp-fullsync] ... addr=0x0076B768` / `0x0076BA90` / `0x0076DF60`,
`[fs-pipe-inject]`, `[overlay] start-match: section 2` / `section 4`,
`[mat3inv-entry]`, `[mat3inv-abnormal]`, `mat3x3InverseInto`,
`packTlutEntriesRgba5551`, `loadDebugAssets`, `loadTextureToMemory`,
`parseHmtMaterials`, `osViSetMode` width=24, `[CRASH][pc-symbol]`,
guest material noise `0x8000e29c`, `setByteAcrossEntryList`/`0x800aafa8`.
