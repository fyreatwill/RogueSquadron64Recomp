# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s600 recap (read this first)

Item -338 (`beginFrameDLChunk` / `last-guest-pc=0x8000afa0`, 5 occurrences) was offline-
characterized against all 5 crash logs and root-caused: guest `0x8000AFA0` is
`lw $v0, 0x8($s0)` after a null-only check on a stack-slot-loaded node pointer
(`lw $s0, 0($s1)`). 4/5 SIGBUS at `si_addr=0x335000008`. Same item -317 idiom family,
missed by the hi16-reload sweep. Guard `BEGINFRAME_S0_GUARD` landed at that site
(range-check `ctx->r16`; OOB → `s2--` + `goto L_8000B208`). Binary rebuilt. Verify soak
queued: `scratch/agent/soak_queue/s600_item338_beginframe_s0_verify.sh` (fast-retry
case6+inject + `ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1`). Full: CURRENT-TRUTH items -365/-338/-361;
PORTING-STATE Session 600.

## This iteration's work unit

**Fold in the `s600_item338_beginframe_s0_verify` soak result and act on the
discriminating outcome.**

1. Read the new SOAK-RESULTS.md line for `s600_item338_*` and the scored attempt's
   gate line from the recipe stderr / soak_results log. Extract:
   `beginframe_s0_guard=N`, `sec4`, `sec2`, `coalesce_guard2_r2`, `crash`, `crash_pc`.
2. Classify against the recipe's A/B/C/D table:
   - **A** guard fires + no `0x8000afa0` crash + `sec4>=2` → item -338 CLOSED 1/2;
     item -361 R2 path may now be live — check `coalesce_guard2_r2` and thr-12.
   - **B** guard fires, no `0x8000afa0`, dies on a different crash or `sec4` still 1 →
     file the new crash as a breadcrumb (or escalate if it's a known item), keep -338
     at 1/2 pending a clean 2nd confirm, do not claim -361 unblocked.
   - **C** still dies at `0x8000afa0` with 0 guard fires → guard miss; re-read the
     site / check binary has the patch / check env var armed.
   - **D** 0 fires, no `0x8000afa0` (path not exercised) → not discriminating; requeue
     the same recipe (do not redesign).
3. If A or B and the guard fired: that is the same-run positive control for the
   instrument. Queue a 2nd confirm soak (copy the s600 recipe, new tag) for the 2/2
   CLOSE of item -338/-365.
4. If A and `coalesce_guard2_r2>=1`: that is the first live hit of the s593 R2 fix —
   fold into item -361 and decide thr-12 next step from that log.

## Do NOT
- Re-characterize item -338 from the 5 historical logs (done s600).
- Raise `HOLD_S` past 210.
- Chase `waitForAnyAudioSlot+244` (item -362: symtab misattribution).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Full regen unless you need to re-apply fixup from a cleared RecompiledFuncs; the
  guard is already in `funcs_3.c` and `fixup_game_funcs.py`.

### Reference tags
`[beginframe-s0-guard] site=0x8000AFA0`, `[case6-force-start]`, `[hangar-sel]`,
`[thr-create]/`/`[thr-destroy]`, `[rdp-fullsync] ... addr=0x0076B768`,
`[overlay] start-match: section 4`, `[coalesce-heap-r2-guard]`,
`[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`.
