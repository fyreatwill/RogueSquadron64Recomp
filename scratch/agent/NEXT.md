# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s602 recap (read this first)

Folded `s601_item338_beginframe_s0_verify_r2` (533s, rc=2): **no scored attempt**
(not A/B/C/D). Attempt 1 pre-engagement `0x80010134`/item -347 discard. Attempt 2
full HOLD survived at hangar **state=5** with 0 ACE80 / 0 ACE94 / 0 case6.

**Engagement gate diagnosed:** `ROGUESQ_FORCE_CASE6_START` injects Start at ACE94,
which only runs in hangar state 6. 5→6 is automatic camera-settle
`[state-write] site=0x800ACE80`, not a button. All prior engagements have ACE80.
Default stick pulses (hold+10/+25/+40) co-timed with A2's stuck-at-5 window; s600
engaged in ~3s pre-stick. Item -338/-365 still 0/2 live confirms; item -361 still
blocked. Full: CURRENT-TRUTH -367/-366/-365/-361; PORTING-STATE Session 602.

Requeued as `scratch/agent/soak_queue/s602_item338_beginframe_s0_verify_r3.sh`
with `STICK_SCHEDULE=999:sr` (no stick pulses during hold).

## This iteration's work unit

**Fold in the `s602_item338_beginframe_s0_verify_r3` soak result and act on it.**

1. Read the new SOAK-RESULTS.md line and any scored attempt's gate line. Extract:
   `beginframe_s0_guard=N`, `ace80`, `sec4`, `sec2`, `coalesce_guard2_r2`,
   `crash`, `crash_pc`, engagement (case6+hangar-sel).
2. Classify:
   - **A** guard fires + no `0x8000afa0` + `sec4>=2` → item -338 CLOSED 1/2;
     check `coalesce_guard2_r2` for -361.
   - **B** guard fires, no `0x8000afa0`, other crash or `sec4` still 1 → file
     breadcrumb, keep -338 at 1/2 pending clean 2nd confirm.
   - **C** dies at `0x8000afa0` with 0 guard fires → guard miss.
   - **D** engagement but 0 fires, no `0x8000afa0` → not discriminating; requeue
     same no-sticks recipe. Count consecutive Ds (s601 was D; if this is D #2,
     one more then pivot).
   - **E** budget exhausted / no engagement **again** despite no-sticks → ACE80
     settle is nondet independent of sticks. **Pivot (code):** under
     `ROGUESQ_FORCE_CASE6_START`, after N case5 frames still at state 5,
     force-write hangar state byte to 6 (the ACE80 write) so ACE94 path becomes
     reachable. Land in `fixup_game_funcs.py` + rebuild; do not redesign the
     rest of the force path.
3. If A or B and guard fired: queue a 2nd confirm soak for 2/2 CLOSE of -338/-365.

## Do NOT
- Re-characterize item -338 from the 5 historical logs (done s600).
- Escalate `0x8000241c` / `coalesceFreeHeapBlocks+3192` (catalogued noise).
- Escalate `0x80010134` / transformLightByType (item -347 coverage artifact).
- Raise `HOLD_S` past 210.
- Chase `waitForAnyAudioSlot+244` (item -362: symtab misattribution).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-arm default stick schedule on this verify recipe.

### Reference tags
`[beginframe-s0-guard] site=0x8000AFA0`, `[case6-force-start]`, `[hangar-sel]`,
`[state-write] site=0x800ACE80`, `[hangar-state]`, `[buttons-hangar] site=0x800ACE94`,
`[thr-create COP`/`[thr-destroy]`, `[rdp-fullsync] ... addr=0x0076B768`,
`[overlay] start-match: section 4`, `[coalesce-heap-r2-guard]`,
`[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`.
