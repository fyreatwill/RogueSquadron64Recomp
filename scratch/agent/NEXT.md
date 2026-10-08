# Next work unit (s4315): requalify the exact retail consumer-read stream

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4314): the port probe is qualified at hangar VI 512/origin
`0x006AB400`, with both positive controls and 16,384 keyed reads. The retail
oracle passed its whole-RDRAM control and recorded 5.46M target reads, but the
new detail stream began with `0x8008FCE8,0x17DA40,0x17DA40`, not the s4313
boundary `0x8008FCE8,0x17D9E0,0x8017D9F8`. This is an instrument/route
qualification failure, not evidence of a retail divergence.

Competing hypotheses:

- H-filter: the s4313 oracle selected a narrower consumer-read stream; the
  broad physical watch currently includes unrelated target-block traversal.
- H-route: the current retail save/input/video route reaches a different
  stream state than the s4313 qualified route.
- H-port: the port's first tuple is not stable under the current seeded route.

Discriminator: one oracle build/run must emit a phase-tagged target read table
with the executing PC, address, value, and VI origin, while also watching the
consumer PC `0x8008FCE8`. The first tuple after the first hangar-phase
consumer-PC hit is compared with the known s4313 boundary and the first 256
port rows. If it reproduces `0x8008FCE8 @ 0x17D9E0 -> 0x8017D9F8`, the exact
filter is requalified and the 16,384 comparison can resume. If it differs
again, classify H-route or H-port using the phase-tagged table; do not call it
a game mismatch. Missing whole-RDRAM control, title/hangar phases, or consumer
PC hits invalidates the run.

Before building, inspect the s4313 oracle implementation/history and the
current `tools/oracle/rs64_oracle.c` watch-detail path. Then build once:

    ./tools/oracle/build.sh

Run from the repository root with Rice video, the whole-RDRAM positive control,
target physical watch `0x17D000:0x17E200`, consumer PC watch `0x8008FCE8`, and
the documented eleven `start` presses. Keep `RS64_DETAIL_HANGAR_READ=1` and
phase-tag every emitted row. No port change or mitigation is authorised.
