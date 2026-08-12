# NEXT work unit (after s688 saved-frame audit)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Attribute the eight unpopped display-list frames in each of the 61 section-2
LLE cap tasks. s688 proved the observed pop→resume pairs are coherent
(`mis=0`) but every cap row has `push-pop=8` and reaches slot 8; natural rows
are balanced at slot 0. Do not alter decoding, submission, or FULL_SYNC.

## Competing hypotheses

- **H-legitimate-open-chain:** the eight residual pushes come from valid Factor
  5 DL/branch commands and the stream genuinely lacks a root terminator.
- **H-repeat-callsite:** one LLE call path repeatedly pushes the same saved
  target/PC, accumulating the eight residual frames.
- **H-stack-write-corrupt:** the saved-frame slot/target/PC changes before a
  matching pop, so an invalid stack write—not a legitimate command—creates
  the residual depth.

## Discriminating measurement

Add phase-scoped bounded call-site (`r31`) and frame payload (`slot`, saved
target, saved PC) markers at `L_12A0`, retaining the first push into each slot
and the first/last push at slot 8. Join those with the existing pop/resume
records in `[e9-prov]`. Keep four boot controls, the section-2 latch, and 64
target rows. The visible positive control is the existing natural
push→pop→resume chain plus a balanced slot histogram; a counter alone is
insufficient.

- The eight retained pushes have distinct, command-consistent call sites and
  payloads: H-legitimate-open-chain supported.
- The same call-site/payload supplies repeated residual pushes: H-repeat-callsite
  supported.
- A slot's saved payload changes without its matching pop: H-stack-write-corrupt
  supported.
- Missing boot/natural controls: reject the run.

## Commands

    # Extend the regeneration-safe L_12A0 marker through
    # tools/fixup_factor5_ucode.py, then build and reuse the phase-gated recipe.
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
