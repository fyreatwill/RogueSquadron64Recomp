# NEXT work unit (identify the parser condition behind late range disjointness)

HYPOTHESIS-ID: m3-e9-command-boundary

Perform one bounded telemetry-only source/runtime probe on s840's late
ordinary population. Carry ordinary submit serial/range identity into the
parser command-start and pending records, with per-task budgets; retain the
existing positive controls and phase gates, build all arms together, and run
once. Do not change behavior or add a mitigation.

Competing hypotheses and discriminator:

- H-parser-range-transition: parser call ranges genuinely differ from the
  ordinary submit ranges at the late boundary.
- H-parser-record-loss: ordinary parser calls have the expected range, but
  command telemetry omits or filters their contents.
- H-pending-or-filter: pending completion or a parser-side filter accounts for
  the missing rows.

Discriminator: matching parser ranges with absent command records select
H-parser-record-loss; pending/filter coverage selects H-pending-or-filter; and
genuinely disjoint parser ranges select H-parser-range-transition.
