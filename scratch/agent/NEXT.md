# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s603 recap (read this first)

Folded `s602_item338_beginframe_s0_verify_r3` (554s, rc=0): **scored D** for
item -338 (3rd: s600/s601/s602) + **first clean post-engagement survival**.
Gate A4: `case6=1 hangar-sel=1 ace80=1 inject_max_n=550 recov=0 sec4=1
beginframe_s0_guard=0 last_guest_afa0=0 crash=ok`. No-sticks engagement OK.

**Pipeline corrected:** thr-11 = `saveServiceWorker` `entry=0x8006F2CC` (not
thr495FC double-count). s592_a: thr-11 destroy → sec4=2 → crash `0x8000247c`
(R2 site). s602: thr-11 still live under HOLD_S=90. Queued
`s603_item338_item361_hold180.sh` (HOLD_S=180, fixed gate).

Full: CURRENT-TRUTH -368/-365/-361; PORTING-STATE Session 603.

## This iteration's work unit

**Fold in the `s603_item338_item361_hold180` soak result and act on it.**

1. Read SOAK-RESULTS.md line + scored attempt gate:
   `beginframe_s0_guard`, `thr11_destroy`, `sec4_post`, `inject_max_n`,
   `recov76B768`, `coalesce_guard2_r2`, `crash`, `crash_pc`, `class_hint`.
2. Classify (scored attempt only):
   - **A** `beginframe_s0_guard>=1` + no `0x8000afa0` → -338 confirm 1/2; queue 2nd.
   - **B** `thr11_destroy=1` + `sec4_post>=1` + `coalesce_guard2_r2>=1` + no
     crash at `0x8000247c` → -361 confirm 1/2; queue 2nd confirm.
   - **C** thr11 destroy + sec4_post + crash `0x8000247c` + 0 r2 guard → guard miss;
     debug R2 guard placement.
   - **D** thr11 destroy + sec4_post + other crash → file breadcrumb; progress on
     pipeline.
   - **E** `thr11_destroy=0` at HOLD end → time alone insufficient; **pivot** to
     recovery-cell reliability (why s592 had 76B768 and s602/s603 did not). Do
     NOT raise HOLD_S past 210.
   - **F** neither beginframe nor thr11 path (0 guard, thr11 live, no afa0) →
     stop dedicated -338 soaks; park passive arm; pivot same as E or to offline
     recovery-writer hunt.
3. If B or A: queue one confirm soak only (not a third requeue of the same D).

## Hypotheses for E/F pivot (do not run until soak scores E or F)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-recov1 | Recovery cell `0x76B768` is required for cutscene advance that stops thr-11 | Compare thr11_destroy rate on runs with recov>0 vs recov=0 at equal HOLD |
| H-recov2 | Inject mode-1 non-mutating path never promotes guest FULL_SYNC into the recovery cell | Instrument whether any guest E9 lands at 0x76B768 under inject |
| H-time | 180s still short vs cutscene length variance | Only if thr11_destroy seen at least once under 180 |

## Do NOT
- Raise HOLD_S past 210.
- Re-characterize -338 from the 5 historical logs (done s600).
- Chase `waitForAnyAudioSlot+244` (item -362).
- Treat thr495FC_creates as post-exit thr-12 (boot-only; gate fixed in s603 recipe).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-arm default stick schedule (no-sticks works).

### Reference tags
`[beginframe-s0-guard]`, `[case6-force-start]`, `[hangar-sel]`,
`[state-write] site=0x800ACE80`, `[buttons-hangar] site=0x800ACE94`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC`,
`[rdp-fullsync] ... addr=0x0076B768`, `[fs-pipe-inject]`,
`[overlay] start-match: section 4`, `[coalesce-heap-r2-guard]`,
`[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`.
