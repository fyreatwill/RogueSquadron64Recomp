# NEXT work unit — independently qualify the zero PCM output writer

HYPOTHESIS-ID: m5-zero-pcm-output-writer

The corrected s3373 port run reached both target phases with live audio-task,
PCM, and filter controls. Its named `m5-consumer-entry` marker stayed at zero,
but task joins showed consumer matches and completions; PCM source and
consumer rows were present with `nz=0`. This is a provisional output-data
gap, not permission to modify a gate or consumer.

Competing hypotheses:

- `H-RetailZeroPCMIsLegitimate`: retail writes the observed zero PCM spans as
  a legitimate silence/clear path; the port matches the same writer/value.
- `H-PortPCMWriterGap`: retail has a guest writer/value transition for the
  destination spans that is absent from the port, despite task completion.
- `H-PortPCMJoinMisattribution`: the port PCM join observes a different
  buffer than retail's output consumer, so the zero result is a join-key error.

Discriminating measurement: first use the oracle's whole-RDRAM positive
control, then one retail target-phase watch for the exact PCM destination
spans already emitted by `[pcm-boundary-source]` and
`[pcm-boundary-consumer]`, recording guest PC, value/hash, and ordering. In
the same iteration compare those spans with the existing port rows and
controls; do not change behavior. Retail writer/value matching port selects
`H-RetailZeroPCMIsLegitimate`; a retail nonzero/clear writer absent from port
selects `H-PortPCMWriterGap`; mismatched addresses or ordering selects
`H-PortPCMJoinMisattribution`. Missing whole-RDRAM control makes the run
invalid and selects nothing.

Preparation: read `tools/oracle/README.md`, identify the existing watch and
positive-control recipe, and do not build a new port instrument first. Arm
both retail watches in one run, retaining title `1024 @ 0x00790400` and
hangar `512 @ 0x006AB400` controls. Use the existing fixed port recipe only
for comparison if the oracle control passes. Do not change waits, slots,
status handling, consumer dispatch, or PCM writeback until the independent
writer/value result names one legitimate edge.
