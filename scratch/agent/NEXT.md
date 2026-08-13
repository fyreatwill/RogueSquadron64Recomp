# NEXT work unit (source-audit the disjoint parser call ranges)

HYPOTHESIS-ID: m3-e9-command-boundary

Perform one bounded source-only audit; do not build or run. Enumerate every
writer and consumer of the submit serial, `[lo,hi)` range, and parser task
label from `rs64_dpc_record_submit` through `run_rdp_submission` and the RT64
command telemetry. Use s838's retained late records as the target. Confirm or
refute whether producer/consumer ordering or the latest-submit label can make
the parser call range appear disjoint from the bridge range despite exact
consumer identity.

Competing hypotheses and discriminator:

- H-range-association: source shows the parser receives a different range or
  task-era than the bridge record, so disjointness is real.
- H-label-ordering: source shows the parser receives the same range, but a
  latest-submit label or call-boundary ordering associates it with another
  serial/task.
- H-parser-record-loss: source identifies a bounded or filtered parser path
  that omits commands from an otherwise matching parser call range.

Discriminator: a source-proven range/label divergence selects
H-range-association; a source-proven same-range/latest-label race selects
H-label-ordering; a parser telemetry omission path selects
H-parser-record-loss. Do not add mitigation or behavior changes.
