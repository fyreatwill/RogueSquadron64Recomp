# NEXT work unit (after s683 authoritative E9 join)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Add parser-span attribution to the phase-scoped E9 probe, then rerun the same
one-window section-2 audit. s683 proved 40 submitted emitted E9s did not reach
either direct or pending-command raw fetch; do not alter decoding, submission,
or FULL_SYNC behavior.

## Competing hypotheses

- **H-preceding-span:** an executed authoritative RDP command's declared
  length covers each missing emitted E9, treating its bytes as inline data.
- **H-range-gap:** no authoritative parser span covers a missing emitted E9;
  the parser never enters the relevant submitted subrange.
- **H-address-join-bug:** bridge/parser address domains diverge only after
  boot, despite the four same-run exact-address controls.

## Discriminating measurement

At RT64's authoritative parser, compare every executed `address..nextAddress`
span with the active task's emitted-address vector. Print one scoped
`[e9-prov-span]` row for every emitted E9 skipped by a non-E9 span, including
span start/end/raw opcode/length and whether it came from pending completion.
Retain four boot controls, one latch, 64 `scope=sec2` rows, and matching
`dl-sync-probe2` rows.

- Every missing E9 is covered by a non-E9 span: H-preceding-span supported.
- Missing E9s have no covering span: H-range-gap supported.
- A section-2 raw E9 has a nonmatching address while boot controls match:
  H-address-join-bug supported.

## Commands

    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=0 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
