# NEXT work unit — repair and qualify the retail frequency phase signal

HYPOTHESIS-ID: m5-frequency-result-writer

Session 3432 showed that the port result is stable across silent/image arms,
but the retail oracle's expected title/hangar phase buckets remained zero.
Its lifetime target histogram is therefore not a phase discriminator.

Competing hypotheses and the single discriminating measurement:

- `H-OraclePhaseOriginMismatch`: the configured origins/widths do not match
  the oracle's actual VI transition, so target attribution is merely hidden.
- `H-OracleDrivenRouteStallsBeforeTarget`: the oracle does not reach the
  target route, despite its whole-RDRAM control and VI count.
- `H-TargetWritesArePrephaseOnly`: the 41 target writes are genuinely limited
  to boot/pre-phase state and cannot answer the title/hangar question.

Exact work: run the oracle first with `--vi-trace`, whole-RDRAM control, the
validated input schedule, and no high-frequency execution watch. Use the
observed target VI origin/width to configure a second same-run target watch
with `--pc-hist-phase`, `--post-value-watch`, and `--pc-hist-watch`. A nonzero
title/hangar bucket selects `H-OraclePhaseOriginMismatch`; a zero bucket with
only prephase target writes selects `H-TargetWritesArePrephaseOnly`; no target
route despite a live control selects `H-OracleDrivenRouteStallsBeforeTarget`.
Do not change waits, slots, dispatch, clear behavior, or PCM writeback.
