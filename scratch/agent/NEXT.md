# NEXT work unit — census the port-side PCM writer/source edge

HYPOTHESIS-ID: m5-port-pcm-writer-source

The corrected s3373 port run reached both target phases with live audio-task,
PCM, and filter controls. Its named `m5-consumer-entry` marker stayed at zero,
but task joins showed consumer matches and completions; PCM source and
consumer rows were present with `nz=0`. Retail ground truth now shows a
nonzero guest writer for the same primary spans. This names a port-side
writer/source gap, not permission to modify a gate or consumer.

Competing hypotheses:

- `H-PortWriterAbsent`: the port has no execution/store path corresponding to
  retail `0x800078EC` for the primary spans.
- `H-PortWriterPresentButZero`: the port executes the corresponding writer
  path, but its source/value is zero before the PCM callback.
- `H-PortPCMJoinMisattribution`: the port's zero rows are not the same physical
  spans as the retail writer ranges.

Discriminating measurement: first use the oracle's whole-RDRAM positive
control, then enumerate every port-side store/copy source for
`0x166450..0x166750`, `0x169150..0x169450`, and `0x168E50..0x169150` in one
regeneration-surviving instrument. A matching port writer with zero source
selects `H-PortWriterPresentButZero`; no matching writer selects
`H-PortWriterAbsent`; rows outside the three ranges select
`H-PortPCMJoinMisattribution`. Do not change behavior.

Preparation: use the existing fixed port route and follow the regeneration
order. Batch the writer/source census into one build and one run; positive
controls must include host/task/PCM plus title and hangar phase markers. Do
not change waits, slots, status handling, consumer dispatch, or PCM writeback
until the writer source is named.
