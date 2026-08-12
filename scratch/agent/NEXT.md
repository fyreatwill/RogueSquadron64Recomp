# NEXT work unit (after s686 source-stream completion audit)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Classify the 61 section-2 LLE tasks that reach the synthetic cap after the
three genuine FULL_SYNC tasks. s686 proved the E9 count is real, but not
whether cap completion is an expected consequence of the SP_STATUS stub or a
stale display-list unwind defect. Do not alter decoding, submission, or
FULL_SYNC behavior.

## Competing hypotheses

- **H-cap-is-expected:** cap tasks execute the real `L_12C4` EndDL/unwind
  path, but the unmodelled SP_STATUS halt prevents its normal task boundary;
  the cap is only our scheduler surrogate.
- **H-unwind-missed:** cap tasks emit RDP data without visiting `L_12C4`, so
  the Factor 5 control flow is bypassing the actual display-list completion
  path and keeps consuming stale DMEM.
- **H-unwind-corrupt:** cap tasks visit `L_12C4`, but its stack-depth/unwind
  state never reaches the `L_10E8` natural-exit branch, identifying a corrupt
  stack or return-address transition rather than a missing handler.

## Discriminating measurement

Add phase-scoped, per-task markers at `L_12C4` (EndDL entry and post-decrement
stack byte) and its natural-exit branch to `L_10E8`, alongside the existing
source fetch/endpoint fields. Keep four boot controls, the section-2 latch,
and 64 target rows. The positive control is visible: boot and the three
natural section-2 rows must show EndDL plus natural exit; a mere branch count
is not enough.

- Cap rows have EndDL visits and the stack byte crosses below zero: H-cap-is-expected
  supported.
- Cap rows have no EndDL visits: H-unwind-missed supported.
- Cap rows visit EndDL but never cross below zero: H-unwind-corrupt supported.
- Missing boot/natural-row controls: reject the run.

## Commands

    # Add bounded EndDL/unwind markers through tools/fixup_factor5_ucode.py,
    # regenerate if needed, then build and reuse the phase-gated s670 recipe.
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
