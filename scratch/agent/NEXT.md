# NEXT work unit (after s685 parser→State discriminator)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Trace the section-2 source-side FULL_SYNC scarcity through the Factor 5 LLE
dispatch. s685 proved that there are exactly three genuine parser E9s and all
three call `State::fullSync`; do not alter decoding, submission, or FULL_SYNC
behavior.

## Competing hypotheses

- **H-legitimate-source:** the active section-2 guest DLs themselves present
  exactly three E9s; the producer legitimately stopped emitting frame
  boundaries, so the next audit belongs in the guest scheduler/overlay path.
- **H-lle-control-flow:** the factor5 RSP loop leaves or resets a section-2
  guest stream before later E9s, so the deficit is an LLE control-flow defect.
- **H-source-probe-scope:** the L_1090 guest-E9 counter misses another valid
  Factor 5 input path; a second source-side marker disagrees with it.

## Discriminating measurement

At the Factor 5 LLE boundary, record per task: every L_1090 E9 fetch, the
normal task exit/iter-cap path, and an independent source-stream endpoint
marker. Keep four boot controls, the existing section-2 latch, and 64 target
rows. The marker must show a visible all-path positive control in the same
run; branch execution alone is not a control.

- Both source markers report three E9s and normal completion: H-legitimate-source
  supported.
- The independent marker reaches stream content past L_1090's last E9 or shows
  an early/reset exit: H-lle-control-flow supported.
- The controls disagree: H-source-probe-scope supported; reject the run.

## Commands

    # Add the bounded source-side markers through tools/fixup_factor5_ucode.py,
    # regenerate if needed, then build and reuse the phase-gated s670 recipe.
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
