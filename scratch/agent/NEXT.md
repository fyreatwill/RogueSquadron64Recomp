# NEXT work unit (bounded post-sec2 FULL_SYNC reachability capture)

HYPOTHESIS-ID: m3-postsec2-authoritative-e9

Run one bounded, phase-gated capture using the successful s815
`s790_postsec2_reachability` recipe. Keep the existing provenance controls
(`emit`, `raw`, `dispatch`, `match`), `[vi-arg]` pointer-only logging, and
the phase-relative key schedule. Do not change game logic or add a
mitigation. The capture is valid only if the phase and provenance positive
controls fire and VI reaches 1024.

## Competing hypotheses

- H-authoritative-advance: post-sec2 aligned E9 commands reach the
  authoritative parser and advance FULL_SYNC accounting.
- H-pre-authoritative-loss: aligned E9 commands remain abundant, but the
  authoritative parser/dispatch sees no corresponding advances.
- H-prechain-transient: the run fails or remains at VI 640 before a parser
  sample, leaving both parser hypotheses unevaluable.

## Discriminating measurement

Compare aligned-walker E9 provenance with authoritative parser advance and
`State::fullSync` records after the VI-1024 gate in the same run. A positive
authoritative advance selects H-authoritative-advance; positive provenance
with zero authoritative advance selects H-pre-authoritative-loss; no
post-gate sample selects H-prechain-transient.

## Exact command

Use the existing self-contained recipe/script for
`s790_postsec2_reachability`, with its normal 300-second watchdog and SIGKILL
cleanup. Confirm `ROGUESQ_LOG_VI_ARGS=1` is present before launch. Do not run a
second arm or rebuild in this work unit unless the first launch is invalid due
to a missing positive control.
