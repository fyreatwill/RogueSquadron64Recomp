# NEXT work unit (after s687 EndDL/unwind audit)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Classify the saved display-list frame responsible for the 61 section-2 LLE
tasks that reach the synthetic cap after the three genuine FULL_SYNC tasks.
s687 proved those tasks execute `L_12C4` EndDL 106–122 times, but none takes
its root `L_10E8` exit. Do not alter decoding, submission, or FULL_SYNC.

## Competing hypotheses

- **H-stale-resume:** balanced push/pop returns through `L_12DC` to a stale
  saved `r17`, cycling a parent display-list frame instead of reaching root.
- **H-push-corrupt:** `L_12A0` pushes an invalid or unbalanced frame, so the
  depth never underflows even though EndDL executes.
- **H-root-terminator-absent:** push/pop and resume pairs are coherent, but
  this stream lacks the final root EndDL; the cap is an SP_STATUS surrogate.

## Discriminating measurement

Add phase-scoped per-task push/save (`L_12A0`), pop/return-slot (`L_12C4`),
and resumed-PC (`L_12DC`) markers. Report bounded first/last pairs, counts,
depth range, and zero-depth returns in `[e9-prov]`. Keep four boot controls,
the section-2 latch, and 64 target rows. The visible positive control is a
coherent final boot/natural push→pop→resume chain followed by
`unwind_natural=1`; a counter alone is insufficient.

- Repeated zero-depth returns resume a previously saved stale `r17`:
  H-stale-resume supported.
- Push/pop count or depth-range imbalance precedes repeated returns:
  H-push-corrupt supported.
- Frames advance coherently but never receive final root termination:
  H-root-terminator-absent supported.
- Missing boot/natural controls: reject the run.

## Commands

    # Add bounded L_12A0/L_12C4/L_12DC frame markers through
    # tools/fixup_factor5_ucode.py, then build and reuse the phase-gated recipe.
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
