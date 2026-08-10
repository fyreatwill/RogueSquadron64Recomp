# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s597 recap (read this first)

s597 executed NEXT.md's own scoped option (a): tally which breadcrumb killed
each of the 9 non-discriminating s593-s596 `coalesce_r2_verify` attempts, to
see whether one dominant noise family exists worth a targeted guard. Result:
**CLOSED NEGATIVE.** Full tally + method: `PORTING-STATE.md` Session 597,
`docs/CURRENT-TRUTH.md` item -362.

- No single family is a majority: item -306 (2×), a new
  `waitForAnyAudioSlot+244`/`0x8000834c` cluster (2×), item -331 2nd occ
  (1×), a genuinely distinct recovery-cell-reliability failure (1×,
  `s594_c`), non-crash early death/hang (2×).
- The new `waitForAnyAudioSlot+244` cluster looked like a fresh M5 lead but
  **failed its own implied positive control**: the function's unconditional
  `[audio-drain-enter]` entry print never fired in either crashing log
  despite the env var being armed correctly and the instrument working in
  199 other historical run dirs. Conclusion: `nm -n` nearest-symbol
  misattribution (item -310/-311 family), not a real crash inside that
  function. **Do not chase it as an audio bug.**
- Both `waitForAnyAudioSlot+244` deaths happened in 7-8 seconds, VI still at
  640 — pre-title-screen, i.e. **before** `ROGUESQ_FORCE_CASE6_START` could
  possibly engage. This applies to 6 of the 8 tallied nulls: they die with
  `case6=0 hangar-sel=0`. That undercuts the original rationale for redesign
  option (b) ("the force mechanism adds fragility") — the force mechanism
  hasn't run yet when most of these deaths happen, so switching to a natural
  double_start path would not obviously touch this early-boot noise.

## This iteration's work unit

Two real options remain (both cheaper than another blind identical retry):

**(1) Fast-retry wrapper (recommended first).** ~89% of attempts die
pre-engagement, but the two fastest deaths cost only 7-8s of the 600s soak
budget — the expensive nulls are the 100-200s pre-engagement deaths
(s593_a/b, s595_f) and the reached-but-no-recovery ones (s594_c, ~199s).
Build a wrapper script (`scratch/agent/soak_queue/`-compatible) that:
  - Launches the game with the existing case6+inject recipe.
  - Polls for a `case6=1`/`hangar-sel=1` signal (or just VI width) in the
    growing `run.log`; if the process dies or crashes with `case6=0` before
    that point, SIGKILL, discard, and immediately relaunch — do NOT count
    it against the 600s budget the same way (log it as a fast reroll, not a
    soak result).
  - Once a launch survives to `case6=1`, let it run the FULL `HOLD_S=90-210`
    window as normal, then evaluate `sec4>=2` per the existing decision
    tree.
  - Cap total wall time at the loop's existing 600s hard cap regardless of
    how many fast rerolls happen inside it.
  This turns the current 1-attempt-per-slot model into effectively several
  attempts per slot, multiplying the number of shots at the *actual*
  remaining question: does the FULL_SYNC recovery cell `0x76B768` fire
  reliably once case6 is reached? (H12c/H13c, still open: s589/s592a fired,
  s591/s594_c did not — 2/4 known reached-case6 runs recover.)

**(2) Natural (non-force) double_start path, re-scoped.** If (1) is
impractical this iteration, fall back to the original option (b), but
**target it correctly**: the comparison that matters is not
"does natural survive pre-engagement noise better" (unlikely, per the s597
finding above) but "does natural reach the recovery-cell firing more
reliably than forced once hangar exit happens." Design the discriminating
measurement around `recov76B768~=0` vs `>0` counts across N runs of each
path, not around raw survival-to-case6 rate.

Pick ONE, name the discriminating measurement explicitly before running
anything, then either run it directly or queue it to
`scratch/agent/soak_queue/`.

### Do NOT
- Raise `HOLD_S` past 210 — already tried twice (90, 210), no effect on
  recovery-cell-firing rate specifically.
- Chase `waitForAnyAudioSlot+244` as a real audio bug — s597 disproved its
  own positive control (see above). If it recurs, the next step is closing
  the underlying symtab-misattribution gap (item -310/-311 family), not
  patching `waitForAnyAudioSlot` itself.
- Treat a `sec4=1`-only, `case6=0`, or reached-but-no-recovery null as
  evidence about the R2 guard fix (iron rule 1) — only a run reaching
  `sec4>=2` with the guarded path live counts.
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Chase item -347/-331/-306 reactively — filed breadcrumbs, watch-only.

### Reference: exact command used for prior attempts (case6+inject baseline)
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s598_<name> 5 12
```
For option (2), drop `ROGUESQ_FORCE_CASE6_START` and drive a natural
double_start leave sequence instead (see `PROBE_KEYS`/leave-sequence recipes
referenced in items -359/-590 for the natural path shape).
