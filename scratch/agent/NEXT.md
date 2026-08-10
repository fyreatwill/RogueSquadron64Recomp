# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s601 recap (read this first)

Folded `s600_item338_beginframe_s0_verify` (334s, rc=1): attempt 1 pre-engagement
discard; attempt 2 scored engagement then **outcome D** — `beginframe_s0_guard=0`,
`last_guest_afa0=0`, crash at already-catalogued `coalesceFreeHeapBlocks+3192` /
`0x8000241c` (s354-366 noise), `sec4=1`, no inject/recovery. Path not exercised;
not discriminating. Guard binary + env confirmed present. Same recipe requeued as
`scratch/agent/soak_queue/s601_item338_beginframe_s0_verify_r2.sh`. Item -338/-365
still 0/2 live confirms; item -361 still blocked. Full: CURRENT-TRUTH -366/-365/-361;
PORTING-STATE Session 601.

## This iteration's work unit

**Fold in the `s601_item338_beginframe_s0_verify_r2` soak result and act on the
discriminating outcome.**

1. Read the new SOAK-RESULTS.md line for `s601_item338_*` and the scored attempt's
   gate line. Extract:
   `beginframe_s0_guard=N`, `sec4`, `sec2`, `coalesce_guard2_r2`, `crash`, `crash_pc`.
2. Classify against the recipe's A/B/C/D table:
   - **A** guard fires + no `0x8000afa0` crash + `sec4>=2` → item -338 CLOSED 1/2;
     item -361 R2 path may now be live — check `coalesce_guard2_r2` and thr-12.
   - **B** guard fires, no `0x8000afa0`, dies on a different crash or `sec4` still 1 →
     file the new crash as a breadcrumb (or escalate if known), keep -338 at 1/2
     pending a clean 2nd confirm, do not claim -361 unblocked.
   - **C** still dies at `0x8000afa0` with 0 guard fires → guard miss; re-read the
     site / check binary has the patch / check env var armed.
   - **D** 0 fires, no `0x8000afa0` (path not exercised) → not discriminating; requeue
     the same recipe (do not redesign). If this is the **3rd consecutive D** on this
     slug after s601, stop requeueing and write a pivot: either (i) a longer post-
     engagement hold that survives catalogued `0x8000241c` noise long enough for
     beginframe to run, or (ii) offline-force a bad `$s0` positive control for the
     guard instrument alone.
3. If A or B and the guard fired: same-run positive control. Queue a 2nd confirm
   soak (new tag) for the 2/2 CLOSE of item -338/-365.
4. If A and `coalesce_guard2_r2>=1`: first live hit of the s593 R2 fix — fold into
   item -361 and decide thr-12 next step from that log.

## Do NOT
- Re-characterize item -338 from the 5 historical logs (done s600).
- Escalate `0x8000241c` / `coalesceFreeHeapBlocks+3192` as a new M3 lead (s354-366
  background noise; already ruled out s601).
- Raise `HOLD_S` past 210.
- Chase `waitForAnyAudioSlot+244` (item -362: symtab misattribution).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Full regen unless you need to re-apply fixup from a cleared RecompiledFuncs.

### Reference tags
`[beginframe-s0-guard] site=0x8000AFA0`, `[case6-force-start]`, `[hangar-sel]`,
`[thr-create]/`/`[thr-destroy]`, `[rdp-fullsync] ... addr=0x0076B768`,
`[overlay] start-match: section 4`, `[coalesce-heap-r2-guard]`,
`[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`.
