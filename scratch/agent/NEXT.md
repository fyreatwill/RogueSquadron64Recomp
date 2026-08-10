# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s598 recap (read this first)

s598 built and queued `scratch/agent/soak_queue/s598_fast_retry_case6.sh`,
implementing NEXT.md's redesign option (1) from s597: instead of one
case6+inject attempt per 600s soak_queue slot (8/9 of which died pre-
engagement in s593-s596, per item -362's tally), it loops the same recipe
inside a 560s budget, discarding pre-engagement deaths as free rerolls (up
to 8 attempts) and only scoring the first attempt that reaches real
engagement (`[case6-force-start]` + `[hangar-sel]` both present), which then
runs its full `HOLD_S=90` window and gets the standard sec4-decision-tree
analysis. Full detail: `PORTING-STATE.md` Session 598, `docs/CURRENT-TRUTH.md`
item -363.

**It has not run yet.** It was queued, not executed, this session (a direct
standalone invocation would have needed interactive approval; the loop's own
queued-soak runner will execute it normally on the next pass, up to 2
recipes between iterations, 600s hard cap per recipe — comfortably above the
wrapper's internal 560s budget).

## This iteration's work unit

1. **First, check whether `s598_fast_retry_case6` already ran.** Read the
   tail of `scratch/agent/SOAK-RESULTS.md` for a line naming it. Also check
   `ls scratch/agent/soak_queue/` — if the `.sh` file is gone (moved to
   `soak_queue/done/`), it ran regardless of whether a result line landed.
   - If it ran and exited 0/1 (an attempt reached engagement): read the
     scored attempt's `run.log` (path is in the wrapper's own captured
     stdout, `scratch/agent/soak_results/s598_fast_retry_case6_*.log`, under
     the `=== scored attempt analysis ===` line) and apply the item -361
     decision tree — `sec4>=2` with the guarded path live is the only
     outcome that counts as a real verify (positive or negative) for the
     `coalesceFreeHeapBlocks` R2 guard fix landed s593. Fold the result into
     item -361 (close it FIXED+CLOSED 2/2 if this is a clean 2nd confirm, or
     record the new data point if still inconclusive).
   - If it ran and exited 2 (no engagement across up to 8 rerolls in the
     560s budget): that's a sharper data point than item -362's 8-sample
     tally — pre-engagement noise is dense enough to eat an 8x-retry budget.
     Worth a quick frequency read of which crash signature(s) killed each of
     the (likely ~4-8) sub-attempts logged in the wrapper's own stdout
     before deciding whether option (2) (natural-path, recovery-cell-
     reliability-scoped) is now the better remaining move.
   - If it has NOT run yet (still sitting in `scratch/agent/soak_queue/`):
     that's fine, the loop runs up to 2 queued recipes between iterations —
     do NOT re-invoke it manually. Pick a DIFFERENT work unit this iteration
     (see fallback below) rather than stalling on it.

2. **Fallback if s598's soak hasn't landed a result yet:** do NOT start a
   3rd redesign of the same item -361 verify loop without new evidence —
   iron rule 8 (3 consecutive non-discriminating iterations on one
   hypothesis forces a pivot preamble; s595/s596/s597 already spent 3+ on
   this exact question). Instead, treat this as a scheduling gap and do
   ONE of:
   - A short M3 idiom-class audit unrelated to item -361 (per the strategic
     priority in `docs/CURRENT-TRUTH.md`'s USER DIRECTIVE, item 3: systematic
     idiom-class audits only, not reactive chases). No open idiom-class
     bucket is currently flagged in Next-steps as ready to start — check
     items -328..-336 (six filed-not-chased breadcrumbs) for a 3rd
     occurrence before opening new ground.
   - Re-run Step 0's maintenance check (`wc -c < docs/CURRENT-TRUTH.md`) —
     if it's crept back over 60000 bytes, that's this iteration's unit.

### Do NOT
- Manually invoke `scratch/agent/soak_queue/s598_fast_retry_case6.sh`
  directly (bypasses the loop's one-game-at-a-time + budget accounting).
- Raise `HOLD_S` past 210 inside the wrapper's recipe without new evidence
  that duration (not engagement rate) is still the bottleneck.
- Chase `waitForAnyAudioSlot+244` as a real audio bug (item -362: disproved
  its own positive control, `nm -n` misattribution).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Chase item -347/-331/-306 reactively — filed breadcrumbs, watch-only.

### Reference: wrapper internals, if the scored log needs re-deriving
`scratch/agent/soak_queue/s598_fast_retry_case6.sh` uses the same
`GAME_EXTRA_ENV` as the s593-s596 attempts (`ROGUESQ_FORCE_CASE6_START=5
ROGUESQ_FS_PIPE_INJECT=1` + the DL_SYNC/FS_SLOT/RDP_FULLSYNC/AUDIO_DRAIN/
HANGARBAY_ENTRY/COALESCE_HEAP_GUARD/COALESCE_HEAP_R2_GUARD log flags),
`PROBE_MODE=start_only HOLD_S=90` — same decision-tree python block as the
s595 script (`sec4`, `sec2`, `case6`, `hangar-sel`, `inject_lines`,
`recov76B768~=`, `thr495FC_creates`, `coalesce_guard1/2_r2`, `crash`).
